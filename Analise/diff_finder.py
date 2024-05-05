""" Funções para encontrar diferenças entre diversos traces
"""
from typing import List
from os import getcwd, chdir, listdir ,path
from random import choice
from difflib import unified_diff
import re


def readLines(fileName: str) -> List[str]:
    with open(fileName, "r") as f:
        lines = f.readlines()
    f.close()

    return lines

def flakyFinder(dirName: str) -> tuple:
    def extractRuns(line: str):
        matchFailed = re.search(r'Run (\d+): (\bFAILED\b) Tempo: (\d+\.\d+)', line)
        matchPassed = re.search(r'Run (\d+): (\bPASSED\b) Tempo: (\d+\.\d+)', line)
        matchEnd = re.search(r"Tempo total: (\d+\.\d+)", line)
        if matchFailed:
            runNo = int(matchFailed.group(1))
            status = matchFailed.group(2)
            timeTaken = float(matchFailed.group(3))
            return (runNo, status, timeTaken)
        elif matchPassed:
            runNo = int(matchPassed.group(1))
            status = matchPassed.group(2)
            timeTaken = float(matchPassed.group(3))
            return (runNo, status, timeTaken)
        elif matchEnd:
            return ("END")
        else:
            return None

    cwd = getcwd()
    tests = [test for test in listdir(getcwd() + f"/{dirName}") if path.isdir(path.join(getcwd() + f"/{dirName}", test))]
    
    for test in tests:
        failedIndex = list()
        passedIndex = list()
        chdir(f"{cwd}/{dirName}/{test}")
        with open("runsSummary.txt", "a+") as f:
            f.seek(0)
            i = 0
            for line in f:
                testResult = extractRuns(line)
                if testResult[0] == "END":
                    break
                if testResult[1] == "FAILED":
                    failedIndex.append(i)
                elif testResult[1] == "PASSED":
                    passedIndex.append(i)
                i += 1
            if len(passedIndex) != 0 and len(failedIndex) != 0:
                f.write("Veredito: FLAKY")
                selectedPassed = choice(passedIndex)
                selectedFailed = choice(failedIndex)

                f.write(f"\nEntre as runs {selectedPassed} e {selectedFailed}: \n")
                try:
                    trace = traceDiff(f"Run-{selectedPassed}/calls.txt", f"Run-{selectedFailed}/calls.txt")
                    if trace:
                        f.write("\nNo trace, foram encontradas as diferencas: \n")
                        for traceLine in trace:
                            f.writelines(traceLine)
                    else:
                        f.write("\nNenhuma diferença encontrada no trace.")
                except FileNotFoundError as e:
                    print(f"Opção para trace não escolhida. Erro: {e}")

                try:
                    stats = traceDiff(f"Run-{selectedPassed}/stats.txt", f"Run-{selectedFailed}/stats.txt")
                    if stats:
                        f.write("\nNo profiler, foram encontradas as diferencas: \n")
                        for statsLine in stats:
                            f.writelines(statsLine)
                    else:
                        f.write("\nNenhuma diferença encontrada no profiler\n")
                except FileNotFoundError as e:
                    print(f"Opção para profiling não escolhida. Erro: {e}")

            elif len(passedIndex) == 0 or len(failedIndex) == 0:
                f.write("Veredito: NOT FLAKY")
                if len(passedIndex) == 0:
                    selectedFailedA = choice(failedIndex)
                    selectedFailedB = choice(failedIndex)

                    while selectedFailedA == selectedFailedB:
                        selectedFailedB = choice(failedIndex)

                    f.write(f"\nEntre as runs {selectedFailedA} e {selectedFailedB}: \n")    
                    try:
                        trace = traceDiff(f"Run-{selectedFailedA}/calls.txt", f"Run-{selectedFailedB}/calls.txt")
                        if trace:
                            f.write("\nNo trace, foram encontradas as diferencas: \n")
                            for traceLine in trace:
                                f.writelines(traceLine)
                        else:
                            f.write("\nNenhuma diferença encontrada no trace\n")
                    except FileNotFoundError as e:
                        print(f"Opção para trace não escolhida. Erro: {e}")

                    try:
                        stats = traceDiff(f"Run-{selectedFailedA}/stats.txt", f"Run-{selectedFailedA}/stats.txt")
                        if stats:
                            f.write("\nNo profiler, foram encontradas as diferencas: \n")
                            for statsLine in stats:
                                f.writelines(statsLine)
                        else:
                            f.write("\nNenhuma diferença encontrada no profiler\n")
                    except FileNotFoundError as e:
                        print(f"Opção para profiling não escolhida. Erro: {e}")

                else:
                    selectedPassedA = choice(passedIndex)
                    selectedPassedB = choice(passedIndex)

                    while selectedPassedA == selectedPassedB:
                        selectedPassedB = choice(passedIndex)

                    f.write(f"\nEntre as runs {selectedPassedA} e {selectedPassedB}: \n")
                    try:
                        trace = traceDiff(f"Run-{selectedPassedA}/calls.txt", f"Run-{selectedPassedB}/calls.txt")
                        if trace:
                            f.write("\nNo trace, foram encontradas as diferencas: \n")
                            for traceLine in trace:
                                f.writelines(traceLine)
                        else:
                            f.write("\nNenhuma diferença encontrada no trace\n")
                    except FileNotFoundError as e:
                        print(f"Opção para trace não escolhida. Erro: {e}")

                    try:
                        stats = traceDiff(f"Run-{selectedPassedA}/stats.txt", f"Run-{selectedPassedB}/stats.txt")
                        if stats:
                            f.write("\nNo profiler, foram encontradas as diferencas: \n")
                            for statsLine in stats:
                                f.writelines(statsLine)
                        else:
                            f.write("\nNenhuma diferença encontrada no profiler\n")
                    except FileNotFoundError as e:
                        print(f"Opção para profiling não escolhida. Erro: {e}")

        f.close()
        chdir(cwd)

def traceDiff(runA: str, runB: str) -> List[str]:
    """Funcao para comparar dois traces dos diversos testes de um repositório
    :param runA: Caminho para o trace A
    :param runB: Caminho para o trace B
    :returns: Lista com as linhas do diff
    """

    def separateDiff(diff: List[str]) -> List[str]:
        currentDiff = []
        allDiffs = []

        for line in diff:
            if line.startswith("@@"):
                if currentDiff:
                    if not any("at 0x" in line or "---" in line for line in currentDiff):
                        allDiffs.append(currentDiff)
                    currentDiff = [line + "\n"]
                else:
                    currentDiff.append(line)
            else:
                currentDiff.append(line)

        if currentDiff and not any("at 0x" in line or "---" in line for line in currentDiff):
            allDiffs.append(currentDiff)

        return allDiffs

    linesA = readLines(runA)
    linesB = readLines(runB)

    diff = list()
    for line in unified_diff(linesA, linesB, lineterm = ""):
        diff.append(line)

    return separateDiff(diff)