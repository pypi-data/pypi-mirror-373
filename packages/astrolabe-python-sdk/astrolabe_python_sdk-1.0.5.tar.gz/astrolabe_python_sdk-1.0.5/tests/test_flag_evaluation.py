from astrolabe.rule_engine import RuleEngine

def test_attribute_key_conditions_supported():
    engine = RuleEngine()
    flag = {
        "key": "test-flag",
        "environments": [
            {
                "environment": "development",
                "enabled": True,
                "defaultValue": False,
                "rules": [
                    {
                        "id": "1",
                        "name": "Premium users in Jordan",
                        "conditions": [
                            {"attribute_key": "country", "operator": "equals", "value": "Jordan"},
                            {"attribute_key": "plan", "operator": "equals", "value": "premium"},
                        ],
                        "logicalOperator": "AND",
                        "returnValue": True,
                        "enabled": True,
                    }
                ],
            }
        ],
    }
    attrs = {"country": "Jordan", "plan": "premium"}
    res = engine.evaluate_flag(flag, "development", attrs, False)
    assert res is True


def test_mixed_attribute_key_and_attributeId():
    engine = RuleEngine()
    flag = {
        "key": "mixed-flag",
        "environments": [
            {
                "environment": "development",
                "enabled": True,
                "defaultValue": False,
                "rules": [
                    {
                        "id": "1",
                        "conditions": [
                            {"attribute_key": "country", "operator": "equals", "value": "Jordan"},
                            {"attributeId": "plan", "operator": "equals", "value": "premium"},
                        ],
                        "logicalOperator": "AND",
                        "returnValue": True,
                        "enabled": True,
                    }
                ],
            }
        ],
    }
    attrs = {"country": "Jordan", "plan": "premium"}
    res = engine.evaluate_flag(flag, "development", attrs, False)
    assert res is True

"""
Unit tests for flag evaluation scenarios - covering complex flag cases and rule evaluation
"""

import unittest
import os
from unittest.mock import Mock, patch
from astrolabe.client import AstrolabeClient, Environment


