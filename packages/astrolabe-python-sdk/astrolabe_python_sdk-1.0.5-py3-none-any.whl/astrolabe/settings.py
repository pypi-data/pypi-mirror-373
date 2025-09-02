"""
Astrolabe SDK Settings and Configuration
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


# Default configuration constants
DEFAULT_API_URL = "https://asdsa.free.beeceptor.com/api/flags"
DEFAULT_POLL_INTERVAL = 60
DEFAULT_REQUEST_TIMEOUT = 10
DEFAULT_MAX_RETRIES = 3
DEFAULT_ENABLE_LOGGING = True
DEFAULT_CACHE_TTL = 300


@dataclass
class AstrolabeSettings:
    """
    Configuration settings for Astrolabe SDK.
    """
    api_url: str = DEFAULT_API_URL
    poll_interval: int = DEFAULT_POLL_INTERVAL
    request_timeout: int = DEFAULT_REQUEST_TIMEOUT
    max_retries: int = DEFAULT_MAX_RETRIES
    enable_logging: bool = DEFAULT_ENABLE_LOGGING
    cache_ttl: int = DEFAULT_CACHE_TTL
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'AstrolabeSettings':
        """
        Create settings from a dictionary, merging with defaults.
        
        Args:
            config_dict: Dictionary containing configuration values
            
        Returns:
            AstrolabeSettings instance with provided values merged with defaults
        """
        # Start with default instance
        defaults = cls()
        
        # Update only the provided values
        for key, value in config_dict.items():
            if hasattr(defaults, key):
                setattr(defaults, key, value)
        
        return defaults
    
    @classmethod
    def get_default(cls) -> 'AstrolabeSettings':
        """
        Get default configuration settings.
        
        Returns:
            AstrolabeSettings instance with default values
        """
        return cls()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert settings to dictionary.
        
        Returns:
            Dictionary representation of settings
        """
        return {
            'api_url': self.api_url,
            'poll_interval': self.poll_interval,
            'request_timeout': self.request_timeout,
            'max_retries': self.max_retries,
            'enable_logging': self.enable_logging,
            'cache_ttl': self.cache_ttl
        }



