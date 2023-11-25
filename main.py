from Analise import analise
from os import chdir, getcwd

if __name__ == "__main__":
    files = analise.getTestFiles("analytic_shrinkage/nonlinshrink/test")
    tests = analise.getTestCases(files)
    cwd = getcwd()
    for file in files:
        for test in tests[file]:
            analise.traceFuncs("analytic_shrinkage/nonlinshrink/test/test_analytic_shrinkage.py", test, "analytic_shrinkage")
            analise.refineCovers("analytic_shrinkage", files)
            analise.getTestCoverage("analytic_shrinkage", test)
            chdir(cwd)


