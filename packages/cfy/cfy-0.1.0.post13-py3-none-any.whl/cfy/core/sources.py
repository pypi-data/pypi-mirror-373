"""
Configuration sources for hierarchical configuration loading.

This module defines different sources of configuration data and provides
a unified interface for loading configuration from multiple sources with
proper precedence handling.
"""

import os
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any

from rich.console import Console

from .exceptions import ConfigurationSourceError

console = Console()

if TYPE_CHECKING:
    from ..formats.base import FileFormatManager


class ConfigurationSource(ABC):
    """
    Abstract base class for configuration sources.

    This class defines the interface that all configuration sources must implement.
    Sources can include files, environment variables, CLI arguments, or custom sources.

    Example:
        ```python
        class CustomSource(ConfigurationSource):
            def load_data(self) -> dict[str, Any]:
                # Custom loading logic
                return {"custom_setting": "value"}

            @property
            def name(self) -> str:
                return "custom_source"

            @property
            def source_type(self) -> str:
                return "custom"
        ```
    """

    @abstractmethod
    def load_data(self) -> dict[str, Any]:
        """
        Load configuration data from this source.

        Returns:
            Dictionary containing configuration data

        Raises:
            ConfigurationSourceError: If loading fails
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Get the name of this configuration source.

        Returns:
            Human-readable name for this source
        """
        pass

    @property
    @abstractmethod
    def source_type(self) -> str:
        """
        Get the type of this configuration source.

        Returns:
            Source type identifier (e.g., "file", "environment", "cli")
        """
        pass

    def is_available(self) -> bool:
        """
        Check if this configuration source is available.

        Returns:
            True if the source can provide configuration data
        """
        try:
            self.load_data()
            return True
        except Exception:
            return False


class FileConfigurationSource(ConfigurationSource):
    """
    Configuration source that loads data from files.

    This source can load configuration from various file formats including
    JSON, YAML, TOML, and INI files. It uses the FileFormatManager for parsing.

    Example:
        ```python
        source = FileConfigurationSource(Path("config.yaml"))
        config_data = source.load_data()
        ```
    """

    def __init__(self, file_path: str | Path) -> None:
        """
        Initialize file configuration source.

        Args:
            file_path: Path to the configuration file
        """
        self.file_path = Path(file_path)
        self._format_manager: FileFormatManager | None = None

    @property
    def format_manager(self) -> "FileFormatManager":
        """Lazy-load format manager to avoid circular imports."""
        if self._format_manager is None:
            from ..formats.base import FileFormatManager

            self._format_manager = FileFormatManager()
        return self._format_manager

    def load_data(self) -> dict[str, Any]:
        """
        Load configuration data from file.

        Returns:
            Dictionary containing configuration data from file

        Raises:
            ConfigurationSourceError: If file cannot be read or parsed
        """
        if not self.file_path.exists():
            raise ConfigurationSourceError(
                f"Configuration file does not exist: {self.file_path}",
                source_name=self.name,
                source_type=self.source_type,
            )

        try:
            return self.format_manager.parse_file(self.file_path)
        except Exception as e:
            raise ConfigurationSourceError(
                f"Failed to parse configuration file {self.file_path}: {e}",
                source_name=self.name,
                source_type=self.source_type,
                details={"file_path": str(self.file_path), "error": str(e)},
            )

    @property
    def name(self) -> str:
        """Get the name of this file source."""
        return f"file:{self.file_path.name}"

    @property
    def source_type(self) -> str:
        """Get the source type."""
        return "file"

    def is_available(self) -> bool:
        """Check if file exists and is readable."""
        return self.file_path.exists() and self.file_path.is_file()


