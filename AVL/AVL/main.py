"""
    Nome: Eugenio Akinori Kisi Nishimiya
    RA: 811598
"""

from AVL import *

if __name__ == "__main__":
    # Criacao de arvore
    raiz = Node.criaArvore()
    arvore = AVL()

    # Elementos a serem inseridos na arvore:
    # Leitura inorder esperada: -21, 20, 4, 5, 7, 9, 60, 70
    chaves = [5, 4, 9, -20, 60, 70, -21, 7]

    # Insercao de chaves
    for chave in chaves:
        raiz = arvore.insere(raiz, chave)

    print("Leitura inOrder da arvore apos a insercao das chaves 5, 4, 9, -20, 60, 70, -21, 7: ")
    arvore.inOrder(raiz)
    print()

    # Remocao de noh com apenas um filho da arvore [5, 4, 9, -20, 60, 70, -21, 7]
    # Leitura preodem esperada: 5, -20, -21, 4, 60, 7, 70
    print("Leitura preOrdem da arvore apos delecao da chave 9:")
    raiz = arvore.deleta(raiz, 9)
    arvore.preOrder(raiz)
    print()

    # Remocao de noh com um filho da arvore [5, 4, -20, 60, 70, -21, 7]
    # Leitura posordem esperada:-21, 4, -20, 70, 60, 5
    print("Leitura posOrdem da arvore apos delecao da chave 7:")
    raiz = arvore.deleta(raiz, 7)
    arvore.posOrder(raiz)
    print()

    # Remocao de noh com dois filhos da arvore [5, 4, -20, 60, 70, -21]
    # Leitra inorder esperada: -21, 4, 5, 60, 70
    print("Leitura inOrder da arvore apos delecao da chave -20:")
    raiz = arvore.deleta(raiz, -20)
    arvore.inOrder(raiz)
    print()

    # Remocao da raiz da arvore [5, 4, 60, 70, -21]
    # Leitura preorder esperada: 60, 4, -21, 70
    print("Leitura preOrdem da arvore apos delecao da raiz:")
    raiz = arvore.deleta(raiz, 5)
    arvore.preOrder(raiz)
    print()

    # Criacao da nova arvore
    arvore2 = AVL()
    raiz2 = Node.criaArvore()

    chaves = [0, 1, 2, 3, 4, 5]
    for chave in chaves:
        raiz2 = arvore.insere(raiz2, chave)

    # Buscando por elemento na folha da arvore [0, 1, 2, 3, 4, 5]
    # Resultado esperado: True
    print("Buscando pelo elemento 2 da arvore [0, 1, 2, 3, 4, 5]: ", end = "")
    print(arvore2.busca(raiz2, 2))

    # Buscando por elemento com 1 filho da arvore [0, 1, 2, 3, 4, 5]
    # Resultado esperado: True
    print("Buscando pelo elemento 4 da arvore [0, 1, 2, 3, 4, 5]: ", end = "")
    print(arvore2.busca(raiz2, 4))

    # Buscando por elemento com 2 filhos da arvore [0, 1, 2, 3, 4, 5]
    # Resultado esperado: True
    print("Buscando pelo elemento 1 da arvore [0, 1, 2, 3, 4, 5]: ", end = "")
    print(arvore2.busca(raiz2, 1))

    # Buscando pela raiz da arvore [0, 1, 2, 3, 4, 5]
    # Resultado esperado: True
    print("Buscando pelo elemento 3 da arvore [0, 1, 2, 3, 4, 5]: ", end = "")
    print(arvore2.busca(raiz2, 3))

    # Buscando por elemento inexistente da arvore [0, 1, 2, 3, 4, 5]
    # Resultado esperado: False
    print("Buscando pelo elemento -1 da arvore [0, 1, 2, 3, 4, 5]: ", end = "")
    print(arvore2.busca(raiz2, -1))