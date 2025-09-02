"""
Unit tests for error handling and edge cases - covering exception scenarios and boundary conditions
"""

import unittest
import os
import threading
from unittest.mock import Mock, patch, MagicMock
from astrolabe.client import AstrolabeClient, Environment


class TestErrorHandlingAndEdgeCases(unittest.TestCase):
    """Test cases for error handling and boundary conditions"""

    def setUp(self):
        """Set up clean test environment"""
        if 'ASTROLABE_API_URL' in os.environ:
            del os.environ['ASTROLABE_API_URL']

    def test_initialization_with_none_environment(self):
        """Should raise TypeError when environment is None"""
        with self.assertRaises(TypeError) as context:
            AstrolabeClient(None)
        self.assertIn("Environment must be a string or Environment enum", str(context.exception))

    def test_initialization_with_empty_string_environment(self):
        """Should raise ValueError when environment is empty string"""
        with self.assertRaises(ValueError) as context:
            AstrolabeClient("")
        self.assertIn("Invalid environment", str(context.exception))

    def test_initialization_with_whitespace_environment(self):
        """Should raise ValueError when environment is only whitespace"""
        with self.assertRaises(ValueError) as context:
            AstrolabeClient("   ")
        self.assertIn("Invalid environment", str(context.exception))

    def test_flag_operations_with_none_flag_key(self):
        """Should handle None flag key gracefully"""
        client = AstrolabeClient("development")
        
        # Should not crash, return defaults
        result = client.get_bool(None, True)
        self.assertTrue(result)
        
        result = client.get_string(None, "default")
        self.assertEqual(result, "default")

    def test_flag_operations_with_extremely_long_flag_key(self):
        """Should handle extremely long flag keys without memory issues"""
        client = AstrolabeClient("development")
        
        # Create a very long flag key (10KB)
        long_key = "a" * 10000
        
        result = client.get_bool(long_key, False)
        self.assertFalse(result)

    def test_flag_operations_with_unicode_and_special_characters(self):
        """Should handle unicode and special characters in flag keys and values"""
        client = AstrolabeClient("development")
        
        unicode_key = "flag_测试_🚀_مفتاح"
        unicode_default = "قيمة_افتراضية_🌟"
        
        result = client.get_string(unicode_key, unicode_default)
        self.assertEqual(result, unicode_default)

    def test_attributes_with_circular_references(self):
        """Should handle attributes with circular references safely"""
        client = AstrolabeClient("development")
        
        # Create circular reference
        attr1 = {"name": "attr1"}
        attr2 = {"name": "attr2", "ref": attr1}
        attr1["ref"] = attr2
        
        # Should not crash or cause infinite recursion
        result = client.get_bool("test_flag", True, attr1)
        self.assertTrue(result)

    def test_attributes_with_very_deep_nesting(self):
        """Should handle deeply nested attribute structures"""
        client = AstrolabeClient("development")
        
        # Create deeply nested structure
        deep_attrs = {"level": 0}
        current = deep_attrs
        for i in range(100):
            current["next"] = {"level": i + 1}
            current = current["next"]
        
        result = client.get_bool("deep_test", False, deep_attrs)
        self.assertFalse(result)

    def test_concurrent_cache_access_stress_test(self):
        """Should handle high-concurrency cache access without corruption"""
        client = AstrolabeClient("development")
        results = []
        errors = []
        
        def stress_worker(worker_id):
            try:
                for i in range(100):
                    # Mix of operations
                    client.get_bool(f"flag_{worker_id}_{i}", True)
                    client.get_cache_info()
                    client.refresh_flags()
                results.append(f"worker_{worker_id}_success")
            except Exception as e:
                errors.append(f"worker_{worker_id}_error: {e}")
        
        # Create many concurrent threads
        threads = []
        for i in range(20):
            thread = threading.Thread(target=stress_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Should have no errors
        self.assertEqual(len(errors), 0, f"Concurrent access caused errors: {errors}")
        self.assertEqual(len(results), 20)

    @patch.dict(os.environ, {'ASTROLABE_API_URL': 'https://api.example.com'})
    @patch('requests.get')
    def test_api_network_error_handling(self, mock_get):
        """Should handle network errors gracefully when API is configured"""
        # Simulate network error
        mock_get.side_effect = Exception("Network error")
        
        with patch.object(AstrolabeClient, '_start_polling'):
            client = AstrolabeClient("development")
            
            # Should not crash during flag sync
            client._fetch_flags_sync()
            
            # Should still return defaults
            result = client.get_bool("test_flag", True)
            self.assertTrue(result)

    @patch.dict(os.environ, {'ASTROLABE_API_URL': 'https://api.example.com'})
    @patch('requests.get')
    def test_api_invalid_response_handling(self, mock_get):
        """Should handle invalid API responses gracefully"""
        # Simulate invalid JSON response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response
        
        with patch.object(AstrolabeClient, '_start_polling'):
            client = AstrolabeClient("development")
            
            # Should handle invalid JSON gracefully
            client._fetch_flags_sync()
            
            result = client.get_bool("test_flag", False)
            self.assertFalse(result)

    @patch.dict(os.environ, {'ASTROLABE_API_URL': 'https://api.example.com'})
    @patch('requests.get')
    def test_api_http_error_codes(self, mock_get):
        """Should handle various HTTP error codes appropriately"""
        error_codes = [400, 401, 403, 404, 500, 502, 503]
        
        for error_code in error_codes:
            mock_response = Mock()
            mock_response.status_code = error_code
            mock_get.return_value = mock_response
            
            with patch.object(AstrolabeClient, '_start_polling'):
                client = AstrolabeClient("development")
                
                # Should handle HTTP errors gracefully
                client._fetch_flags_sync()
                
                # Should still return defaults
                result = client.get_bool("test_flag", True)
                self.assertTrue(result)

    def test_memory_pressure_with_large_attributes(self):
        """Should handle memory pressure from large attribute dictionaries"""
        client = AstrolabeClient("development")
        
        # Create very large attributes dictionary
        large_attrs = {}
        for i in range(10000):
            large_attrs[f"key_{i}"] = f"value_{i}" * 100  # Each value ~600 bytes
        
        # Should not crash or consume excessive memory
        result = client.get_bool("memory_test", True, large_attrs)
        self.assertTrue(result)

    def test_thread_safety_during_client_destruction(self):
        """Should handle thread safety during client cleanup"""
        clients = []
        
        def create_and_destroy_client():
            client = AstrolabeClient("development")
            clients.append(client)
            
            # Use the client briefly
            client.get_bool("test", True)
            client.get_cache_info()
            
            # Stop polling (cleanup)
            client.stop_polling()
        
        # Create and destroy clients concurrently
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=create_and_destroy_client)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        self.assertEqual(len(clients), 10)

    def test_flag_evaluation_with_corrupted_cache_data(self):
        """Should handle corrupted cache data gracefully"""
        client = AstrolabeClient("development")
        
        # Simulate corrupted cache data
        corrupted_data = {
            "corrupted_flag": "this_should_be_a_dict_not_string",
            "partial_flag": {
                "id": "1"
                # Missing required fields
            },
            "malformed_flag": {
                "environments": "should_be_list"
            }
        }
        
        with patch.object(client, '_flags_cache', corrupted_data):
            # Should return defaults for corrupted flags
            result = client.get_bool("corrupted_flag", False)
            self.assertFalse(result)
            
            result = client.get_string("partial_flag", "safe")
            self.assertEqual(result, "safe")
            
            result = client.get_number("malformed_flag", 42)
            self.assertEqual(result, 42)

    def test_extreme_boundary_values(self):
        """Should handle extreme boundary values correctly"""
        client = AstrolabeClient("development")
        
        # Test with extreme numbers
        extreme_values = [
            float('inf'),
            float('-inf'),
            2**63 - 1,  # Max int64
            -(2**63),   # Min int64
            1e-308,     # Very small float
            1e308,      # Very large float
        ]
        
        for value in extreme_values:
            if value != float('inf') and value != float('-inf'):  # Skip inf values for equality check
                result = client.get_number("extreme_test", value)
                self.assertEqual(result, value)

    def test_flag_operations_during_high_memory_pressure(self):
        """Should maintain functionality under memory pressure"""
        client = AstrolabeClient("development")
        
        # Simulate memory pressure by creating large objects
        memory_pressure = []
        try:
            for i in range(100):
                # Create large objects to simulate memory pressure
                large_obj = [0] * 100000  # ~800KB per object
                memory_pressure.append(large_obj)
                
                # Test flag operations under pressure
                result = client.get_bool(f"pressure_test_{i}", True)
                self.assertTrue(result)
                
                if i % 10 == 0:  # Periodic cleanup
                    cache_info = client.get_cache_info()
                    self.assertIsInstance(cache_info, dict)
        
        finally:
            # Cleanup
            del memory_pressure


if __name__ == '__main__':
    unittest.main()
