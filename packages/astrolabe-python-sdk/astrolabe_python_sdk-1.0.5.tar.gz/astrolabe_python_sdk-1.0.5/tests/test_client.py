"""
Unit tests for AstrolabeClient - covering flag evaluation cases and edge scenarios
"""

import unittest
import os
import threading
import time
from unittest.mock import Mock, patch, MagicMock
from astrolabe.client import AstrolabeClient, Environment
from astrolabe.settings import AstrolabeSettings


class TestAstrolabeClientInitialization(unittest.TestCase):
    """Test cases for AstrolabeClient initialization with various configurations"""

    def setUp(self):
        """Clean environment before each test"""
        if "ASTROLABE_API_URL" in os.environ:
            del os.environ["ASTROLABE_API_URL"]

    def test_initialization_with_string_environment_development(self):
        """Should initialize client with development environment as string"""
        client = AstrolabeClient("development")
        self.assertEqual(client.env, Environment.DEVELOPMENT)

    def test_initialization_with_string_environment_production(self):
        """Should initialize client with production environment as string"""
        client = AstrolabeClient("production")
        self.assertEqual(client.env, Environment.PRODUCTION)

    def test_initialization_with_enum_environment(self):
        """Should initialize client with Environment enum value"""
        client = AstrolabeClient(Environment.STAGING)
        self.assertEqual(client.env, Environment.STAGING)

    def test_initialization_with_invalid_string_environment(self):
        """Should raise ValueError for invalid environment string"""
        with self.assertRaises(ValueError) as context:
            AstrolabeClient("invalid_env")
        self.assertIn("Invalid environment", str(context.exception))

    def test_initialization_with_invalid_environment_type(self):
        """Should raise TypeError for invalid environment type"""
        with self.assertRaises(TypeError) as context:
            AstrolabeClient(123)
        self.assertIn(
            "Environment must be a string or Environment enum", str(context.exception)
        )

    def test_initialization_with_case_insensitive_environment(self):
        """Should handle case-insensitive environment strings"""
        client = AstrolabeClient("DEVELOPMENT")
        self.assertEqual(client.env, Environment.DEVELOPMENT)

        client2 = AstrolabeClient("Production")
        self.assertEqual(client2.env, Environment.PRODUCTION)

    def test_initialization_with_dict_settings(self):
        """Should initialize with dictionary settings"""
        settings_dict = {"poll_interval": 120, "timeout": 10}
        client = AstrolabeClient("development", settings=settings_dict)
        self.assertIsInstance(client.settings, AstrolabeSettings)

    def test_initialization_with_astrolabe_settings_object(self):
        """Should initialize with AstrolabeSettings object"""
        settings = AstrolabeSettings(poll_interval=180)
        client = AstrolabeClient("development", settings=settings)
        self.assertEqual(client.settings.poll_interval, 180)

    def test_initialization_with_invalid_settings_type(self):
        """Should raise TypeError for invalid settings type"""
        with self.assertRaises(TypeError) as context:
            AstrolabeClient("development", settings="invalid")
        self.assertIn(
            "Settings must be AstrolabeSettings object or dictionary",
            str(context.exception),
        )

    def test_initialization_without_api_url(self):
        """Should initialize without API URL and disable API usage"""
        client = AstrolabeClient("development")
        self.assertFalse(client._use_api)

    @patch.dict(os.environ, {"ASTROLABE_API_URL": "https://api.example.com"})
    def test_initialization_with_api_url(self):
        """Should initialize with API URL and enable API usage"""
        with patch.object(AstrolabeClient, "_fetch_flags_sync"), patch.object(
            AstrolabeClient, "_start_polling"
        ):
            client = AstrolabeClient("development")
            self.assertTrue(client._use_api)
            self.assertEqual(client._api_url, "https://api.example.com")


