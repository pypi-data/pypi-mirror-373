"""
Integration tests for AstrolabeClient - testing end-to-end flag evaluation workflows
"""

import unittest
import os
import threading
import time
from unittest.mock import Mock, patch, MagicMock
from astrolabe.client import AstrolabeClient, Environment


class TestAstrolabeClientIntegration(unittest.TestCase):
    """Integration tests for complete flag evaluation workflows"""

    def setUp(self):
        """Set up test environment"""
        if 'ASTROLABE_API_URL' in os.environ:
            del os.environ['ASTROLABE_API_URL']

    def test_complete_client_lifecycle_without_api(self):
        """Should handle complete client lifecycle when API is unavailable"""
        # Initialize client
        client = AstrolabeClient("development")
        
        # Verify initial state
        self.assertEqual(client.env, Environment.DEVELOPMENT)
        self.assertFalse(client._use_api)
        self.assertIsNone(client._polling_thread)
        
        # Test flag operations
        bool_result = client.get_bool("test_bool", True)
        self.assertTrue(bool_result)
        
        string_result = client.get_string("test_string", "default")
        self.assertEqual(string_result, "default")
        
        number_result = client.get_number("test_number", 42)
        self.assertEqual(number_result, 42)
        
        json_result = client.get_json("test_json", {"key": "value"})
        self.assertEqual(json_result, {"key": "value"})
        
        # Test cache info
        cache_info = client.get_cache_info()
        self.assertEqual(cache_info['flag_count'], 0)
        
        # Test manual refresh
        client.refresh_flags()
        
        # Test stop polling (should be safe even when not started)
        client.stop_polling()

    @patch.dict(os.environ, {'ASTROLABE_API_URL': 'https://api.example.com'})
    @patch('requests.get')
    def test_complete_client_lifecycle_with_api(self, mock_get):
        """Should handle complete client lifecycle when API is available"""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "flags": {
                "test_flag": {
                    "id": "1",
                    "key": "test_flag",
                    "environments": [
                        {
                            "environment": "development",
                            "enabled": True,
                            "defaultValue": True,
                            "rules": [],
                        }
                    ]
                }
            }
        }
        mock_get.return_value = mock_response
        
        # Initialize client with mocked API
        with patch.object(AstrolabeClient, '_start_polling'):
            client = AstrolabeClient("development")
            
            # Verify API is enabled
            self.assertTrue(client._use_api)
            self.assertEqual(client._api_url, 'https://api.example.com')
            
            # Test flag operations
            result = client.get_bool("test_flag", False)
            self.assertIsInstance(result, bool)
            
            # Test cleanup
            client.stop_polling()

    def test_multi_environment_flag_evaluation(self):
        """Should correctly evaluate flags across different environments"""
        environments = ["development", "staging", "production"]
        
        for env_name in environments:
            client = AstrolabeClient(env_name)
            
            # Each environment should work independently
            result = client.get_bool("env_specific_flag", True)
            self.assertTrue(result)
            
            # Verify environment is set correctly
            self.assertEqual(client.env.value, env_name)

    def test_concurrent_client_operations(self):
        """Should handle concurrent operations across multiple clients safely"""
        clients = []
        results = []
        
        def client_worker(client_id):
            client = AstrolabeClient("development")
            clients.append(client)
            
            # Perform multiple operations
            bool_result = client.get_bool(f"flag_{client_id}", True)
            string_result = client.get_string(f"string_{client_id}", f"value_{client_id}")
            cache_info = client.get_cache_info()
            
            results.append({
                'client_id': client_id,
                'bool_result': bool_result,
                'string_result': string_result,
                'cache_info': cache_info
            })
        
        # Create multiple threads with different clients
        threads = []
        for i in range(5):
            thread = threading.Thread(target=client_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        self.assertEqual(len(results), 5)
        self.assertEqual(len(clients), 5)
        
        for i, result in enumerate(results):
            self.assertTrue(result['bool_result'])
            self.assertEqual(result['string_result'], f"value_{result['client_id']}")
            self.assertIsInstance(result['cache_info'], dict)

    def test_flag_evaluation_with_complex_attribute_scenarios(self):
        """Should handle complex real-world attribute scenarios"""
        client = AstrolabeClient("production")
        
        # Simulate real user attributes
        user_scenarios = [
            {
                "user_id": "user_123",
                "country": "Jordan",
                "plan": "premium",
                "signup_date": "2023-01-15",
                "usage_score": 85,
                "features_enabled": ["feature_a", "feature_b"],
                "metadata": {
                    "source": "mobile_app",
                    "version": "2.1.0"
                }
            },
            {
                "user_id": "user_456", 
                "country": "USA",
                "plan": "basic",
                "signup_date": "2023-06-20",
                "usage_score": 45,
                "features_enabled": ["feature_a"],
                "metadata": {
                    "source": "web",
                    "version": "1.8.5"
                }
            },
            {
                "user_id": "user_789",
                "country": "Germany",
                "plan": "enterprise",
                "signup_date": "2022-11-10",
                "usage_score": 95,
                "features_enabled": ["feature_a", "feature_b", "feature_c"],
                "metadata": {
                    "source": "api",
                    "version": "3.0.0"
                }
            }
        ]
        
        # Test different flag types with each scenario
        for scenario in user_scenarios:
            # Boolean flags
            premium_access = client.get_bool("premium_access", False, scenario)
            self.assertIsInstance(premium_access, bool)
            
            # String flags
            theme = client.get_string("ui_theme", "light", scenario)
            self.assertIsInstance(theme, str)
            
            # Number flags
            rate_limit = client.get_number("api_rate_limit", 100, scenario)
            self.assertIsInstance(rate_limit, (int, float))
            
            # JSON flags
            config = client.get_json("user_config", {"default": True}, scenario)
            self.assertIsInstance(config, dict)

    def test_error_recovery_and_resilience(self):
        """Should recover gracefully from various error conditions"""
        client = AstrolabeClient("development")
        
        # Test with various problematic inputs
        problematic_scenarios = [
            # Empty attributes
            {},
            # None attributes
            None,
            # Attributes with None values
            {"user_id": None, "country": None},
            # Very large attributes dictionary
            {f"attr_{i}": f"value_{i}" for i in range(1000)},
            # Attributes with special characters
            {"user🚀": "test", "cöuntry": "spëcial"},
        ]
        
        for attributes in problematic_scenarios:
            try:
                # Should not crash with any of these scenarios
                bool_result = client.get_bool("resilience_test", True, attributes)
                self.assertIsInstance(bool_result, bool)
                
                string_result = client.get_string("resilience_test", "safe", attributes)
                self.assertIsInstance(string_result, str)
                
                number_result = client.get_number("resilience_test", 0, attributes)
                self.assertIsInstance(number_result, (int, float))
                
                json_result = client.get_json("resilience_test", {}, attributes)
                self.assertIsInstance(json_result, dict)
                
            except Exception as e:
                self.fail(f"Client should handle problematic attributes gracefully, but got: {e}")

    def test_memory_and_performance_characteristics(self):
        """Should maintain reasonable memory usage and performance"""
        client = AstrolabeClient("development")
        
        # Test with many flag evaluations
        start_time = time.time()
        
        for i in range(1000):
            flag_key = f"perf_test_flag_{i % 10}"  # Reuse some keys
            attributes = {"iteration": i, "batch": i // 100}
            
            # Mix of different flag types
            if i % 4 == 0:
                result = client.get_bool(flag_key, True, attributes)
            elif i % 4 == 1:
                result = client.get_string(flag_key, "default", attributes)
            elif i % 4 == 2:
                result = client.get_number(flag_key, 42, attributes)
            else:
                result = client.get_json(flag_key, {"default": True}, attributes)
            
            # Verify result is of expected type
            self.assertIsNotNone(result)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete 1000 evaluations reasonably quickly (under 5 seconds)
        self.assertLess(execution_time, 5.0, 
                       f"1000 flag evaluations took {execution_time:.2f}s, which seems too slow")
        
        # Cache should remain manageable
        cache_info = client.get_cache_info()
        self.assertIsInstance(cache_info, dict)


if __name__ == '__main__':
    unittest.main()
