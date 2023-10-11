from main import *
from datetime import date

CSV_REPOS = 'repos_csv.csv'

if __name__ == '__main__':
    data = date.today()
    directory = 'FlaPy-Repos-' + str(data)
    comando = 'mkdir ' + directory
    os.system(comando)

    writer()
    repos = dict()
    repos = reader(CSV_REPOS)
    cloning(repos)

    numRuns = getNumRuns(repos)
    comando = './flapy.sh run --plus-random-runs --out-dir ' + directory + CSV_REPOS + str(numRuns)