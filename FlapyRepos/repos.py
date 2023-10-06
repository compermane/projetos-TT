import csv

if __name__ == "__main__":
    with open('TestsOverview.csv', 'r', encoding = "utf8") as csv_repos:
        repos = list()
        csv_reader = csv.reader(csv_repos, delimiter = ',')
        line_count = 0
        for row in csv_reader:
            if line_count != 0:
                if row[0] not in repos:
                    repos.append(row[0])
            line_count += 1

        csv_repos.close()

    with open('repos.txt', 'w') as repos_txt:
        for repo in repos:
            print(f"{repo}", file = repos_txt)