class TestAstrolabeClientFlagEvaluation(unittest.TestCase):
    """Test cases for flag evaluation with various scenarios"""

    def setUp(self):
        """Set up test client without API"""
        if "ASTROLABE_API_URL" in os.environ:
            del os.environ["ASTROLABE_API_URL"]
        self.client = AstrolabeClient("development")

    def test_get_bool_flag_with_default_when_flag_not_exists(self):
        """Should return default boolean value when flag doesn't exist"""
        result = self.client.get_bool("non_existent_flag", True)
        self.assertTrue(result)

        result = self.client.get_bool("non_existent_flag", False)
        self.assertFalse(result)

    def test_get_string_flag_with_default_when_flag_not_exists(self):
        """Should return default string value when flag doesn't exist"""
        result = self.client.get_string("non_existent_flag", "default_value")
        self.assertEqual(result, "default_value")

    def test_get_number_flag_with_default_when_flag_not_exists(self):
        """Should return default number value when flag doesn't exist"""
        result = self.client.get_number("non_existent_flag", 42)
        self.assertEqual(result, 42)

        result = self.client.get_number("non_existent_flag", 3.14)
        self.assertEqual(result, 3.14)

    def test_get_json_flag_with_default_when_flag_not_exists(self):
        """Should return default JSON value when flag doesn't exist"""
        default_json = {"key": "value", "count": 10}
        result = self.client.get_json("non_existent_flag", default_json)
        self.assertEqual(result, default_json)

    def test_get_flag_routes_to_correct_type_methods(self):
        """Should route get_flag calls to appropriate type-specific methods"""
        # Test boolean routing
        result = self.client.get_flag("test_flag", True)
        self.assertIsInstance(result, bool)

        # Test string routing
        result = self.client.get_flag("test_flag", "test")
        self.assertIsInstance(result, str)

        # Test number routing (int)
        result = self.client.get_flag("test_flag", 42)
        self.assertIsInstance(result, (int, float))

        # Test number routing (float)
        result = self.client.get_flag("test_flag", 3.14)
        self.assertIsInstance(result, (int, float))

        # Test JSON routing
        result = self.client.get_flag("test_flag", {"key": "value"})
        self.assertIsInstance(result, dict)

    def test_flag_evaluation_with_user_attributes(self):
        """Should handle flag evaluation with user attributes"""
        attributes = {"user_id": "user123", "country": "Jordan", "plan": "premium"}

        # Should not crash and return defaults when no flags exist
        result = self.client.get_bool("premium_feature", False, attributes)
        self.assertFalse(result)

    def test_flag_evaluation_with_empty_attributes(self):
        """Should handle flag evaluation with empty attributes dictionary"""
        result = self.client.get_bool("test_flag", True, {})
        self.assertTrue(result)

    def test_flag_evaluation_with_none_attributes(self):
        """Should handle flag evaluation with None attributes"""
        result = self.client.get_bool("test_flag", False, None)
        self.assertFalse(result)

    def test_concurrent_flag_access(self):
        import queue
        from concurrent.futures import ThreadPoolExecutor, wait

        """Should handle concurrent flag access safely under contention."""
        n_threads = 20
        rounds = 3  # run a few waves to increase chances of catching races

        errors = queue.Queue()
        results = queue.Queue()

        def worker(barrier):
            try:
                barrier.wait()  # coordinate a simultaneous start
                val = self.client.get_bool("concurrent_flag", True)
                results.put(val)
            except Exception as e:
                errors.put(e)

        for _ in range(rounds):
            barrier = threading.Barrier(n_threads)
            with ThreadPoolExecutor(max_workers=n_threads) as pool:
                futures = [pool.submit(worker, barrier) for _ in range(n_threads)]
                done, not_done = wait(futures, timeout=5)
                # Fail fast on hangs
                self.assertFalse(
                    not_done, "Threads hung or timed out during get_bool() calls"
                )

            # Drain result/error queues for this round
            round_results = [results.get_nowait() for _ in range(n_threads)]
            self.assertTrue(
                errors.empty(),
                f"Exceptions from threads: {[errors.get_nowait() for _ in range(errors.qsize())]}",
            )
            self.assertEqual(len(round_results), n_threads)
            self.assertTrue(
                all(round_results), "Expected all True (default) values from get_bool()"
            )


