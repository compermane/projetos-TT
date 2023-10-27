from utils import *
from datetime import date
import subprocess
import os
import time
import requests

CSV_REPOS = 'repos_csv.csv'
PRE_REPOS = 'pre_repos.csv'
REPOS_TO_CLONE = 'flaky_repos.csv'
REPOS_TO_FLAPY = 'repos_to_flapy.csv'

if __name__ == '__main__':
    cwd = os.getcwd()
    data = date.today()
    directory = 'FlaPy-Repos-' + str(data)
    subprocess.run(["mkdir", directory])

    preRepos = dict()
    preRepos = reader(REPOS_TO_CLONE)

    # Executa o flapy para cara repositorio separadamente
    for hash in preRepos:
        os.chdir(cwd)
        numRuns = preRepos[hash][2]
        url = preRepos[hash][1]
        http_code = requests.get(url)

        # Pula repositorios que ja nao existem
        if http_code.status_code == 404:
            writeLog(preRepos[hash][0], 0, "Repositorio nao existe mais")
            continue

        os.chdir(cwd)
        writer(preRepos[hash], hash)
        start = time.time()
        flapper(directory, REPOS_TO_FLAPY, int(float(numRuns)))
        end = time.time()
        writeLog(preRepos[hash][0], end - start)