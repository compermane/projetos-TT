import pytest
from AVL.AVL import *

"""
    Teste para criacao de arvore: testa se a funcao
    criaArvore cria um noh corretamente de acordo 
    com o parametro 'chave'. 
"""
param1 = (
    [None, None],
    [1, 1],
    [2, 2],
    [-1, -1]
)
@pytest.mark.parametrize("chave, expected", param1)
def test_criaArvore(chave, expected):
    raiz = Node.criaArvore(chave)
    if raiz == None:
        assert None == expected
    else:
        assert raiz.chave == expected

"""
    Teste para insercao: testa se a funcao insere() insere corretamente
    os elementos na arvore. Para tanto, compara se a chave inserida é igual
    ao resultado esperado.
"""
param2 = (
    [0, 0],
    [1, 1],
    [-1, -1]
)
@pytest.mark.parametrize("chave, expected", param2)
def test_insere(chave, expected):
    arvore = AVL()
    raiz = Node.criaArvore()

    raiz = arvore.insere(raiz, chave)
    assert raiz.chave == expected

"""
    Teste de multiplas insercoes: testa se a funcao insere() insere
    as chaves corretamente na arvore. Para tanto, realiza uma leitura preOrder
    já sabendo de seu resultado e, se a leitura for igual a esperada, entao
    o teste passa.
"""
param3 = (
    [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [3, 1, 0, 2, 7, 5, 4, 6, 9, 8, 10]],
    [[10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0], [7, 3, 1, 0, 2, 5, 4, 6, 9, 8, 10]],
    [[5, 4, 9, -20, 60, 70, -21, 7], [5, -20, -21, 4, 60, 9, 7, 70]]
)
@pytest.mark.parametrize("chaves, expected", param3)
def test_multiplasInsercoes(chaves, expected):
    arvore = AVL()
    raiz = Node.criaArvore()

    for chave in chaves:
        raiz = arvore.insere(raiz, chave)

    assert arvore.preOrderVetor(raiz, []) == expected

"""
    Teste de delecao de nohs: testa se um noh eh corretamente removido.
    Para tanto, realiza uma leitura preOrder sabendo de seu resultado
    previamente. Caso a leitura esteja igual a esperada, entao o teste passou.
"""
param4 = (
    [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], -1, [3, 1, 0, 2, 7, 5, 4, 6, 9, 8, 10]], # Remocao de noh inexistente
    [[10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0], 3, [7, 4, 1, 0, 2, 5, 6, 9, 8, 10]],     # Remocao de noh com 2 filhos
    [[5, 4, 9, -20, 60, 70, -21, 7], 9, [5, -20, -21, 4, 60, 7, 70]],             # Remocao de noh com 1 filho
    [[5, 4, 9, -20, 60, 70, -21, 7], 4, [5, -20, -21, 60, 9, 7, 70]]              # Remocao de noh folha
)
@pytest.mark.parametrize("chaves, deletado, expected", param4)
def test_delecao(chaves, deletado, expected):
    arvore = AVL()
    raiz = Node.criaArvore()

    for chave in chaves:
        raiz = arvore.insere(raiz, chave)
    raiz = arvore.deleta(raiz, deletado)
    assert arvore.preOrderVetor(raiz, []) == expected

"""
    Teste de busca: testa se a funcao busca() retorna o valor correto.
    Caso o elemento exista na arvore, eh esperado true. Eh esperado
    false caso contrario
"""
param5 = (
    [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 4, True], # Noh folha
    [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 3, True], # Noh raiz
    [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5, True], # Noh qualquer
    [[0, 1, 2, 3, 4, 5, 6, 7, 7, 9, 10], -1, False]# Noh inexistente
)
@pytest.mark.parametrize("chaves, buscado, expected", param5)
def test_busca(chaves, buscado, expected):
    arvore = AVL()
    raiz = Node.criaArvore()
    
    for chave in chaves:
        raiz = arvore.insere(raiz, chave)

    assert arvore.busca(raiz, buscado) == expected

def test_preOrder():
    chaves = [0, 1, 2, 3, 4, 5]
    arvore = AVL()
    raiz = Node.criaArvore()

    for chave in chaves:
        raiz = arvore.insere(raiz, chave)

    assert arvore.preOrderVetor(raiz) == [3, 1, 0, 2, 4, 5]

def test_inOrder():
    chaves = [0, 1, 2, 3, 4, 5]
    arvore = AVL()
    raiz = Node.criaArvore()

    for chave in chaves:
        raiz = arvore.insere(raiz, chave)

    assert arvore.inOrderVetor(raiz) == [0, 1, 2, 3, 4, 5]

def test_posOrder():
    chaves = [0, 1, 2, 3, 4, 5]
    arvore = AVL()
    raiz = Node.criaArvore()

    for chave in chaves:
        raiz = arvore.insere(raiz, chave)

    assert arvore.posOrderVetor(raiz) == [0, 2, 1, 5, 4, 3]