"""
CLI parser for automatic command-line option generation.

This module provides automatic CLI generation from Pydantic configuration
schemas with support for nested configurations, type coercion, and help text.
"""

import argparse
import sys
from pathlib import Path
from typing import Any, get_args, get_origin

from pydantic.fields import FieldInfo

from ..core.base import BaseConfiguration
from ..core.exceptions import CLIParsingError


class CLIParser:
    """
    Automatic CLI parser generator for Pydantic configuration models.

    This class analyzes Pydantic models and automatically generates
    command-line argument parsers with proper type handling, help text,
    and nested configuration support.

    Example:
        ```python
        from cfy import CLIParser, BaseConfiguration
        from pydantic import Field

        class AppConfig(BaseConfiguration):
            debug: bool = Field(False, description="Enable debug mode")
            port: int = Field(8080, description="Server port")
            host: str = Field("localhost", description="Server host")

        parser = CLIParser(AppConfig)
        args = parser.parse_args()
        config_overrides = parser.to_config_dict(args)
        ```

    <!-- Example Test:
    >>> from cfy.cli.parser import CLIParser
    >>> from cfy.core.base import BaseConfiguration
    >>> from pydantic import Field
    >>> class TestConfig(BaseConfiguration):
    ...     debug: bool = Field(False, description="Debug mode")
    ...     port: int = Field(8080, description="Port number")
    >>> parser = CLIParser(TestConfig)
    >>> assert isinstance(parser, CLIParser)
    >>> args = parser.parse_args(['--debug', '--port', '9000'])
    >>> config_dict = parser.to_config_dict(args)
    >>> assert config_dict['debug'] is True
    >>> assert config_dict['port'] == 9000
    -->
    """

    def __init__(
        self,
        config_class: type[BaseConfiguration],
        prog: str | None = None,
        description: str | None = None,
        add_config_file: bool = True,
    ) -> None:
        """
        Initialize CLI parser for configuration class.

        Args:
            config_class: Pydantic configuration model class
            prog: Program name for help text
            description: Program description for help text
            add_config_file: Whether to add --config-file option

        Example:
            ```python
            parser = CLIParser(
                AppConfig,
                prog="myapp",
                description="My application server",
                add_config_file=True
            )
            ```
        """
        self.config_class = config_class
        self.parser = argparse.ArgumentParser(
            prog=prog,
            description=description or getattr(config_class, "__doc__", None),
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        # Add standard config file option
        if add_config_file:
            self.parser.add_argument(
                "--config-file", type=Path, help="Path to configuration file (JSON, YAML, or TOML)"
            )

        # Generate arguments from model
        self._generate_arguments()

    def _generate_arguments(self) -> None:
        """Generate command-line arguments from Pydantic model."""
        try:
            # Get model fields
            model_fields = self.config_class.model_fields

            # Process each field
            for field_name, field_info in model_fields.items():
                self._add_field_argument(field_name, field_info)

        except Exception as e:
            raise CLIParsingError(
                f"Failed to generate CLI arguments for {self.config_class.__name__}: {e}",
                details={"config_class": self.config_class.__name__, "generation_error": str(e)},
            ) from e

    def _add_field_argument(self, field_name: str, field_info: FieldInfo) -> None:
        """
        Add command-line argument for a single field.

        Args:
            field_name: Name of the configuration field
            field_info: Pydantic field information
        """
        try:
            # Get field type and default value
            field_type = field_info.annotation
            default_value = field_info.default

            # Skip fields without annotation
            if field_type is None:
                return

            # Create argument name
            arg_name = f"--{field_name.replace('_', '-')}"

            # Get help text from field description
            help_text = field_info.description or f"Set {field_name}"
            if default_value is not None and default_value != ...:
                help_text += f" (default: {default_value})"

            # Handle different field types
            self._add_typed_argument(
                arg_name=arg_name,
                field_name=field_name,
                field_type=field_type,
                default_value=default_value,
                help_text=help_text,
                field_info=field_info,
            )

        except Exception as e:
            raise CLIParsingError(
                f"Failed to add CLI argument for field '{field_name}': {e}",
                details={"field_name": field_name, "field_error": str(e)},
            ) from e

    def _add_typed_argument(
        self,
        arg_name: str,
        field_name: str,
        field_type: Any,
        default_value: Any,
        help_text: str,
        field_info: FieldInfo,
    ) -> None:
        """Add typed command-line argument based on field type."""
        # Handle Union types (including Optional)
        origin_type = get_origin(field_type)
        if origin_type is not None:
            type_args = get_args(field_type)

            # Handle Optional[Type] (Union[Type, None])
            if origin_type is type(None) or (len(type_args) == 2 and type(None) in type_args):
                # Extract the non-None type
                actual_type = next(arg for arg in type_args if arg is not type(None))
                self._add_simple_argument(arg_name, actual_type, default_value, help_text)
                return

            # Handle other Union types - use string as fallback
            if len(type_args) > 1:
                self._add_simple_argument(arg_name, str, default_value, help_text)
                return

            # Handle List types
            if origin_type is list:
                element_type = type_args[0] if type_args else str
                self.parser.add_argument(
                    arg_name,
                    nargs="*",
                    type=element_type,
                    default=default_value if default_value != ... else None,
                    help=help_text,
                )
                return

        # Handle simple types
        self._add_simple_argument(arg_name, field_type, default_value, help_text)

    def _add_simple_argument(
        self, arg_name: str, field_type: type, default_value: Any, help_text: str
    ) -> None:
        """Add simple typed argument."""
        if field_type is bool:
            # Handle boolean flags
            if default_value is True:
                # If default is True, add --no-flag option
                no_flag_name = arg_name.replace("--", "--no-", 1)
                self.parser.add_argument(
                    no_flag_name,
                    action="store_false",
                    dest=arg_name[2:].replace("-", "_"),
                    default=default_value if default_value != ... else None,
                    help=f"Disable {help_text.lower()}",
                )
            else:
                # If default is False, add regular flag
                self.parser.add_argument(
                    arg_name,
                    action="store_true",
                    default=default_value if default_value != ... else None,
                    help=help_text,
                )
        elif field_type is int:
            self.parser.add_argument(
                arg_name,
                type=int,
                default=default_value if default_value != ... else None,
                help=help_text,
            )
        elif field_type is float:
            self.parser.add_argument(
                arg_name,
                type=float,
                default=default_value if default_value != ... else None,
                help=help_text,
            )
        elif field_type is Path:
            self.parser.add_argument(
                arg_name,
                type=Path,
                default=default_value if default_value != ... else None,
                help=help_text,
            )
        else:
            # Default to string type
            self.parser.add_argument(
                arg_name,
                type=str,
                default=default_value if default_value != ... else None,
                help=help_text,
            )

    def parse_args(self, args: list[str] | None = None) -> argparse.Namespace:
        """
        Parse command-line arguments.

        Args:
            args: List of arguments to parse (uses sys.argv if None)

        Returns:
            Parsed arguments namespace

        Raises:
            CLIParsingError: If argument parsing fails

        Example:
            ```python
            parser = CLIParser(AppConfig)

            # Parse from command line
            args = parser.parse_args()

            # Parse specific arguments
            args = parser.parse_args(['--debug', '--port', '9000'])
            ```
        """
        try:
            return self.parser.parse_args(args)
        except SystemExit as e:
            if e.code != 0:  # Only handle error exits, not help exits
                raise CLIParsingError(
                    "Failed to parse command-line arguments",
                    details={"exit_code": e.code, "args": args or sys.argv[1:]},
                ) from e
            raise  # Re-raise help exits
        except Exception as e:
            raise CLIParsingError(
                f"Unexpected error parsing command-line arguments: {e}",
                details={"args": args or sys.argv[1:], "parse_error": str(e)},
            ) from e

    def to_config_dict(self, args: argparse.Namespace) -> dict[str, Any]:
        """
        Convert parsed arguments to configuration dictionary.

        Args:
            args: Parsed arguments from parse_args()

        Returns:
            Configuration dictionary suitable for model creation

        Example:
            ```python
            parser = CLIParser(AppConfig)
            args = parser.parse_args(['--debug', '--port', '9000'])
            config_dict = parser.to_config_dict(args)
            # {'debug': True, 'port': 9000}
            ```
        """
        config_dict = {}

        for key, value in vars(args).items():
            # Skip None values and special keys
            if value is None or key == "config_file":
                continue

            # Convert back to original field name
            field_name = key.replace("-", "_")

            # Only include fields that exist in the model
            if field_name in self.config_class.model_fields:
                config_dict[field_name] = value

        return config_dict

    def get_config_file_path(self, args: argparse.Namespace) -> Path | None:
        """
        Extract configuration file path from parsed arguments.

        Args:
            args: Parsed arguments from parse_args()

        Returns:
            Configuration file path if provided, None otherwise

        Example:
            ```python
            parser = CLIParser(AppConfig)
            args = parser.parse_args(['--config-file', 'app.yaml'])
            config_file = parser.get_config_file_path(args)
            # Path('app.yaml')
            ```
        """
        return getattr(args, "config_file", None)

    def print_help(self) -> None:
        """
        Print help message.

        Example:
            ```python
            parser = CLIParser(AppConfig)
            parser.print_help()
            ```
        """
        self.parser.print_help()

    def generate_help_text(self) -> str:
        """
        Generate help text as string.

        Returns:
            Complete help text for the parser

        Example:
            ```python
            parser = CLIParser(AppConfig)
            help_text = parser.generate_help_text()
            console.print(help_text)
            ```
        """
        return self.parser.format_help()


def create_cli_parser(
    config_class: type[BaseConfiguration], prog: str | None = None, description: str | None = None
) -> CLIParser:
    """
    Factory function to create CLI parser for configuration class.

    Args:
        config_class: Pydantic configuration model class
        prog: Program name for help text
        description: Program description for help text

    Returns:
        Configured CLI parser instance

    Example:
        ```python
        from cfy import create_cli_parser, BaseConfiguration
        from pydantic import Field

        class AppConfig(BaseConfiguration):
            debug: bool = Field(False, description="Enable debug mode")
            port: int = Field(8080, description="Server port")

        parser = create_cli_parser(AppConfig, prog="myapp")
        args = parser.parse_args()
        config_overrides = parser.to_config_dict(args)
        ```

    <!-- Example Test:
    >>> from cfy.cli.parser import create_cli_parser
    >>> from cfy.core.base import BaseConfiguration
    >>> from pydantic import Field
    >>> class TestConfig(BaseConfiguration):
    ...     debug: bool = Field(False, description="Debug mode")
    >>> parser = create_cli_parser(TestConfig, prog="test")
    >>> assert isinstance(parser, CLIParser)
    >>> assert parser.parser.prog == "test"
    -->
    """
    return CLIParser(config_class=config_class, prog=prog, description=description)
