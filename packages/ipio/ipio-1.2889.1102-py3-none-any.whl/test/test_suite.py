import unittest

import logging
from test.test_example import ExampleTest


def functional_suite():
    """
    Gather all the tests from this module in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTests(
        [
            unittest.makeSuite(ExampleTest),
        ]
    )
    return test_suite


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    runner = unittest.TextTestRunner(verbosity=3)
    ts = functional_suite()
    runner.run(ts)
