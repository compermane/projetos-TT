# Uso
Para a testagem de repositórios individuais
```bash
python3 main.py --repo-dir </path/to/repo> --repo-name <repo-name> --output-dir <dir> --no-runs <no-runs>
 --include-test-tracing <bool> --include-test-profiling <bool> --include-test-coverage <bool>
```
Ou, para a testagem de vários repositórios
```bash
python3 main.py --read-from-csv <csv-file> --output-dir <dir>
--include-test-tracing <bool> --include-test-profiling <bool> --include-test-coverage <bool>
```
Onde <csv-file> possui as colunas "RepoName", "Repo", "GitHash" e "#Runs".

# Resultados
Os resultados são postos no diretório indicado por <dir>. Então são criados outros diretórios para cada repositório xxx no formato "Test-xxx" e, para cada caso de teste em cada arquivo de teste, são criadas diretórios que contém dados sobre cada run individual. Esses dados podem ser sobre tracing, coverage ou profiling de testes.

# Tracing
Armazena dados de tracing do teste da seguinte forma:
- ">" representa a chamada de uma função
- ">>" representa a chamada de outra função dentro da função inicial (cria uma pilha de chamadas)
- "<" representa o retorno de uma função correspondente a função no topo da pilha de chamadas
Assim, o tracing de um teste fica parecido com:
```text
>Funcao1: ArquivoDeOrigem (ArquivoRaiz, LinhaDoArquivoRaiz, FuncaoDoArquivoRaiz)
>>Funcao2: ArquivoDeOrigem (ArquivoRaiz, LinhaDoArquivoRaiz, FuncaoDoArquivoRaiz)
<<Funcao2: ValorDeRetorno (ArquivoRaiz, LinhaDoArquivoRaiz, FuncaoDoArquivoRaiz)
...
```