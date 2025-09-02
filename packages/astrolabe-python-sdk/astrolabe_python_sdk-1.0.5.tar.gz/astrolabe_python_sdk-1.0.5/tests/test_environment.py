import unittest
from astrolabe.client import Environment


class TestEnvironmentEnum(unittest.TestCase):
    def test_environment_values_are_correct(self):
        """Should have correct string values for all environments"""
        self.assertEqual(Environment.DEVELOPMENT.value, "development")
        self.assertEqual(Environment.STAGING.value, "staging")
        self.assertEqual(Environment.PRODUCTION.value, "production")

    def test_environment_from_string_development(self):
        """Should create Environment from development string"""
        env = Environment("development")
        self.assertEqual(env, Environment.DEVELOPMENT)

    def test_environment_from_string_staging(self):
        """Should create Environment from staging string"""
        env = Environment("staging")
        self.assertEqual(env, Environment.STAGING)

    def test_environment_from_string_production(self):
        """Should create Environment from production string"""
        env = Environment("production")
        self.assertEqual(env, Environment.PRODUCTION)

    def test_environment_invalid_string_raises_error(self):
        """Should raise ValueError for invalid environment string"""
        with self.assertRaises(ValueError):
            Environment("invalid")

    def test_environment_case_sensitivity(self):
        """Should be case sensitive - uppercase should fail"""
        with self.assertRaises(ValueError):
            Environment("DEVELOPMENT")

        with self.assertRaises(ValueError):
            Environment("Development")

    def test_environment_equality_comparison(self):
        """Should support equality comparison between enum instances"""
        env1 = Environment.DEVELOPMENT
        env2 = Environment("development")
        self.assertEqual(env1, env2)

    def test_environment_inequality_comparison(self):
        """Should support inequality comparison between different environments"""
        self.assertNotEqual(Environment.DEVELOPMENT, Environment.PRODUCTION)
        self.assertNotEqual(Environment.STAGING, Environment.DEVELOPMENT)

    def test_environment_string_representation(self):
        """Should have proper string representation"""
        self.assertEqual(str(Environment.DEVELOPMENT), "Environment.DEVELOPMENT")
        self.assertEqual(
            repr(Environment.STAGING), "<Environment.STAGING: 'staging'>"
        )

    def test_environment_membership_testing(self):
        """Should support membership testing"""
        environments = [Environment.DEVELOPMENT, Environment.STAGING]
        self.assertIn(Environment.DEVELOPMENT, environments)
        self.assertNotIn(Environment.PRODUCTION, environments)

    def test_all_environments_enumeration(self):
        """Should be able to enumerate all environment values"""
        all_envs = list(Environment)
        self.assertEqual(len(all_envs), 3)
        self.assertIn(Environment.DEVELOPMENT, all_envs)
        self.assertIn(Environment.STAGING, all_envs)
        self.assertIn(Environment.PRODUCTION, all_envs)


if __name__ == "__main__":
    unittest.main()
