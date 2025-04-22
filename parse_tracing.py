import gzip
import csv
import re
import argparse
from collections import Counter, defaultdict

def parse_tracing_file(file_path):
    """
    Processa o arquivo de tracing para obter frequência de chamadas e valores de retorno.
    """
    function_calls = Counter()
    return_values = defaultdict(list)
    
    stack = []

    with gzip.open(file_path, 'rt') as file:
        for line in file:
            if line.startswith(('>', '>>', '>>>', '>>>>')):
                # Captura a função chamada
                func_match = re.match(r'^[>]+([^:]+):', line)
                if func_match:
                    func_name = func_match.group(1).strip()
                    stack.append(func_name)
                    function_calls[func_name] += 1
            elif line.startswith(('<', '<<', '<<<', '<<<<')):
                # Captura o valor de retorno
                return_match = re.match(r'^[<]+([^:]+):\s*(.*)', line)
                if return_match:
                    func_name, return_value = return_match.groups()
                    func_name = func_name.strip()
                    return_value = return_value.strip()
                    if return_value:
                        return_values[func_name].append(return_value)
                    if stack and stack[-1] == func_name:
                        stack.pop()
    
    return function_calls, return_values

def save_to_csv(output_file, function_calls, return_values):
    """
    Salva os resultados de frequência e valores de retorno em um arquivo CSV.
    """
    with open(output_file, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Function', 'Call Frequency', 'Unique Return Values'])
        
        for func, count in function_calls.items():
            unique_returns = ', '.join(set(return_values[func]))
            writer.writerow([func, count, unique_returns])

def main():
    parser = argparse.ArgumentParser(description="Analisa um arquivo compactado de tracing.")
    parser.add_argument('--input_file', required=True, help="Caminho do arquivo .gz de entrada.")
    parser.add_argument('--output_file', required=True, help="Caminho do arquivo CSV de saída.")
    args = parser.parse_args()

    if args.input_file and args.output_file:
        print(f"Processando arquivo: {args.input_file}")
        function_calls, return_values = parse_tracing_file(args.input_file)
        save_to_csv(args.output_file, function_calls, return_values)
        print(f"Análise concluída. Resultados salvos em {args.output_file}")
    else:
        print("Erro: Você deve fornecer --input_file e --output_file.")
  

if __name__ == "__main__":
    main()