class TestAstrolabeClientFlagCache(unittest.TestCase):
    """Test cases for flag caching functionality"""

    def setUp(self):
        """Set up test client without API"""
        if "ASTROLABE_API_URL" in os.environ:
            del os.environ["ASTROLABE_API_URL"]
        self.client = AstrolabeClient("development")

    def test_cache_info_returns_valid_structure(self):
        """Should return cache information with expected structure"""
        cache_info = self.client.get_cache_info()

        self.assertIsInstance(cache_info, dict)
        self.assertIn("flag_count", cache_info)
        self.assertIn("last_updated", cache_info)

        # Initially should have 0 flags
        self.assertEqual(cache_info["flag_count"], 0)

    def test_cache_thread_safety(self):
        """Should handle cache access from multiple threads safely"""

        def cache_worker():
            cache_info = self.client.get_cache_info()
            self.assertIsInstance(cache_info, dict)

        threads = []
        for _ in range(5):
            thread = threading.Thread(target=cache_worker)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    def test_manual_flag_refresh_without_api(self):
        """Should handle manual flag refresh when API is not available"""
        # Should not crash when API is not available
        self.client.refresh_flags()

        # Cache should still be empty
        cache_info = self.client.get_cache_info()
        self.assertEqual(cache_info["flag_count"], 0)


class TestAstrolabeClientPolling(unittest.TestCase):
    """Test cases for background polling functionality"""

    def setUp(self):
        """Set up test client without API"""
        if "ASTROLABE_API_URL" in os.environ:
            del os.environ["ASTROLABE_API_URL"]

    def test_polling_not_started_without_api(self):
        """Should not start polling when API URL is not available"""
        client = AstrolabeClient("development")
        self.assertIsNone(client._polling_thread)
        self.assertFalse(client._use_api)

    def test_stop_polling_when_not_started(self):
        """Should handle stop_polling gracefully when polling wasn't started"""
        client = AstrolabeClient("development")
        # Should not crash
        client.stop_polling()

    @patch.dict(os.environ, {"ASTROLABE_API_URL": "https://api.example.com"})
    def test_polling_started_with_api(self):
        """Should start polling when API URL is available"""
        with patch.object(AstrolabeClient, "_fetch_flags_sync"), patch.object(
            AstrolabeClient, "_start_polling"
        ) as mock_start:
            client = AstrolabeClient("development")
            mock_start.assert_called_once()

    @patch.dict(os.environ, {"ASTROLABE_API_URL": "https://api.example.com"})
    def test_stop_polling_cleanup(self):
        """Should properly clean up polling thread when stopped"""
        with patch.object(AstrolabeClient, "_fetch_flags_sync"), patch.object(
            AstrolabeClient, "_start_polling"
        ):
            client = AstrolabeClient("development")

            # Mock a running thread
            mock_thread = Mock()
            mock_thread.is_alive.return_value = True
            client._polling_thread = mock_thread

            client.stop_polling()

            # Should set stop event
            self.assertTrue(client._stop_polling.is_set())


