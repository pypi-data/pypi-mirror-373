"""
Configuration loader for hierarchical configuration management.

This module provides the ConfigurationLoader class that orchestrates loading
configuration data from multiple sources and creating validated configuration
instances using user-defined schemas.
"""

import inspect
import sys
import uuid
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError
from rich.console import Console

from .exceptions import (
    ConfigurationLoadError,
    ConfigurationValidationError,
)
from .sources import (
    CLIConfigurationSource,
    ConfigurationSources,
    EnvironmentConfigurationSource,
    FileConfigurationSource,
)

T = TypeVar("T", bound=BaseModel)

console = Console()


def _generate_default_app_name() -> str:
    """
    Generate a sensible default application name.

    This function attempts to derive an application name from:
    1. The main module name (if running as __main__)
    2. The calling script filename
    3. The parent module name
    4. A UUID as fallback

    Returns:
        A string suitable for use as an application name
    """
    # Try to get the main module name
    main_module = sys.modules.get("__main__")
    if main_module and hasattr(main_module, "__file__") and main_module.__file__:
        main_file = Path(main_module.__file__)
        if main_file.name != "__main__.py":
            # Use the script filename without extension
            return main_file.stem

    # Try to get the calling module from the stack
    try:
        # Look up the stack to find the calling module
        frame = inspect.currentframe()
        while frame:
            if frame.f_code.co_filename != __file__:
                caller_file = Path(frame.f_code.co_filename)
                if caller_file.suffix == ".py" and caller_file.name != "__main__.py":
                    return caller_file.stem
            frame = frame.f_back
    except Exception:
        pass  # noqa: S110 - Acceptable to pass here as it's a fallback mechanism
    finally:
        del frame

    # Try package name from sys.modules
    for module_name, module in sys.modules.items():
        if (
            hasattr(module, "__file__")
            and module.__file__
            and not module_name.startswith("_")
            and "." not in module_name
            and module_name not in {"sys", "os", "pathlib", "typing", "pydantic", "rich"}
        ):
            return module_name

    # Fallback to a short UUID
    return f"app_{str(uuid.uuid4())[:8]}"


