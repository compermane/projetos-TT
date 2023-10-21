from main import *
from datetime import date
import subprocess
import os

CSV_REPOS = 'repos_csv.csv'
PRE_REPOS = 'pre_repos.csv'
REPOS_TO_CLONE = 'flaky_repos.csv'
REPOS_TO_FLAPY = 'repos_to_flapy.csv'

if __name__ == '__main__':
    data = date.today()
    directory = 'FlaPy-Repos-' + str(data)
    subprocess.run(["mkdir", directory])

    preRepos = dict()
    preRepos = reader(REPOS_TO_CLONE)

    # Executa o flapy para cara repositorio separadamente
    for hash in preRepos:
        cwd = os.getcwd()
        cloning(preRepos, hash)
        numRuns = preRepos[hash][2]
        writer(preRepos[hash])
        os.chdir(cwd)
        flapper(directory, REPOS_TO_FLAPY, numRuns)
        depipping(preRepos, hash)