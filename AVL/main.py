import os
import sys
from analise import *

if __name__ == "__main__":
    # Executa os testes
    os.system('cmd /c "py -m pytest"')

    # Executa a funcao de pos-analise
    postAnalysis("out.txt")