"""
Secret management utilities for PyConfig.

This module provides secure handling of sensitive configuration data
including environment variable loading, secret masking, and validation.
"""

import os
import re
from functools import lru_cache
from pathlib import Path
from re import Pattern

from pydantic import SecretStr

from ..core.exceptions import SecurityError


class SecretManager:
    """
    Manager for secure handling of sensitive configuration data.

    This class provides utilities for loading secrets from environment
    variables, files, and other sources while ensuring they are properly
    masked in logs and error messages.

    Example:
        ```python
        from cfy.security import SecretManager

        manager = SecretManager()

        # Load secret from environment
        api_key = manager.get_secret_env('API_KEY')

        # Load secret from file
        db_password = manager.get_secret_file('db_password.txt')

        # Validate secret format
        if manager.is_valid_secret(api_key, min_length=32):
            console.print("API key is valid")
        ```

    <!-- Example Test:
    >>> from cfy.security.secrets import SecretManager
    >>> import os
    >>> os.environ['TEST_SECRET'] = 'test_value_123'
    >>> manager = SecretManager()
    >>> secret = manager.get_secret_env('TEST_SECRET')
    >>> assert isinstance(secret, SecretStr)
    >>> assert secret.get_secret_value() == 'test_value_123'
    >>> del os.environ['TEST_SECRET']
    -->
    """

    # Common patterns for secret validation
    SECRET_PATTERNS = {
        "api_key": re.compile(r"^[a-zA-Z0-9_-]{16,}$"),
        "token": re.compile(r"^[a-zA-Z0-9._-]{20,}$"),
        "password": re.compile(r"^.{8,}$"),  # Minimum 8 characters
        "uuid": re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
        ),
        "hex": re.compile(r"^[0-9a-f]+$", re.IGNORECASE),
    }

    def __init__(self, mask_in_logs: bool = True) -> None:
        """
        Initialize secret manager.

        Args:
            mask_in_logs: Whether to automatically mask secrets in logs

        Example:
            ```python
            # Create manager with default settings
            manager = SecretManager()

            # Create manager with custom settings
            manager = SecretManager(mask_in_logs=False)
            ```
        """
        self.mask_in_logs = mask_in_logs
        self._secret_cache: dict[str, SecretStr] = {}

    def get_secret_env(
        self, var_name: str, default: str | None = None, required: bool = True
    ) -> SecretStr:
        """
        Load secret from environment variable.

        Args:
            var_name: Environment variable name
            default: Default value if variable not found
            required: Whether the variable is required

        Returns:
            Secret string wrapper

        Raises:
            SecurityError: If required variable is missing or invalid

        Example:
            ```python
            manager = SecretManager()

            # Load required secret
            api_key = manager.get_secret_env('API_KEY')

            # Load optional secret with default
            debug_key = manager.get_secret_env('DEBUG_KEY', default='debug', required=False)
            ```
        """
        try:
            value = os.getenv(var_name, default)

            if value is None and required:
                raise SecurityError(
                    f"Required environment variable '{var_name}' is not set",
                    details={"variable": var_name, "required": True},
                )

            if value is None:
                # Return empty secret for optional variables
                return SecretStr("")

            # Validate secret value
            if required and not value.strip():
                raise SecurityError(
                    f"Environment variable '{var_name}' is empty",
                    details={"variable": var_name, "empty": True},
                )

            return SecretStr(value)

        except SecurityError:
            raise
        except Exception as e:
            raise SecurityError(
                f"Failed to load secret from environment variable '{var_name}': {e}",
                details={"variable": var_name, "load_error": str(e)},
            ) from e

    def get_secret_file(
        self, file_path: str | Path, encoding: str = "utf-8", strip_whitespace: bool = True
    ) -> SecretStr:
        """
        Load secret from file.

        Args:
            file_path: Path to secret file
            encoding: File encoding
            strip_whitespace: Whether to strip leading/trailing whitespace

        Returns:
            Secret string wrapper

        Raises:
            SecurityError: If file cannot be read or is invalid

        Example:
            ```python
            manager = SecretManager()

            # Load secret from file
            db_password = manager.get_secret_file('/etc/secrets/db_password')

            # Load with custom encoding
            api_key = manager.get_secret_file('api_key.txt', encoding='ascii')
            ```
        """
        file_path = Path(file_path)

        try:
            if not file_path.exists():
                raise SecurityError(
                    f"Secret file does not exist: {file_path}", file_path=str(file_path)
                )

            if not file_path.is_file():
                raise SecurityError(
                    f"Secret path is not a file: {file_path}", file_path=str(file_path)
                )

            # Check file permissions (should not be world-readable)
            file_stat = file_path.stat()
            if file_stat.st_mode & 0o044:  # World or group readable
                raise SecurityError(
                    f"Secret file has insecure permissions: {file_path}",
                    file_path=str(file_path),
                    details={"permissions": oct(file_stat.st_mode)},
                )

            # Read file content
            content = file_path.read_text(encoding=encoding)

            if strip_whitespace:
                content = content.strip()

            if not content:
                raise SecurityError(f"Secret file is empty: {file_path}", file_path=str(file_path))

            return SecretStr(content)

        except SecurityError:
            raise
        except Exception as e:
            raise SecurityError(
                f"Failed to load secret from file '{file_path}': {e}",
                file_path=str(file_path),
                details={"read_error": str(e)},
            ) from e

    def is_valid_secret(
        self,
        secret: SecretStr | str,
        pattern_name: str | None = None,
        custom_pattern: Pattern[str] | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
    ) -> bool:
        """
        Validate secret format and strength.

        Args:
            secret: Secret to validate
            pattern_name: Name of predefined pattern to use
            custom_pattern: Custom regex pattern for validation
            min_length: Minimum length requirement
            max_length: Maximum length requirement

        Returns:
            True if secret is valid, False otherwise

        Example:
            ```python
            manager = SecretManager()

            # Validate using predefined pattern
            is_valid = manager.is_valid_secret(api_key, pattern_name='api_key')

            # Validate using custom pattern
            pattern = re.compile(r'^[A-Z0-9]{32}$')
            is_valid = manager.is_valid_secret(token, custom_pattern=pattern)

            # Validate length only
            is_valid = manager.is_valid_secret(password, min_length=12)
            ```
        """
        try:
            # Extract secret value
            if isinstance(secret, SecretStr):
                secret_value = secret.get_secret_value()
            else:
                secret_value = secret

            # Check length requirements
            if min_length is not None and len(secret_value) < min_length:
                return False

            if max_length is not None and len(secret_value) > max_length:
                return False

            # Check pattern requirements
            if pattern_name is not None:
                if pattern_name not in self.SECRET_PATTERNS:
                    raise SecurityError(
                        f"Unknown secret pattern: {pattern_name}",
                        details={
                            "pattern_name": pattern_name,
                            "available": list(self.SECRET_PATTERNS.keys()),
                        },
                    )
                pattern = self.SECRET_PATTERNS[pattern_name]
                return bool(pattern.match(secret_value))

            if custom_pattern is not None:
                return bool(custom_pattern.match(secret_value))

            # If no pattern specified, just check it's not empty
            return bool(secret_value.strip())

        except Exception as e:
            raise SecurityError(
                f"Failed to validate secret: {e}", details={"validation_error": str(e)}
            ) from e

    def mask_secret(self, secret: SecretStr | str, show_chars: int = 4) -> str:
        """
        Create masked representation of secret for logging.

        Args:
            secret: Secret to mask
            show_chars: Number of characters to show at the end

        Returns:
            Masked secret string

        Example:
            ```python
            manager = SecretManager()

            # Mask API key for logging
            masked = manager.mask_secret(api_key)
            # "****1234" (shows last 4 chars)

            # Show more characters
            masked = manager.mask_secret(password, show_chars=2)
            # "****ab"
            ```
        """
        try:
            # Extract secret value
            if isinstance(secret, SecretStr):
                secret_value = secret.get_secret_value()
            else:
                secret_value = secret

            if not secret_value:
                return "****"

            if len(secret_value) <= show_chars:
                return "*" * len(secret_value)

            visible_part = secret_value[-show_chars:] if show_chars > 0 else ""
            mask_length = max(4, len(secret_value) - show_chars)

            return "*" * mask_length + visible_part

        except Exception:
            return "****"

    @lru_cache(maxsize=128)
    def get_cached_secret_env(self, var_name: str, default: str | None = None) -> SecretStr:
        """
        Get environment secret with caching.

        Args:
            var_name: Environment variable name
            default: Default value if not found

        Returns:
            Cached secret string

        Example:
            ```python
            manager = SecretManager()

            # First call loads from environment
            secret1 = manager.get_cached_secret_env('API_KEY')

            # Second call returns cached value
            secret2 = manager.get_cached_secret_env('API_KEY')
            ```
        """
        return self.get_secret_env(var_name, default, required=False)

    def clear_cache(self) -> None:
        """
        Clear the secret cache.

        Example:
            ```python
            manager = SecretManager()

            # Clear cached secrets (useful for testing)
            manager.clear_cache()
            ```
        """
        self.get_cached_secret_env.cache_clear()
        self._secret_cache.clear()

    def add_secret_pattern(self, name: str, pattern: Pattern[str]) -> None:
        """
        Add custom secret validation pattern.

        Args:
            name: Pattern name
            pattern: Compiled regex pattern

        Example:
            ```python
            import re

            manager = SecretManager()

            # Add custom pattern for JWT tokens
            jwt_pattern = re.compile(r'^[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+$')
            manager.add_secret_pattern('jwt', jwt_pattern)

            # Use the pattern for validation
            is_valid = manager.is_valid_secret(token, pattern_name='jwt')
            ```
        """
        self.SECRET_PATTERNS[name] = pattern

    def remove_secret_pattern(self, name: str) -> bool:
        """
        Remove custom secret validation pattern.

        Args:
            name: Pattern name to remove

        Returns:
            True if pattern was removed, False if not found

        Example:
            ```python
            manager = SecretManager()

            # Remove custom pattern
            removed = manager.remove_secret_pattern('jwt')
            if removed:
                console.print("JWT pattern removed")
            ```
        """
        return self.SECRET_PATTERNS.pop(name, None) is not None

    def list_secret_patterns(self) -> list[str]:
        """
        List available secret validation patterns.

        Returns:
            List of pattern names

        Example:
            ```python
            manager = SecretManager()
            patterns = manager.list_secret_patterns()
            console.print(f"Available patterns: {patterns}")
            ```
        """
        return list(self.SECRET_PATTERNS.keys())


