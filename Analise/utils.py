import csv
import re
import subprocess
from os import listdir, getcwd, path
from sys import builtin_module_names
from typing import List, Tuple

class NoRepositoryNameException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class Repository:
    def __init__(self, url: str, noruns: str, githash = ".", isgitrepo = False) -> None:
        self._url = url
        self._noruns = noruns
        self._githash = githash
        self._isgitrepo = isgitrepo

        if isgitrepo:
            self._name = getRepoName(url)
        else:
            self._name = url
    
    @property
    def url(self):
        return self._url
    
    @property
    def noruns(self):
        return self._noruns
    
    @property
    def githash(self):
        return self._githash
    
    @property
    def name(self):
        return self._name
    
def readCSV(fileName: str) -> List[Repository]:
    """Lê um arquivo CSV, obtendo informações de repositório e número de runs
    :param fileName: Nome do arquivo CSV
    :returns: Lista com informações de repositório e seu determinado número de runs
    """
    with open(fileName, "r") as f:
        repos = list()
        csv_reader = csv.DictReader(f, delimiter = ",")

        for row in csv_reader:
            repos.append(Repository(url = row["Repo"], noruns = row["#Runs"], githash = row["GitHash"], isgitrepo = isGithubRepo(row["Repo"])))

    f.close()
    return repos

def isGithubRepo(repoName: str) -> bool:
    """Lê uma string e determina se a string se refere a um repositório do Github
    :param repoName: String a ser testada. Obtida após execução de readCSV
    :returns: Booleano (true se repoName é um repositório do Github e false caso contrário)
    """
    urlPattern = re.compile(r'^https?://github\.com/([a-zA-Z0-9-]+)/([a-zA-Z0-9-]+)$')
    
    return bool(re.match(urlPattern, repoName))

def getRepoName(gitUrl: str) -> str:
    """Lê uma URL do github e extrai o nome do repositório
    :param gitUrl: URL do github
    :returns: String do nome do repositório
    """
    urlPattern = r'ĥttps?://github\.com/\w+/(\w+)$'
    match = re.match(urlPattern, gitUrl)

    if match:
        return match.group(1)
    else:
        raise NoRepositoryNameException(f"Nenhum nome de repositório para {gitUrl}")

def activating(repo: Repository) -> None:
    venvPath = f"venv-{repo.name}"
    activate = path.join(venvPath, "bin", "activate")

    requirementsFile = path.abspath(path.join(repo.name, "requirements.txt"))
    subprocess.call(f"source {activate}", shell = True, executable="/bin/bash" if "posix" in builtin_module_names else None)
    subprocess.run([path.join(venvPath, "bin", "pip"), "install", "-r", path.join(repo.name, requirementsFile)], check=True)


def venving(repo: Repository) -> None:
    p1 = subprocess.Popen(["python3", "-m", "venv", f"venv-{repo.name}"])
    p1.wait()

    return

def cloning(repo: Repository) -> None:
    """Faz o clone de um repositório e realiza o checkout para o commit indicado
    :param repo: Repositório para se clonado
    :returns: None
    """
    p1 = subprocess.Popen(["git", "clone", repo.url])
    p1.wait()

    p1 = subprocess.Popen(["git", "checkout", repo.githash])
    p1.wait()

    return