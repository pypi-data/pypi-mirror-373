import unittest
from lumipy.helpers.backoff_handler import BackoffHandler


class TestQueryJob(unittest.TestCase):
    def test_pause_time_smaller_than_max_pause_time(self):
        backoff_handler_test = BackoffHandler(pause_time = 0.5, max_pause_time=20, beta=1.0001)
        backoff_handler_test.sleep()
        self.assertAlmostEqual(backoff_handler_test.pause_time, 0.50005, places = 5)

    def test_pause_time_equals_max_pause_time(self):
        backoff_handler_test = BackoffHandler(pause_time = 30, max_pause_time=30, beta=1.001)
        backoff_handler_test.sleep()
        self.assertEqual(backoff_handler_test.pause_time, 30)

    def test_pause_time_bigger_than_max_pause_time(self):
        with self.assertRaises(ValueError) as ve:  # test that the ctor is raising a ValueError
            _ = BackoffHandler(pause_time=100, max_pause_time=20, beta=1.1)

        ex = str(ve.exception)
        self.assertIn("Pause time must be between 0.1 and 20, both inclusive.", ex)

    def test_default_optional_values(self):
        backoff_handler_test = BackoffHandler()
        backoff_handler_test.sleep()
        self.assertAlmostEqual(backoff_handler_test.pause_time, 0.1005012520859401, places = 5)

    def test_call_1000_times_pause_time_equals_max_pause_time(self):
        backoff_handler_test = BackoffHandler()
        # I have checked that this is constant after 922 requests
        for i in range(1000):
            backoff_handler_test._update_pause_time()
        self.assertEqual(backoff_handler_test.pause_time, 10)
