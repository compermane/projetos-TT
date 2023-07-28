"""
    Nome: Eugenio Akinori Kisi Nishimiya
    RA: 811598
"""

# Definicao da classe de nohs da arvore AVL
class Node:
    def __init__(self, chave: int):
        self.chave = chave      # Chave do noh
        self.esq = None         # Filho a esquerda do noh
        self.dir = None         # Filho a direita do noh
        self.altura = 1         # Altura do noh

    # Retorna um noh vazio ou um noh ja com uma chave
    def criaArvore(chave = None):
        if chave == None:
            return None
        return Node(chave)
    
    @property
    def chave(self):
        return self._chave
    
    @chave.setter
    def chave(self, chave):
        self._chave = chave

# Definicao da arvore AVL
class AVL:
    # Insere um noh dada sua chave, fazendo todas as rotacoes caso necessario
    def insere(self, raiz: Node, chave: int):
        # Caso a raiz nao exista, insere a chave na raiz
        if raiz == None:
            return Node(chave)
        
        # Se nao, insere recursivamente como uma arvore binaria de busca.
        # Se a chave a ser inserida for menor ou igual a chave da raiz, insere
        # no noh a esquerda da raiz.
        if chave <= raiz.chave:
            raiz.esq = self.insere(raiz.esq, chave)

        # Caso contrario, insere no noh a direita da raiz.
        if chave > raiz.chave:
            raiz.dir = self.insere(raiz.dir, chave)

        # Agora, a chave esta posicionada corretamente onde deve ser inserida.
        # Atualizar a altura da arvore
        raiz.altura = self.atualizaAltura(raiz)

        # Calculo do fator de balanceamento
        balanco = self.getBalanco(raiz)

        if balanco > 1:
            if chave <= raiz.esq.chave:
                return self.rotacaoDir(raiz)
            elif chave > raiz.esq.chave:
                return self.rotacaoEsqDir(raiz)
            
        if balanco < -1:
            if chave > raiz.dir.chave:
                return self.rotacaoEsq(raiz)
            elif chave <= raiz.dir.chave:
                return self.rotacaoDirEsq(raiz)
            
        return raiz

    # Deleta um noh da arvore dado a sua chave, fazendo o rebalanceamento
    # caso necessario
    def deleta(self, raiz: Node, chave: int) -> Node:
        # Caso em que ou a raiz esta vazia ou o elemento a ser
        # deletado nao existe
        if raiz == None or not self.busca(raiz, chave):
            return raiz
        
        elif chave < raiz.chave:
            raiz.esq = self.deleta(raiz.esq, chave)
        elif chave > raiz.chave:
            raiz.dir = self.deleta(raiz.dir, chave)
        # Aqui, o noh a ser deletado ja esta posicionado
        # Caso o noh tenha apenas 1 filho ou seja um noh folha,
        # substitua-o com o noh filho
        else:
            if raiz.esq == None:
                novo = raiz.dir
                raiz = None
                return novo
                
            elif raiz.dir == None:
                novo = raiz.esq
                raiz = None
                return novo
            # Caso o noh tenha os dois filhos, encontre o menor no
            # da subarvore a direita e troque de posicao com o noh
            # a ser deletado
            novo = raiz.dir
            while novo.esq != None:
                novo = novo.esq
            raiz.chave = novo.chave
            raiz.dir = self.deleta(raiz.dir, novo.chave)

        if raiz == None:
            return raiz
        
        # Atualizacao da altura
        raiz.altura = self.atualizaAltura(raiz)

        # Pode ser necessario rebalancear a arvore
        balanco = self.getBalanco(raiz)

        if balanco > 1:
            if self.getBalanco(raiz.esq) >= 0:
                return self.rotacaoDir(raiz)
            if self.getBalanco(raiz.esq) < 0:
                return self.rotacaoEsqDir(raiz)
            
        if balanco < -1:
            if self.getBalanco(raiz.dir) <= 0:
                return self.rotacaoEsq(raiz)
            if self.getBalanco(raiz.dir) > 0:
                return self.rotacaoDirEsq(raiz)
        
        return raiz

    # Retorna a altura de uma arvore
    def getAltura(self, raiz: Node) -> int:
        if raiz == None:
            return 0
        
        return raiz.altura
    
    # Retorna o calculo de altura para um dado noh
    def atualizaAltura(self, raiz: Node) -> int:
        return 1 + max(self.getAltura(raiz.esq), self.getAltura(raiz.dir))
    
    # Retorna o fator de balanceamento de um noh
    def getBalanco(self, raiz: Node) -> int:
        return self.getAltura(raiz.esq) - self.getAltura(raiz.dir)
    
    # Retorna uma rotacao a esquerda, isto eh, quando o fator de
    # balanceamento eh menor que -1 (a altura da subarvore a direita
    # eh maior que a altura da subarvore a esquerda)
    def rotacaoEsq(self, raiz: Node) -> Node:
        y = raiz.dir
        b = y.esq

        raiz.dir = b
        y.esq = raiz

        # Atualizacao de alturas
        raiz.altura = self.atualizaAltura(raiz)
        y.altura  = self.atualizaAltura(y)

        return y
    
    # Retorna uma rotacao a direita, isto eh, quando o fator de
    # balanceamento for maior 1 (a altura da subarvore a esquerda
    # eh maior que a altura da subarvore a direita)
    def rotacaoDir(self, raiz: Node) -> Node:
        x = raiz.esq
        b = x.dir 

        raiz.esq = b
        x.dir = raiz

        # Atualizacao de alturas
        raiz.altura = self.atualizaAltura(raiz)
        x.altura = self.atualizaAltura(x)

        return x
    
    # Realiza a rotacao esquerda-direita de um noh
    def rotacaoEsqDir(self, raiz: Node) -> Node:
        raiz.esq = self.rotacaoEsq(raiz.esq)
        return self.rotacaoDir(raiz)
    
    # Realiza a rotacao direita-esquerda de um noh
    def rotacaoDirEsq(self, raiz: Node) -> Node:
        raiz.dir = self.rotacaoDir(raiz.dir)
        return self.rotacaoEsq(raiz)
    
    # Busca recursivamente o valor de uma chave na arvore.
    # Retorna true caso encontre e false caso contrario
    def busca(self, raiz: Node, chave: int) -> bool:
        if raiz == None:
            return False

        if chave == raiz.chave:
            return True
        
        if chave <= raiz.chave:
            return self.busca(raiz.esq, chave)
        
        return self.busca(raiz.dir, chave)

    # Percorre a arvore em preorder, armazenando os elementos em uma lista.
    # Retorna a lista contendo os elementos percorridos em preordem
    def preOrderVetor(self, raiz: Node, res = []) -> list:
        if raiz != None:
            res.append(raiz.chave)
            self.preOrderVetor(raiz.esq, res)
            self.preOrderVetor(raiz.dir, res)
        return res

    # Percorre a arvore em preorder, porem printa no console cada elemento
    # visitado, sem que haja armazenamento desses elementos
    def preOrder(self, raiz: Node) -> None:
        if raiz != None:
            print(f"{raiz.chave} ", end = "")
            self.preOrder(raiz.esq)
            self.preOrder(raiz.dir)
        return
    
    # Percorre a arvore em inorder, armazenando as chaves dos nohs percorridos
    # em um vetor. Retorna esse vetor preenchido de acordo com a ordem em que os
    # nohs sao visitados
    def inOrderVetor(self, raiz: Node, res = []) -> list:
        if raiz != None:
            self.inOrderVetor(raiz.esq, res)
            res.append(raiz.chave)
            self.inOrderVetor(raiz.dir, res)
        return res

    # Percorre a arvore em inorder, porem apenas printa no console os valores dos nohs
    # visitados.
    def inOrder(self, raiz: Node) -> None:
        if raiz != None:
            self.inOrder(raiz.esq)
            print(f"{raiz.chave} ", end = "")
            self.inOrder(raiz.dir)
        return
    
    # Percorre a arvore em posorder, armazenando os valores das chaves dos nohs visitados
    # em um vetor. Retorna esse vetor preenchido de acordo com a ordem dos nohs visitados
    # em posordem
    def posOrderVetor(self, raiz: Node, res = []) -> list:
        if raiz != None:
            self.posOrderVetor(raiz.esq, res)
            self.posOrderVetor(raiz.dir, res)

            res.append(raiz.chave)
        return res
    
    # Percorre a arvore em posordem, porem apenas printa no console os valores das chaves 
    # visitadas em posorder
    def posOrder(self, raiz: Node) -> None:
        if raiz != None:
            self.posOrder(raiz.esq)
            self.posOrder(raiz.dir)

            print(f"{raiz.chave} ", end = "")
        return