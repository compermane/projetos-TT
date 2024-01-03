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
    outputdir = request.config.getoption("--dir")
    traceBuffer = []
    callCounter = [1]
    
    rootFile = [""]
    rootFileNo = [""]
    rootFuncName = [""]

    def traceCalls(frame, event, arg):
        nonlocal traceBuffer, callCounter, rootFile, rootFileNo, rootFuncName

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
                rootFile[0] = fileName
                rootFileNo[0] = line
                rootFuncName[0] = funcName
            traceBuffer.append(callCounter[0] * ">" + f"{funcName}: {fileName} ({rootFile[0]}, {rootFileNo[0]}, {rootFuncName[0]})\n")
            callCounter[0] += 1
        if event == 'return':
            callCounter[0] -= 1
            if arg is not None:
                traceBuffer.append(callCounter[0] * "<" + f"{funcName}: {arg} ({rootFile[0]}, {rootFileNo[0]}, {rootFuncName[0]})\n")
            else:
                traceBuffer.append(callCounter[0] * "<" + f"{funcName}: None ({rootFile[0]}, {rootFileNo[0]}, {rootFuncName[0]})\n")

        return traceCalls
    
    def end():
        settrace(None)
        writeTrace()

    def writeTrace() -> None:
        nonlocal traceBuffer
        if len(traceBuffer) > 0:
            with open(outputdir + "calls.txt", "a") as f:
                f.writelines(traceBuffer)
                f.close()


    settrace(traceCalls)
    request.addfinalizer(end)

    return traceCalls