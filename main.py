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

def test_settrace() -> None:
    dirs = analise.getTestDir(getcwd() + "/" + "analytic_shrinkage")
    
    for dir in dirs:
        analise.createTestFileCopy(dir)
        analise.implementTracer(dir)

def test_profiler() -> None:
    analise.profiling("analytic_shrinkage")

if __name__ == "__main__":
    # analise.runTest("analytic_shrinkage/nonlinshrink/test/test_analytic_shrinkage.py", "test_demean")
    # print(analise.getTestFiles(analise.getTestDir("analytic_shrinkage")[0]))
    # print(analise.getTestFiles("analytic_shrinkage"))
    analise.runMultipleTimes("analytic_shrinkage", "analytic_shrinkage", 100)
    # analise.runTest(analise.getTestFiles(analise.getTestDir("analytic_shrinkage")[0]), "test_demean", "/home/eugenio/Área de trabalho/Grad")
    # res = analise.runTest("analytic_shrinkage/nonlinshrink/test/test_analytic_shrinkage.py", "test_bruh", ".")
    # print(res)
