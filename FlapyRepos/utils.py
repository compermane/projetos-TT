import csv
import os
import subprocess
from typing import Dict, Tuple

def cloning(repos: Dict, hash: str) -> None:
    """ (descontinuado) Realiza o cloning de um repositório, dado o dicionário de repositórios e sua respectiva chave.
    :param repos: dicionário de repositórios
    :param hash: hash do repositório a ser clonado
    :returns: None
    """
    cwd = os.getcwd() + "/Repos"
    os.chdir(cwd)
    nome = repos[hash][0]
    url = repos[hash][1]

    # Roda o git clone
    subprocess.run(["git", "clone", url])

    # Entra na pasta do repositorio clonado
    os.chdir(cwd + "/" + nome)

    # Faz o checkout para o commit da hash
    subprocess.run(["git", "checkout", hash])

    pipping()

def pipping() -> None:
    """ (descontinuado) Realiza a instalação das dependências de um repositório. Recomendado utilizar junto com a função cloning()
    :returns: None
    """
    subprocess.run(["pip", "install", "-r", "requirements.txt"])

def depipping(repos: Dict, hash: str) -> None:
    """ (descontinuado) Realiza a desinstalação das dependências de um repositório.
    :param repos: dicionário de repositórios
    :param hash: hash do repositório dentro do dicionário
    :returns: None
    """
    comando = 'pip uninstall -r requirements.txt -y'
    cwd = os.getcwd()

    nome = repos[hash][0]
    os.chdir(os.getcwd() + "/Repos/" + nome)
    os.system(comando)
    os.chdir(cwd)

def flapper(directory: str, csv: str, numRuns: int) -> None:
    """ Realiza a execução do FlaPy.
    :param directory: diretório de saída dos resultados
    :param csv: arquivo .csv contendo os repositórios de teste
    :param numRuns: número de execuções dos testes do repositório
    :returns: None
    """
    p1 = subprocess.Popen("./flapy.sh run --plus-random-runs --out-dir %s %s %s" % (str(directory), str(csv), str(numRuns)), shell = True)
    p1.wait()

def reader(csv_name: str) -> Dict:
    """ Realiza a leitura de um arquivo .csv e retorna informações dos repositórios contidos nele.
    :param csv_name: nome do arquivo .csv
    :returns: Dict, o qual cada chave é o GitHash do repositório que relaciona a uma tupla contendo o nome do repositório, sua URL e a quantidade de execuções segundo o FlaPy
    """
    subprocess.run(["mkdir", "Repos"])
    with open(csv_name, 'r') as csv_flapy:
        repos = dict()
        csv_reader = csv.DictReader(csv_flapy, delimiter = ',')
        for row in csv_reader:
            # Representa um repositorio com seu respectivo commit hash em uma tupla.
            # Cada chave do dicionario eh uma 
            repos[row["Project_Hash"]] = (row["Project_Name"], row["Project_URL"], row["Num_Runs"])
        csv_flapy.close()    

    return repos

def writer(repos: Tuple, hash: str) -> None:
    """ Realiza a escrita de um arquivo .csv contendo informações de um repositório para a execução do FlaPy
    :param repos: tupla contendo informação do repositório
    :param hash: hash do repositório
    :returns: None
    """
    with open('repos_to_flapy.csv', 'w', newline = '') as toFlapy:
        writer = csv.writer(toFlapy)
        header = ["PROJECT_NAME", "PROJECT_URL", "PROJECT_HASH", "PYPI_TAG", "FUNCS_TO_TRACE", "TESTS_TO_BE_RUN", "NUM_RUNS"]
        writer.writerow(header)

        row = [repos[0], repos[1], hash, None, None, None, repos[2]]
        writer.writerow(row)

        toFlapy.close()

def getFlakyRepos() -> None:
    """ Escreve em um .csv os repositórios que contém pelo menos 1 flaky test.
    :returns: None
    """
    with open("TestsOverview.csv", "r", encoding = "utf8") as flapy_csv:
        reader = csv.DictReader(flapy_csv, delimiter = ",")
        flaky_repos = dict()

        for row in reader:
            if (row["Verdict_sameOrder"] == "Flaky" or row["Verdict_randomOrder"] == "Flaky") and row["Project_Hash"] not in flaky_repos:
                flaky_repos[row["Project_Hash"]] = (row["Project_Name"], row["Project_URL"], row["Project_Hash"], row["#Runs_sameOrder"])

        flapy_csv.close()

    with open("flaky_repos.csv", "w", newline = '') as flapy_csv:
        writer = csv.writer(flapy_csv)
        header = ["Project_Name", "Project_URL", "Project_Hash", "Num_Runs"]
        writer.writerow(header)

        for hash in flaky_repos:
            row = [flaky_repos[hash][0], flaky_repos[hash][1], flaky_repos[hash][2], flaky_repos[hash][3]]
            writer.writerow(row)

        flapy_csv.close()

def writeLog(repo_name: str, time_taken: float, observacoes: str = "Nenhuma") -> None:
    """ Escreve um "log", contendo informações sobre a execução do FlaPy sobre um determinado repositório.
    :param repo_name: nome do repositório
    :param time_taken: tempo de execução do FlaPy (em horas)
    :param observacoes: observação da execução, caso haja
    :returns: None
    """
    with open("log.txt", "a", encoding = "utf8") as logFile:
        print(f"{repo_name}: {time_taken} Observacoes: {observacoes}", file = logFile)
        logFile.close()

def getNonOrderDependentRepos(csv_repos: str) -> None:
    """ Escreve, em um arquivo .csv, repositórios que possuam pelo menos 1 teste flaky NOD
    :param csv_repos: .csv inicial contendo os repositórios e os vereditos dos testes
    :returns: None
    """
    with open(csv_repos, "r", encoding = "utf8") as csvFile:
        reader = csv.DictReader(csvFile, delimiter = ",")
        repos = dict()

        for row in reader:
            if row["Verdict_sameOrder"] == "Flaky" and row["Project_Hash"] not in repos:
                repos[row["Project_Hash"]] = (row["Project_Name"], row["Project_URL"], row["Project_Hash"], row["#Runs_sameOrder"])

        csvFile.close()

    with open("nonOrderDependent.csv", "w", encoding = "utf8", newline = "") as csvFile:
        writer = csv.writer(csvFile)
        header = ["Project_Name", "Project_URL", "Project_Hash", "Num_Runs"]
        writer.writerow(header)

        for hash in repos:
            row = [repos[hash][0], repos[hash][1], repos[hash][2], repos[hash][3]]
            writer.writerow(row)

        csvFile.close()

def diff(csv1: str, csv2: str) -> None:
    """ (descontinuado) Realiza a diferença entre dois .csv e escreve em outro .csv
    :param csv1: uma das planilhas
    :param csv2: a outra planilha
    :returns: None
    """
    repos1 = dict()
    repos1 = reader(csv1)

    repos2 = dict()
    repos2 = reader(csv2)

    keys_to_remove = set(repos1.keys()) & set(repos2.keys())

    for key in keys_to_remove:
        del repos1[key]

    with open("diff.csv", "w", encoding = "utf8", newline = "") as diff:
        writer = csv.writer(diff)
        header = ["Project_Name", "Project_URL", "Project_Hash", "Num_Runs"]
        writer.writerow(header)

        for hash in repos1:
            row = [repos1[hash][0], repos1[hash][1], hash, repos1[hash][2]]
            writer.writerow(row)

        diff.close()