class EnvironmentConfigurationSource(ConfigurationSource):
    """
    Configuration source that loads data from environment variables.

    This source can load environment variables with optional prefixes and
    supports nested configurations using delimiter patterns.

    Example:
        ```python
        # Load all environment variables with prefix "MYAPP_"
        source = EnvironmentConfigurationSource(prefix="MYAPP_")
        config_data = source.load_data()

        # With nested delimiter support
        source = EnvironmentConfigurationSource(
            prefix="MYAPP_",
            nested_delimiter="__"
        )
        ```
    """

    def __init__(
        self, prefix: str = "", nested_delimiter: str = "__", case_sensitive: bool = False
    ) -> None:
        """
        Initialize environment configuration source.

        Args:
            prefix: Environment variable prefix to filter by
            nested_delimiter: Delimiter for nested configuration keys
            case_sensitive: Whether environment variable names are case sensitive
        """
        self.prefix = prefix
        self.nested_delimiter = nested_delimiter
        self.case_sensitive = case_sensitive

    def load_data(self) -> dict[str, Any]:
        """
        Load configuration data from environment variables.

        Returns:
            Dictionary containing configuration data from environment
        """
        config_data: dict[str, Any] = {}

        for key, value in os.environ.items():
            # Skip if prefix doesn't match
            if self.prefix and not key.startswith(self.prefix):
                continue

            # Remove prefix from key
            config_key = key[len(self.prefix) :] if self.prefix else key

            # Convert case if not case sensitive
            if not self.case_sensitive:
                config_key = config_key.lower()

            # Handle nested keys
            if self.nested_delimiter in config_key:
                self._set_nested_value(config_data, config_key, value)
            else:
                config_data[config_key] = self._cast_value(value)

        return config_data

    def _set_nested_value(self, config: dict[str, Any], key_path: str, value: str) -> None:
        """
        Set nested configuration value from delimited key path.

        Args:
            config: Configuration dictionary to update
            key_path: Delimited key path
            value: String value to set
        """
        keys = key_path.split(self.nested_delimiter)
        current = config

        # Navigate/create nested structure
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Set final value
        current[keys[-1]] = self._cast_value(value)

    def _cast_value(self, value: str) -> Any:
        """
        Cast string environment variable value to appropriate Python type.

        Args:
            value: String value from environment variable

        Returns:
            Value cast to appropriate type (bool, int, float, list, or str)
        """
        # Handle boolean values
        if value.lower() in ("true", "yes", "1", "on", "enabled"):
            return True
        elif value.lower() in ("false", "no", "0", "off", "disabled"):
            return False

        # Handle numeric values
        if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
            return int(value)

        # Handle float values
        try:
            if "." in value:
                return float(value)
        except ValueError:
            pass

        # Handle list values (comma-separated)
        if "," in value:
            return [item.strip() for item in value.split(",") if item.strip()]

        # Handle JSON-like values
        if value.startswith(("{", "[", '"')) and value.endswith(("}", "]", '"')):
            try:
                import json

                return json.loads(value)
            except (json.JSONDecodeError, ValueError):
                pass

        # Return as string
        return value

    @property
    def name(self) -> str:
        """Get the name of this environment source."""
        return f"environment:{self.prefix}*" if self.prefix else "environment"

    @property
    def source_type(self) -> str:
        """Get the source type."""
        return "environment"


class CLIConfigurationSource(ConfigurationSource):
    """
    Configuration source that loads data from command-line arguments.

    This source parses CLI arguments and converts them into configuration
    data that can override other sources.

    Example:
        ```python
        source = CLIConfigurationSource(sys.argv[1:])
        config_data = source.load_data()
        ```
    """

    def __init__(self, args: list[str] | None = None) -> None:
        """
        Initialize CLI configuration source.

        Args:
            args: List of command-line arguments. If None, uses sys.argv[1:]
        """
        self.args = args if args is not None else sys.argv[1:]
        self._cli_parser = None

    def load_data(self) -> dict[str, Any]:
        """
        Load configuration data from CLI arguments.

        Returns:
            Dictionary containing configuration data from CLI arguments

        Raises:
            ConfigurationSourceError: If CLI parsing fails
        """
        try:
            # Parse CLI arguments into configuration overrides
            config_data = {}

            i = 0
            while i < len(self.args):
                arg = self.args[i]

                # Handle --key=value format
                if "=" in arg and arg.startswith("--"):
                    key, value = arg[2:].split("=", 1)
                    config_data[self._normalize_key(key)] = self._cast_value(value)
                    i += 1

                # Handle --key value format
                elif arg.startswith("--") and i + 1 < len(self.args):
                    key = arg[2:]
                    value = self.args[i + 1]

                    # Skip if next arg is also a flag
                    if not value.startswith("--"):
                        config_data[self._normalize_key(key)] = self._cast_value(value)
                        i += 2
                    else:
                        # Boolean flag without value
                        config_data[self._normalize_key(key)] = True
                        i += 1

                # Handle boolean flags
                elif arg.startswith("--"):
                    key = arg[2:]
                    if key.startswith("no-"):
                        # --no-flag sets flag to False
                        config_data[self._normalize_key(key[3:])] = False
                    else:
                        config_data[self._normalize_key(key)] = True
                    i += 1

                else:
                    # Skip non-flag arguments
                    i += 1

            return config_data

        except Exception as e:
            raise ConfigurationSourceError(
                f"Failed to parse CLI arguments: {e}",
                source_name=self.name,
                source_type=self.source_type,
                details={"args": self.args, "error": str(e)},
            )

    def _normalize_key(self, key: str) -> str:
        """
        Normalize CLI key to configuration key format.

        Args:
            key: CLI argument key (e.g., "database-url")

        Returns:
            Normalized configuration key (e.g., "database_url")
        """
        return key.replace("-", "_").lower()

    def _cast_value(self, value: str) -> Any:
        """Cast CLI argument value to appropriate Python type."""
        # Reuse environment source casting logic
        env_source = EnvironmentConfigurationSource()
        return env_source._cast_value(value)

    @property
    def name(self) -> str:
        """Get the name of this CLI source."""
        return "cli"

    @property
    def source_type(self) -> str:
        """Get the source type."""
        return "cli"


