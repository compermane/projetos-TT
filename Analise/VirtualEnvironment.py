from typing import List, Tuple, Optional
from pathlib import Path
from os import getcwd, chdir
from . import analise
import subprocess
import pytest
import shutil

class VirtualEnvironment:
    """ Adaptado de FlaPy
    """
    def __init__(self, venv_dir: str, root_dir: str, requirements: List[Path]) -> None:
        self._venv_dir = f"{root_dir}/{venv_dir}"
        self._requirements = requirements
        self._root_dir = root_dir

        # Criando o venv para o repositório
        create_venv_cmd = ["virtualenv", self._venv_dir]
        subprocess.run(create_venv_cmd, check = True)

    @property
    def venv_name(self):
        return self._venv_name
    
    @property
    def requirements(self):
        return self._requirements
    
    @property
    def venv_dir(self):
        return self._venv_dir
    
    def cleanUp(self):
        shutil.rmtree(self._venv_dir)

    def runCommands(self, commands: Optional[List[str]] = None) -> Tuple[str, str]:
        command_list = [
            f"source '{self._venv_dir}/bin/activate'",
            "python3 -V"
        ]

        for requirement in self._requirements:
            command_list.append(f"pip3 install -r {requirement}")

        if commands is not None:
            command_list.extend(commands)

        cmd = ";".join(command_list)

        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, executable="/bin/bash"
        )
        out, err = process.communicate()

        return (out.decode("utf-8"), err.decode("utf-8"))
    
    def uninstallDependencies(self):
        command_list = [
            f"source '{self._venv_dir}/bin/activate'",
            "python3 -V"
        ]

        for requirement in self._requirements:
            command_list.append(f"pip3 uninstall -r {requirement} -y")

        cmd = ";".join(command_list)

        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, executable="/bin/bash"
        )
        out, err = process.communicate()

        print(f" {out} \n {err}")
        return (out.decode("utf-8"), err.decode("utf-8"))
    
    def executePytest(self, test_node: str, params: List[bool], output_dir: str, origin_dir: str) -> Tuple[str, float, int, int, int, int]:
        cwd = getcwd()
        chdir(origin_dir)

        # print(f"\n\n\n {origin_dir} \n\n\n")
        include_tracing = params[0]
        include_coverage = params[1]
        include_profiling = params[2]

        test_result = analise.TestResult(include_tracing, include_profiling, include_coverage,
                                         outputDir = output_dir, testName = test_node.split("/")[-1],
                                         repoVenv = self)

        pytest.main([test_node], plugins=[test_result])

        passed_count = 0
        failed_count = 0
        xfailed_count = 0
        skipped_count = 0

        if test_result.passed != 0:
            result = "PASSED"
            passed_count += 1
        elif test_result.failed != 0:
            result = "FAILED"
            failed_count += 1
        elif test_result.skipped != 0:
            result = "SKIPPED"
            skipped_count += 1
        else:
            result = "XFAILED"
            xfailed_count += 1

        chdir(cwd)
        return (result, test_result.total_duration, passed_count, failed_count, skipped_count, xfailed_count)