class TestFlagEvaluationScenarios(unittest.TestCase):
    """Test cases for complex flag evaluation scenarios"""

    def setUp(self):
        """Set up test client and mock flag data"""
        if 'ASTROLABE_API_URL' in os.environ:
            del os.environ['ASTROLABE_API_URL']
        self.client = AstrolabeClient("development")
        
        # Mock complex flag configuration
        self.mock_flag_data = {
            "premium_feature": {
                "id": "1",
                "key": "premium_feature",
                "name": "Premium Feature Access",
                "dataType": "boolean",
                "environments": [
                    {
                        "environment": "development",
                        "enabled": True,
                        "defaultValue": False,
                        "rules": [
                            {
                                "id": "1",
                                "name": "Premium users in Jordan",
                                "conditions": [
                                    {"attributeId": "country", "operator": "equals", "value": "Jordan"},
                                    {"attributeId": "plan", "operator": "equals", "value": "premium"}
                                ],
                                "logicalOperator": "AND",
                                "returnValue": True,
                                "enabled": True
                            }
                        ],
                    }
                ]
            },
            "feature_rollout": {
                "id": "2", 
                "key": "feature_rollout",
                "name": "Feature Rollout",
                "dataType": "boolean",
                "environments": [
                    {
                        "environment": "development",
                        "enabled": True,
                        "defaultValue": False,
                        "rules": [],
                    }
                ]
            }
        }

    def test_flag_evaluation_with_matching_rule_conditions(self):
        """Should return rule value when all conditions match"""
        with patch.object(self.client, '_flags_cache', self.mock_flag_data):
            attributes = {"country": "Jordan", "plan": "premium"}
            result = self.client.get_bool("premium_feature", False, attributes)
            # Expect the rule's returnValue = True
            self.assertTrue(result)

    def test_flag_evaluation_with_non_matching_rule_conditions(self):
        """Should fall back to default when rule conditions don't match"""
        with patch.object(self.client, '_flags_cache', self.mock_flag_data):
            attributes = {"country": "USA", "plan": "premium"}  # country mismatch
            result = self.client.get_bool("premium_feature", False, attributes)
            # Expect environment defaultValue = False
            self.assertFalse(result)

    def test_flag_evaluation_with_partial_matching_conditions(self):
        """Should not match when only some conditions are met (AND logic)"""
        with patch.object(self.client, '_flags_cache', self.mock_flag_data):
            attributes = {"country": "Jordan", "plan": "basic"}  # plan mismatch
            result = self.client.get_bool("premium_feature", False, attributes)
            # Expect environment defaultValue = False
            self.assertFalse(result)

    def test_flag_evaluation_with_missing_attributes(self):
        """Should handle missing attributes gracefully"""
        with patch.object(self.client, '_flags_cache', self.mock_flag_data):
            attributes = {"country": "Jordan"}  # missing 'plan'
            result = self.client.get_bool("premium_feature", False, attributes)
            # Expect environment defaultValue = False
            self.assertFalse(result)


    def test_flag_evaluation_with_disabled_environment(self):
        """Should return caller-provided fallback when environment is disabled"""
        disabled_flag_data = {
            "disabled_feature": {
                "id": "3",
                "key": "disabled_feature", 
                "environments": [
                    {
                        "environment": "development",
                        "enabled": False,  # Disabled
                        "defaultValue": True,
                        "rules": [],
                    }
                ]
            }
        }
        
        with patch.object(self.client, '_flags_cache', disabled_flag_data):
            result = self.client.get_bool("disabled_feature", False)
            # When the environment is disabled, expect the method to return the provided default (fallback arg)
            self.assertEqual(result, False)

    def test_flag_evaluation_with_wrong_environment(self):
        """Should return caller-provided fallback when flag is not configured for client's environment"""
        prod_only_flag = {
            "prod_feature": {
                "id": "4",
                "key": "prod_feature",
                "environments": [
                    {
                        "environment": "production",  # Different environment
                        "enabled": True,
                        "defaultValue": True,
                        "rules": [],
                    }
                ]
            }
        }
        
        with patch.object(self.client, '_flags_cache', prod_only_flag):
            # Client is in development, flag only exists for production
            result = self.client.get_bool("prod_feature", False)
            self.assertEqual(result, False)

    def test_string_flag_evaluation_with_rules(self):
        """Should evaluate string flags with rule-based values"""
        string_flag_data = {
            "theme_config": {
                "id": "5",
                "key": "theme_config",
                "dataType": "string",
                "environments": [
                    {
                        "environment": "development",
                        "enabled": True,
                        "defaultValue": "light",
                        "rules": [
                            {
                                "id": "1",
                                "conditions": [
                                    {"attributeId": "user_type", "operator": "equals", "value": "premium"}
                                ],
                                "returnValue": "dark",
                                "enabled": True
                            }
                        ],
                    }
                ]
            }
        }
        
        with patch.object(self.client, '_flags_cache', string_flag_data):
            # premium user should get rule value "dark"
            result = self.client.get_string("theme_config", "default", {"user_type": "premium"})
            self.assertEqual(result, "dark")
            
            # regular user should get flag environment default "light"
            result = self.client.get_string("theme_config", "default", {"user_type": "basic"})
            self.assertEqual(result, "light")

    def test_number_flag_evaluation_with_complex_rules(self):
        """Should evaluate number flags with complex rule conditions"""
        number_flag_data = {
            "rate_limit": {
                "id": "6",
                "key": "rate_limit",
                "dataType": "number",
                "environments": [
                    {
                        "environment": "development",
                        "enabled": True,
                        "defaultValue": 100,
                        "rules": [
                            {
                                "id": "1",
                                "conditions": [
                                    {"attributeId": "usage_score", "operator": "greater_than", "value": "80"}
                                ],
                                "returnValue": 1000,
                                "enabled": True
                            }
                        ],
                    }
                ]
            }
        }
        
        with patch.object(self.client, '_flags_cache', number_flag_data):
            # Test high usage user -> rule value
            result = self.client.get_number("rate_limit", 50, {"usage_score": 90})
            self.assertEqual(result, 1000)
            # Test low usage user -> env default
            result = self.client.get_number("rate_limit", 50, {"usage_score": 30})
            self.assertEqual(result, 100)

    def test_json_flag_evaluation_with_nested_configuration(self):
        """Should evaluate JSON flags with complex nested configurations"""
        json_flag_data = {
            "ui_config": {
                "id": "7",
                "key": "ui_config",
                "dataType": "json",
                "environments": [
                    {
                        "environment": "development",
                        "enabled": True,
                        "defaultValue": {"theme": "light", "sidebar": "collapsed"},
                        "rules": [
                            {
                                "id": "1",
                                "conditions": [
                                    {"attributeId": "role", "operator": "equals", "value": "admin"}
                                ],
                                "returnValue": {
                                    "theme": "dark",
                                    "sidebar": "expanded",
                                    "admin_panel": True
                                },
                                "enabled": True
                            }
                        ],
                    }
                ]
            }
        }
        
        with patch.object(self.client, '_flags_cache', json_flag_data):
            default_config = {"theme": "default"}
            
            # admin -> rule value
            result = self.client.get_json("ui_config", default_config, {"role": "admin"})
            self.assertEqual(
                result,
                {"theme": "dark", "sidebar": "expanded", "admin_panel": True}
            )
            
            # regular user -> environment default
            result = self.client.get_json("ui_config", default_config, {"role": "user"})
            self.assertEqual(result, {"theme": "light", "sidebar": "collapsed"})