class ConfigurationSources:
    """
    Manager for multiple configuration sources with precedence handling.

    This class manages a collection of configuration sources and provides
    methods to load and merge configuration data according to precedence rules.

    Example:
        ```python
        sources = ConfigurationSources([
            FileConfigurationSource("config.yaml"),
            EnvironmentConfigurationSource(prefix="MYAPP_"),
            CLIConfigurationSource()
        ])

        merged_config = sources.load_merged()
        ```
    """

    def __init__(self, sources: list[ConfigurationSource] | None = None) -> None:
        """
        Initialize configuration sources manager.

        Args:
            sources: List of configuration sources in precedence order (first = lowest precedence)
        """
        self.sources = sources or []

    def add_source(self, source: ConfigurationSource, index: int | None = None) -> None:
        """
        Add a configuration source.

        Args:
            source: Configuration source to add
            index: Position to insert source. If None, appends to end (highest precedence)
        """
        if index is None:
            self.sources.append(source)
        else:
            self.sources.insert(index, source)

    def remove_source(self, source_name: str) -> bool:
        """
        Remove a configuration source by name.

        Args:
            source_name: Name of the source to remove

        Returns:
            True if source was found and removed, False otherwise
        """
        for i, source in enumerate(self.sources):
            if source.name == source_name:
                del self.sources[i]
                return True
        return False

    def load_merged(self, include_unavailable: bool = False) -> dict[str, Any]:
        """
        Load and merge configuration data from all sources.

        Sources are merged in order, with later sources taking precedence
        over earlier ones.

        Args:
            include_unavailable: Whether to attempt loading from unavailable sources

        Returns:
            Merged configuration dictionary
        """
        merged_config: dict[str, Any] = {}

        for source in self.sources:
            if not include_unavailable and not source.is_available():
                continue

            try:
                source_data = source.load_data()
                self._deep_merge(merged_config, source_data)
            except Exception as e:
                # Log warning but continue with other sources
                console.print(f"Warning: Failed to load from {source.name}: {e}")
                continue

        return merged_config

    def load_individual(self) -> dict[str, dict[str, Any]]:
        """
        Load configuration data from each source individually.

        Returns:
            Dictionary mapping source names to their configuration data
        """
        individual_configs = {}

        for source in self.sources:
            if source.is_available():
                try:
                    individual_configs[source.name] = source.load_data()
                except Exception as e:
                    individual_configs[source.name] = {"error": str(e)}

        return individual_configs

    def _deep_merge(self, target: dict[str, Any], source: dict[str, Any]) -> None:
        """
        Deep merge source dictionary into target dictionary.

        Args:
            target: Target dictionary to merge into
            source: Source dictionary to merge from
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value

    def get_source_by_name(self, name: str) -> ConfigurationSource | None:
        """
        Get configuration source by name.

        Args:
            name: Name of the source to find

        Returns:
            Configuration source if found, None otherwise
        """
        for source in self.sources:
            if source.name == name:
                return source
        return None

    def get_sources_by_type(self, source_type: str) -> list[ConfigurationSource]:
        """
        Get all configuration sources of a specific type.

        Args:
            source_type: Type of sources to find

        Returns:
            List of matching configuration sources
        """
        return [source for source in self.sources if source.source_type == source_type]
