import csv
import argparse
import re
from pathlib import Path

def analysis_definer(value: str) -> str:
    """Valida e normaliza o tipo de análise."""
    value = value.lower()
    if value in {"cov", "coverage", "c"}:
        return "coverage"
    elif value in {"prof", "profiling", "p"}:
        return "profiling"
    elif value in {"trace", "tracing", "t"}:
        return "tracing"
    else:
        raise argparse.ArgumentTypeError(f"Análise inválida: {value}")
    
def str_to_int(value: str) -> int:
    """Valida e converte uma string para um inteiro."""
    if value.isdigit() and int(value) >= 0:
        return int(value)
    raise argparse.ArgumentTypeError(f"Valor inteiro inválido: {value}")

def comparar_csvs(diretorio: str, analise: str, numero_de_runs: int, coluna_chave: str):
    """Função principal que compara ou compila os resultados das runs de teste."""
    
    base_dir = Path(diretorio)
    if not base_dir.is_dir():
        print(f"Erro: O diretório de teste especificado não existe: {diretorio}")
        return

    teste = base_dir.name
    
    try:
        projeto = base_dir.parent.name.split("Test-")[1]
    except IndexError:
        print(f"AVISO: Não foi possível extrair o nome do projeto de '{base_dir.parent.name}'. A categorização de profiling pode falhar.")
        projeto = "unknown"

    # --- Lógica de COMPILAÇÃO para Coverage ---
    if analise == "coverage":
        print(f"Iniciando compilação de dados de '{analise}' para o teste '{teste}'...")
        dados_compilados, cabecalho = [], None
        for i in range(numero_de_runs):
            arquivo_csv = base_dir / f"Run-{i}" / f"{teste}-coverage.csv"
            if not arquivo_csv.is_file():
                print(f"Aviso: Arquivo não encontrado para a Run-{i}, pulando: {arquivo_csv}")
                continue
            try:
                with open(arquivo_csv, mode='r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    current_cabecalho = next(reader)
                    if cabecalho is None: cabecalho = current_cabecalho
                    for linha in reader: dados_compilados.append(linha)
            except Exception as e:
                print(f"Erro ao processar {arquivo_csv}: {e}")
        
        if not dados_compilados:
            print("Nenhum dado de coverage foi encontrado para compilar.")
            return
        
        arquivo_saida = base_dir / f"{teste}-coverage-summary.csv"
        try:
            with open(arquivo_saida, mode='w', newline='', encoding='utf-8') as f_out:
                writer = csv.writer(f_out)
                if cabecalho: writer.writerow(cabecalho)
                writer.writerows(dados_compilados)
            print(f"Sucesso! {len(dados_compilados)} linhas de runs compiladas em: {arquivo_saida}")
        except Exception as e:
            print(f"Erro ao escrever o arquivo de resumo '{arquivo_saida}': {e}")
        return

    # --- Lógica de COMPARAÇÃO para Tracing e Profiling ---
    for i in range(numero_de_runs - 1):
        print(f"Comparando Run-{i} com Run-{i+1} para '{analise}'...")

        arquivo1_path = base_dir / f"Run-{i}" / f"{teste}-{analise}.csv"
        arquivo2_path = base_dir / f"Run-{i+1}" / f"{teste}-{analise}.csv"

        if not arquivo1_path.is_file() or not arquivo2_path.is_file():
            print(f"Aviso: Pulando comparação, arquivo não encontrado para Run-{i} ou Run-{i+1}.")
            continue
        
        # --- Lógica para Tracing ---
        if analise == "tracing":
            coluna_chave = "Function"
            try:
                with open(arquivo1_path, newline='', encoding='utf-8') as f1:
                    reader1 = csv.DictReader(f1)
                    linhas1_dict = {linha[coluna_chave]: linha for linha in reader1}
                with open(arquivo2_path, newline='', encoding='utf-8') as f2:
                    reader2 = csv.DictReader(f2)
                    linhas2_dict = {linha[coluna_chave]: linha for linha in reader2}
            except KeyError: print(f"Erro: A coluna chave '{coluna_chave}' não foi encontrada. Pulando."); continue
            except Exception as e: print(f"Erro ao ler os arquivos CSV: {e}"); continue

            chaves1 = set(linhas1_dict.keys()); chaves2 = set(linhas2_dict.keys())
            apenas_em_run1 = sorted(list(chaves1 - chaves2))
            apenas_em_run2 = sorted(list(chaves2 - chaves1))
            chaves_comuns = chaves1.intersection(chaves2)
            diferencas_comuns = []
            
            for chave in sorted(list(chaves_comuns)):
                linha1 = linhas1_dict[chave]; linha2 = linhas2_dict[chave]
                diffs_nesta_chave = []
                if linha1.get('Call_Frequency') != linha2.get('Call_Frequency'):
                    diffs_nesta_chave.append(f"Frequência: Run{i}={linha1.get('Call_Frequency')} vs Run{i+1}={linha2.get('Call_Frequency')}")
                if linha1.get('Unique_Return_Values') != linha2.get('Unique_Return_Values'):
                    diffs_nesta_chave.append(f"Retornos: Run{i}='{linha1.get('Unique_Return_Values')}' vs Run{i+1}='{linha2.get('Unique_Return_Values')}'")
                if diffs_nesta_chave:
                    diferencas_comuns.append(f"- {chave}:\n    - {'; '.join(diffs_nesta_chave)}")

            arquivo_saida = base_dir / f"Run-{i}_vs_{i+1}-{teste}-tracing-diff.txt"
            with open(arquivo_saida, 'w', encoding='utf-8') as saida:
                saida.write(f"Comparação de Tracing: Run {i} vs Run {i+1}\n\n")
                if not apenas_em_run1 and not apenas_em_run2 and not diferencas_comuns:
                    saida.write("Nenhuma diferença encontrada.")
                else:
                    if apenas_em_run1:
                        saida.write(f"--- Funções chamadas apenas na Run {i} ({len(apenas_em_run1)}) ---\n")
                        for func in apenas_em_run1: saida.write(f"- {func}\n")
                        saida.write("\n")
                    if apenas_em_run2:
                        saida.write(f"--- Funções chamadas apenas na Run {i+1} ({len(apenas_em_run2)}) ---\n")
                        for func in apenas_em_run2: saida.write(f"- {func}\n")
                        saida.write("\n")
                    if diferencas_comuns:
                        saida.write(f"--- Funções com comportamento diferente ({len(diferencas_comuns)}) ---\n")
                        for diff in diferencas_comuns: saida.write(f"{diff}\n")
            print(f"Relatório de diferença de tracing salvo em: {arquivo_saida}")
        
        # --- Lógica para Profiling ---
        elif analise == "profiling":
            try:
                with open(arquivo1_path, newline='', encoding='utf-8') as f1:
                    reader1 = csv.DictReader(f1)
                    linhas1 = {linha[coluna_chave]: linha for linha in reader1}
                with open(arquivo2_path, newline='', encoding='utf-8') as f2:
                    reader2 = csv.DictReader(f2)
                    linhas2 = {linha[coluna_chave]: linha for linha in reader2}
            except KeyError: print(f"Erro: A coluna chave '{coluna_chave}' não foi encontrada. Pulando."); continue
            except Exception as e: print(f"Erro ao ler os arquivos CSV: {e}"); continue
            
            dynamically_generated_pattern = re.compile(r'<.*?>:\d+\(([\w<>,]+)\)') 
            internal_methods_pattern = re.compile(r'{method \'(.+)\' of \'(.+)\' objects}')
            internal_functions_pattern = re.compile(r'\{function\s([a-zA-Z0-9_\.]+)\s+at\s0x[a-f0-9]+\}')
            sys_functions_pattern = re.compile(r'{built-in method (.+)}')
            
            todas_as_chaves = set(linhas1.keys()).union(set(linhas2.keys()))
            (dynamically_generated_diffs, internal_methods_diffs, sys_functions_diffs, 
             internal_functions_diffs, misc_diffs, pylibs_diffs, 
             project_diffs, dependencies_diffs) = ([] for _ in range(8))

            for chave in sorted(todas_as_chaves):
                linha1 = linhas1.get(chave); linha2 = linhas2.get(chave)
                diff_message = ""
                if linha1 and linha2:
                    for coluna, valor1 in linha1.items():
                        if coluna == coluna_chave: continue
                        valor2 = linha2.get(coluna, 'N/A')
                        if valor1 != valor2:
                            diff_message = f"DIFERENÇA DE VALOR em '{chave}': Coluna '{coluna}' -> Run{i}='{valor1}' vs Run{i+1}='{valor2}'"
                            break
                elif linha1: diff_message = f"APENAS NA Run {i}: Chave '{chave}'"
                elif linha2: diff_message = f"APENAS NA Run {i+1}: Chave '{chave}'"

                if diff_message:
                    if "site-packages" in chave: dependencies_diffs.append(diff_message)
                    elif projeto in chave: project_diffs.append(diff_message)
                    elif "lib/python" in chave: pylibs_diffs.append(diff_message)
                    elif dynamically_generated_pattern.match(chave): dynamically_generated_diffs.append(diff_message)
                    elif internal_methods_pattern.match(chave): internal_methods_diffs.append(diff_message)
                    elif sys_functions_pattern.match(chave): sys_functions_diffs.append(diff_message)
                    elif internal_functions_pattern.match(chave): internal_functions_diffs.append(diff_message)
                    else: misc_diffs.append(diff_message)
            
            arquivo_saida = base_dir / f"Run-{i}_vs_{i+1}-{teste}-profiling-diff.txt"
            with open(arquivo_saida, 'w', encoding='utf-8') as saida:
                all_diffs_lists = [project_diffs, dependencies_diffs, pylibs_diffs, dynamically_generated_diffs, internal_methods_diffs, sys_functions_diffs, internal_functions_diffs, misc_diffs]
                total_diff_count = sum(len(d) for d in all_diffs_lists)
                
                saida.write(f"Comparação de Profiling: Run {i} vs Run {i+1}\n\n")
                if total_diff_count == 0: saida.write("Nenhuma diferença encontrada.")
                else:
                    saida.write(f"Encontradas {total_diff_count} diferenças:\n\n")
                    if project_diffs: saida.write(f"--- Diffs do Projeto ({len(project_diffs)}) ---\n" + '\n'.join(project_diffs) + '\n\n')
                    if dependencies_diffs: saida.write(f"--- Diffs de Dependências ({len(dependencies_diffs)}) ---\n" + '\n'.join(dependencies_diffs) + '\n\n')
                    if pylibs_diffs: saida.write(f"--- Diffs de Bibliotecas Padrão do Python ({len(pylibs_diffs)}) ---\n" + '\n'.join(pylibs_diffs) + '\n\n')
                    if dynamically_generated_diffs: saida.write(f"--- Diffs de Funções Geradas Dinamicamente ({len(dynamically_generated_diffs)}) ---\n" + '\n'.join(dynamically_generated_diffs) + '\n\n')
                    if internal_methods_diffs: saida.write(f"--- Diffs de Métodos Internos de Objetos ({len(internal_methods_diffs)}) ---\n" + '\n'.join(internal_methods_diffs) + '\n\n')
                    if sys_functions_diffs: saida.write(f"--- Diffs de Funções Internas do Sistema ({len(sys_functions_diffs)}) ---\n" + '\n'.join(sys_functions_diffs) + '\n\n')
                    if internal_functions_diffs: saida.write(f"--- Diffs de Funções Internas do Python ({len(internal_functions_diffs)}) ---\n" + '\n'.join(internal_functions_diffs) + '\n\n')
                    if misc_diffs: saida.write(f"--- Outras Diffs ({len(misc_diffs)}) ---\n" + '\n'.join(misc_diffs) + '\n')

def main():
    parser = argparse.ArgumentParser(description="Compara ou compila arquivos CSV de runs de teste.")
    parser.add_argument("test_directory", help="Diretório do teste (ex: Test-projeto/nome_do_teste)", type=str)
    parser.add_argument("analysis", help="Tipo de análise (coverage, profiling, tracing)", type=analysis_definer)
    parser.add_argument("number_of_runs", help="Número total de runs executadas", type=str_to_int)
    parser.add_argument("column", help="Nome da coluna a ser usada como chave/valor.", type=str)
    args = parser.parse_args()
    
    comparar_csvs(args.test_directory, args.analysis, args.number_of_runs, args.column)

if __name__ == "__main__":
    main()