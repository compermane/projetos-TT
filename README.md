# instruções para execução dos projetos:

- tenha um arquivo flaky.csv dentro da pasta "FlapyRepos" com os dados dos repositórios nesse formato:

Name,URL,Hash,Test,No_Runs
rs3clans.py,https://github.com/johnvictorfs/rs3clans.py,692ffb859d954a304d039a6e20cc39bc55ed13cb,rs3clans.py/tests/test_players.py::test_skill_exp[CoNsTiTutioN-1154],10.0

Atenção! o caminho para o teste deve estar correto.
Seguindo o padrão:
test_example.py::Classe(se houver)::nome_do_teste
exemplo:
rs3clans.py/tests/test_players.py::test_skill_exp[CoNsTiTutioN-1154] - Está correto

rs3clans.py/tests/test_players.py::test_players::test_skill_exp[CoNsTiTutioN-1154] - Está errado, o nome do arquivo "test_players" aprece duplicado.

service-manager/test/unit/test_smdownload.py::TestSmDownload::test_reporthook10percent - Está correto

Para executar as análises:
Para tracing
```bash
python3 csv_runner.py --analise tracing
```
Para profiling
```bash
python3 csv_runner.py --analise profiling
```
Para coverage
```bash
python3 csv_runner.py --analise coverage
```

Será criado um ambiente virtual especifico para cada repositório, e uma pasta "Test-(nome_do_repo)" onde estarão os dados das análises. Dentro dela, haverá uma subpasta para cada teste, contendo os dados brutos, relatórios de cada execução (Run-0, Run-1, etc.) e os arquivos de comparação gerados pelo diff_finder.py.

Atenção: O sistema instala um conjunto de pacotes base (pytest==7.2.1, pytest-cov, coverage) em cada ambiente virtual. Em seguida, ele tenta instalar as dependências do projeto, mas ignora se o projeto pedir uma versão diferente desses pacotes base. Isso pode causar conflitos ou erros se um repositório for estritamente dependente de uma versão muito antiga ou muito nova do pytest, por exemplo.

