import csv
import argparse

def comparar_csvs(arquivo1, arquivo2, coluna_chave, arquivo_saida):

    with open (arquivo1, newline='', encoding='utf-8') as f1, open (arquivo2, newline='', encoding='utf-8') as f2:
        reader1 = csv.DictReader(f1)
        reader2 = csv.DictReader(f2)

        linhas1 = {linha[coluna_chave]: linha for linha in reader1}
        linhas2 = {linha[coluna_chave]: linha for linha in reader2}

        apenas_em_arquivo1 = set(linhas1.keys()) - set(linhas2.keys())
        apenas_em_arquivo2 = set(linhas2.keys()) - set(linhas1.keys())

    total_diferencas_arquivo1 = len(apenas_em_arquivo1)
    total_diferencas_arquivo2 = len(apenas_em_arquivo2)

    with open(arquivo_saida, 'w', encoding='utf-8') as saida:
        if (total_diferencas_arquivo1 or total_diferencas_arquivo2 != 0):
            saida.write("Diferenças encontradas:\n\n")
        else:
            saida.write("Nenhuma diferença encontrada.")

        if apenas_em_arquivo1:
            saida.write(f"Diferenças no arquivo 1 ({arquivo1}) ({total_diferencas_arquivo1} itens):\n")
            saida.write(f"Presentes apenas em {arquivo1}:\n")
            for chave in sorted(apenas_em_arquivo1):
                saida.write(f"{linhas1[chave]}\n")
            saida.write("\n")

        if apenas_em_arquivo2:
            saida.write(f"Diferenças no arquivo 2 ({arquivo2}) ({total_diferencas_arquivo2} itens):\n")
            saida.write(f"Presentes apenas em {arquivo2}:\n")
            for chave in sorted(apenas_em_arquivo2):
                saida.write(f"{linhas2[chave]}\n")
            saida.write("\n")



def main():
    parser = argparse.ArgumentParser(description="Compara dois arquivos CSVs e mostra as suas diferenças.")
    parser.add_argument("input_file1",help="Arquivo de entrada 1 (.csv)")
    parser.add_argument("input_file2",help="Arquivo de entrada 2 (.csv)")
    parser.add_argument("coluna", help="Nome da coluna a ser usada como chave.")
    parser.add_argument("output_file", help="Caminho para o arquivo de saída (.txt).")
    args = parser.parse_args()
    comparar_csvs(args.input_file1,args.input_file2,args.coluna,args.output_file)

if __name__ == "__main__":
    main()