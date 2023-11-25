from Analise import analise

if __name__ == "__main__":
    analise.traceFuncs("analytic_shrinkage/nonlinshrink/test/test_analytic_shrinkage.py", "test_demean", "analytic_shrinkage")
    analise.refineCovers("analytic_shrinkage")
    analise.getTestCoverage("nonlinshrink.test.test_analytic_shrinkage.cover", "analytic_shrinkage", "test_demean")