"""
Configuration interpolation and templating utilities for PyConfig.

This module provides variable substitution, template processing, and dynamic
value resolution for configuration files and values.
"""

import os
import re
from collections.abc import Callable
from functools import lru_cache
from pathlib import Path
from typing import Any

from ..core.exceptions import PyConfigError


class InterpolationError(PyConfigError):
    """
    Raised when interpolation processing fails.

    This error occurs when variable substitution, template processing, or
    dynamic value resolution encounters issues such as circular references,
    missing variables, or invalid syntax.

    Example:
        ```python
        try:
            interpolator = ConfigInterpolator()
            result = interpolator.interpolate("${MISSING_VAR}")
        except InterpolationError as e:
            console.print(f"Interpolation failed: {e.message}")
        ```
    """

    def __init__(
        self,
        message: str,
        variable_name: str | None = None,
        template_content: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize interpolation error.

        Args:
            message: Human-readable error message
            variable_name: Name of the variable that caused the error
            template_content: Template content that failed processing
            details: Additional error context
        """
        super().__init__(message, details)
        self.variable_name = variable_name
        self.template_content = template_content


class ConfigInterpolator:
    """
    Configuration value interpolator with multiple substitution patterns.

    This class provides variable substitution and template processing for
    configuration values, supporting environment variables, cross-references,
    and custom variable sources.

    Supported patterns:
    - ${VAR} - Environment variable substitution
    - ${env:VAR} - Explicit environment variable
    - ${config:path.to.value} - Cross-reference to other config values
    - ${file:/path/to/file} - File content substitution
    - ${default:VAR:fallback} - Environment variable with default

    Example:
        ```python
        from cfy.utils import ConfigInterpolator

        interpolator = ConfigInterpolator()

        # Environment variable substitution
        result = interpolator.interpolate("Database: ${DATABASE_URL}")

        # With fallback values
        result = interpolator.interpolate("Port: ${default:PORT:8080}")

        # Cross-reference other config values
        config_data = {"database": {"host": "localhost"}}
        result = interpolator.interpolate(
            "URL: http://${config:database.host}:5432",
            config_context=config_data
        )
        ```

    <!-- Example Test:
    >>> import os
    >>> from cfy.utils.interpolation import ConfigInterpolator
    >>> os.environ['TEST_VAR'] = 'test_value'
    >>> interpolator = ConfigInterpolator()
    >>> result = interpolator.interpolate('Value: ${TEST_VAR}')
    >>> assert result == 'Value: test_value'
    >>> del os.environ['TEST_VAR']
    -->
    """

    # Pattern for variable substitution: ${type:name} or ${name}
    INTERPOLATION_PATTERN = re.compile(r"\$\{([a-zA-Z_][a-zA-Z0-9_]*(?::[^}]+)?)\}", re.MULTILINE)

    # Patterns for different substitution types
    ENV_PATTERN = re.compile(r"^(?:env:)?([A-Z_][A-Z0-9_]*)$")
    CONFIG_PATTERN = re.compile(r"^config:([a-zA-Z_][a-zA-Z0-9_.]*)")
    FILE_PATTERN = re.compile(r"^file:(.+)$")
    DEFAULT_PATTERN = re.compile(r"^default:([A-Z_][A-Z0-9_]*):(.*)$")

    def __init__(
        self, max_recursion_depth: int = 10, strict_mode: bool = True, cache_enabled: bool = True
    ) -> None:
        """
        Initialize configuration interpolator.

        Args:
            max_recursion_depth: Maximum depth for recursive interpolation
            strict_mode: Whether to raise errors for missing variables
            cache_enabled: Whether to cache interpolation results

        Example:
            ```python
            # Strict mode (raises errors for missing variables)
            interpolator = ConfigInterpolator(strict_mode=True)

            # Permissive mode (leaves unresolved variables as-is)
            interpolator = ConfigInterpolator(strict_mode=False)
            ```
        """
        self.max_recursion_depth = max_recursion_depth
        self.strict_mode = strict_mode
        self.cache_enabled = cache_enabled
        self._cache: dict[str, str] = {}
        self._custom_resolvers: dict[str, Callable[[str], str]] = {}

    def add_custom_resolver(self, prefix: str, resolver_func: Callable[[str], str]) -> None:
        """
        Add custom variable resolver function.

        Args:
            prefix: Prefix for this resolver (e.g., 'vault', 'aws')
            resolver_func: Function that takes variable name and returns value

        Example:
            ```python
            def vault_resolver(var_name: str) -> str:
                # Resolve from Vault
                return vault_client.get_secret(var_name)

            interpolator = ConfigInterpolator()
            interpolator.add_custom_resolver('vault', vault_resolver)

            # Now you can use: ${vault:secret-name}
            result = interpolator.interpolate("Secret: ${vault:api-key}")
            ```
        """
        self._custom_resolvers[prefix] = resolver_func

    def interpolate(
        self,
        value: str | dict | list | Any,
        config_context: dict[str, Any] | None = None,
        env_context: dict[str, str] | None = None,
        _recursion_depth: int = 0,
    ) -> Any:
        """
        Interpolate variables in configuration value.

        Args:
            value: Value to interpolate (string, dict, list, or other)
            config_context: Configuration data for cross-references
            env_context: Environment variables (defaults to os.environ)
            _recursion_depth: Internal recursion tracking

        Returns:
            Interpolated value with variables resolved

        Raises:
            InterpolationError: If interpolation fails or max recursion exceeded

        Example:
            ```python
            interpolator = ConfigInterpolator()

            # String interpolation
            result = interpolator.interpolate("Host: ${HOST}")

            # Dict interpolation
            config = {
                "database": {
                    "url": "postgres://${DB_USER}:${DB_PASS}@${DB_HOST}/mydb"
                }
            }
            result = interpolator.interpolate(config)

            # List interpolation
            servers = ["${SERVER1}", "${SERVER2}"]
            result = interpolator.interpolate(servers)
            ```
        """
        # Handle different value types
        if isinstance(value, str):
            return self._interpolate_string(value, config_context, env_context, _recursion_depth)
        elif isinstance(value, dict):
            return self._interpolate_dict(value, config_context, env_context, _recursion_depth)
        elif isinstance(value, list):
            return self._interpolate_list(value, config_context, env_context, _recursion_depth)
        else:
            # Return non-string values as-is
            return value

    def _interpolate_string(
        self,
        value: str,
        config_context: dict[str, Any] | None,
        env_context: dict[str, str] | None,
        recursion_depth: int,
    ) -> str:
        """Interpolate variables in string value."""
        # Check recursion depth before processing
        if recursion_depth > self.max_recursion_depth:
            raise InterpolationError(
                f"Maximum recursion depth ({self.max_recursion_depth}) exceeded during interpolation",
                details={"recursion_depth": recursion_depth, "value": str(value)[:100]},
            )

        if self.cache_enabled and value in self._cache:
            return self._cache[value]

        env_context = env_context or dict(os.environ)
        result = value

        # Find all variable references
        matches = list(self.INTERPOLATION_PATTERN.finditer(value))

        # Process matches in reverse order to avoid position shifts
        for match in reversed(matches):
            var_spec = match.group(1)
            start, end = match.span()

            try:
                resolved_value = self._resolve_variable(var_spec, config_context, env_context)

                # Replace the variable reference
                result = result[:start] + str(resolved_value) + result[end:]

            except InterpolationError:
                if self.strict_mode:
                    raise
                # In non-strict mode, leave unresolved variables as-is
                continue

        # Recursively interpolate the result if it contains more variables
        if self.INTERPOLATION_PATTERN.search(result) and result != value:
            result = self._interpolate_string(
                result, config_context, env_context, recursion_depth + 1
            )

        if self.cache_enabled:
            self._cache[value] = result

        return result

    def _interpolate_dict(
        self,
        value: dict[str, Any],
        config_context: dict[str, Any] | None,
        env_context: dict[str, str] | None,
        recursion_depth: int,
    ) -> dict[str, Any]:
        """Interpolate variables in dictionary values."""
        result = {}
        for key, val in value.items():
            result[key] = self.interpolate(val, config_context, env_context, recursion_depth + 1)
        return result

    def _interpolate_list(
        self,
        value: list[Any],
        config_context: dict[str, Any] | None,
        env_context: dict[str, str] | None,
        recursion_depth: int,
    ) -> list[Any]:
        """Interpolate variables in list items."""
        result = []
        for item in value:
            result.append(self.interpolate(item, config_context, env_context, recursion_depth + 1))
        return result

    def _resolve_variable(
        self, var_spec: str, config_context: dict[str, Any] | None, env_context: dict[str, str]
    ) -> str:
        """
        Resolve a single variable specification.

        Args:
            var_spec: Variable specification (e.g., 'env:VAR', 'config:path')
            config_context: Configuration data for cross-references
            env_context: Environment variables

        Returns:
            Resolved variable value

        Raises:
            InterpolationError: If variable cannot be resolved
        """
        # Check custom resolvers first
        for prefix, resolver in self._custom_resolvers.items():
            if var_spec.startswith(f"{prefix}:"):
                var_name = var_spec[len(prefix) + 1 :]
                try:
                    if callable(resolver):
                        return resolver(var_name)
                    raise InterpolationError(
                        f"Resolver for '{prefix}' is not callable",
                        variable_name=var_name,
                        details={"resolver": prefix, "error": "not callable"},
                    )
                except Exception as e:
                    raise InterpolationError(
                        f"Custom resolver '{prefix}' failed for variable '{var_name}': {e}",
                        variable_name=var_name,
                        details={"resolver": prefix, "error": str(e)},
                    ) from e

        # Environment variable with default
        default_match = self.DEFAULT_PATTERN.match(var_spec)
        if default_match:
            env_var, default_value = default_match.groups()
            return env_context.get(env_var, default_value)

        # Environment variable
        env_match = self.ENV_PATTERN.match(var_spec)
        if env_match:
            env_var = env_match.group(1)
            if env_var in env_context:
                return env_context[env_var]

            if self.strict_mode:
                raise InterpolationError(
                    f"Environment variable '{env_var}' not found",
                    variable_name=env_var,
                    details={"variable_type": "environment"},
                )
            return f"${{{var_spec}}}"

        # Configuration cross-reference
        config_match = self.CONFIG_PATTERN.match(var_spec)
        if config_match:
            config_path = config_match.group(1)

            if config_context is None:
                if self.strict_mode:
                    raise InterpolationError(
                        f"No configuration context provided for '{config_path}'",
                        variable_name=config_path,
                        details={"variable_type": "config"},
                    )
                return f"${{{var_spec}}}"

            try:
                return self._get_nested_value(config_context, config_path)
            except KeyError:
                if self.strict_mode:
                    raise InterpolationError(
                        f"Configuration path '{config_path}' not found",
                        variable_name=config_path,
                        details={
                            "variable_type": "config",
                            "available_keys": list(config_context.keys()),
                        },
                    )
                return f"${{{var_spec}}}"

        # File content
        file_match = self.FILE_PATTERN.match(var_spec)
        if file_match:
            file_path = file_match.group(1)
            return self._read_file_content(file_path)

        # Default to environment variable lookup
        if var_spec in env_context:
            return env_context[var_spec]

        if self.strict_mode:
            raise InterpolationError(
                f"Cannot resolve variable '{var_spec}'",
                variable_name=var_spec,
                details={"variable_spec": var_spec},
            )

        return f"${{{var_spec}}}"

    def _get_nested_value(self, data: dict[str, Any], path: str) -> Any:
        """
        Get nested value from dictionary using dot notation.

        Args:
            data: Dictionary to search
            path: Dot-separated path (e.g., 'database.host')

        Returns:
            Value at the specified path

        Raises:
            KeyError: If path is not found
        """
        keys = path.split(".")
        current = data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                raise KeyError(f"Path '{path}' not found")

        return current

    def _read_file_content(self, file_path: str) -> str:
        """
        Read content from file.

        Args:
            file_path: Path to file to read

        Returns:
            File content as string

        Raises:
            InterpolationError: If file cannot be read
        """
        try:
            path = Path(file_path).expanduser().resolve()
            return path.read_text(encoding="utf-8").strip()
        except Exception as e:
            raise InterpolationError(
                f"Cannot read file '{file_path}': {e}",
                details={"file_path": file_path, "read_error": str(e)},
            ) from e

    def clear_cache(self) -> None:
        """
        Clear interpolation cache.

        Example:
            ```python
            interpolator = ConfigInterpolator()
            interpolator.clear_cache()
            ```
        """
        self._cache.clear()

    def validate_template(self, template: str) -> list[str]:
        """
        Validate template and return list of variables.

        Args:
            template: Template string to validate

        Returns:
            List of variable names found in template

        Example:
            ```python
            interpolator = ConfigInterpolator()
            variables = interpolator.validate_template("Host: ${HOST}, Port: ${PORT}")
            # Returns: ['HOST', 'PORT']
            ```
        """
        matches = self.INTERPOLATION_PATTERN.findall(template)
        variables = []

        for var_spec in matches:
            # Extract variable name based on type
            if ":" in var_spec:
                prefix, name = var_spec.split(":", 1)
                if prefix in ["env", "config", "file"]:
                    variables.append(name)
                elif prefix == "default":
                    # For default patterns, extract the variable name
                    default_match = self.DEFAULT_PATTERN.match(var_spec)
                    if default_match:
                        variables.append(default_match.group(1))
            else:
                variables.append(var_spec)

        return list(set(variables))  # Remove duplicates


# Convenience functions


@lru_cache(maxsize=128)
def interpolate_string(
    value: str, env_context: dict[str, str] | None = None, strict_mode: bool = True
) -> str:
    """
    Convenience function to interpolate a single string value.

    Args:
        value: String value to interpolate
        env_context: Environment variables (defaults to os.environ)
        strict_mode: Whether to raise errors for missing variables

    Returns:
        Interpolated string

    Example:
        ```python
        from cfy.utils import interpolate_string

        result = interpolate_string("Database: ${DATABASE_URL}")
        console.print(result)
        ```

    <!-- Example Test:
    >>> import os
    >>> from cfy.utils.interpolation import interpolate_string
    >>> os.environ['TEST_HOST'] = 'localhost'
    >>> result = interpolate_string('Server: ${TEST_HOST}')
    >>> assert result == 'Server: localhost'
    >>> del os.environ['TEST_HOST']
    -->
    """
    interpolator = ConfigInterpolator(strict_mode=strict_mode)
    return interpolator.interpolate(value, env_context=env_context)


def interpolate_config(
    config_data: dict[str, Any], env_context: dict[str, str] | None = None, strict_mode: bool = True
) -> dict[str, Any]:
    """
    Convenience function to interpolate entire configuration dictionary.

    Args:
        config_data: Configuration dictionary to interpolate
        env_context: Environment variables (defaults to os.environ)
        strict_mode: Whether to raise errors for missing variables

    Returns:
        Interpolated configuration dictionary

    Example:
        ```python
        from cfy.utils import interpolate_config

        config = {
            "database": {
                "url": "postgres://${DB_USER}:${DB_PASS}@${DB_HOST}/mydb"
            },
            "redis": {
                "url": "redis://${REDIS_HOST}:${default:REDIS_PORT:6379}"
            }
        }

        interpolated = interpolate_config(config)
        ```

    <!-- Example Test:
    >>> import os
    >>> from cfy.utils.interpolation import interpolate_config
    >>> os.environ.update({'DB_HOST': 'localhost', 'DB_PORT': '5432'})
    >>> config = {'database': {'host': '${DB_HOST}', 'port': '${DB_PORT}'}}
    >>> result = interpolate_config(config)
    >>> assert result['database']['host'] == 'localhost'
    >>> assert result['database']['port'] == '5432'
    >>> del os.environ['DB_HOST']
    >>> del os.environ['DB_PORT']
    -->
    """
    interpolator = ConfigInterpolator(strict_mode=strict_mode)
    return interpolator.interpolate(
        config_data, config_context=config_data, env_context=env_context
    )


def create_template_processor(
    template_dir: str | Path, file_extension: str = ".template"
) -> Callable[[str], str]:
    """
    Create a template processor function for processing template files.

    Args:
        template_dir: Directory containing template files
        file_extension: Extension for template files

    Returns:
        Template processor function

    Example:
        ```python
        from cfy.utils import create_template_processor

        # Create processor for templates in ./templates/
        process_template = create_template_processor("./templates")

        # Process template file
        config = process_template("database.yaml.template")
        ```
    """
    template_path = Path(template_dir)
    interpolator = ConfigInterpolator()

    def process_template(template_name: str) -> str:
        """Process template file and return interpolated content."""
        if not template_name.endswith(file_extension):
            template_name += file_extension

        template_file = template_path / template_name

        if not template_file.exists():
            raise InterpolationError(
                f"Template file '{template_file}' not found",
                template_content=template_name,
                details={"template_dir": str(template_path), "template_name": template_name},
            )

        try:
            template_content = template_file.read_text(encoding="utf-8")
            return interpolator.interpolate(template_content)
        except Exception as e:
            raise InterpolationError(
                f"Failed to process template '{template_name}': {e}",
                template_content=template_name,
                details={"template_file": str(template_file), "error": str(e)},
            ) from e

    return process_template
