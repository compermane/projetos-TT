import csv
import re
import subprocess
import contextlib
import ast
from . import VirtualEnvironment
from . import analise
from os import path, getcwd, chdir
from sys import builtin_module_names
from typing import List, Tuple, Generator, Any
from pathlib import Path
from shutil import rmtree

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
            name = getRepoName(url)
            if len(name.split(".")) > 1:
                self._name = name.split(".")[0]
            else:
                self._name = name

            
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
    
    def deleteRepoDirectory(self) -> None:
        rmtree(self.name)
    
def activateVenv(venv_dir: str) -> None:
    if venv_dir:
        activate_command = [f"source '{venv_dir}/bin/activate'"]
        subprocess.Popen(activate_command, shell = True, executable = "/bin/bash")

@contextlib.contextmanager
def venv(venv_dir: Path, root_dir: str, requirements: List[str]) -> Generator[VirtualEnvironment.VirtualEnvironment, Any, None]:
    v = VirtualEnvironment.VirtualEnvironment(venv_dir, root_dir, requirements)
    try:
        yield v
    finally:
        # v.cleanUp()
        pass

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
    urlPattern = r'https?://github\.com/[\w-]+/([\w-]+)(?:\.git)?$'
    match = re.match(urlPattern, gitUrl)
    if match:
        return match.group(1)
    else:
        raise NoRepositoryNameException(f"Nenhum nome de repositório para {gitUrl}")

def getRepoRequirements(repo: Repository) -> List[str]:
    """ Obtem os requirements de um repositório.
    :param repo: Repositório
    :returns: Lista contendo os arquivos de dependências do repositório
    """
    return list(Path(repo.name).glob("*requirements*.txt"))

def activating(repo: Repository) -> None:
    """Ativa um repositório, instalando suas depências dentro de seu venv
    :param repo: Repositório a ter seu venv ativado
    :returns: None
    """
    venvPath = f"venv-{repo.name}"
    activate = path.join(venvPath, "bin", "activate")

    requirementsFile = path.abspath(path.join(repo.name, "requirements.txt"))
    subprocess.call(f"source {activate}", shell = True, executable="/bin/bash" if "posix" in builtin_module_names else None)

    # Instalação de dependências do repositório
    try:
        subprocess.run([path.join(venvPath, "bin", "pip"), "install", "-r", path.join(repo.name, requirementsFile)], check=True)
    except:
        print("Não há arquivo de requirements")

    # Instalação de dependências do plugin
    subprocess.run([path.join(venvPath, "bin","pip"), "install", "-r", "requirements.txt"], check=True)

def venving(repo: Repository) -> None:
    """Cria um virtual environment (venv; não confundir com a biblioteca virtual-environment) para um repositório
    :param repo: Repositório a ser criado o venv
    :returns: None
    """
    p1 = subprocess.Popen(["python3", "-m", "venv", f"venv-{repo.name}"])
    p1.wait()

    return

def cloning(repo: Repository) -> None:
    """Faz o clone de um repositório e realiza o checkout para o commit indicado
    :param repo: Repositório para ser clonado
    :returns: None
    """
    cwd = getcwd()

    p1 = subprocess.Popen(["git", "clone", repo.url])
    p1.wait()

    chdir(repo.name)

    p1 = subprocess.Popen(["git", "checkout", repo.githash])
    p1.wait()

    chdir(cwd)
    return

def checkIfClassExist(file_path: str, className: str) -> bool:
    """ (deprecated) Verifica a existência de uma classe em um arquivo.
    :param file_path: Caminho para o arquivo
    :param className: Nome da classe a ser procurada
    :returns: True caso a classe exista, false caso contrário
    """
    try:
        with open(file_path, "r") as f:
            tree = ast.parse(f.read())

            for node in tree.body:
                if isinstance(node, ast.ClassDef) and node.name == className:
                    return True

            return False
    except Exception as e:
        print(f"Erro durante checagem por classe: {e}")

def checkForDots(test_node: str) -> bool:
    """ Verifica a existência de pontos em um test node
    :param test_node: Node a ser verificado
    :returns: True caso exista, False caso contrário
    """
    if len(test_node.split("/")[0].split(".")) > 1:
        return True
    
    return False

def runSpecificTests(repo: Repository, mod_name: str, params: List[bool], test_node: str, no_runs: int,
                     env_path: Path) -> None:
    """ Executa um teste específico.
    :param repo: Repositório do teste
    :param mod_name: Nome do repositório de teste
    :param params: Parâmetros da execução do teste
    :param test_node: Node de execução do teste
    :param no_runs: Quantidade de execuções de um teste
    :returns: None
    """
    cwd = getcwd()
    requirements = getRepoRequirements(repo)

    include_tracing = params[0]
    include_coverage = params[1]
    include_profiling = params[2]
    
    test_name = test_node.split("::")[-1]
    test_file = test_node.split("::")[0]
    class_name = ""

    subprocess.run(["mkdir", f"Test-{mod_name}"])
    
    if len(test_node.split("::")) == 3:
        class_name = test_node.split("::")[-2]

    if not path.exists(mod_name):
        cloning(repo)

    run_summary = []
    total_time = 0
    failed_count = 0
    passed_count = 0 
    skipped_count = 0
    xfailed_count = 0

    class_exist = checkIfClassExist(test_file, class_name)
    dotted_repo_name = checkForDots(test_node)

    # gamble.git/tests/models/test_cards.py::test_deck_init
    if dotted_repo_name:
        aux_node = test_node.split(".")[0]

        for node in test_node.split("/")[1:]:
            aux_node += "/" + node

        test_node = aux_node

    chdir(f"Test-{mod_name}")
    subprocess.run(["mkdir", test_name])
    chdir(test_name)
    test_cwd = getcwd()

    with venv(env_path, cwd, requirements) as env:
        chdir(cwd)
        env.runCommands()
        chdir(test_cwd)
        for run in range(no_runs):
            subprocess.run(["mkdir", f"Run-{run}"])

            results: Tuple = tuple()
            if class_exist:
                results = env.executePytest(test_node = test_node, params = [include_tracing, include_coverage, include_profiling],
                                        output_dir = cwd + f"/Test-{mod_name}/{test_name}/Run-{run}", origin_dir = cwd)
            else:
                results = env.executePytest(test_node = test_node.split("::")[0] + "::" + test_node.split("::")[-1], params = [include_tracing, include_coverage, include_profiling],
                                        output_dir = cwd + f"/Test-{mod_name}/{test_name}/Run-{run}", origin_dir = cwd)
            total_time += results[1]
            passed_count += results[2]
            failed_count += results[3]
            skipped_count += results[4]
            xfailed_count += results[5]
            run_summary.append(f"Run {run}: {results[0]} Tempo: {results[1]}\n")

        env.uninstallDependencies()
        chdir(cwd + f"/Test-{mod_name}/{test_name}")

    run_summary.append(f"Tempo total: {total_time}\n")
    if skipped_count != 0:
        run_summary.append("Resultado: SKIPPED")
    elif xfailed_count != 0:
        run_summary.append("Resultado: XFAILED")
    else:
        if passed_count == 0 and failed_count != 0:
            run_summary.append("Resultado: FAILED")
        elif passed_count != 0 and failed_count == 0:
            run_summary.append("Resultado: PASSED")
        elif passed_count !=0 and failed_count !=0:
            run_summary.append("Resultado: FLAKY")

    with open("runsSummary.txt", "a") as f:
        f.writelines(run_summary)

    chdir(cwd)
    # repo.deleteRepoDirectory()
