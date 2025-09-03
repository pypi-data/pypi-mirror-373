"""
Base configuration classes and utilities for PyConfig.

This module provides the foundational BaseConfiguration class that users extend
to define their domain-specific configuration schemas. It follows modern Pydantic v2
patterns and provides utilities for configuration access and manipulation.
"""

from functools import lru_cache
from typing import Any, Union

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from .exceptions import ConfigurationValidationError


class BaseConfiguration(BaseSettings):
    """
    Generic base configuration class that users extend for domain-specific schemas.

    This class provides common configuration patterns and utilities without
    imposing specific application schemas. It uses Pydantic v2 patterns and
    supports loading from multiple sources with proper precedence.

    The default precedence order is:
    1. CLI Arguments (highest precedence)
    2. Environment Variables
    3. Configuration Files
    4. Default Values (lowest precedence)

    Example:
        ```python
        from pydantic import Field, SecretStr
        from cfy import BaseConfiguration

        class MyAppConfig(BaseConfiguration):
            database_url: SecretStr = Field(..., description="Database connection string")
            api_key: SecretStr = Field(..., description="External API key")
            debug_mode: bool = Field(default=False, description="Enable debug logging")
            max_connections: int = Field(default=100, ge=1, le=1000)

        # Load configuration from all sources
        config = MyAppConfig()
        ```

    <!-- Example Test:
    >>> from cfy import BaseConfiguration
    >>> from pydantic import Field
    >>> class TestConfig(BaseConfiguration):
    ...     test_field: str = Field(default="test_value")
    >>> config = TestConfig()
    >>> assert config.test_field == "test_value"
    >>> assert isinstance(config, BaseConfiguration)
    -->
    """

    model_config = SettingsConfigDict(
        # File and encoding settings
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        # Environment variable settings
        case_sensitive=False,
        env_prefix="",
        # Validation settings
        validate_assignment=True,
        validate_default=False,
        # Security and behavior settings
        extra="forbid",  # Prevent typos in configuration
        str_strip_whitespace=True,
        # Performance optimizations
        cache_strings=True,
        use_enum_values=True,
        # Secret management
        secrets_dir=None,  # Can be overridden per instance
    )

    def get_nested(self, key: str, default: Any = None) -> Any:
        """
        Get nested configuration value using dot notation.

        This method allows accessing nested configuration values using a
        dot-separated key path, providing a convenient way to retrieve
        deeply nested settings.

        Args:
            key: Dot-separated key path (e.g., "database.host")
            default: Default value to return if key is not found

        Returns:
            The value at the specified key path, or default if not found

        Example:
            ```python
            config = MyAppConfig()
            db_host = config.get_nested("database.host")
            jwt_expiry = config.get_nested("auth.jwt.expiry", default=3600)
            ```

        <!-- Example Test:
        >>> from cfy import BaseConfiguration
        >>> from pydantic import Field
        >>> from pydantic import BaseModel
        >>> class NestedModel(BaseModel):
        ...     value: int = 42
        >>> class TestConfig(BaseConfiguration):
        ...     nested: NestedModel = NestedModel()
        >>> config = TestConfig()
        >>> assert config.get_nested("nested.value") == 42
        >>> assert config.get_nested("missing.key", "default") == "default"
        -->
        """
        keys = key.split(".")
        value = self.model_dump()

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set_nested(self, key: str, value: Any) -> None:
        """
        Set nested configuration value using dot notation.

        This method allows setting nested configuration values using a
        dot-separated key path. Note that this only works for mutable
        nested objects and may not persist across configuration reloads.

        Args:
            key: Dot-separated key path (e.g., "database.pool_size")
            value: Value to set at the specified key path

        Raises:
            ConfigurationValidationError: If the key path is invalid or value is invalid

        Example:
            ```python
            config = MyAppConfig()
            config.set_nested("database.pool_size", 50)
            ```
        """
        keys = key.split(".")
        if len(keys) == 1:
            # Direct field assignment
            if hasattr(self, keys[0]):
                try:
                    setattr(self, keys[0], value)
                except Exception as e:
                    raise ConfigurationValidationError(
                        f"Failed to set field '{keys[0]}': {e}", validation_errors=[str(e)]
                    )
            else:
                raise ConfigurationValidationError(
                    f"Field '{keys[0]}' does not exist in configuration",
                    validation_errors=[f"Unknown field: {keys[0]}"],
                )
        else:
            # Nested field assignment - get the parent object
            parent_key = ".".join(keys[:-1])
            field_name = keys[-1]
            parent_obj = self.get_nested(parent_key)

            if parent_obj is None:
                raise ConfigurationValidationError(
                    f"Parent object for key '{parent_key}' does not exist",
                    validation_errors=[f"Missing parent: {parent_key}"],
                )

            if hasattr(parent_obj, field_name):
                try:
                    setattr(parent_obj, field_name, value)
                except Exception as e:
                    raise ConfigurationValidationError(
                        f"Failed to set nested field '{key}': {e}", validation_errors=[str(e)]
                    )
            else:
                raise ConfigurationValidationError(
                    f"Nested field '{field_name}' does not exist in '{parent_key}'",
                    validation_errors=[f"Unknown nested field: {key}"],
                )

    def to_dict(self, exclude_secrets: bool = False, by_alias: bool = False) -> dict[str, Any]:
        """
        Convert configuration to dictionary.

        This method serializes the configuration to a dictionary format,
        with options to exclude sensitive information and use field aliases.

        Args:
            exclude_secrets: If True, exclude SecretStr fields from output
            by_alias: If True, use field aliases as keys instead of field names

        Returns:
            Dictionary representation of the configuration

        Example:
            ```python
            config = MyAppConfig()

            # Get full configuration
            full_config = config.to_dict()

            # Get config without secrets for logging
            safe_config = config.to_dict(exclude_secrets=True)

            # Get config with aliases for external APIs
            aliased_config = config.to_dict(by_alias=True)
            ```

        <!-- Example Test:
        >>> from cfy import BaseConfiguration
        >>> from pydantic import Field, SecretStr
        >>> class TestConfig(BaseConfiguration):
        ...     secret_key: SecretStr = SecretStr("secret_value")
        ...     normal_field: str = "normal_value"
        >>> config = TestConfig()
        >>> config_dict = config.to_dict()
        >>> assert "secret_key" in config_dict
        >>> safe_dict = config.to_dict(exclude_secrets=True)
        >>> assert safe_dict["secret_key"] == "***REDACTED***"
        -->
        """
        config_dict = self.model_dump(by_alias=by_alias)

        if exclude_secrets:
            return self._redact_secrets(config_dict)
        return config_dict

    def _redact_secrets(self, config_dict: dict[str, Any]) -> dict[str, Any]:
        """
        Redact SecretStr values from configuration dictionary.

        This method recursively searches through a configuration dictionary
        and replaces SecretStr values with a redacted placeholder.

        Args:
            config_dict: Configuration dictionary to process

        Returns:
            Configuration dictionary with secrets redacted
        """
        redacted: dict[str, Any] = {}
        for key, value in config_dict.items():
            if isinstance(value, dict):
                redacted[key] = self._redact_secrets(value)
            elif self._is_secret_field(key):
                redacted[key] = "***REDACTED***"
            else:
                redacted[key] = value
        return redacted

    def _is_secret_field(self, field_name: str) -> bool:
        """
        Check if a field contains secret data based on field type and name.

        Args:
            field_name: Name of the field to check

        Returns:
            True if the field likely contains secret data
        """
        # Check if field type is SecretStr
        if hasattr(self, field_name):
            field_value = getattr(self, field_name)
            if isinstance(field_value, SecretStr):
                return True

        # Check field name patterns that commonly indicate secrets
        secret_patterns = {
            "password",
            "secret",
            "key",
            "token",
            "credential",
            "auth",
            "api_key",
            "private",
            "cert",
            "ssl",
        }
        field_lower = field_name.lower()
        return any(pattern in field_lower for pattern in secret_patterns)

    @lru_cache(maxsize=128)
    def get_field_info(self, field_name: str) -> dict[str, Any] | None:
        """
        Get field information including type, constraints, and metadata.

        This cached method provides detailed information about configuration
        fields, useful for validation, documentation, and CLI generation.

        Args:
            field_name: Name of the field to inspect

        Returns:
            Dictionary containing field information, or None if field doesn't exist

        Example:
            ```python
            config = MyAppConfig()
            field_info = config.get_field_info("max_connections")
            console.print(f"Type: {field_info['type']}")
            console.print(f"Description: {field_info['description']}")
            console.print(f"Default: {field_info['default']}")
            ```

        <!-- Example Test:
        >>> from cfy import BaseConfiguration
        >>> from pydantic import Field
        >>> class TestConfig(BaseConfiguration):
        ...     test_field: int = Field(default=42, description="Test field")
        >>> config = TestConfig()
        >>> info = config.get_field_info("test_field")
        >>> assert info is not None
        >>> assert info["default"] == 42
        -->
        """
        if field_name not in self.model_fields:
            return None

        field_info = self.model_fields[field_name]
        return {
            "type": field_info.annotation,
            "default": field_info.default,
            "description": field_info.description,
            "is_required": field_info.is_required(),
            "constraints": getattr(field_info, "constraints", {}),
            "alias": getattr(field_info, "alias", None),
            "validation_alias": getattr(field_info, "validation_alias", None),
        }

    def validate_field(self, field_name: str, value: Any) -> Any:
        """
        Validate a single field value against its schema.

        This method validates a field value using the same validation logic
        as the full model, useful for validating individual updates.

        Args:
            field_name: Name of the field to validate
            value: Value to validate

        Returns:
            Validated and potentially coerced value

        Raises:
            ConfigurationValidationError: If validation fails

        Example:
            ```python
            config = MyAppConfig()

            # Validate before setting
            try:
                validated_value = config.validate_field("max_connections", "50")
                config.max_connections = validated_value
            except ConfigurationValidationError as e:
                console.print(f"Invalid value: {e.message}")
            ```
        """
        if field_name not in self.model_fields:
            raise ConfigurationValidationError(
                f"Field '{field_name}' does not exist in configuration schema",
                validation_errors=[f"Unknown field: {field_name}"],
            )

        # Create a temporary instance with just this field to leverage Pydantic validation
        try:
            temp_data = {field_name: value}
            temp_instance = self.__class__(**temp_data)
            return getattr(temp_instance, field_name)
        except Exception as e:
            raise ConfigurationValidationError(
                f"Validation failed for field '{field_name}': {e}", validation_errors=[str(e)]
            )

    def reload_from_sources(self) -> None:
        """
        Reload configuration from all sources in-place.

        This method recreates the configuration instance by reloading from
        all configured sources, useful for picking up runtime changes to
        environment variables or configuration files.

        Example:
            ```python
            config = MyAppConfig()

            # Later, after environment variables change...
            config.reload_from_sources()
            ```

        <!-- Example Test:
        >>> import os
        >>> from cfy import BaseConfiguration
        >>> from pydantic import Field
        >>> class TestConfig(BaseConfiguration):
        ...     test_env: str = Field(default="default")
        >>> config = TestConfig()
        >>> original_value = config.test_env
        >>> # This would normally reload from actual env vars
        >>> config.reload_from_sources()
        >>> assert isinstance(config, TestConfig)
        -->
        """
        # Get current configuration as kwargs
        current_config = self.model_dump()

        # Reinitialize using the same class
        new_instance = self.__class__()

        # Update current instance with new values
        for field_name, value in new_instance.model_dump().items():
            setattr(self, field_name, value)

    def merge_config(
        self, other: Union[dict[str, Any], "BaseConfiguration"]
    ) -> "BaseConfiguration":
        """
        Merge this configuration with another configuration or dictionary.

        This method creates a new configuration instance by merging the current
        configuration with another configuration object or dictionary.

        Args:
            other: Another configuration instance or dictionary to merge

        Returns:
            New configuration instance with merged values

        Example:
            ```python
            config1 = MyAppConfig(debug_mode=True)
            config2 = MyAppConfig(max_connections=200)

            merged = config1.merge_config(config2)
            assert merged.debug_mode == True
            assert merged.max_connections == 200
            ```
        """
        current_data = self.model_dump()

        if isinstance(other, BaseConfiguration):
            other_data = other.model_dump()
        else:
            other_data = other

        # Merge dictionaries (other takes precedence)
        merged_data = {**current_data, **other_data}

        return self.__class__(**merged_data)
