"""
Unit tests for project subscription validation functionality
"""

import unittest
import os
import logging
from unittest.mock import Mock, patch
from astrolabe.client import AstrolabeClient, Environment


class TestProjectSubscriptionValidation(unittest.TestCase):
    """Test cases for project subscription validation"""

    def setUp(self):
        """Set up test environment"""
        if 'ASTROLABE_API_URL' in os.environ:
            del os.environ['ASTROLABE_API_URL']

    def test_initialization_with_subscribed_projects(self):
        """Should initialize client with subscribed_projects parameter"""
        client = AstrolabeClient("development", subscribed_projects=['project1', 'project2'])
        self.assertEqual(client._subscribed_projects, ['project1', 'project2'])

    def test_initialization_without_subscribed_projects(self):
        """Should initialize client without subscribed_projects for backward compatibility"""
        client = AstrolabeClient("development")
        self.assertEqual(client._subscribed_projects, [])

    def test_flag_key_format_validation(self):
        """Should validate flag key format correctly"""
        client = AstrolabeClient("development")
        
        self.assertTrue(client._validate_flag_key_format('project1/feature1'))
        self.assertTrue(client._validate_flag_key_format('my-project/my-flag'))
        self.assertTrue(client._validate_flag_key_format('project_123/flag_456'))
        
        self.assertFalse(client._validate_flag_key_format('invalid'))
        self.assertFalse(client._validate_flag_key_format('project/'))
        self.assertFalse(client._validate_flag_key_format('/flag'))
        self.assertFalse(client._validate_flag_key_format('project/sub/flag'))
        self.assertFalse(client._validate_flag_key_format(''))

    def test_project_key_extraction(self):
        """Should extract project key correctly"""
        client = AstrolabeClient("development")
        
        self.assertEqual(client._extract_project_key('project1/feature1'), 'project1')
        self.assertEqual(client._extract_project_key('my-project/my-flag'), 'my-project')
        self.assertEqual(client._extract_project_key('invalid'), '')

    def test_project_subscription_check(self):
        """Should check project subscription correctly"""
        client = AstrolabeClient("development", subscribed_projects=['project1', 'project2'])
        
        self.assertTrue(client._is_project_subscribed('project1/feature1'))
        self.assertTrue(client._is_project_subscribed('project2/feature2'))
        self.assertFalse(client._is_project_subscribed('project3/feature3'))

    def test_allow_all_projects_when_no_subscription(self):
        """Should allow all projects when no subscribed_projects specified"""
        client = AstrolabeClient("development")
        
        self.assertTrue(client._is_project_subscribed('project1/feature1'))
        self.assertTrue(client._is_project_subscribed('project2/feature2'))
        self.assertTrue(client._is_project_subscribed('any-project/any-flag'))

    def test_invalid_flag_key_format_returns_default_and_logs_warning(self):
        """Should return default value and log warning for invalid flag key format when subscribed_projects are specified"""
        mock_logger = Mock()
        client = AstrolabeClient("development", logger=mock_logger, subscribed_projects=['project1'])
        
        result = client.get_bool('invalid-format', True)
        self.assertTrue(result)
        mock_logger.warning.assert_called_with(
            "Invalid flag key format 'invalid-format'. Expected format: 'project-key/flag-key'. Using default value."
        )

    def test_unsubscribed_project_returns_default_and_logs_warning(self):
        """Should return default value and log warning for unsubscribed project"""
        mock_logger = Mock()
        client = AstrolabeClient("development", logger=mock_logger, subscribed_projects=['project1'])
        
        result = client.get_bool('project2/feature', False)
        self.assertFalse(result)
        mock_logger.warning.assert_called_with(
            "Flag 'project2/feature' belongs to unsubscribed project 'project2'. Using default value."
        )

    def test_subscribed_project_evaluates_flags_normally(self):
        """Should evaluate flags normally for subscribed projects"""
        client = AstrolabeClient("development", subscribed_projects=['project1'])
        
        mock_flag_data = {
            'project1/feature': {
                'key': 'project1/feature',
                'environments': [{
                    'environment': 'development',
                    'enabled': True,
                    'defaultValue': True,
                    'rules': []
                }]
            }
        }
        
        with patch.object(client, '_flags_cache', mock_flag_data):
            result = client.get_bool('project1/feature', False)
            self.assertTrue(result)

    def test_all_flag_methods_respect_subscription_validation(self):
        """Should work with all flag methods"""
        mock_logger = Mock()
        client = AstrolabeClient("development", logger=mock_logger, subscribed_projects=['project1'])
        
        client.get_bool('project2/flag', False)
        client.get_string('project2/flag', 'default')
        client.get_number('project2/flag', 42)
        client.get_json('project2/flag', {})
        client.get_flag('project2/flag', True)
        
        subscription_warnings = [call for call in mock_logger.warning.call_args_list 
                               if 'unsubscribed project' in str(call)]
        self.assertEqual(len(subscription_warnings), 5)

    def test_backward_compatibility_with_existing_code(self):
        """Should maintain backward compatibility with existing code"""
        client = AstrolabeClient("development")
        
        result1 = client.get_bool('project1/feature', True)
        result2 = client.get_string('project2/flag', 'default')
        result3 = client.get_number('project3/setting', 42)
        
        self.assertTrue(result1)
        self.assertEqual(result2, 'default')
        self.assertEqual(result3, 42)


if __name__ == '__main__':
    unittest.main()
