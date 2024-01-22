# TODO: - levar em consideração testes com o mesmo nome (criar pastas diferentes)
#       - levar em consideração testes implementados na forma de classes
#       - levar em consideração testes com múltiplos valores (parametrizados)
#       - investigar por que a ferramenta roda todos os testes novamente após rodar um repositório
from sys import settrace
from os import chdir, listdir, getcwd, path, remove
from pathlib import Path
from ast import parse, walk, FunctionDef, ClassDef
from time import time
from difflib import unified_diff
from typing import List, Tuple, Dict, Optional
from random import choice
import trace as trc
import subprocess
import pytest
import cProfile, pstats
import re
import coverage

class TestResult:
    def __init__(self, trace = True, prof = False, cov = False, outputDir = ".", testName = "", modName = ""):
        self.testName = testName
        self.modName = modName

        self.reports = []
        self.passed = 0
        self.failed = 0
        self.xfailed = 0
        self.skipped = 0
        self.total_duration = 0

        self.traceBuffer = []
        self.callCounter = [1]
        self.rootFile = [""]
        self.rootFileNo = [""]
        self.rootFuncName = [""]

        self.outputDir = outputDir
        self.cov = cov
        self.trace = trace
        self.prof = prof

        if self.prof:
            self.profiler = cProfile.Profile()

        if self.cov:
            self.coverage = coverage.Coverage()

    @pytest.hookimpl(hookwrapper = True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report = outcome.get_result()
        if report.when == 'call':
            self.reports.append(report)

    def pytest_collection_modifyitems(self, items):
        self.collected = len(items)

    def pytest_terminal_summary(self, terminalreporter, exitstatus):
        self.passed = len(terminalreporter.stats.get('passed', []))
        self.failed = len(terminalreporter.stats.get('failed', []))
        self.xfailed = len(terminalreporter.stats.get('xfailed', []))
        self.skipped = len(terminalreporter.stats.get('skipped', []))
        self.total_duration = time() - terminalreporter._sessionstarttime

    @pytest.hookimpl(tryfirst = True)
    def pytest_sessionstart(self, session):    
        if self.prof:
            self.profiler.enable()

        if self.cov:
            self.coverage.start()

        if self.trace:
            traceCalls = self.createTraceCalls()
            settrace(traceCalls)

    @pytest.hookimpl(tryfirst = True)
    def pytest_sessionfinish(self, session, exitstatus):
        if self.trace:
            self.end(self.outputDir)

        if self.prof:
            self.profiler.disable()
            stats = pstats.Stats(self.profiler)
            filteredStats = pstats.Stats()

            for entry in stats.stats.items():
                if not self.ignoreEntry(entry):
                    filteredStats.stats[entry[0]] = entry[1]

            with open("stats.txt", "w") as f:
                filteredStats.stream = f
                filteredStats.sort_stats("ncalls").print_stats()
            f.close()

        if self.cov:
            self.coverage.stop()
            self.coverage.save()

            with open("coverage.txt", "w") as f:
                self.coverage.report(file = f, show_missing = True)
            f.close()
    
    def ignoreEntry(self, entry: Tuple[Tuple[str, str, str], Tuple]):
        ignore = {"pytest", "pluggy", "builtins"}
        fileName = entry[0][0]

        return any(ignoredDir in fileName for ignoredDir in ignore)
    
    def createTraceCalls(self) -> callable:
        """Faz o trace de chamadas para funções de uma função
        """
        def traceCalls(frame, event, arg):
            if event not in ['call', 'return'] or frame == None:
                return
            
            line = str(frame.f_lineno)
            code = frame.f_code
            funcName = code.co_name
            fileName = code.co_filename

            if self.callCounter[0] == 1:
                self.rootFile[0] = fileName
                self.rootFileNo[0] = line
                self.rootFuncName[0] = funcName

            # Ignora chamadas do pytest
            if self.rootFuncName[0] not in self.testName:
                return

            if event == 'call':
                self.traceBuffer.append(self.callCounter[0] * ">" + f"{funcName}: {fileName} ({self.rootFile[0]}, {self.rootFileNo[0]}, {self.rootFuncName[0]})\n")
                self.callCounter[0] += 1
            if event == 'return':
                self.callCounter[0] -= 1
                if arg is not None:
                    self.traceBuffer.append(self.callCounter[0] * "<" + f"{funcName}: {arg} ({self.rootFile[0]}, {self.rootFileNo[0]}, {self.rootFuncName[0]})\n")
                else:
                    self.traceBuffer.append(self.callCounter[0] * "<" + f"{funcName}: None ({self.rootFile[0]}, {self.rootFileNo[0]}, {self.rootFuncName[0]})\n")

            return traceCalls

        settrace(traceCalls)
        return traceCalls

    def end(self, outDir: str):
        settrace(None)
        self.writeTrace(outDir)

    def writeTrace(self, outDir: str) -> None:
        if len(self.traceBuffer) > 0:
            with open(outDir + "/calls.txt", "a") as f:
                f.writelines(self.traceBuffer)
                f.close()

def runMultipleTimes(modDir: str, modName: str, count: int, params: List[bool]):
    dirList = getTestDir(modDir)

    cwd = getcwd()
    subprocess.run(["mkdir", f"Test-{modName}"])

    for dir in dirList:
        testFiles = getTestFiles(dir)
        for testFile in testFiles:
            chdir(cwd + "/" + f"Test-{modName}")
            currentFile = "file_" + path.basename(testFile)[:-3]

            subprocess.run(["mkdir", currentFile])
            chdir(path.abspath(currentFile))
            if checkForTestClasses(testFile) is None:
                tests = getTestCases([testFile])

                for testCase in tests[testFile]:
                    subprocess.run(["mkdir", testCase])
                    runSummary = list()
                    totalTime = 0

                    for run in range(count):
                        chdir(getcwd() + "/" + testCase)
                        subprocess.run(["mkdir", f"Run-{run}"])
                        runDir = getcwd() + "/" + f"Run-{run}"
                        chdir(runDir)
                        runResult = runTest(testFile, testCase, params)
                        totalTime += runResult[1]
                        chdir(cwd + "/" + f"Test-{modName}/{currentFile}/{testCase}")
                        runSummary.append(f"Run {run}: {runResult[0]} Tempo: {runResult[1]}\n")
                        chdir(cwd + "/" + f"Test-{modName}/{currentFile}")

                    with open("runsSummary.txt", "a") as f:
                        f.writelines(runSummary)
                        print(f"Tempo total: {totalTime}", file = f)
                    f.close()
                    chdir(cwd + "/" + f"Test-{modName}/{currentFile}")

                chdir(cwd)
            else:
                for className in checkForTestClasses(testFile):
                    tests = getTestsFromClass(className, testFile)
                    for test in tests:
                        subprocess.run(["mkdir", f"{className}::{test}"])
                        runSummary = list()
                        totalTime = 0

                        for run in range(count):
                            chdir(getcwd() + f"/{className}::{test}")
                            subprocess.run(["mkdir", f"Run-{run}"])
                            runDir = getcwd() + "/" + f"Run-{run}"
                            chdir(runDir)
                            runResult = runTest(testFile, test, params, className)
                            totalTime += runResult[1]
                            chdir(cwd + "/" + f"Test-{modName}/{currentFile}/{className}::{test}")
                            runSummary.append(f"Run {run}: {runResult[0]} Tempo: {runResult[1]}\n")
                            chdir(cwd + "/" + f"Test-{modName}/{currentFile}")

                        with open("runsSummary.txt", "a") as f:
                            f.writelines(runSummary)
                            print(f"Tempo total: {totalTime}", file = f)
                        f.close()
                        chdir(cwd + "/" + f"Test-{modName}/{currentFile}")

                chdir(cwd)

def checkForTestClasses(filePath: str) -> Optional[List[str]]:
    with open(filePath, "r") as f:
        content = f.read()
    f.close()

    tree = parse(content)
    classNames = [node.name for node in walk(tree) if isinstance(node, ClassDef)]

    return classNames if classNames != [] else None

def getTestsFromClass(className: str, filePath: str) -> List[str]:
    with open(filePath, "r") as f:
        content = f.read()
    f.close()

    tree = parse(content)
    tests = list()
    for node in walk(tree):
        if isinstance(node, ClassDef) and node.name == className:
            for item in node.body:
                if isinstance(item, FunctionDef):
                    tests.append(item.name)

    return tests

def runTest(dir: str, testName: str, params: List[bool], className: Optional[str] = None) -> Tuple[str, int]:
    """Roda um teste, dado o diretório do arquivo de testes e o nome do teste
    :param dir: diretório do arquivo de testes
    :param testName: nome do teste
    :returns: resultado do teste 
    """

    includeTracing = params[0]
    includeCoverage = params[1]
    includeProfiling = params[2]

    testResult = TestResult(trace = includeTracing, cov = includeCoverage, prof = includeProfiling, testName = testName)

    if className is None:
        pytest.main([f"{dir}::{testName}"], plugins=[testResult])
    else:
        print(f"\n\n\n\n{testName}\n\n\n\n")
        pytest.main([f"{dir}::{className}::{testName}"], plugins=[testResult])

    if testResult.passed != 0:
        result = "PASSED"
    elif testResult.failed != 0:
        result = "FAILED"
    elif testResult.skipped != 0:
        result = "SKIPPED"
    else:
        result = "XFAILED"

    return (result, testResult.total_duration)

def getTestDir(modDir: str, dirList = []) -> List[str]:
    """Busca por diretórios em um diretório contendo testes
    :param modDir: Caminho para o diretório do módulo
    :returns: Lista contendo os diretórios contendo testes (ex: ../foo/bar/test)
    """
    cwd = getcwd()
    chdir(modDir)

    files = list()
    files = listdir(".")

    for file in files:
        if path.isdir(path.join(getcwd(), file)):
            if file in ["test", "tests"] and path.join(getcwd(), file) not in dirList:
                dirList.append(path.join(getcwd(), file))
            else:
                getTestDir(path.join(getcwd(), file))
    chdir(cwd)
    return dirList

def cleanUp(modDir: str) -> None:
    """Exlui arquivos de copia de teste adicionados ao repositorio.
    :param modDir: diretorio do repositorio
    :returns: None
    """
    cwd = getcwd()
    chdir(modDir)

    files = list()
    files = listdir(".")

    for file in files:
        if path.isdir(path.join(getcwd(), file)):
            cleanUp(path.join(getcwd(), file))
        else:
            if "_copy.py" in file:
                remove(path.join(getcwd(), file))
    chdir(cwd)

def getTestCases(files: List[str]) -> Dict[str, str]:
    """Procura por casos de teste
    :param files: lista contendo o caminho para os arquivos de teste
    :returns: dicionario contendo nome dos casos de teste de acordo com seu arquivo (ex: {'..test/test_foo.py: [test_bar, test_fulano]'})
    """
    tests = dict()
    names = list()
    for file in files:
        with open(file, "r", encoding = "utf8") as f:
            tree = parse(f.read())
            f.close()
        names = [
            node.name for node in walk(tree) if isinstance(node, FunctionDef) and "test" in node.name
        ]

        tests[file] = names
    return tests

def getTestFiles(dir: str) -> List[str]:
    """Procura por arquivos de teste
    :param dir: Diretório onde se quer procurar
    :returns: lista contendo aquivos dos testes (ex: ['../test/test_foo.py', '../test/test_bar.py'])
    """
    dirPath = Path(dir)
    testFiles = dirPath.glob("test_*.py")

    return [str(file) for file in testFiles]

def traceFuncs(dir: str, funcName: str, modName: str) -> None:
    """Roda um teste específico do pytest
    :param dir: Diretório onde se encontra o teste
    :param funcName: Nome do teste
    :param modName: Nome do módulo
    :returns: Nada
    """
    subprocess.run(["mkdir", f"Test-{modName}"])
    def runTest(dir: str, funcName: str) -> None:
        pytest.main(["-v", f"{dir}::{funcName}"]) 
        
    tracer = trc.Trace(
        count = 1,
        trace = 0,
        ignoredirs = [pytest.__file__, trc.__file__]
    )

    tracer.runfunc(runTest, dir, funcName)
    res = tracer.results()
    res.write_results(summary = True, coverdir = f"Test-{modName}")

def refineCovers(modName: str, testFiles: str) -> None:
    """Função para filtrar todos os arquivos gerados pelo trace da biblioteca trace. Mantém apenas os arquivos que tenha relação com o módulo modName
    :param modName: Nome do módulo
    :param testFiles: Arquivos de teste
    :returns: None
    """
    cwd = getcwd()
    chdir(f"Test-{modName}")

    # Seleciona os arquivos para manter
    files = list()
    for file in listdir("."):
        for testFile in testFiles:
            tail = path.basename(testFile)
            if tail[:-3] in file:
                files.append(file)
    # Deleta os não selecionados
    for file in listdir("."):
        if file not in files:
            subprocess.run(["rm", file])

    # Retorna para o diretorio de comeco
    chdir(cwd)


def getTestCoverage(modName: str, testName: str) -> None:
    """Gera arquivos de texto contendo o cover para um dado caso de teste.
    :param modName: Módulo do teste
    :param testName: Nome do teste
    :returns: None
    """
    cwd = getcwd()
    chdir(f"Test-{modName}")
    files = [file for file in listdir(".") if path.isfile(path.join(getcwd(), file))]
    print(files)
    for file in files:
        with open(file, "r") as f:
            content = f.read()

            if testName in content:
                subprocess.run(["mkdir", testName])
                chdir(testName)
                with open(f"{testName}-cover.txt", "w") as w:
                    f.seek(0)
                    flag = False
                    for line in f.readlines():
                        if "def" in line and flag == True:
                            break
                        if testName in line or flag == True:
                            print(line, file = w)
                            flag = True
                    w.close()
            f.close()
    chdir(cwd)

def profiling(modName: str):
    dirList = getTestDir(getcwd() + "/" + modName)
    for dir in dirList:
        fileList = getTestFiles(dir)
        testList = getTestCases(fileList)
        for file in fileList:
            for test in testList[file]:
                profiler = cProfile.Profile()
                profiler.enable()
                runTest(dir, modName, test)
                profiler.disable()
                stats = pstats.Stats(profiler)
                with open(f"Stats-{test}.txt", "w") as f:
                    stats.stream = f
                    stats.print_stats()

def readLines(fileName: str) -> List[str]:
    with open(fileName, "r") as f:
        lines = f.readlines()
    f.close()

    return lines

# TODO: Adicionar metodo para comparacao de diffs (como pedido)
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