from Analise import analise, utils, VirtualEnvironment
from os import chdir, getcwd, path
from typing import List
from time import sleep
import argparse
import csv
import subprocess
import shutil

def str_to_bool(value: str) -> bool:
    if value.lower() in {"true", "t"}:
        return True
    elif value.lower() in {"false", "f"}:
        return False
    else:
        raise argparse.ArgumentTypeError(f"Valor booleano invalido: {value}")

def str_to_int(value: str) -> int:
    if value.isdigit() and int(value) > 0:
        return int(value)
    raise argparse.ArgumentTypeError(f"Valor inteiro invalido: {value}")

def argsDefiner():
    # Criando um objeto ArgumentParser
    parser = argparse.ArgumentParser()

    # Adicionando parâmetros command-line
    parser.add_argument("--repo-dir", help = "Diretorio para o repositorio", type = str, default = "")
    parser.add_argument("--repo-name", help = "Nome do repositorio", type = str, default = "")
    parser.add_argument("--read-from-csv", help = "CSV com informações do repositório a ser lido", type = str, default = "")
    parser.add_argument("--output-dir", help = "Especificar o diretorio para onde os resultados de teste serao armazenados", default =  ".")
    parser.add_argument("--no-runs", help =  "Especificar a quantidade de rodadas que cada repositorio tera", type = str_to_int, default = 1)
    parser.add_argument("--include-test-tracing", help = "Determinar se a ferramenta deve executar o tracing de cada teste. O default eh False", type = str_to_bool, default = False)
    parser.add_argument("--include-test-coverage", help = "Determinar se a ferramenta deve executar o coverage de cada teste. O default eh False", type = str_to_bool, default = False)
    parser.add_argument("--include-test-profiling", help = "Determinar se a ferramente deve realizar o profiling dos testes. O default eh False", type = str_to_bool, default = False)
    parser.add_argument("--run-specific-test", help = "Rodar a ferramenta em testes específicos. Deve-se ser informados, em um csv, o nome do repositório, sua URL, seu GitHash, o node do teste e a quantidade de execuções.", type = str, default = "")
    parser.add_argument("--venv-dir", help = "Virtual environment associado a reprodução dos resultados", type = str, default = True)

    # Adicionando os parametros
    args = parser.parse_args()

    csvFile = args.read_from_csv
    tracing = args.include_test_tracing
    coverage = args.include_test_coverage
    profiling = args.include_test_profiling
    specificTests = args.run_specific_test
    venvDir = args.venv_dir

    if csvFile == "" and specificTests == "":
        # Obtendo os parametros especificados
        repo = args.repo_dir
        name = args.repo_name
        noruns = args.no_runs

        analise.runMultipleTimes(repo, name, noruns, [tracing, coverage, profiling])
    elif specificTests != "":
        if venvDir == "":
            raise ValueError("Nao foi informado um diretorio para o ambiente virtual")
        else:
            with open(specificTests, "r", encoding = "utf8") as csv_file:

                reader = list(csv.DictReader(csv_file,  delimiter = ","))
                if not reader:
                    print|("CSV vazio")
                else:

                    row = reader[0]
                        
                    repo_name = row["Name"]
                    repo_hash = row["Hash"]
                    repo_url = row["URL"]
                    test_no_runs = int(float(row["No_Runs"]))
                    test_node = row["Test"]

                    repo = utils.Repository(githash = repo_hash, url = repo_url, isgitrepo = True, noruns = str(test_no_runs))

                    utils.runSpecificTests(repo, repo_name, [tracing, coverage, profiling], test_node, test_no_runs, env_path = venvDir)
                    
                    shutil.rmtree(repo_name, ignore_errors=True) # Adicione ignore_errors para evitar falhas se o diretório não existir
                    sleep(1) # Reduza o tempo de espera para testes
                
                    chdir(getcwd()) # Volte para o diretório principal após remover o repositório

            if reader:
                with open(specificTests, mode="w", newline="") as csv_file:
                    fieldnames = reader[0].keys()
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(reader[1:])  # Escreve a partir da segunda linha

    elif csvFile != "" and specificTests == "":
        repos: List[utils.Repository] = utils.readCSV(csvFile)
        for repo in repos:
            utils.cloning(repo)
            utils.venving(repo)
            utils.activating(repo)
            analise.runMultipleTimes(repo.name, repo.name, int(repo.noruns), [tracing, coverage, profiling])
    test_dir = test_node.split('/')[0]
    test_name = test_node.split('/')[-1].split("::")[-1]
    if tracing:
        subprocess.run([f"python3","diff_finder.py",f"Test-{test_dir}/{test_name}","t","10","Function"])
    elif profiling:
        subprocess.run([f"python3","diff_finder.py",f"Test-{test_dir}/{test_name}","p","10","filename:lineno(function)"])
    elif coverage:
        subprocess.run([f"python3","diff_finder.py",f"Test-{test_dir}/{test_name}","c","10","Percentual de Cobertura (%)"])

def test_trace() -> None:
    files = analise.getTestFiles("analytic_shrinkage/nonlinshrink/test")
    tests = analise.getTestCases(files)
    cwd = getcwd()
    for file in files:
        for test in tests[file]:
            analise.traceFuncs("analytic_shrinkage/nonlinshrink/test/test_analytic_shrinkage.py", test, "analytic_shrinkage")
            analise.refineCovers("analytic_shrinkage", files)
            analise.getTestCoverage("analytic_shrinkage", test)
            chdir(cwd)

def test_settrace() -> None:
    dirs = analise.getTestDir(getcwd() + "/" + "analytic_shrinkage")
    
    for dir in dirs:
        analise.createTestFileCopy(dir)
        analise.implementTracer(dir)

def test_profiler() -> None:
    analise.profiling("analytic_shrinkage")

if __name__ == "__main__":
    argsDefiner()