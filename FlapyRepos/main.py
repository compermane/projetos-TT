import csv
import os
from time import sleep

def cloning(repos: dict()) -> None:
    os.system('cd Repos')
    
    for hash in repos: 
        nome = repos[hash][0]
        url = repos[hash][1]
        comando = 'git clone ' + url
        os.system(comando)
        cwd = os.getcwd()
        os.chdir(cwd + "/" + nome)
        comando = 'git checkout ' + hash
        os.system(comando)

if __name__ == "__main__":
    with open('repos.csv', 'r') as csv_flapy:
        repos = dict()
        csv_reader = csv.DictReader(csv_flapy, delimiter = ',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are: {", ".join(row)}')
            line_count += 1
            repos[row["Project_Hash"]] = (row["Project_Name"], row["Project_Hash"])
        csv_flapy.close()    

    cloning(repos)