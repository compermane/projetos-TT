import os
from analise import *

if __name__ == "__main__":
    # Reseta os arquivos
    file = open('Resultados/out.txt', 'w')
    file.close()
    file = open('Resultados/post.txt', 'w')
    file.close()
    file = open('Resultados/funcoes.txt', 'w')
    file.close()
    # Executa os testes
    os.chdir('..')
    os.system('cmd /c "py -m pytest"')

    # Executa a funcao de pos-analise
    postAnalysis("Analise/Resultados/out.txt")