class TestAstrolabeClientEdgeCases(unittest.TestCase):
    """Test cases for edge cases and error scenarios"""

    def setUp(self):
        """Set up test client without API"""
        if "ASTROLABE_API_URL" in os.environ:
            del os.environ["ASTROLABE_API_URL"]
        self.client = AstrolabeClient("development")

    def test_flag_key_with_special_characters(self):
        """Should handle flag keys with special characters"""
        special_keys = [
            "flag-with-dashes",
            "flag_with_underscores",
            "flag.with.dots",
            "flag123with456numbers",
            "UPPERCASE_FLAG",
        ]

        for key in special_keys:
            result = self.client.get_bool(key, True)
            self.assertTrue(result)

    def test_flag_key_empty_string(self):
        """Should handle empty string flag key"""
        result = self.client.get_bool("", False)
        self.assertFalse(result)

    def test_very_long_flag_key(self):
        """Should handle very long flag keys"""
        long_key = "a" * 1000
        result = self.client.get_bool(long_key, True)
        self.assertTrue(result)

    def test_unicode_flag_key(self):
        """Should handle unicode characters in flag keys"""
        unicode_key = "flag_测试_🚀"
        result = self.client.get_string(unicode_key, "default")
        self.assertEqual(result, "default")

    def test_complex_json_default_value(self):
        """Should handle complex nested JSON as default value"""
        complex_json = {
            "users": [
                {"id": 1, "name": "John", "active": True},
                {"id": 2, "name": "Jane", "active": False},
            ],
            "settings": {
                "theme": "dark",
                "notifications": {"email": True, "push": False},
            },
            "metadata": None,
        }

        result = self.client.get_json("complex_flag", complex_json)
        self.assertEqual(result, complex_json)

    def test_extreme_number_values(self):
        """Should handle extreme number values as defaults"""
        # Very large numbers
        large_int = 2**63 - 1
        result = self.client.get_number("large_flag", large_int)
        self.assertEqual(result, large_int)

        # Very small numbers
        small_float = 1e-10
        result = self.client.get_number("small_flag", small_float)
        self.assertEqual(result, small_float)

        # Zero
        result = self.client.get_number("zero_flag", 0)
        self.assertEqual(result, 0)

        # Negative numbers
        result = self.client.get_number("negative_flag", -42.5)
        self.assertEqual(result, -42.5)

    def test_attributes_with_various_data_types(self):
        """Should handle attributes with various data types"""
        complex_attributes = {
            "string_attr": "value",
            "int_attr": 42,
            "float_attr": 3.14,
            "bool_attr": True,
            "list_attr": [1, 2, 3],
            "dict_attr": {"nested": "value"},
            "none_attr": None,
        }

        # Should not crash with complex attributes
        result = self.client.get_bool("test_flag", False, complex_attributes)
        self.assertFalse(result)


