import compilertests 
compilersuite = compilertests.GetTestSuite()
def run_all():
    import unittest
    unittest.main(compilertests)
