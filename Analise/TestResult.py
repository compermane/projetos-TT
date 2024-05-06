""" Pluggin principal para rastreio da execução do Pytest
"""
from typing import List, Tuple, Optional, Any
from .VirtualEnvironment import VirtualEnvironment
from .analise import *
from .utils import activateVenv
from sys import settrace
from time import time
from inspect import getmembers
import pytest
import sys
import cProfile
import trace as trc
import pstats

class TestResult:
    def __init__(self, trace: bool = True, prof: bool = False, cov: bool = False, 
                 outputDir: str = ".", testName: str = "", modName: str = "", testFileName: str = "",
                 isParametrized: Optional[bool] = False, params: Optional[List[Any]] = [], 
                 repoVenv: VirtualEnvironment = None):
        self.testName = testName
        self.modName = modName
        self.testFileName = testFileName

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

        self.repoVenv = repoVenv

        if self.prof:
            self.profiler = cProfile.Profile()

        if isParametrized:
            self.params = getParamsValues(params)
        else:
            self.params = None
    
    def pytest_runtest_protocol(self, item, nextitem):
        if self.cov:
            testName = item.nodeid.split("::")[-1]
            open(f"{testName}-cov.txt", "a").close()
            with open(f"{testName}-cov.txt", "w") as traceFile:

                if self.params is not None:
                    if len(self.params) != len(item.fixturenames):
                        raise Exception(f"Number of test arguments is different from the number of the given arguments: expected {len(item.funcargs)} got {len(self.params)}")
                    else:
                        item.funcargs = {item.fixturenames[i]: self.params[i] for i in range(len(item.fixturenames))}
                        locals_ = {**locals(), **item.funcargs}
                else:
                    locals_ = {**locals()}

                sys.stdout = traceFile
                try:
                    tracer = trc.Trace(trace=1, count=1)
                    tracer.runctx("item.runtest()", globals=globals(), locals=locals_)
                finally:
                    sys.stdout = sys.__stdout__

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
        activateVenv(self.repoVenv._venv_dir)
        if self.prof:
            self.profiler.enable()

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
                    builtins = (int, float, str, complex, list, tuple, range, dict, set, frozenset, bool, bytes, bytearray)
                    if isinstance(arg, object) and type(arg) not in builtins:
                        try:
                            attrs = getmembers(arg)
                        except Exception as e:
                            attrs = []
                        returnObj = f"{type(arg)}:\n"
                        for name, value in attrs:
                            # Ignora builtins
                            if not name.startswith("__") and not name.endswith("__"):
                                returnObj += self.callCounter[0] * "\t" + f"{name}: {value}\n"
                        self.traceBuffer.append(self.callCounter[0] * "<" + f"{funcName}: {returnObj} ({self.rootFile[0]}, {self.rootFileNo[0]}, {self.rootFuncName[0]})\n")
                    else:
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
        # print(f"\n\n\n {len(self.traceBuffer)} \n\n\n")
        if len(self.traceBuffer) > 0:
            with open(outDir + "/calls.txt", "a") as f:
                f.writelines(self.traceBuffer)
            f.close()