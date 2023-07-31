from AVL import *

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

def showTrace(frame, event, arg):
    code =  frame.f_code
    func_name = code.co_name
    line = frame.f_lineno
    origin  = code.co_filename

    match event:
        case "call":
            with open('out.txt', 'a') as f:
                print(f"Chamada da funçao {func_name} na linha {line} do arquivo {origin}", file = f)
        case "line":
            with open('out.txt', 'a'):
                print(f"O interpretador vai executar a linha {line} do arquivo {origin}", file = f)
        case "return":
            with open('out.txt', 'a'):
                print(f"A funcao {func_name} vai retornar o valor {arg}, origem: {origin}", file = f)
        case "exception":
            with open('out.txt', 'a'):
                print(f"Uma excecao ocorreu na função {func_name}, origem: {origin}, detalhamento: {arg}", file = f)
    
    # return showTrace

    