from Analise import analise, utils
from os import chdir, getcwd, path
from typing import List
import argparse

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
    parser.add_argument("--repo_dir", help = "Diretorio para o repositorio", type = str, default = "")
    parser.add_argument("--repo_name", help = "Nome do repositorio", type = str, default = "")
    parser.add_argument("--read-from-csv", help = "CSV com informações do repositório a ser lido", type = str, default = "")
    parser.add_argument("--output-dir", help = "Especificar o diretorio para onde os resultados de teste serao armazenados", default =  ".")
    parser.add_argument("--no-runs", help =  "Especificar a quantidade de rodadas que cada repositorio tera", type = str_to_int, default = 1)
    parser.add_argument("--include-test-tracing", help = "Determinar se a ferramenta deve executar o tracing de cada teste. O default eh True", type = str_to_bool, default = True)
    parser.add_argument("--include-test-coverage", help = "Determinar se a ferramenta deve executar o coverage de cada teste. O default eh False", type = str_to_bool, default = False)
    parser.add_argument("--include-test-profiling", help = "DEterminar se a ferramente deve realizar o profiling dos testes. O default eh False", type = str_to_bool, default = False)

    # Adicionando os parametros
    args = parser.parse_args()

    csvFile = args.read_from_csv
    tracing = args.include_test_tracing
    coverage = args.include_test_coverage
    profiling = args.include_test_profiling

    if csvFile == "":
        # Obtendo os parametros especificados
        repo = args.repo_dir
        name = args.repo_name
        noruns = args.no_runs

        analise.runMultipleTimes(repo, name, noruns, [tracing, coverage, profiling])
    else:
        repos: List[utils.Repository] = utils.readCSV(csvFile)
        for repo in repos:
            utils.cloning(repo)
            utils.venving(repo)
            utils.activating(repo)
            analise.runMultipleTimes(repo.name, repo.name, int(repo.noruns), [tracing, coverage, profiling])

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
    # analise.traceDiff("Test-analytic_shrinkage")
    # analise.flakyFinder("Test-analytic_shrinkage")
    # print(path.abspath("analytic_shrinkage"))
    # print(ignoreSpaces(path.abspath("analytic_shrinkage")))
    # bruh = utils.Repository("analytic_shrinkage", 100)
    # utils.venving(bruh)
    # utils.activating(bruh)