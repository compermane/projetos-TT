import csv
import os
import random

def cloning(repos: dict()) -> None:
    os.chdir(os.getcwd() + '/Repos')
    for hash in repos: 
        nome = repos[hash][0]
        url = repos[hash][1]
        comando = 'git clone ' + url
        os.system(comando)
        cwd = os.getcwd()
        os.chdir(cwd + "/" + nome)
        comando = 'git checkout ' + hash
        os.system(comando)
        pipping()
        os.chdir(cwd)

def pipping() -> None:
    comando = 'pip install -r requirements.txt'
    try:
        os.system(comando)
    except OSError as e:
        print(f"Nao foi possivel instalar as dependencias: {e}")

def depipping() -> None:
    comand = 'pip uninstal -r requirements.txt -Y'

def reader(csv_name: str) -> dict():
    os.system('mkdir Repos')
    with open(csv_name, 'r') as csv_flapy:
        repos = dict()
        csv_reader = csv.DictReader(csv_flapy, delimiter = ',')
        for row in csv_reader:
            # Representa um repositorio com seu respectivo commit hash em uma tupla.
            # Cada chave do dicionario eh uma 
            repos[row["Project_Hash"]] = (row["Project_Name"], row["Project_URL"], row["Num_Runs"])
        csv_flapy.close()    

    return repos

def writer() -> None:
    with open('repos_csv.csv', 'a', newline = '') as repos_csv:
        writer =  csv.writer(repos_csv)
        header = ["Project_Hash", "Project_Name", "Project_URL", "Num_Runs"]
        writer.writerow(header)

        with open('TestsOverview.csv', 'r', encoding = "utf8") as flapy_repos:
            reader = csv.reader(flapy_repos)

            randRepo = random.choice(list(reader))
            name = randRepo[0]
            url = randRepo[1]
            hash = randRepo[2]
            runs = randRepo[11]
            writer.writerow([hash, name, url, runs])

            flapy_repos.close()

        repos_csv.close()

def getNumRuns(repos: dict()) -> int:
    for hash in repos:
        num = repos[hash][2]

    return num