from Analise import analise
from os import chdir, getcwd

def test_trace() -> None:
    files = analise.getTestFiles("analytic_shrinkage/nonlinshrink/test")
    tests = analise.getTestCases(files)
    cwd = getcwd()
    for file in files:
        for test in tests[file]:
            analise.traceFuncs("analytic_shrinkage/nonlinshrink/test/test_analytic_shrinkage.py", test, "analytic_shrinkage")
            analise.refineCovers("analytic_shrinkage", files)
            analise.getTestCoverage("analytic_shrinkage", test)
            chdir(cwd)

if __name__ == "__main__":
    # analise.runTest("Algoritmos/tests/test_ordenacao.py", "Algoritmos","test_bubbleSort")
    dirs = analise.getTestDir(getcwd() + "/" + "analytic_shrinkage")
    
    for dir in dirs:
        analise.createTestFileCopy(dir)
        analise.implementTracer(dir)


