import subprocess
import csv
import time

csv_path = "FlapyRepos/carnossauro.csv"

def csv_has_data(path):
    with open(path, newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)
        return len(rows) > 1 

while csv_has_data(csv_path):
    result = subprocess.run(
        ["python3", "main.py", "--run-specific-test", csv_path, "--include-test-profiling", "True"],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    
    if result.stderr:
        print("Erros:")
        print(result.stderr)
    
    time.sleep(5)

print("CSV vazio. Fim da execução.")
