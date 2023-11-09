import csv
import os
import subprocess

def cloning(repos: dict(), hash: str) -> None:
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
    subprocess.run(["pip", "install", "-r", "requirements.txt"])

def depipping(repos: dict(), hash: str) -> None:
    comando = 'pip uninstall -r requirements.txt -y'
    cwd = os.getcwd()

    nome = repos[hash][0]
    os.chdir(os.getcwd() + "/Repos/" + nome)
    os.system(comando)
    os.chdir(cwd)

def flapper(directory: str, csv: str, numRuns: int) -> None:
    p1 = subprocess.Popen("./flapy.sh run --plus-random-runs --out-dir %s %s %s" % (str(directory), str(csv), str(numRuns)), shell = True)
    p1.wait()

"""
    Retorna um dicionario contendo informacoes sobre o nome do projeto, URL do projeto
    e numero de runs de cada repositorio do artigo do FlaPy. 
"""
def reader(csv_name: str) -> dict():
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

"""
    Escreve um csv de acordo com o modo:
    1: escolher os repositorios de TestsOveview
    2: montar um csv com os repositorios ja escolhidos
"""
def writer(repos, hash) -> None:
    with open('repos_to_flapy.csv', 'w', newline = '') as toFlapy:
        writer = csv.writer(toFlapy)
        header = ["PROJECT_NAME", "PROJECT_URL", "PROJECT_HASH", "PYPI_TAG", "FUNCS_TO_TRACE", "TESTS_TO_BE_RUN", "NUM_RUNS"]
        writer.writerow(header)

        row = [repos[0], repos[1], hash, None, None, None, repos[2]]
        writer.writerow(row)

        toFlapy.close()

"""
    Funcao para obter os repositorios com pelo menos 1 flaky test
"""
def getFlakyRepos() -> None:
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

def writeLog(repo_name: str, time_taken: float, observacoes = "Nenhuma") -> None:
    with open("log.txt", "a", encoding = "utf8") as logFile:
        print(f"{repo_name}: {time_taken} Observacoes: {observacoes}", file = logFile)
        logFile.close()

def getNonOrderDependentRepos(csv_repos: str) -> None:
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