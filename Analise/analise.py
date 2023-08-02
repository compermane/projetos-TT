# from AVL.Arvore.AVL import AVL, Node
from os import sep
from inspect import currentframe

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

    funcoes = open('Analise/Resultados/funcoes.txt', 'a')
    f = open('Analise/Resultados/out.txt', 'a')
    match event:
        case "call":
            print(f"Chamada da funcao {func_name} na linha {line} do arquivo {caminho[-2:]}", file = f)
        case "line":
            print(f"O interpretador vai executar a linha {line} do arquivo {caminho[-2:]}", file = f)
            print(f"{func_name}", file = funcoes)
        case "return":
            print(f"A funcao {func_name} vai retornar o valor {arg}, origem: {caminho[-2:]}", file = f)
            print(f"----------fim da execucao da funcao {func_name}------------", file = f)
        case "exception":
            print(f"Uma excecao ocorreu na funcao {func_name}, origem: {caminho[-2:]}, detalhamento: {arg}", file = f)
        
    f.close()
    return showTrace

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
        for j in funcoes:
            print(f"{j}: {funcoes[j]} vezes", file = writer)
    writer.close()