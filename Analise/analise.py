# from AVL.Arvore.AVL import AVL, Node
from os import sep, chdir, listdir, getcwd, path
from inspect import currentframe
from pathlib import Path
from ast import parse, walk, FunctionDef
from sys import settrace
from shutil import copyfile
from atexit import register
import trace
import subprocess
import pytest
import cProfile, pstats

"""
    Funcao showTrace(frame, event, arg)
    - frame: é o stack frame atual, isto é, é uma pilha em que são dispostas
    chamadas para funções. Funções que são chamadas por outras funções são empilhadas
    e removidas apenas quando retornam algum valor para a função que a chamou.
    - event: é uma string que representa o tipo de evento.
    - arg: argumento que depende do valot de 'event'.
    O argumento 'event' pode ser:
    - 'call': Ocorre quando uma função é chamada. Nesse caso, a função de diagnóstico
    global é chamada 'arg' é None e o valor de retorno especifica a função de trace local, 
    isto é, especifica o diagnóstico da função que foi chamada.
    - 'line': Ocorre quando o interpretador está para executar uma nova linha de código 
    ou re-executar uma condicional de um laço. Nesse caso, a função de diagnóstico da função
    é chamada, 'arg' é None e o valor de retorno especifica a nova função de diagnóstico local. 
    - 'return': Ocorre quando uma função está para retornar um valor. A funçaõ de diagnóstico
    local é chamada, 'arg' é o valor a ser retornado ou é None caso o evento seja causado por 
    uma exceção. O valor de retorno da função de diagnóstico é ignorado.
    - 'exception': Ocorre quando uma exceção acontece. A função de diagnóstico é chamada e 'arg'
    é uma tupla (exception, value, traceback); o valor de retorno especifica a nova função de
    diagnóstico local.
    - 'opcode': Ocorre quando o interpretador está para executar um novo opcode. A função de 
    diagnóstico local é chamada e 'arg' é None. O valor de retorno especifica a nova função de
    diagnóstico local.
"""

def showTrace(frame = currentframe(), event = None, arg = None):
    if frame == None:
        return 
    
    code =  frame.f_code
    func_name = code.co_name
    line = frame.f_lineno
    origin  = code.co_filename
    caminho = origin.split(sep)
    dir = caminho[-1:]
    if(len(caminho) >= 4):
        dir = "../" + caminho[-3] + "/" + caminho[-2] + "/" + caminho[-1]

    funcoes = open('Analise/Resultados/funcoes.txt', 'a')
    f = open('Analise/Resultados/out.txt', 'a')
    match event:
        case "call":
            print(f"Chamada da funcao {func_name} na linha {line} do arquivo {dir}", file = f)
            print(f"{func_name} - Origem: {dir} - ", file = funcoes)
        case "line":
            print(f"O interpretador vai executar a linha {line} do arquivo {dir}", file = f)
        case "return":
            print(f"A funcao {func_name} vai retornar o valor {arg}, origem: {dir}", file = f)
            print(f"----------fim da execucao da funcao {func_name}------------", file = f)
        case "exception":
            print(f"Uma excecao ocorreu na funcao {func_name}, origem: {dir}, detalhamento: {arg}", file = f)
        
    f.close()
    funcoes.close()

    return showTrace

def createTraceCalls() -> callable:
    """Faz o trace de chamadas para funções de uma função
    """
    traceBuffer = []
    callCounter = [1]
    
    def traceCalls(frame, event, arg):
        if event not in ['call', 'return'] or frame == None:
            return
        
        code = frame.f_code
        funcName = code.co_name
        fileName = code.co_filename

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

        if len(traceBuffer) >= 300:
            with open("calls.txt", "a") as f:
                f.writelines(traceBuffer)
            traceBuffer.clear()

        return traceCalls
    
    def writeTrace() -> None:
        if len(traceBuffer) > 0:
            with open("calls.txt", "a") as f:
                f.writelines(traceBuffer)
                f.close()
    
    register(writeTrace)
    return traceCalls

