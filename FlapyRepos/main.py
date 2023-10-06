import csv
import os
from time import sleep

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

if __name__ == "__main__":
    os.system('mkdir Repos')
    with open('teste.csv', 'r') as csv_flapy:
        repos = dict()
        csv_reader = csv.DictReader(csv_flapy, delimiter = ',')
        for row in csv_reader:
            # Representa um repositorio com seu respectivo commit hash em uma tupla.
            # Cada chave do dicionario eh uma 
            repos[row["Project_Hash"]] = (row["Project_Name"], row["Project_URL"])
        csv_flapy.close()    

    cloning(repos)