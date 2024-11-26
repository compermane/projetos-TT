import json
import csv
import argparse

def parse_coverage_data(input_file: str, output_file: str):
    """Extrai dados de cobertura de arquivos JSON e escreve em um arquivo CSV."""
    # Lista para armazenar os dados extraídos
    coverage_data = []

    try:
        # Lê o arquivo JSON
        with open(input_file, 'r') as f:
            json_data = json.load(f)
        
        # Coleta os dados de cobertura
        if "totals" in json_data:
            totals = json_data["totals"]
            percent_covered = totals.get("percent_covered", 0.0)
            covered_lines = totals.get("covered_lines", 0)
            
            coverage_data.append([input_file.split("/")[-1], percent_covered, covered_lines])
        else:
            print(f"Chave 'totals' não encontrada no arquivo: {input_file}")
    
    except FileNotFoundError:
        print(f"Erro: Arquivo '{input_file}' não encontrado.")
    except json.JSONDecodeError:
        print(f"Erro: Arquivo '{input_file}' não é um JSON válido.")
    except Exception as e:
        print(f"Erro desconhecido ao processar o arquivo '{input_file}': {e}")

    # Escreve os dados extraídos em um arquivo CSV
    with open(output_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        # Escrever cabeçalho
        csv_writer.writerow(['Arquivo', 'Percentual de Cobertura (%)', 'Linhas Cobertas'])
        # Escrever os dados
        csv_writer.writerows(coverage_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Converte arquivos JSON de cobertura para CSV.")
    parser.add_argument("--input_file", help="Arquivo de entrada (JSON) com dados de cobertura.")
    parser.add_argument("--output_file", help="Arquivo de saída para os dados (CSV).")
    args = parser.parse_args()

    if args.input_file and args.output_file:
        parse_coverage_data(args.input_file, args.output_file)
    else:
        print("Erro: Você deve fornecer --input_file e --output_file.")
