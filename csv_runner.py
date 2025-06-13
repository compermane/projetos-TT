import subprocess
import csv
import time
import argparse
import os

parser = argparse.ArgumentParser(description="Executa testes com análise selecionada.")
parser.add_argument(
    "--analise",
    choices=["profiling", "coverage", "tracing"],
    required=True,
    help="Tipo de análise a ser executada"
)
args = parser.parse_args()

csv_path = "FlapyRepos/flakytests.csv"

def csv_has_data(path):
    with open(path, newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)
        return len(rows) > 1

n = 0
while csv_has_data(csv_path):
    venv_dir = f"venv-{n}"
    subprocess.run(["python3", "-m", "venv", venv_dir])

    pip_path = os.path.join(venv_dir, "bin", "pip")
    os.environ["PIP_PATH"] = pip_path
    python_path = os.path.join(venv_dir, "bin", "python")

    subprocess.run([pip_path, "install", "pytest==7.2.1"])
    subprocess.run([pip_path, "install", "pytest-cov"])
    subprocess.run([pip_path, "install", "virtualenv"])

    result = subprocess.run(
        [
            python_path, "main.py",
            "--run-specific-test", csv_path,
            f"--include-test-{args.analise}", "True"
        ],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.stderr:
        print("Erros:")
        print(result.stderr)

    subprocess.run(["rm", "-rf", venv_dir])
    test_dir = os.environ.get("TEST_DIR")
    #subprocess.run(["rm", "-rf", test_dir])

    n += 1
    time.sleep(5)

print("CSV vazio. Fim da execução.")
