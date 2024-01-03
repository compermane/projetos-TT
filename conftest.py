import pytest
from atexit import register
from sys import settrace

def pytest_addoption(parser):
    parser.addoption(
        "--dir", 
        action = "store", 
        default = None, 
        help = "Local onde o trace será salvo"
        )
    parser.addoption(
        "--coverage",
        action = "store",
        default = False,
        help = "Coverage dos testes"
    )

@pytest.fixture
def cover_dir(request):
    return request.config.getoption("--coverage")

@pytest.fixture
def trace_dir(request):
    return request.config.getoption("--dir")

@pytest.fixture
def createTraceCalls(request) -> callable:
    """Faz o trace de chamadas para funções de uma função
    """

    class Trace:
        def __init__(self, counter, rootFile, rootFileNo, rootFuncName, childTrace = []):
            self._counter = counter
            self._rootFile = rootFile
            self._rootFileNo = rootFileNo
            self._rootFuncName = rootFuncName
            self._childTrace = childTrace

        @property
        def counter(self):
            return self._counter

        @property
        def rootFile(self):
            return self._rootFile
        
        @property
        def rootFileNo(self):
            return self._rootFileNo
        
        @property
        def rootFuncName(self):
            return self._rootFuncName
        
        @property
        def childTrace(self):
            return self._childTrace
        
        def addCall(self, funcName: str, fileName: str, counter: int):
            self.childTrace.append([funcName, fileName, self.rootFile, self.rootFileNo, self.rootFuncName, "CALL", counter])

        def addReturn(self, funcName: str, returnValue: str, counter: int):
            self.childTrace.append([funcName, returnValue, self.rootFile, self.rootFileNo, self.rootFuncName, "RETURN", counter])

    outputdir = request.config.getoption("--dir")
    traceBuffer = []
    traceCounter = [0]
    traceList = []
    callCounter = [1]

    def traceCalls(frame, event, arg):
        nonlocal traceBuffer, callCounter, traceList, traceCounter

        if event not in ['call', 'return'] or frame == None:
            return
        
        line = str(frame.f_lineno)
        code = frame.f_code
        funcName = code.co_name
        fileName = code.co_filename

        # Ignora chamadas do pytest
        if any(keyword in fileName for keyword in ["pytest", "pluggy", "contextlib", "importlib", "frozen"]):
            return

        if event == 'call':
            if callCounter[0] == 1:
                traceList.append(Trace(callCounter[0], fileName, line, funcName))
            else:
                currentTrace = traceList[traceCounter[0]]
                currentTrace.addCall(funcName, fileName, callCounter[0])
            callCounter[0] += 1
        if event == 'return':
            callCounter[0] -= 1
            currentTrace = traceList[traceCounter[0]]
            if arg is not None:
                currentTrace.addReturn(funcName, arg, callCounter[0])
            else:
                currentTrace.addReturn(funcName, "None", callCounter[0])
            if callCounter[0] == 1:
                traceCounter[0] += 1

        return traceCalls
    
    def end():
        settrace(None)
        writeTrace()

    def writeTrace() -> None:
        nonlocal traceBuffer, traceList
        for trace in traceList:
            traceBuffer.append(">" + f"{trace.rootFuncName}: {trace.rootFile}, {trace.rootFileNo} len: {len(traceList)} (raiz)\n")
            for child in trace.childTrace:
                if child[5] == "CALL":
                    traceBuffer.append(child[6] * ">" + f"{child[0]}: {child[1]} (raiz: {child[2] + ', ' + child[3] + ', ' + child[4]}) {child[7]}\n")
                else:
                    traceBuffer.append(child[6] * "<" + f"{child[0]}: {child[1]} (raiz: {child[2] + ', ' + child[3] + ', ' + child[4]}) {child[7]}\n")


        if len(traceBuffer) > 0:
            with open(outputdir + "calls.txt", "w") as f:
                f.writelines(traceBuffer)
                f.close()


    settrace(traceCalls)
    request.addfinalizer(end)

    return traceCalls