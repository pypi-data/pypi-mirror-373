"""
Astrolabe Client - Main SDK class for feature flag evaluation (Refactored with new method names)
"""

from enum import Enum
from typing import Any, Dict, Optional, Union, List
import json
import threading
import time
import requests
import logging
import os
import re
from .settings import AstrolabeSettings
from .rule_engine import RuleEngine


class Environment(Enum):
    """Supported environments for Astrolabe"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


def normalize_environment(env_input: str) -> str:
    """
    Normalize various environment input formats to standard environment names.
    
    Args:
        env_input: User-provided environment string
        
    Returns:
        Normalized environment string (development, staging, or production)
        
    Raises:
        ValueError: If environment input cannot be mapped to a valid environment
    """
    if not isinstance(env_input, str):
        raise ValueError("Environment input must be a string")
    
    # Convert to lowercase for case-insensitive matching
    env_lower = env_input.lower().strip()
    
    # Development environment mappings
    if env_lower in ['dev', 'develop', 'development']:
        return Environment.DEVELOPMENT.value
    
    # Staging environment mappings  
    elif env_lower in ['stg', 'stag', 'staging']:
        return Environment.STAGING.value
    
    # Production environment mappings
    elif env_lower in ['prod', 'production']:
        return Environment.PRODUCTION.value
    
    else:
        valid_inputs = ['dev', 'develop', 'development', 'stg', 'stag', 'staging', 'prod', 'production']
        raise ValueError(f"Invalid environment: '{env_input}'. Valid inputs: {valid_inputs}")


class AstrolabeClient:
    """
    Main client class for Astrolabe feature flag system.
    
    Supports number, string, boolean, and JSON flags with environment-based configuration.
    Implements local evaluation with background polling for flag updates.
    """
    
    def __init__(self, env: Union[str, Environment], settings: Optional[Union[AstrolabeSettings, Dict[str, Any]]] = None, logger: Optional[logging.Logger] = None, subscribed_projects: Optional[List[str]] = None):
        """
        Initialize the Astrolabe client.
        
        Args:
            env: Environment (development, staging, or production)
            settings: Configuration settings (AstrolabeSettings object or dict)
            logger: Optional external logger; if not provided, creates internal logger
            subscribed_projects: Optional list of project keys that this client is subscribed to
        """
        # Set environment
        if isinstance(env, str):
            try:
                # Use the normalize_environment function to handle various input formats
                normalized_env = normalize_environment(env)
                self.env = Environment(normalized_env)
            except ValueError as e:
                raise ValueError(str(e))
        elif isinstance(env, Environment):
            self.env = env
        else:
            raise TypeError("Environment must be a string or Environment enum")
        
        # Load settings
        if settings is None:
            self.settings = AstrolabeSettings.get_default()
        elif isinstance(settings, dict):
            self.settings = AstrolabeSettings.from_dict(settings)
        elif isinstance(settings, AstrolabeSettings):
            self.settings = settings
        else:
            raise TypeError("Settings must be AstrolabeSettings object or dictionary")
        
        # Setup logging
        self._setup_logging(logger)
        
        # Flag cache and synchronization - using RLock for thread safety
        self._flags_cache: Dict[str, Any] = {}
        self._cache_lock = threading.RLock()
        self._last_updated = 0
        self._polling_thread: Optional[threading.Thread] = None
        self._stop_polling = threading.Event()
        
        # Initialize rule engine
        self._rule_engine = RuleEngine(logger=self.logger)
        
        self._subscribed_projects = subscribed_projects or []
        
        # Check if API URL is available
        self._api_url = os.getenv('ASTROLABE_API_URL')
        if not self._api_url:
            self.logger.warning("ASTROLABE_API_URL environment variable not set. SDK will only use default values and not fetch from backend.")
            self._use_api = False
        else:
            self._use_api = True
            self.logger.info(f"Using API URL from environment: {self._api_url}")
        
        # Initialize flags and start polling (only if API is available)
        if self._use_api:
            self.logger.info(f"Starting flag initialization and polling (interval: {self.settings.poll_interval}s)")
            self._fetch_flags_sync()
            self._start_polling()
        else:
            self.logger.info("API not available, SDK will use default values only")
    
    def _setup_logging(self, external_logger: Optional[logging.Logger] = None) -> None:
        """
        Setup logging for the SDK.
        
        Args:
            external_logger: Optional external logger to use
        """
        # Check if debug logging is enabled via environment variable
        debug_logging_enabled = os.getenv('ASTROLABE_DEBUG_LOGGING_ENABLED', 'false').lower() in ('true', '1', 'yes', 'on')
        
        if external_logger:
            self.logger = external_logger
            self.logger.info(f"Astrolabe [{self.env.value}] - Using external logger")
        elif debug_logging_enabled:
            # Create internal logger with astrolabe prefix and environment
            logger_name = f"astrolabe.{self.env.value}"
            self.logger = logging.getLogger(logger_name)
            
            # Only add handler if it doesn't already exist
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    'Astrolabe [%(name)s] - %(levelname)s - %(message)s'
                )
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
                self.logger.setLevel(logging.INFO)
                
            self.logger.info(f"Initialized Astrolabe SDK for {self.env.value} environment")
        else:
            # Use null handler when logging is disabled
            self.logger = logging.getLogger(f"astrolabe.{self.env.value}")
            self.logger.addHandler(logging.NullHandler())
    
    def _fetch_flags_sync(self) -> None:
        """
        Synchronously fetch flags from the backend API using project-based endpoints with pagination.
        """
        if not self._use_api:
            self.logger.debug("API not available, skipping flag fetch")
            return
        
        if not self._subscribed_projects:
            self.logger.warning("No subscribed projects configured, skipping flag fetch")
            return
            
        try:
            total_flags_fetched = 0
            
            # Fetch flags for each subscribed project
            for project_key in self._subscribed_projects:
                project_flags = self._fetch_project_flags(project_key)
                total_flags_fetched += len(project_flags)
                
                with self._cache_lock:
                    # Update cache with new flags from this project
                    for flag in project_flags:
                        if isinstance(flag, dict) and 'key' in flag:
                            # Ensure flag key includes project prefix
                            flag_key = flag['key']
                            if not flag_key.startswith(f"{project_key}/"):
                                flag_key = f"{project_key}/{flag_key}"
                            self._flags_cache[flag_key] = flag
            
            with self._cache_lock:
                self._last_updated = time.time()
                
            self.logger.info(f"Successfully fetched {total_flags_fetched} flags from {len(self._subscribed_projects)} projects")
                
        except Exception as e:
            # Log error but don't crash - use cached values or defaults
            self.logger.warning(f"Failed to fetch flags: {e}")
    
    def _fetch_project_flags(self, project_key: str) -> List[Dict[str, Any]]:
        """
        Fetch all flags for a specific project using pagination.
        
        Args:
            project_key: The project key to fetch flags for
            
        Returns:
            List of flag definitions for the project
        """
        all_flags = []
        offset = 0
        limit = 1000  # Page size as requested
        total_count = None
        
        while True:
            try:
                # Construct the project-specific API URL with pagination
                url = f"{self._api_url}/api/v1/feature-flags/project/{project_key}"
                params = {
                    'limit': limit,
                    'offset': offset
                }
                
                self.logger.debug(f"Fetching flags for project '{project_key}' with offset {offset}, limit {limit}")
                
                response = requests.get(url, params=params, timeout=self.settings.request_timeout)
                response.raise_for_status()
                
                flags_data = response.json()
                
                # Handle different response formats
                if isinstance(flags_data, dict):
                    # Handle the actual API response format: { feature_flags: [], total_count: }
                    if 'feature_flags' in flags_data:
                        page_flags = flags_data['feature_flags']
                        # Use total_count for efficient pagination
                        if 'total_count' in flags_data and total_count is None:
                            total_count = flags_data['total_count']
                            self.logger.debug(f"Total flags available for project '{project_key}': {total_count}")
                    # Legacy fallback formats
                    elif 'flags' in flags_data:
                        page_flags = flags_data['flags']
                    elif 'data' in flags_data:
                        page_flags = flags_data['data']
                    else:
                        # Assume the dict itself contains flag data
                        page_flags = [flags_data] if flags_data else []
                elif isinstance(flags_data, list):
                    page_flags = flags_data
                else:
                    page_flags = []
                
                if not page_flags:
                    # No more flags to fetch
                    break
                    
                all_flags.extend(page_flags)
                
                # Use total_count for early termination if available
                if total_count is not None and len(all_flags) >= total_count:
                    self.logger.debug(f"Fetched all {total_count} flags for project '{project_key}', stopping pagination")
                    break
                
                # If we got fewer flags than the limit, we've reached the end
                if len(page_flags) < limit:
                    break
                    
                offset += limit
                
            except Exception as e:
                self.logger.warning(f"Failed to fetch flags for project '{project_key}' at offset {offset}: {e}")
                break
        
        self.logger.debug(f"Fetched {len(all_flags)} flags for project '{project_key}'")
        return all_flags
    
    def _start_polling(self) -> None:
        """
        Start the background polling thread.
        """
        if self._polling_thread is None or not self._polling_thread.is_alive():
            self._stop_polling.clear()
            self._polling_thread = threading.Thread(target=self._polling_loop, daemon=True)
            self._polling_thread.start()
            self.logger.info(f"Started background polling thread (interval: {self.settings.poll_interval}s)")
        else:
            self.logger.debug("Polling thread already running")
    
    def _polling_loop(self) -> None:
        """
        Background polling loop that fetches flags at regular intervals.
        """
        self.logger.debug("Polling loop started")
        while not self._stop_polling.wait(self.settings.poll_interval):
            self.logger.debug("Polling interval elapsed, fetching flags")
            self._fetch_flags_sync()
        self.logger.info("Polling loop stopped")
    
    def _validate_flag_key_format(self, key: str) -> bool:
        """Validate that flag key follows 'project-key/flag-key' format."""
        pattern = r'^[^/]+/[^/]+$'
        return bool(re.match(pattern, key))
    
    def _extract_project_key(self, key: str) -> str:
        """Extract project key from flag key."""
        slash_index = key.find('/')
        return key[:slash_index] if slash_index > 0 else ''
    
    def _is_project_subscribed(self, key: str) -> bool:
        """Check if the project for this flag key is subscribed."""
        if not self._subscribed_projects:
            return True
        project_key = self._extract_project_key(key)
        return project_key in self._subscribed_projects

    def _get_flag_value(self, key: str, default: Any, attributes: Optional[Dict[str, Any]] = None) -> Any:
        """
        Internal method to get flag value from cache with advanced rule evaluation.
        
        Args:
            key: Flag key identifier
            default: Default value if flag is not found
            attributes: Optional attributes for flag evaluation context
            
        Returns:
            Flag value or default
        """
        if self._subscribed_projects:
            if not self._validate_flag_key_format(key):
                self.logger.warning(f"Invalid flag key format '{key}'. Expected format: 'project-key/flag-key'. Using default value.")
                return default
            
            if not self._is_project_subscribed(key):
                project_key = self._extract_project_key(key)
                self.logger.warning(f"Flag '{key}' belongs to unsubscribed project '{project_key}'. Using default value.")
                return default
        
        # Ensure attributes is not None for rule evaluation
        if attributes is None:
            attributes = {}
            
        with self._cache_lock:
            flag_config = self._flags_cache.get(key)
            
            if flag_config is None:
                self.logger.debug(f"Flag '{key}' not found in cache, using default: {default}")
                return default
            
            # Check if this is an advanced flag configuration with environments
            if isinstance(flag_config, dict) and 'environments' in flag_config:
                # Use rule engine for advanced evaluation
                self.logger.debug(f"Flag '{key}' has advanced configuration, using rule engine")
                return self._rule_engine.evaluate_flag(flag_config, self.env.value, attributes, default)
            
            # If flag_config is a simple value (this should not happen - flags should be proper configurations)
            self.logger.warning(f"Flag '{key}' has invalid configuration (simple value instead of flag config): {flag_config}. Using default value.")
            return default
    
    def stop_polling(self) -> None:
        """
        Stop the background polling thread. Useful for cleanup.
        """
        self.logger.info("Stopping background polling")
        self._stop_polling.set()
        if self._polling_thread and self._polling_thread.is_alive():
            self._polling_thread.join(timeout=1)
            if self._polling_thread.is_alive():
                self.logger.warning("Polling thread did not stop within timeout")
            else:
                self.logger.info("Background polling stopped successfully")
    
    def refresh_flags(self) -> None:
        """
        Manually refresh flags from the backend.
        """
        self.logger.info("Manual flag refresh requested")
        self._fetch_flags_sync()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about the current flag cache.
        
        Returns:
            Dictionary with cache statistics
        """
        with self._cache_lock:
            return {
                'flag_count': len(self._flags_cache),
                'last_updated': self._last_updated,
                'seconds_since_update': time.time() - self._last_updated,
                'environment': self.env.value,
                'poll_interval': self.settings.poll_interval,
                'api_url': self._api_url
            }
    
    def get_number(self, key: str, default: Union[int, float], attributes: Optional[Dict[str, Any]] = None) -> Union[int, float]:
        """
        Get and evaluate a number flag using the complete flag configuration.
        
        This method:
        1. Retrieves the entire flag JSON from cache
        2. Evaluates environment enable/disable status
        3. Processes rules and conditions with user attributes
        4. Returns the final evaluated number value
        
        Args:
            key: Flag key identifier
            default: Default number value if flag is not found or evaluation fails
            attributes: Optional attributes for flag evaluation context (user_id, country, plan, etc.)
            
        Returns:
            Evaluated number value (int or float) based on flag configuration
        """
        try:
            value = self._get_flag_value(key, default, attributes)
            
            # Ensure the value is a number
            if isinstance(value, (int, float)):
                return value
            elif isinstance(value, str):
                try:
                    # Try to convert string to number
                    if '.' in value:
                        return float(value)
                    else:
                        return int(value)
                except ValueError:
                    return default
            else:
                return default
        except Exception as e:
            self.logger.warning(f"Error evaluating number flag '{key}': {e}. Using default value: {default}")
            return default
    
    def get_string(self, key: str, default: str, attributes: Optional[Dict[str, Any]] = None) -> str:
        """
        Get and evaluate a string flag using the complete flag configuration.
        
        This method:
        1. Retrieves the entire flag JSON from cache
        2. Evaluates environment enable/disable status
        3. Processes rules and conditions with user attributes
        4. Returns the final evaluated string value
        
        Args:
            key: Flag key identifier
            default: Default string value if flag is not found or evaluation fails
            attributes: Optional attributes for flag evaluation context (user_id, country, plan, etc.)
            
        Returns:
            Evaluated string value based on flag configuration
        """
        try:
            value = self._get_flag_value(key, default, attributes)
            
            # Ensure the value is a string
            if isinstance(value, str):
                return value
            elif value is not None:
                return str(value)
            else:
                return default
        except Exception as e:
            self.logger.warning(f"Error evaluating string flag '{key}': {e}. Using default value: {default}")
            return default
    
    def get_bool(self, key: str, default: bool, attributes: Optional[Dict[str, Any]] = None) -> bool:
        """
        Get and evaluate a boolean flag using the complete flag configuration.
        
        This method:
        1. Retrieves the entire flag JSON from cache
        2. Evaluates environment enable/disable status
        3. Processes rules and conditions with user attributes
        4. Returns the final evaluated boolean value
        
        Args:
            key: Flag key identifier
            default: Default boolean value if flag is not found or evaluation fails
            attributes: Optional attributes for flag evaluation context (user_id, country, plan, etc.)
            
        Returns:
            Evaluated boolean value based on flag configuration
        """
        try:
            value = self._get_flag_value(key, default, attributes)
            
            # Handle different boolean representations
            if isinstance(value, bool):
                return value
            elif isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on', 'enabled')
            elif isinstance(value, (int, float)):
                return bool(value)
            else:
                return default
        except Exception as e:
            self.logger.warning(f"Error evaluating boolean flag '{key}': {e}. Using default value: {default}")
            return default
    
    def get_json(self, key: str, default: Dict[str, Any], attributes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get and evaluate a JSON flag using the complete flag configuration.
        
        This method:
        1. Retrieves the entire flag JSON from cache
        2. Evaluates environment enable/disable status
        3. Processes rules and conditions with user attributes
        4. Returns the final evaluated JSON/dictionary value
        
        Args:
            key: Flag key identifier
            default: Default JSON/dict value if flag is not found or evaluation fails
            attributes: Optional attributes for flag evaluation context (user_id, country, plan, etc.)
            
        Returns:
            Evaluated JSON/dictionary value based on flag configuration
        """
        try:
            value = self._get_flag_value(key, default, attributes)
            
            # Ensure the value is a dictionary
            if isinstance(value, dict):
                return value
            elif isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return default
            else:
                return default
        except Exception as e:
            self.logger.warning(f"Error evaluating JSON flag '{key}': {e}. Using default value: {default}")
            return default
    
    def get_flag(self, key: str, default: Any, attributes: Optional[Dict[str, Any]] = None) -> Any:
        """
        Get and evaluate a flag of any type using the complete flag configuration.
        
        This method:
        1. Retrieves the entire flag JSON from cache
        2. Evaluates environment enable/disable status
        3. Processes rules and conditions with user attributes
        4. Routes to appropriate typed method based on default value type
        5. Returns the final evaluated value
        
        Args:
            key: Flag key identifier
            default: Default value of any supported type (determines return type)
            attributes: Optional attributes for flag evaluation context (user_id, country, plan, etc.)
            
        Returns:
            Evaluated flag value of the same type as default
        """
        try:
            # Route to appropriate typed method based on default type
            if isinstance(default, bool):
                return self.get_bool(key, default, attributes)
            elif isinstance(default, (int, float)):
                return self.get_number(key, default, attributes)
            elif isinstance(default, str):
                return self.get_string(key, default, attributes)
            elif isinstance(default, dict):
                return self.get_json(key, default, attributes)
            else:
                # Fallback to direct cache lookup
                return self._get_flag_value(key, default, attributes)
        except Exception as e:
            self.logger.warning(f"Error evaluating flag '{key}': {e}. Using default value: {default}")
            return default
