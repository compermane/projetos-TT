import gzip
import csv
import re
import argparse
from collections import Counter, defaultdict
from pathlib import Path

def parse_hierarchical_trace(input_file: str):
    """
    Processa o arquivo de tracing hierárquico para obter frequência de chamadas
    e os valores de retorno únicos para cada função.
    """
    if not Path(input_file).exists():
        print(f"Erro: Arquivo de entrada não encontrado: {input_file}")
        return None, None

    function_calls = Counter()
    return_values = defaultdict(set)

    # Regex corrigidas para tratar a indentação como opcional usando '*'
    # Ex: (opcional)> func_name in file.py
    call_pattern = re.compile(r"^\s*[>]*\s*([\w<>.-]+)\s+in\s+([\w./\\<>-]+\.py)")
    # Ex: (opcional)< func_name returned: some_value
    return_pattern = re.compile(r"^\s*[<]*\s*([\w<>.-]+)\s+returned:\s*(.*)")

    try:
        with gzip.open(input_file, 'rt', encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                call_match = call_pattern.match(line)
                if call_match:
                    func_name, file_name = call_match.groups()
                    unique_key = f"{file_name}::{func_name}"
                    function_calls[unique_key] += 1
                    continue

                return_match = return_pattern.match(line)
                if return_match:
                    func_name, return_value = return_match.groups()
                    return_values[func_name].add(return_value.strip())

    except Exception as e:
        print(f"Erro ao processar o arquivo de trace '{input_file}': {e}")
        return None, None
    
    return function_calls, return_values

def save_to_csv(output_file: str, function_calls: Counter, return_values: defaultdict):
    """
    Salva os resultados de frequência e valores de retorno em um arquivo CSV.
    """
    if not function_calls:
        print("Nenhuma chamada de função foi extraída. O arquivo CSV não será gerado.")
        return

    try:
        with open(output_file, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['Function', 'Call_Frequency', 'Unique_Return_Values'])
            
            for func_key, count in sorted(function_calls.items()):
                func_name_only = func_key.split("::")[-1]
                unique_returns_set = return_values.get(func_name_only, set())
                returns_str = " | ".join(sorted(list(unique_returns_set)))
                writer.writerow([func_key, count, returns_str])
        
        print(f"Análise concluída. Resultados salvos em {output_file}")
    except Exception as e:
        print(f"Erro ao escrever o arquivo CSV '{output_file}': {e}")

def main():
    parser = argparse.ArgumentParser(description="Analisa um arquivo compactado de tracing hierárquico.")
    parser.add_argument('--input_file', required=True, help="Caminho do arquivo .gz de entrada.")
    parser.add_argument('--output_file', required=True, help="Caminho do arquivo CSV de saída.")
    args = parser.parse_args()

    print(f"Processando arquivo: {args.input_file}")
    function_calls, return_values = parse_hierarchical_trace(args.input_file)
    if function_calls:
        save_to_csv(args.output_file, function_calls, return_values)
    else:
        print("Processamento do arquivo de trace não gerou dados.")

if __name__ == "__main__":
    main()