"""
Configuration management with secure credential storage using macOS Keychain.
"""

import json
import logging
from pathlib import Path
from typing import Any, Optional

try:
    import keyring
    HAS_KEYRING = True
except ImportError:
    HAS_KEYRING = False
    # Fallback to storing password in config file (less secure but works)
    import warnings
    warnings.warn("keyring not available, credentials will be stored in config file")

logger = logging.getLogger(__name__)


class Config:
    """
    Manages application configuration and secure credential storage.
    
    Configuration is stored in ~/.clockintime/config.json
    Passwords are stored securely in macOS Keychain
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Custom config directory. Defaults to ~/.clockintime
        """
        from clockintime.constants import FACTORIAL_SERVICE_NAME
        
        self.service_name = FACTORIAL_SERVICE_NAME
        self.config_dir = config_dir or Path.home() / ".clockintime"
        self.config_file = self.config_dir / "config.json"
        self._settings: dict[str, Any] = {}
        
        self._ensure_config_dir()
        self._load_config()
    
    def _ensure_config_dir(self) -> None:
        """Create config directory if it doesn't exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Config directory: {self.config_dir}")
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._settings = json.load(f)
                logger.debug("Configuration loaded successfully")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse config file: {e}")
                self._settings = {}
        else:
            self._settings = {}
            self._save_config()
    
    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2)
            logger.debug("Configuration saved successfully")
        except IOError as e:
            logger.error(f"Failed to save config file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value or default
        """
        return self._settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Value to store
        """
        self._settings[key] = value
        self._save_config()
    
    def get_email(self) -> Optional[str]:
        """
        Get stored email address.
        
        Returns:
            Email address or None
        """
        return self._settings.get("email")
    
    def set_email(self, email: str) -> None:
        """
        Store email address.
        
        Args:
            email: Email address to store
        """
        self._settings["email"] = email
        self._save_config()
        logger.info(f"Email updated: {email}")
    
    def get_password(self) -> Optional[str]:
        """
        Get password from macOS Keychain (or config file if keyring unavailable).
        
        Returns:
            Password or None
        """
        email = self.get_email()
        if not email:
            return None
        
        if HAS_KEYRING:
            try:
                return keyring.get_password(self.service_name, email)
            except Exception as e:
                logger.error("Failed to retrieve password: %s", e)
                return None
        else:
            # Fallback: read from config file (less secure)
            return self._settings.get("password")
    
    def set_password(self, email: str, password: str) -> None:
        """
        Store password in macOS Keychain (or config file if keyring unavailable).
        
        Args:
            email: Email address (used as username in keychain)
            password: Password to store
        """
        if HAS_KEYRING:
            try:
                keyring.set_password(self.service_name, email, password)
                logger.info("Password stored in keychain")
            except Exception as e:
                logger.error("Failed to store password: %s", e)
                raise
        else:
            # Fallback: store in config file (less secure)
            self._settings["password"] = password
            self._save_config()
            logger.warning("Password stored in config file (keyring not available)")
    
    def clear_credentials(self) -> None:
        """Clear stored credentials from both config and keychain."""
        email = self.get_email()
        if email and HAS_KEYRING:
            try:
                keyring.delete_password(self.service_name, email)
                logger.info("Password removed from keychain")
            except Exception:
                logger.warning("No password found in keychain")
        
        if "email" in self._settings:
            del self._settings["email"]
        if "password" in self._settings:
            del self._settings["password"]
        self._save_config()
        logger.info("Credentials removed from config")
    
    def has_credentials(self) -> bool:
        """
        Check if valid credentials are stored.
        
        Returns:
            True if both email and password are available
        """
        email = self.get_email()
        if not email:
            return False
        
        password = self.get_password()
        return password is not None
    
    def get_workday_hours(self) -> int:
        """
        Get configured workday hours.
        
        Returns:
            Number of hours in a workday (default: 8)
        """
        from clockintime.constants import DEFAULT_WORKDAY_HOURS
        return self.get("workday_hours", DEFAULT_WORKDAY_HOURS)
    
    def set_workday_hours(self, hours: int) -> None:
        """
        Set workday hours.
        
        Args:
            hours: Number of hours in a workday
        """
        if hours < 1 or hours > 24:
            raise ValueError("Workday hours must be between 1 and 24")
        self.set("workday_hours", hours)
        logger.info(f"Workday hours set to: {hours}")
