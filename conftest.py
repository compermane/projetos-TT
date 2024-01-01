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
    
    def traceCalls(frame, event, arg):
        nonlocal traceBuffer, callCounter

        if event not in ['call', 'return'] or frame == None:
            return
        
        code = frame.f_code
        funcName = code.co_name
        fileName = code.co_filename

        # Ignora chamadas do pytest
        if "pytest" in fileName or "pluggy" in fileName:
            return
        
        if event == 'call':
            traceBuffer.append(callCounter[0] * ">" + f"{funcName}: {fileName}\n")
            callCounter[0] += 1
        if event == 'return':
            callCounter[0] -= 1
            if arg is not None:
                try:
                    traceBuffer.append(callCounter[0] * "<" + f"{funcName}: {arg}\n")
                except AttributeError as e:
                    traceBuffer.append(callCounter[0] * "<" + f"{funcName}: Objeto de retorno: {type(arg)} (Erro: {e})")
            else:
                traceBuffer.append(callCounter[0] * "<" + f"{funcName}: None\n")

        return traceCalls
    
    def end():
        settrace(None)
        writeTrace()

    def writeTrace() -> None:
        nonlocal traceBuffer
        if len(traceBuffer) > 0:
            with open(outputdir + "calls.txt", "w") as f:
                f.writelines(traceBuffer)
                f.close()
    
    settrace(traceCalls)
    request.addfinalizer(end)

    return traceCalls