# TODO: função para implementar o settrace em cada teste de repositório
def implementTracer(modDir: str):
    fileList = getTestFiles(modDir)
    traceCallsContent = list()
    with open("Analise/analise.py", "r") as file:
        functionStart = False
        functionEnd = False
        for line in file:
            if "def createTraceCalls() -> callable:" in line or functionStart == True:
                traceCallsContent.append(line)
                functionStart = True
                if "register(writeTrace)" in line:
                    functionEnd = True
                elif functionEnd == True:
                    break
        file.close()

    for file in fileList:
        if "_copy.py" in file:
            try:
                with open(file, "r") as copy:
                    copyContent = list()
                    copyContent.append(["from sys import settrace\n"])
                    copyContent.append(["from atexit import register\n"])
                    copyContent.append(traceCallsContent)

                    flag = False
                    for line in copy:
                        if "def test_" in line and flag == True:
                            copyContent.append(["    settrace(None)\n"])
                            copyContent.append([line])
                            flag = False
                        else:
                            copyContent.append([line])
                            if "def test_" in line and flag == False:
                                copyContent.append(["    traceCalls = createTraceCalls()\n",
                                                    "    settrace(traceCalls)\n"])
                                flag = True


                    copy.close()
                
                with open(file, "w") as copy:
                    for i in range(len(copyContent)):
                        copy.writelines(copyContent[i])
                    copy.close()
            except Exception as e:
                print(f"Erro durante a execução: {e}")

def runTest(dir: str, modName: str, testName: str) -> None:
    traceCalls = createTraceCalls()
    settrace(traceCalls)
    pytest.main([f"{dir}::{testName}"])
    settrace(None)

"""
    Funcao postAnalysis(f)
    Gera um arquivo texto contendo estatísticas sobre a análise
"""
def postAnalysis(name: str) -> None:
    keywords = {
        'Chamada de funcao': 0,
        'Execucao de linha': 0,
        'Retorno de valor': 0,
        'Excecao': 0
    }
    funcoes = {}

    with open('Analise/Resultados/funcoes.txt', 'r') as reader:
        for i in reader:
            func = i[:len(i) - 1]
            if func in funcoes:
                funcoes[func] += 1
            else:
                funcoes[func] = 1
    reader.close()

    with open(name, 'r') as reader:
        for line in reader:
            for word in line.split(" "):
                match word:
                    case 'Chamada':
                        keywords['Chamada de funcao'] += 1
                        break
                    case 'interpretador':
                        keywords['Execucao de linha'] += 1
                        break
                    case 'retornar':
                        keywords['Retorno de valor'] += 1
                        break
                    case 'excecao':
                        keywords['Excecao'] += 1
                        break
    reader.close()
    
    with open('Analise/Resultados/post.txt', 'w') as writer:
        for i in keywords:
            print(f"{i}: {keywords[i]} vezes", file = writer)
        print(file = writer)

        print("Funcoes chamadas: ", file = writer)
        for j in funcoes:
            print(f"{j} :{funcoes[j]} vezes", file = writer)

    writer.close()

def createTestFileCopy(modDir: str) -> None:
    """Cria cópias dos arquvios de teste dado o diretório de teste.
    :param modDir: Diretório para o módulo
    :returns: None
    """
    dirList = getTestDir(modDir)
    
    for dir in dirList:
        fileList = getTestFiles(dir)
        for file in fileList:
            copyfile(file, file[:-3] + "_copy.py")
    

# TODO: implementar uma função que busque por diretórios contendo testes
def getTestDir(modDir: str, dirList = []) -> list:
    """Busca por diretórios em um diretório contendo testes
    :param modDir: Caminho para o diretório do módulo
    :returns: Lista contendo os diretórios contendo testes
    """
    cwd = getcwd()
    chdir(modDir)

    files = list()
    files = listdir(".")

    for file in files:
        if path.isdir(path.join(getcwd(), file)):
            if file in ["test", "tests"]:
                dirList.append(path.join(getcwd(), file))
            else:
                getTestDir(path.join(getcwd(), file))
    chdir(cwd)
    return dirList

def getTestCases(files: list) -> dict:
    """Procura por casos de teste
    :param files: lista contendo o caminho para os arquivos de teste
    :returns: dicionario contendo nome dos casos de teste de acordo com seu arquivo
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

def getTestFiles(dir: str) -> list:
    """Procura por arquivos de teste
    :param dir: Diretório onde se quer procurar
    :returns: lista contendo aquivos dos testes
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
        
    tracer = trace.Trace(
        count = 1,
        trace = 0,
        ignoredirs = [pytest.__file__, trace.__file__]
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
                    
