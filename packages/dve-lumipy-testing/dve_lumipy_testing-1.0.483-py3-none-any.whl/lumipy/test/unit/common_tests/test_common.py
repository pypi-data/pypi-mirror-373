import unittest

from lumipy.provider.common import strtobool, _get_latest_major_semver


class TestStrToBool(unittest.TestCase):

    base_true_values = ['y', 'yes', 't', 'true', 'on', '1']
    base_false_values = ['n', 'no', 'f', 'false', 'off', '0']
    invalid_values = ['problematic', '2', '']

    true_values = base_true_values + [val.upper() for val in base_true_values]
    false_values = base_false_values + [val.upper() for val in base_false_values]

    def test_strtobool_true(self):
        for val in self.true_values:
            self.assertTrue(strtobool(val))

    def test_strtobool_false(self):
        for val in self.false_values:
            self.assertFalse(strtobool(val))

    def test_strtobool_invalid_args(self):
        for val in self.invalid_values:
            with self.assertRaises(ValueError):
                strtobool(val)


class TestGetLatestMajorSemver(unittest.TestCase):

    no_dotnet_semvers = []
    dotnet_6_and_8_semvers = ['5.0.1', '6.0.1', '8.0.1', '8.0.2']

    def test_get_latest_major_semver_with_multiple_versions(self):
        major_version = _get_latest_major_semver(self.dotnet_6_and_8_semvers)
        self.assertEqual(major_version, 8)

    def test_get_latest_major_semver_with_no_versions(self):
        major_version = _get_latest_major_semver(self.no_dotnet_semvers)
        self.assertIsNone(major_version)
