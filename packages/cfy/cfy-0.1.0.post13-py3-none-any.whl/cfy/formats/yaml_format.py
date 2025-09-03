"""
YAML format parser for configuration files.

This module provides YAML parsing capabilities for PyConfig,
handling YAML configuration files with proper error reporting.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

from ..core.exceptions import FileFormatError
from .base import BaseFileFormatParser


class YAMLParser(BaseFileFormatParser):
    """
    YAML configuration file parser.

    This parser handles YAML configuration files with
    comprehensive error reporting and validation. It uses
    safe loading to prevent code execution vulnerabilities.

    Example:
        ```python
        from cfy.formats import YAMLParser

        parser = YAMLParser()
        config_data = parser.parse('''
        debug: true
        database:
          host: localhost
          port: 5432
        ''')
        yaml_content = parser.dump({"key": "value"})
        ```

    <!-- Example Test:
    >>> from cfy.formats.yaml_format import YAMLParser
    >>> parser = YAMLParser()
    >>> data = parser.parse('test: true\\nvalue: 42')
    >>> assert data["test"] == True
    >>> assert data["value"] == 42
    >>> yaml_str = parser.dump({"key": "value"})
    >>> assert "key:" in yaml_str
    >>> assert "value" in yaml_str
    -->
    """

    def __init__(self) -> None:
        """Initialize YAML parser with optional PyYAML dependency."""
        self._yaml: Any = None
        self._import_yaml()

    def _import_yaml(self) -> None:
        """Import YAML library with helpful error message if not available."""
        try:
            import yaml

            self._yaml = yaml
        except ImportError as e:
            raise FileFormatError(
                "PyYAML is required for YAML configuration support. "
                "Install it with: pip install pyyaml",
                details={"missing_dependency": "PyYAML", "import_error": str(e)},
            ) from e

    def parse(self, content: str) -> dict[str, Any]:
        """
        Parse YAML configuration content.

        Args:
            content: YAML content as string

        Returns:
            Parsed configuration data as dictionary

        Raises:
            FileFormatError: If YAML parsing fails

        Example:
            ```python
            parser = YAMLParser()
            yaml_content = '''
            app:
              name: MyApp
              debug: true
            database:
              host: localhost
              port: 5432
            '''
            config = parser.parse(yaml_content)
            console.print(f"App name: {config['app']['name']}")
            ```
        """
        if not content.strip():
            return {}

        try:
            # Use safe_load to prevent code execution
            if self._yaml is None:
                raise FileFormatError("YAML library not available")
            data = self._yaml.safe_load(content)

            # Handle None result (empty YAML)
            if data is None:
                return {}

            # Ensure we return a dictionary
            if not isinstance(data, dict):
                raise FileFormatError(
                    f"YAML configuration must be a mapping, got {type(data).__name__}",
                    details={"content_type": type(data).__name__, "content": str(data)[:100]},
                )

            return data

        except Exception as e:
            # Handle YAML-specific errors
            if (
                self._yaml is not None
                and hasattr(self._yaml, "YAMLError")
                and isinstance(e, self._yaml.YAMLError)
            ):
                error_msg = str(e)
                line_number = None

                # Extract line number if available
                if hasattr(e, "problem_mark") and e.problem_mark is not None:
                    line_number = e.problem_mark.line + 1  # YAML uses 0-based line numbers
                    error_msg = f"{error_msg} at line {line_number}"

                raise FileFormatError(
                    f"Invalid YAML format: {error_msg}",
                    line_number=line_number,
                    parse_error=str(e),
                    details={"yaml_error": str(e)},
                ) from e
            # Re-raise other exceptions
            raise FileFormatError(f"Unexpected error parsing YAML: {e}", parse_error=str(e)) from e

    def dump(self, data: dict[str, Any]) -> str:
        """
        Dump configuration data to YAML format.

        Args:
            data: Configuration data to serialize

        Returns:
            YAML-formatted configuration string

        Raises:
            FileFormatError: If YAML serialization fails

        Example:
            ```python
            parser = YAMLParser()
            config_data = {
                "app": {"name": "MyApp", "version": "1.0.0"},
                "database": {"host": "localhost", "port": 5432},
                "features": ["auth", "logging", "monitoring"]
            }
            yaml_content = parser.dump(config_data)
            console.print(yaml_content)
            ```
        """
        try:
            if self._yaml is None:
                raise FileFormatError("YAML library not available")
            return self._yaml.safe_dump(
                data,
                default_flow_style=False,
                indent=2,
                width=120,
                allow_unicode=True,
                encoding=None,  # Return string, not bytes
                sort_keys=False,
            )
        except Exception as e:
            raise FileFormatError(
                f"Cannot serialize data to YAML: {e}", details={"serialization_error": str(e)}
            ) from e

    @property
    def format_name(self) -> str:
        """Get the format name."""
        return "YAML"

    @property
    def file_extensions(self) -> list[str]:
        """Get supported file extensions."""
        return [".yaml", ".yml"]