class ConfigurationLoader:
    """
    Hierarchical configuration loader supporting multiple sources.

    This class orchestrates the loading of configuration data from multiple
    sources (files, environment variables, CLI arguments) and creates validated
    configuration instances according to user-defined schemas.

    The default precedence order is:
    1. CLI Arguments (highest precedence)
    2. Environment Variables
    3. Configuration Files
    4. Default Values (lowest precedence)

    Example:
        ```python
        from cfy import ConfigurationLoader, BaseConfiguration
        from pydantic import Field, SecretStr

        class MyAppConfig(BaseConfiguration):
            database_url: SecretStr = Field(..., description="Database connection string")
            debug_mode: bool = Field(default=False, description="Enable debug logging")

        # Create loader with automatic app name detection
        loader = ConfigurationLoader(
            config_paths=["config.yaml", "config.toml"],
            env_prefix="MYAPP_"
        )

        # Or specify explicit app name (maintains backward compatibility)
        loader = ConfigurationLoader(
            app_name="myapp",
            config_paths=["config.yaml", "config.toml"]
        )

        # Load and validate configuration
        config = loader.load(MyAppConfig)
        ```

    <!-- Example Test:
    >>> from cfy import ConfigurationLoader, BaseConfiguration
    >>> from pydantic import Field
    >>> class TestConfig(BaseConfiguration):
    ...     test_field: str = Field(default="test_value")
    >>> loader = ConfigurationLoader()  # app_name is now optional
    >>> config = loader.load(TestConfig)
    >>> assert config.test_field == "test_value"
    >>> assert isinstance(config, TestConfig)
    >>> # Backward compatibility still works
    >>> loader_with_name = ConfigurationLoader(app_name="test")
    >>> config_with_name = loader_with_name.load(TestConfig)
    >>> assert config_with_name.test_field == "test_value"
    -->
    """

    def __init__(
        self,
        app_name: str | None = None,
        config_paths: list[str | Path] | None = None,
        env_prefix: str | None = None,
        cli_args: list[str] | None = None,
        nested_delimiter: str = "__",
        case_sensitive: bool = False,
        custom_sources: list[Any] | None = None,
    ) -> None:
        """
        Initialize configuration loader.

        Args:
            app_name: Application name for default configuration paths.
                     If not provided, automatically generated from script/module name.
            config_paths: List of configuration file paths to search
            env_prefix: Prefix for environment variables (defaults to APP_NAME_)
            cli_args: CLI arguments to parse (defaults to sys.argv[1:])
            nested_delimiter: Delimiter for nested environment variables
            case_sensitive: Whether environment variables are case sensitive
            custom_sources: Additional custom configuration sources
        """
        self.app_name = app_name or _generate_default_app_name()
        self.config_paths = self._resolve_config_paths(config_paths)
        self.env_prefix = env_prefix or f"{self.app_name.upper()}_"
        self.cli_args = cli_args if cli_args is not None else sys.argv[1:]
        self.nested_delimiter = nested_delimiter
        self.case_sensitive = case_sensitive
        self.custom_sources = custom_sources or []

        # Initialize sources
        self.sources = self._create_sources()

    def _resolve_config_paths(self, config_paths: list[str | Path] | None) -> list[Path]:
        """
        Resolve configuration file paths with defaults.

        Args:
            config_paths: User-provided configuration paths

        Returns:
            List of resolved Path objects to search for configuration files
        """
        if config_paths is not None:
            return [Path(path) for path in config_paths]

        # Default configuration paths
        default_paths = [
            Path(f"/etc/{self.app_name}/config.yaml"),  # System-wide
            Path.home() / f".{self.app_name}/config.yaml",  # User-specific
            Path.home() / f".{self.app_name}/config.toml",
            Path("config.yaml"),  # Project root
            Path("config.toml"),
            Path("config.json"),
            Path(".env"),
        ]

        return default_paths

    def _create_sources(self) -> ConfigurationSources:
        """
        Create default configuration sources in precedence order.

        Returns:
            ConfigurationSources instance with default sources
        """
        sources = ConfigurationSources()

        # 1. Add file sources (lowest precedence)
        for config_path in self.config_paths:
            if config_path.exists():
                sources.add_source(FileConfigurationSource(config_path))

        # 2. Add custom sources
        for custom_source in self.custom_sources:
            sources.add_source(custom_source)

        # 3. Add environment source
        env_source = EnvironmentConfigurationSource(
            prefix=self.env_prefix,
            nested_delimiter=self.nested_delimiter,
            case_sensitive=self.case_sensitive,
        )
        sources.add_source(env_source)

        # 4. Add CLI source (highest precedence)
        cli_source = CLIConfigurationSource(self.cli_args)
        sources.add_source(cli_source)

        return sources

    def load(self, config_class: type[T]) -> T:
        """
        Load and validate configuration from all sources.

        This method loads configuration data from all configured sources,
        merges them according to precedence rules, and creates a validated
        configuration instance.

        Args:
            config_class: Configuration class (must inherit from BaseModel)

        Returns:
            Validated configuration instance of the specified class

        Raises:
            ConfigurationLoadError: If configuration loading fails
            ConfigurationValidationError: If configuration validation fails

        Example:
            ```python
            loader = ConfigurationLoader(app_name="myapp")
            config = loader.load(MyAppConfig)

            # Access configuration values
            console.print(f"Database URL: {config.database_url.get_secret_value()}")
            console.print(f"Debug mode: {config.debug_mode}")
            ```
        """
        try:
            # Load merged configuration data
            config_data = self.sources.load_merged()

            # Create and validate configuration instance
            return config_class(**config_data)

        except ValidationError as e:
            raise ConfigurationValidationError(
                f"Configuration validation failed for {config_class.__name__}",
                validation_errors=[str(error) for error in e.errors()],
                details={"config_class": config_class.__name__, "errors": e.errors()},
            )
        except Exception as e:
            raise ConfigurationLoadError(
                f"Failed to load configuration for {config_class.__name__}: {e}",
                details={"config_class": config_class.__name__, "error": str(e)},
            )

    def load_raw(self) -> dict[str, Any]:
        """
        Load raw configuration data without validation.

        This method returns the merged configuration data as a dictionary
        without creating a validated configuration instance. Useful for
        debugging or when working with dynamic schemas.

        Returns:
            Raw merged configuration dictionary

        Example:
            ```python
            loader = ConfigurationLoader(app_name="myapp")
            raw_config = loader.load_raw()
            console.print(f"Raw config: {raw_config}")
            ```
        """
        return self.sources.load_merged()

    def load_individual_sources(self) -> dict[str, dict[str, Any]]:
        """
        Load configuration data from each source individually.

        This method loads data from each configured source separately,
        useful for debugging configuration precedence or inspecting
        source-specific data.

        Returns:
            Dictionary mapping source names to their configuration data

        Example:
            ```python
            loader = ConfigurationLoader(app_name="myapp")
            individual_configs = loader.load_individual_sources()

            for source_name, source_data in individual_configs.items():
                console.print(f"{source_name}: {source_data}")
            ```
        """
        return self.sources.load_individual()

    def add_source(self, source: Any, precedence: str = "highest") -> None:
        """
        Add a custom configuration source.

        Args:
            source: Configuration source to add
            precedence: Where to add the source ("highest", "lowest", or numeric index)

        Example:
            ```python
            # Add custom source with highest precedence
            loader.add_source(CustomDatabaseSource(), precedence="highest")

            # Add custom source with lowest precedence
            loader.add_source(DefaultsSource(), precedence="lowest")
            ```
        """
        if precedence == "highest":
            self.sources.add_source(source)
        elif precedence == "lowest":
            self.sources.add_source(source, index=0)
        elif isinstance(precedence, int):
            self.sources.add_source(source, index=precedence)
        else:
            raise ValueError(f"Invalid precedence value: {precedence}")

    def remove_source(self, source_name: str) -> bool:
        """
        Remove a configuration source by name.

        Args:
            source_name: Name of the source to remove

        Returns:
            True if source was found and removed, False otherwise

        Example:
            ```python
            # Remove CLI source to ignore command-line arguments
            removed = loader.remove_source("cli")
            if removed:
                console.print("CLI source removed")
            ```
        """
        return self.sources.remove_source(source_name)

    def get_source_names(self) -> list[str]:
        """
        Get names of all configured sources.

        Returns:
            List of source names in precedence order

        Example:
            ```python
            loader = ConfigurationLoader(app_name="myapp")
            source_names = loader.get_source_names()
            console.print(f"Available sources: {source_names}")
            ```
        """
        return [source.name for source in self.sources.sources]

    def validate_config_class(self, config_class: type[BaseModel]) -> bool:
        """
        Validate that a configuration class is compatible with this loader.

        Args:
            config_class: Configuration class to validate

        Returns:
            True if the class is compatible

        Raises:
            ConfigurationValidationError: If the class is not compatible

        Example:
            ```python
            loader = ConfigurationLoader(app_name="myapp")

            # Check if configuration class is valid
            try:
                loader.validate_config_class(MyAppConfig)
                console.print("Configuration class is valid")
            except ConfigurationValidationError as e:
                console.print(f"Invalid configuration class: {e}")
            ```
        """
        if not issubclass(config_class, BaseModel):
            raise ConfigurationValidationError(
                f"Configuration class {config_class.__name__} must inherit from BaseModel",
                validation_errors=["Class does not inherit from BaseModel"],
            )

        # Try to create an instance with empty data to check for required fields
        try:
            config_class()
            return True
        except ValidationError:
            # This is expected if there are required fields without defaults
            return True
        except Exception as e:
            raise ConfigurationValidationError(
                f"Configuration class {config_class.__name__} is not valid: {e}",
                validation_errors=[str(e)],
            )

    def create_instance(self, config_class: type[T], **overrides: Any) -> T:
        """
        Create configuration instance with runtime overrides.

        This method loads the base configuration and applies runtime overrides,
        useful for testing or programmatic configuration modification.

        Args:
            config_class: Configuration class to instantiate
            **overrides: Runtime configuration overrides

        Returns:
            Configuration instance with overrides applied

        Example:
            ```python
            loader = ConfigurationLoader(app_name="myapp")

            # Create config with overrides for testing
            test_config = loader.create_instance(
                MyAppConfig,
                debug_mode=True,
                database_url="sqlite:///test.db"
            )
            ```
        """
        # Load base configuration data
        base_config = self.load_raw()

        # Apply overrides
        final_config = {**base_config, **overrides}

        # Create and return instance
        return config_class(**final_config)

    def reload(self) -> None:
        """
        Reload configuration sources.

        This method recreates all configuration sources, useful for picking
        up changes to configuration files or environment variables at runtime.

        Example:
            ```python
            loader = ConfigurationLoader(app_name="myapp")

            # Later, after configuration files change...
            loader.reload()
            config = loader.load(MyAppConfig)  # Will use updated sources
            ```
        """
        self.sources = self._create_sources()

    def debug_precedence(self, config_class: type[BaseModel] | None = None) -> dict[str, Any]:
        """
        Debug configuration precedence and source resolution.

        This method provides detailed information about how configuration
        values are resolved across sources, useful for troubleshooting
        configuration issues.

        Args:
            config_class: Optional configuration class for field-specific analysis

        Returns:
            Dictionary containing precedence debugging information

        Example:
            ```python
            loader = ConfigurationLoader(app_name="myapp")
            debug_info = loader.debug_precedence(MyAppConfig)

            console.print("Configuration precedence:")
            for field, info in debug_info["fields"].items():
                console.print(f"  {field}: {info['value']} (from {info['source']})")
            ```
        """
        source_names_list: list[str] = self.get_source_names()
        debug_info: dict[str, Any] = {
            "sources": [],
            "precedence_order": source_names_list,
            "merged_config": self.load_raw(),
            "individual_sources": self.load_individual_sources(),
        }

        # Add source information
        for source in self.sources.sources:
            debug_info["sources"].append(
                {
                    "name": source.name,
                    "type": source.source_type,
                    "available": source.is_available(),
                }
            )

        # Add field-specific precedence if config class provided
        if config_class is not None:
            debug_info["fields"] = {}
            individual_configs = self.load_individual_sources()
            merged_config = self.load_raw()

            # Check each field in the config class
            for field_name in list(config_class.model_fields.keys()):
                field_info = {
                    "final_value": merged_config.get(field_name, "NOT_SET"),
                    "source_values": {},
                    "winning_source": None,
                }

                # Check which sources provide this field
                for source_name, source_data in individual_configs.items():
                    if field_name in source_data:
                        field_info["source_values"][source_name] = source_data[field_name]
                        # The last source with this field (highest precedence) wins
                        field_info["winning_source"] = source_name

                if "fields" not in debug_info:
                    debug_info["fields"] = {}
                debug_info["fields"][field_name] = field_info

        return debug_info
