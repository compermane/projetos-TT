"""
Plugin do Pytest para coletar resultados e acionar análises de tracing e profiling.
"""
from typing import List, Tuple, Any
from pathlib import Path
import pytest
import sys
import cProfile
import pstats
import gzip
import subprocess
import os
from time import time

class TestResult:
    def __init__(self, trace: bool = False, prof: bool = False, cov: bool = False, 
                 outputDir: str = ".", testName: str = "",
                 automation_root: Path = None, project_root_dir: str = ""):
        
        self.testName = testName
        self.outputDir = outputDir
        self.cov = cov
        self.trace = trace
        self.prof = prof
        
        self.automation_root = automation_root
        if not self.automation_root or not self.automation_root.is_dir():
            raise ValueError("O caminho raiz do projeto de automação é inválido ou não foi fornecido.")

        # Novo: Armazena o caminho do projeto sob teste para filtragem
        self.project_root_dir = project_root_dir
        if self.trace and not self.project_root_dir:
            raise ValueError("`project_root_dir` deve ser fornecido para habilitar o tracing.")

        # Atributos para resultados
        self.passed = 0
        self.failed = 0
        self.xfailed = 0
        self.skipped = 0
        self.total_duration = 0.0

        # Atributos para análise
        self.profiler = cProfile.Profile() if self.prof else None
        self.traceBuffer = []
        self.trace_depth = 0 # Contador para a profundidade da chamada

    # --- Hooks do Pytest ---

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        """Captura o resultado e a duração de cada teste executado."""
        outcome = yield
        report = outcome.get_result()
        if report.when == 'call':
            self.total_duration = report.duration

    def pytest_runtest_setup(self, item):
        """Hook chamado antes de cada teste. Habilita as ferramentas de análise."""
        if self.prof and self.profiler:
            self.profiler.enable()
        if self.trace:
            self.trace_depth = 0 # Reseta a profundidade para cada teste
            self.traceBuffer = [] # Limpa o buffer para cada teste
            sys.settrace(self.hierarchical_trace)

    def pytest_runtest_teardown(self, item, nextitem):
        """Hook chamado após cada teste. Desabilita as ferramentas de análise."""
        if self.prof and self.profiler:
            self.profiler.disable()
        if self.trace:
            sys.settrace(None)

    def pytest_sessionfinish(self, session, exitstatus):
        """Processa e salva os dados coletados no final da sessão."""
        # A lógica agora é por teste, mas podemos deixar um hook de sessão para tarefas futuras.
        # Por enquanto, a maior parte do processamento acontecerá no teardown do teste.
        # Vamos mover o processamento para cá para garantir que ele rode uma vez por sessão.
        if self.prof:
            self.process_profiling_data()
        if self.trace:
            self.process_tracing_data()

    def pytest_terminal_summary(self, terminalreporter, exitstatus):
        """Captura as estatísticas finais da sessão do pytest."""
        self.passed = len(terminalreporter.stats.get('passed', []))
        self.failed = len(terminalreporter.stats.get('failed', []))
        self.xfailed = len(terminalreporter.stats.get('xfailed', []))
        self.skipped = len(terminalreporter.stats.get('skipped', []))

    # --- Métodos de Processamento de Dados ---

    def process_profiling_data(self):
        """Salva os dados brutos do profiler e chama o script de parse."""
        if not self.profiler: return
        
        stats_file = Path(self.outputDir) / f"{self.testName}-stats.txt"
        profiling_csv = Path(self.outputDir) / f"{self.testName}-profiling.csv"
        
        with open(stats_file, "w", encoding='utf-8') as f:
            pstats.Stats(self.profiler, stream=f).sort_stats("ncalls").print_stats()
        
        parse_script = self.automation_root / "parse_profiling.py"
        if parse_script.exists():
            subprocess.run([sys.executable, str(parse_script), "--input_file", str(stats_file), "--output_file", str(profiling_csv)])
        else:
            print(f"AVISO: Script de parse de profiling não encontrado em {parse_script}")

    def process_tracing_data(self):
        """Salva o buffer de trace em um arquivo e chama o script de parse."""
        if self.traceBuffer:
            calls_gz_file = Path(self.outputDir) / "calls.gz"
            tracing_csv = Path(self.outputDir) / f"{self.testName}-tracing.csv"
            
            print(f"Escrevendo {len(self.traceBuffer)} linhas de trace em {calls_gz_file}")
            with gzip.open(calls_gz_file, "wt", encoding='utf-8') as f:
                f.writelines(self.traceBuffer)
            
            parse_script = self.automation_root / "parse_tracing.py"
            if parse_script.exists():
                subprocess.run([sys.executable, str(parse_script), "--input_file", str(calls_gz_file), "--output_file", str(tracing_csv)])
            else:
                print(f"AVISO: Script de parse de tracing não encontrado em {parse_script}")
        else:
            print("Buffer de trace vazio, nenhum arquivo será gerado.")

    # --- LÓGICA DE TRACING REFINADA ---

    def hierarchical_trace(self, frame, event, arg):
        """
        Função de callback para sys.settrace que filtra por diretório e
        cria um log hierárquico de chamadas e retornos.
        """
        if event not in ('call', 'return'):
            return self.hierarchical_trace

        code = frame.f_code
        filename = code.co_filename
        
        # O FILTRO PRINCIPAL: Ignora tudo que não está dentro da pasta do projeto testado.
        if not filename.startswith(self.project_root_dir):
            return self.hierarchical_trace

        func_name = code.co_name

        if event == 'call':
            indent = ">" * self.trace_depth
            self.traceBuffer.append(f"{indent} {func_name} in {os.path.basename(filename)}\n")
            self.trace_depth += 1
        
        elif event == 'return':
            self.trace_depth -= 1
            indent = "<" * self.trace_depth
            
            # Captura o valor de retorno de forma segura e concisa
            try:
                return_value_str = repr(arg)
            except Exception:
                return_value_str = "[Unrepresentable object]"

            # Trunca valores de retorno muito longos para manter o log limpo
            if len(return_value_str) > 150:
                return_value_str = return_value_str[:150] + "..."
                
            self.traceBuffer.append(f"{indent} {func_name} returned: {return_value_str}\n")

        return self.hierarchical_trace