class TestFlagEvaluationEdgeCases(unittest.TestCase):
    """Test cases for edge cases in flag evaluation"""

    def setUp(self):
        """Set up test client"""
        if 'ASTROLABE_API_URL' in os.environ:
            del os.environ['ASTROLABE_API_URL']
        self.client = AstrolabeClient("development")

    def test_flag_evaluation_with_malformed_flag_data(self):
        """Should handle malformed flag data gracefully"""
        malformed_data = {
            "broken_flag": {
                "id": "1",
                # Missing required fields
                "environments": "not_a_list"  # Wrong type
            }
        }
        
        with patch.object(self.client, '_flags_cache', malformed_data):
            result = self.client.get_bool("broken_flag", True)
            # Should return default value when flag data is malformed
            self.assertTrue(result)

    def test_flag_evaluation_with_empty_rules(self):
        """Should handle flags with empty rules"""
        empty_config_data = {
            "empty_config": {
                "id": "1",
                "key": "empty_config",
                "environments": [
                    {
                        "environment": "development",
                        "enabled": True,
                        "defaultValue": "fallback",
                        "rules": [],
                    }
                ]
            }
        }
        
        with patch.object(self.client, '_flags_cache', empty_config_data):
            result = self.client.get_string("empty_config", "default")
            # With no rules/splits, expect environment defaultValue
            self.assertEqual(result, "fallback")

    def test_flag_evaluation_null_is_not_supported(self):
        """Should handle null/None values in rule conditions"""
        null_condition_data = {
            "null_test": {
                "id": "1",
                "key": "null_test",
                "environments": [
                    {
                        "environment": "development",
                        "enabled": True,
                        "defaultValue": False,
                        "rules": [
                            {
                                "id": "1",
                                "conditions": [
                                    {"attributeId": "nullable_field", "operator": "equals", "value": None}
                                ],
                                "returnValue": True,
                                "enabled": True
                            }
                        ],
                    }
                ]
            }
        }
        
        with patch.object(self.client, '_flags_cache', null_condition_data):
            # Attribute explicitly None -> matches rule -> True
            result = self.client.get_bool("null_test", False, {"nullable_field": None})
            self.assertFalse(result)
            
            # Missing attribute -> should not match rule -> environment default False
            result = self.client.get_bool("null_test", True, {})
            self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
