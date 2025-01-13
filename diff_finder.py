import csv
import argparse

def str_to_bool(value: str) -> bool:
    if value.lower() in {"true", "t"}:
        return True
    elif value.lower() in {"false", "f"}:
        return False
    else:
        raise argparse.ArgumentTypeError(f"Valor booleano invalido: {value}")
    
def analysis_definer(value: str)-> str:
    if value.lower() in {"cov","coverage","c"}:
        return "coverage"
    elif value.lower() in {"prof","profiling","p"}:
        return "profiling"
    elif value.lower() in {"trace","tracing","t"}:
        return "tracing"
    else:
        raise argparse.ArgumentTypeError(f"Análise invalida: {value}")
    
def str_to_int(value: str) -> int:
    if value.isdigit() and int(value) > 0:
        return int(value)
    raise argparse.ArgumentTypeError(f"Valor inteiro invalido: {value}")

def comparar_csvs(diretorio:str, analise:str, numero_de_runs:int, coluna_chave:str):

    teste = diretorio.split("/")[-1]
    diffs_totais = set()

    for i in range(numero_de_runs-1):

        arquivo1 = f"{diretorio}/Run-{i}/{teste}-{analise}.csv"
        arquivo2 = f"{diretorio}/Run-{i+1}/{teste}-{analise}.csv"
        
        with open (arquivo1, newline='', encoding='utf-8') as f1, open (arquivo2, newline='', encoding='utf-8') as f2:
            reader1 = csv.DictReader(f1)
            reader2 = csv.DictReader(f2)

            linhas1 = {linha[coluna_chave]: linha for linha in reader1}
            linhas2 = {linha[coluna_chave]: linha for linha in reader2}

            apenas_em_arquivo1 = set(linhas1.keys()) - set(linhas2.keys())
            apenas_em_arquivo2 = set(linhas2.keys()) - set(linhas1.keys())
            diffs_totais.update(apenas_em_arquivo1,apenas_em_arquivo2)

        total_diferencas_arquivo1 = len(apenas_em_arquivo1)
        total_diferencas_arquivo2 = len(apenas_em_arquivo2)
       
        if analise == "tracing":

            arquivo_saida = f"{diretorio}/Run-{i}/{teste}-{analise}-{coluna_chave}-diff-{i}-{i+1}.txt"

            with open(arquivo_saida, 'w', encoding='utf-8') as saida:

                if (total_diferencas_arquivo1 or total_diferencas_arquivo2 != 0):
                    saida.write("Diferenças encontradas:\n\n")
                else:
                    saida.write("Nenhuma diferença encontrada.")

                if apenas_em_arquivo1:
                    saida.write(f"Diferenças no arquivo {i} ({arquivo1}) ({total_diferencas_arquivo1} itens):\n")
                    saida.write(f"Presentes apenas em {arquivo1}:\n")
                    for chave in sorted(apenas_em_arquivo1):
                        saida.write(f"{linhas1[chave]}\n")
                    saida.write("\n")

                if apenas_em_arquivo2:
                    saida.write(f"Diferenças no arquivo {i+1} ({arquivo2}) ({total_diferencas_arquivo2} itens):\n")
                    saida.write(f"Presentes apenas em {arquivo2}:\n")
                    for chave in sorted(apenas_em_arquivo2):
                        saida.write(f"{linhas2[chave]}\n")
                    saida.write("\n")
                    
        elif analise == "profiling":

                todas_as_chaves = set(linhas1.keys()).union(set(linhas2.keys()))
                diffs = []
                arquivo_saida = f"{diretorio}/Run-{i}/{teste}-{analise}-{coluna_chave}-diff-{i}-{i+1}.txt"

                for chave in todas_as_chaves:
                    linha1 = linhas1.get(chave)
                    linha2 = linhas2.get(chave)

                    if linha1 and linha2:
                        for coluna, valor1 in linha1.items():
                            if coluna == coluna_chave:
                                continue
                            valor2 = linha2.get(coluna)
                            if valor1 != valor2:
                                diffs.append(f"Chave '{chave}': Coluna '{coluna}' - Arquivo1='{valor1}' vs Arquivo2='{valor2}'\n")
                    elif linha1:
                        diffs.append(f"Chave '{chave}' está apenas no Arquivo1.\n")
                    elif linha2:
                        diffs.append(f"Chave '{chave}' está apenas no Arquivo2.\n")

                with open(arquivo_saida, 'w', encoding='utf-8') as saida:
                    if len(diffs) == 0:
                        saida.write("Nenhuma diferença encontrada.")
                    else:
                        saida.write(f"Diferenças encontradas ({len(diffs)}):\n\n")
                        for diff in diffs:
                            saida.write(diff)

    if analise == "coverage":

        arquivo_saida = f"{diretorio}/{teste}-{analise}-{coluna_chave}-diff.txt"

        with open(arquivo_saida, 'w', encoding='utf-8') as saida:

            if (len(diffs_totais) != 0):
                saida.write(f"Diferenças encontradas de {coluna_chave}:\n\n")
            else:
                saida.write("Nenhuma diferença encontrada.")

            saida.write(f"Número total de diferenças em {numero_de_runs} runs: {len(diffs_totais)}\n")
            saida.write("[")
            saida.write(",".join(f"{valores}" for valores in sorted(diffs_totais)))
            saida.write("]")
            saida.write("\n")



#tracing -> verifica chamadas de função presentes em uma run e não presentes na run seguinte
#coverage -> verifica coberturas totais diferentes entre todas as runs
#profiling -> verifica diferenças de 2 a 2 csvs e registra os valores que forem discrepantes dada uma mesma chave

def main():
    parser = argparse.ArgumentParser(description = "Compara dois arquivos CSVs e mostra as suas diferenças.")
    parser.add_argument("test_directory",help = "Diretório onde estão as runs", type = str)
    parser.add_argument("analysis",help = "Tipo de análise a ser comparada", type = analysis_definer, default= "None")
    parser.add_argument("number_of_runs",help = "Número de runs a serem comparadas", type = str_to_int, default = 0)
    parser.add_argument("column", help = "Nome da coluna a ser usada como chave.", type = str)
    args = parser.parse_args()
    comparar_csvs(args.test_directory,args.analysis,args.number_of_runs,args.column)

if __name__ == "__main__":
    main()