# Convenience functions
def get_secret(var_name: str, default: str | None = None, required: bool = True) -> SecretStr:
    """
    Convenience function to get secret from environment.

    Args:
        var_name: Environment variable name
        default: Default value if not found
        required: Whether the variable is required

    Returns:
        Secret string wrapper

    Example:
        ```python
        from cfy.security import get_secret

        # Load required secret
        api_key = get_secret('API_KEY')

        # Load optional secret
        debug_key = get_secret('DEBUG_KEY', required=False)
        ```

    <!-- Example Test:
    >>> from cfy.security.secrets import get_secret
    >>> import os
    >>> os.environ['TEST_SECRET_2'] = 'test_value_456'
    >>> secret = get_secret('TEST_SECRET_2')
    >>> assert isinstance(secret, SecretStr)
    >>> assert secret.get_secret_value() == 'test_value_456'
    >>> del os.environ['TEST_SECRET_2']
    -->
    """
    manager = SecretManager()
    return manager.get_secret_env(var_name, default, required)


def mask_secret(secret: SecretStr | str, show_chars: int = 4) -> str:
    """
    Convenience function to mask secret for logging.

    Args:
        secret: Secret to mask
        show_chars: Number of characters to show at end

    Returns:
        Masked secret string

    Example:
        ```python
        from cfy.security import mask_secret

        # Mask for logging
        masked = mask_secret("my_secret_key_123")
        console.print(f"Using key: {masked}")  # "Using key: ****_123"
        ```

    <!-- Example Test:
    >>> from cfy.security.secrets import mask_secret
    >>> masked = mask_secret("secret123", show_chars=3)
    >>> assert masked == "****123"
    >>> masked = mask_secret("ab", show_chars=4)
    >>> assert masked == "**"
    -->
    """
    manager = SecretManager()
    return manager.mask_secret(secret, show_chars)
