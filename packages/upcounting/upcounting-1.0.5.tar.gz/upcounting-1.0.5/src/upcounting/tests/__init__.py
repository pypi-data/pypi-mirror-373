import unittest

__all__ = ["test"]


def test() -> unittest.TextTestResult:
    loader: unittest.TestLoader = unittest.TestLoader()
    tests: unittest.TestSuite = loader.discover(start_dir="upcounting.tests")
    runner: unittest.TextTestRunner = unittest.TextTestRunner()
    result: unittest.TextTestResult = runner.run(tests)
    return result
