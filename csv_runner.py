import subprocess
import csv
import time
import argparse
import os
import shutil
from datetime import datetime

# --- Configuração dos Argumentos ---
parser = argparse.ArgumentParser(description="Executa testes com análise selecionada.")
parser.add_argument(
    "--analise",
    choices=["profiling", "coverage", "tracing"],
    required=True,
    help="Tipo de análise a ser executada"
)
args = parser.parse_args()

# --- Constantes e Configurações ---
csv_path = "FlapyRepos/flaky.csv"
ERROR_LOG_DIR = "error_logs"
os.makedirs(ERROR_LOG_DIR, exist_ok=True)
CWD = os.getcwd()

# --- Funções Auxiliares ---
def csv_has_data(path):
    """Verifica se um arquivo CSV existe e tem linhas de dados após o cabeçalho."""
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return False
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
            return any(reader)
        except StopIteration:
            return False

# --- Fluxo Principal ---

processed_lines_in_session = set()

while csv_has_data(csv_path):
     
    repo_name_safe = "unknown_repo"
    repo_full_name = "N/A"
    unique_test_key = None
    
    try:
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            first_data_row = next(reader)
            
            repo_full_name = first_data_row[0]
            repo_name_safe = repo_full_name.replace("/", "_")

            unique_test_key = tuple(first_data_row)

    except (StopIteration, IndexError, FileNotFoundError):
        print("Aviso: Não foi possível ler o nome do repositório do CSV ou o arquivo está vazio.")
        break
    
    if unique_test_key in processed_lines_in_session:
        print(f"Linha de teste para {repo_full_name} ({unique_test_key[3]}) já processada nesta sessão. Removendo do CSV e continuando.")
        with open(csv_path, 'r', newline='', encoding='utf-8') as f_in:
            reader_in = list(csv.reader(f_in))
        with open(csv_path, 'w', newline='', encoding='utf-8') as f_out:
            writer_out = csv.writer(f_out)
            writer_out.writerows(reader_in[0:1] + reader_in[2:])
        continue
    
    processed_lines_in_session.add(unique_test_key)
    
    print(f"\n{'='*20}\n--- Processando repositório: {repo_full_name} ---\n{'='*20}")
    print(f"  - Teste: {unique_test_key[3]}")

    venv_dir_name = f"venv-{repo_name_safe}"
    abs_venv_path = os.path.join(CWD, venv_dir_name)

    pip_path = os.path.join(abs_venv_path, "bin", "pip")
    python_path = os.path.join(abs_venv_path, "bin", "python")

    if not os.path.exists(abs_venv_path):
        print(f"Ambiente virtual não encontrado. Criando em: {abs_venv_path}")
        subprocess.run(["python3", "-m", "venv", abs_venv_path], check=True)

        print("Instalando ferramentas base no novo ambiente virtual...")
        subprocess.run([pip_path, "install", "--upgrade", "pip", "setuptools", "wheel"], check=True, capture_output=True)
    
        base_tools = [
        "pytest==7.2.1",
        "pytest-cov",
        "coverage"
        ]

        subprocess.run([pip_path, "install"] + base_tools, check=True, capture_output=True)
        subprocess.run([pip_path, "install", "setuptools<58"], check=True, capture_output=True)
    else:
        print(f"Reutilizando ambiente virtual existente em: {abs_venv_path}")
    
    print(f"\n--- Iniciando execução do main.py para o teste ---")
    
    result = subprocess.run(
        [
            python_path, "main.py",
            "--run-specific-test", csv_path,
            f"--include-test-{args.analise}", "True",
            "--venv-path", abs_venv_path
        ],
        text=True,
        encoding='utf-8'
    )
    print("--- Fim da execução do main.py ---")

    if result.returncode != 0:
        print(f"\n!!!!!! ERRO: O script main.py terminou com o código de saída {result.returncode}. !!!!!!")
        error_filename = f"{repo_name_safe}_error.txt"
        error_filepath = os.path.join(ERROR_LOG_DIR, error_filename)
        try:
            with open(error_filepath, 'a', encoding='utf-8') as error_file:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                error_file.write(f"Log de Erro em {timestamp} para o repositório: {repo_full_name}\n")
                error_file.write(f"Teste: {unique_test_key[3]}\n")
                error_file.write("="*40 + "\n")
                error_file.write(f"O processo falhou com o código de saída: {result.returncode}\n")
                error_file.write("Verifique a saída do console acima para o traceback detalhado.\n\n")
            print(f"Um registro deste erro foi salvo em: {error_filepath}")
        except Exception as e:
            print(f"Falha ao salvar o arquivo de log de erro: {e}")
        
    time.sleep(1)

print("\nCSV vazio ou processado. Fim da execução.")