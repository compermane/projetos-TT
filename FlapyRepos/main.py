import csv
import os
import random
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
    subprocess.Popen("./flapy.sh run --plus-random-runs --out-dir %s %s %s" % (str(directory), str(csv), str(numRuns)), shell = True)

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
def writer(repos = tuple) -> None:
    with open('repos_to_flapy.csv', 'w', encoding = "utf8") as toFlapy:
        writer = csv.writer(toFlapy)
        header = ["Project_Name", "Project_URL", "Project_Hash", "Num_Runs"]
        writer.writerow(header)

        row = [repos[0], "./Repos/" + repos[0], repos[1], repos[2]]
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

def getFlakyReposSmall() -> None:
    with open("TestsOverview.csv", "r", encoding = "utf8") as flapy_csv:
        reader = csv.DictReader(flapy_csv, delimiter = ",")
        flaky_repos_small = dict()

        for row in reader:
            if (row["Verdict_sameOrder"] == "Flaky" or row["Verdict_randomOrder"] == "Flaky") and row["Project_Hash"] not in flaky_repos_small:
                flaky_repos_small[row["Project_Hash"]] = [row["Project_Name"], row["Project_URL"], row["Project_Hash"], row["#Runs_sameOrder"], 0]
        
        flapy_csv.seek(0)
        
        for row in reader:
            if row["Project_Hash"] in flaky_repos_small:
                flaky_repos_small[row["Project_Hash"]][4] += 1

        flapy_csv.close()

    with open("flaky_repos_small.csv", "w", newline = '') as flaky_csv_small:
        writer = csv.writer(flaky_csv_small)
        header = ["Project_Name", "Project_URL", "Project_Hash", "Num_Runs"]
        writer.writerow(header)

        for hash in flaky_repos_small:
            if flaky_repos_small[hash][4] <= 30:
                print(f"{flaky_repos_small[hash][0]}: {flaky_repos_small[hash][4]}")
                row = [flaky_repos_small[hash][0], flaky_repos_small[hash][1], flaky_repos_small[hash][2], flaky_repos_small[hash][3]]
                writer.writerow(row)

        flaky_csv_small.close()

def reorganize() -> None:
    with open("TestsOverview.csv", "r", encoding = "utf8") as flapy_csv:
        reader = csv.DictReader(flapy_csv, delimiter = ',')

        with open("TestsOverviewReorganized.csv", "w", encoding = "utf8", newline = '') as result:
            writer = csv.writer(result)
            header = ["Project_Name", "Test_funcname", "Verdict_sameOrder", "Verdict_randomOrder"]
            writer.writerow(header)
            for row in reader:
                writer.writerow([row["Project_Name"], row["Test_funcname"], row["Verdict_sameOrder"], row["Verdict_randomOrder"]])

            result.close()
        flapy_csv.close()

reorganize()