class TestAstrolabeClientProjectPolling(unittest.TestCase):
    """Test cases for project-based polling functionality with pagination"""

    def setUp(self):
        """Set up test client with API and subscribed projects"""
        if "ASTROLABE_API_URL" in os.environ:
            del os.environ["ASTROLABE_API_URL"]
        os.environ["ASTROLABE_API_URL"] = "https://api.example.com"

    def tearDown(self):
        """Clean up environment after each test"""
        if "ASTROLABE_API_URL" in os.environ:
            del os.environ["ASTROLABE_API_URL"]

    @patch("requests.get")
    def test_fetch_project_flags_single_page(self, mock_get):
        """Should fetch flags for a single project with single page response"""
        # Mock response with flags
        mock_response = Mock()
        mock_response.json.return_value = {
            "feature_flags": [
                {
                    "key": "flag1",
                    "environments": [
                        {
                            "environment": "development",
                            "enabled": True,
                            "defaultValue": True,
                            "rules": [],
                        }
                    ],
                },
                {
                    "key": "flag2",
                    "environments": [
                        {
                            "environment": "development",
                            "enabled": True,
                            "defaultValue": True,
                            "rules": [],
                        }
                    ],
                },
            ],
            "total_count": 2,
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # clients automatically starts polling
        client = AstrolabeClient("development", subscribed_projects=["p1"])

        # self.assertEqual(len(flags), 2)
        # self.assertEqual(flags[0]["key"], "flag1")
        # self.assertEqual(flags[1]["key"], "flag2")

        # Verify API call
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn("p1", call_args[0][0])
        self.assertEqual(call_args[1]["params"]["limit"], 1000)
        self.assertEqual(call_args[1]["params"]["offset"], 0)
        flag = client.get_bool("p1/flag1", False)
        self.assertTrue(flag)

    @patch("requests.get")
    def test_fetch_project_flags_multiple_pages(self, mock_get):
        """Should fetch flags across multiple pages"""
        # Mock first page response
        first_response = Mock()
        first_response.json.return_value = [
            {
                "key": f"flag{i}",
                "environments": [
                    {
                        "environment": "development",
                        "enabled": True,
                        "defaultValue": i,
                        "rules": [],
                    }
                ],
            }
            for i in range(1000)
        ]
        first_response.raise_for_status.return_value = None

        # Mock second page response (partial)
        second_response = Mock()
        second_response.json.return_value = [
            {"key": f"flag{i}", "value": i} for i in range(1000, 1500)
        ]
        second_response.raise_for_status.return_value = None

        mock_get.side_effect = [first_response, second_response]

        client = AstrolabeClient("development", subscribed_projects=["project1"])

        self.assertEqual(len(client._flags_cache.keys()), 1500)
        self.assertEqual(mock_get.call_count, 2)

        # Verify pagination calls
        first_call_params = mock_get.call_args_list[0][1]["params"]
        self.assertEqual(first_call_params["offset"], 0)
        self.assertEqual(first_call_params["limit"], 1000)

        second_call_params = mock_get.call_args_list[1][1]["params"]
        self.assertEqual(second_call_params["offset"], 1000)
        self.assertEqual(second_call_params["limit"], 1000)

    @patch("requests.get")
    def test_fetch_project_flags_wrapped_response(self, mock_get):
        """Should handle API responses wrapped in data structures"""
        # Test response wrapped in 'flags' key
        mock_response = Mock()
        mock_response.json.return_value = {
            "flags": [{"key": "flag1", "value": True}],
            "total": 1,
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with patch.object(AstrolabeClient, "_start_polling"):
            client = AstrolabeClient("development", subscribed_projects=["project1"])
            flags = client._fetch_project_flags("project1")

        self.assertEqual(len(flags), 1)
        self.assertEqual(flags[0]["key"], "flag1")

    @patch("requests.get")
    def test_fetch_flags_sync_multiple_projects(self, mock_get):
        """Should fetch flags for multiple subscribed projects"""

        # Mock responses for different projects
        def mock_response_side_effect(url, **kwargs):
            response = Mock()
            response.raise_for_status.return_value = None

            if "project1" in url:
                response.json.return_value = [{"key": "flag1", "value": True}]
            elif "project2" in url:
                response.json.return_value = [{"key": "flag2", "value": "test"}]
            else:
                response.json.return_value = []

            return response

        mock_get.side_effect = mock_response_side_effect

        with patch.object(AstrolabeClient, "_start_polling"):
            client = AstrolabeClient(
                "development", subscribed_projects=["project1", "project2"]
            )
            # client._fetch_flags_sync() is already called at initalization time

        # Should have called API for both projects
        self.assertEqual(mock_get.call_count, 2)

        # Check cache contains flags with project prefixes
        with client._cache_lock:
            self.assertIn("project1/flag1", client._flags_cache)
            self.assertIn("project2/flag2", client._flags_cache)

    @patch("requests.get")
    def test_fetch_flags_sync_no_subscribed_projects(self, mock_get):
        """Should skip fetching when no projects are subscribed"""
        with patch.object(AstrolabeClient, "_start_polling"):
            client = AstrolabeClient("development", subscribed_projects=[])
            client._fetch_flags_sync()

        # Should not make any API calls
        mock_get.assert_not_called()

    @patch("requests.get")
    def test_fetch_project_flags_api_error(self, mock_get):
        """Should handle API errors gracefully during project flag fetching"""
        mock_get.side_effect = Exception("API Error")

        with patch.object(AstrolabeClient, "_start_polling"):
            client = AstrolabeClient("development", subscribed_projects=["project1"])
            flags = client._fetch_project_flags("project1")

        # Should return empty list on error
        self.assertEqual(len(flags), 0)

    @patch("requests.get")
    def test_fetch_project_flags_empty_response(self, mock_get):
        """Should handle empty API responses"""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with patch.object(AstrolabeClient, "_start_polling"):
            client = AstrolabeClient("development", subscribed_projects=["project1"])
            flags = client._fetch_project_flags("project1")

        self.assertEqual(len(flags), 0)


if __name__ == "__main__":
    unittest.main()
