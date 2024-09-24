import csv
from typing import List, Tuple, Dict

def getReproducedResultsRepos(csv_name: str) -> List[Tuple[str, str]]:
    """ Obtem repositórios onde o experimento com o Flapy foi reproduzidos
    :param csv_name: Nome do CSV contendo os repositórios reproduzidos
    :returns: Lista com tuplas onde tupla[0] é o nome do repositório e tupla[1] é o seu respectivo git hash
    """
    with open(csv_name, "r", encoding = "utf8") as results:
        resultsDict = csv.DictReader(results, delimiter = ",")
        repos: List[Tuple[str, str]] = list()

        for row in resultsDict:
            if row["RESULTADO"] == "Resultados reproduzidos" and row["# testes Flaky"] != None and int(row["# testes Flaky"]) > 0:
                repos.append((row["NOME"], row["GIT_HASH"]))

        results.close()

    return repos

def getFlakyTestsFromRepos(repos: List[Tuple[str, str]]) -> List[Tuple[str, ...]]:
    """ Obtem os testes flaky dos repositórios onde o experimento com o Flapy foi reproduzido
    :param repos: Lista contendo tuplas do nome do repositório e seu respectivo git hash
    :returns: Listade tuplas contendo informações gerais do teste flaky
    """
    with open("TestsOverview.csv", "r", encoding = "utf8") as testsOverview:
        csvReader = csv.DictReader(testsOverview, delimiter = ",")
        testsInfo: List[Tuple[str, ...]] = list()

        for repo in repos:
            testsOverview.seek(0)
            csvReader = csv.DictReader(testsOverview, delimiter = ",")
            for row in csvReader:
                if (row["Project_Name"] == repo[0] or row["Project_Hash"] == repo[1]) and row["Verdict_sameOrder"] == "Flaky":
                    testsInfo.append((row["Project_Name"], row["Project_URL"], row["Project_Hash"], 
                                      row["Test_filename"], row["Test_classname"].split(".")[-1], row["Test_funcname"], row["Test_parametrization"],
                                      row["#Runs_sameOrder"]))

    return testsInfo

def nodeBuilder(testsInfo: List[Tuple[str, ...]]) -> None:
    """ Constroi o test node dado informações sobre o teste.
    :param testsInfo: lista com as informações sobre os testes (nome, url, hash, filename, classname, funcname, parametrization, #runs)
    :returns: None
    """
    reposWithTests: Dict[str, List[str]] = dict()

    for test in testsInfo:
        if test[0] in reposWithTests:
            if test[4] is None and test[6] is None:
                reposWithTests[test[0]].append(f"{test[0]}/{test[3]}::{test[5]}")
            elif test[4] is not None and test[6] is None:
                reposWithTests[test[0]].append(f"{test[0]}/{test[3]}::{test[4]}::{test[5]}")
            elif test[4] is None and test[6] is not None:
                reposWithTests[test[0]].append(f"{test[0]}/{test[3]}::{test[5]}{test[6]}")
            else:
                reposWithTests[test[0]].append(f"{test[0]}/{test[3]}::{test[4]}::{test[5]}{test[6]}")
        else:
            if test[4] is None and test[6] is None:
                reposWithTests[test[0]] = [test[1], test[2], test[7], f"{test[0]}/{test[3]}::{test[5]}"]
            elif test[4] is not None and test[6] is None:
                reposWithTests[test[0]] = [test[1], test[2], test[7], f"{test[0]}/{test[3]}::{test[4]}::{test[5]}"]
            elif test[4] is None and test[6] is not None:
                reposWithTests[test[0]] = [test[1], test[2], test[7], f"{test[0]}/{test[3]}::{test[5]}{test[6]}"]
            else:
                reposWithTests[test[0]] = [test[1], test[2], test[7], f"{test[0]}/{test[3]}::{test[4]}::{test[5]}{test[6]}"]

    with open("reproducedTests.csv", "w") as results:
        writer = csv.writer(results)

        header = ["Name", "URL", "Hash", "Test", "No_Runs"]
        writer.writerow(header)

        for key in reposWithTests:
            for test in reposWithTests[key]:
                if "::" in test:
                    row = [key, reposWithTests[key][0], reposWithTests[key][1], test, reposWithTests[key][2]]
                    writer.writerow(row)

        results.close()

if __name__ == "__main__" :
    nodeBuilder(getFlakyTestsFromRepos(getReproducedResultsRepos("FlaPy-Repos.csv")))