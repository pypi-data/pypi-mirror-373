import unittest


class SetupErrorTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        raise NotImplementedError('This is a test error inside the setUpClass method.')

    def test_noop(self):
        # no-op because the test runner will never get to here
        pass


class TestingInfraTests(unittest.TestCase):

    def test_error(self):
        raise ValueError('This is a test error.')

    def test_failure(self):
        self.assertEqual(1, 2)

    def test_pass(self):
        self.assertEqual(1, 1)
