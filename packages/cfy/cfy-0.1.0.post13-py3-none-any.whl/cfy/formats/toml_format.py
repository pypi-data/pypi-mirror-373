"""
TOML format parser for configuration files.

This module provides TOML parsing capabilities for PyConfig,
handling TOML configuration files with proper error reporting.
"""

import sys
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

from ..core.exceptions import FileFormatError
from .base import BaseFileFormatParser


class TOMLParser(BaseFileFormatParser):
    """
    TOML configuration file parser.

    This parser handles TOML configuration files with
    comprehensive error reporting and validation. It uses
    the built-in tomllib for Python 3.11+ and falls back
    to tomli/tomli-w for older versions.

    Example:
        ```python
        from cfy.formats import TOMLParser

        parser = TOMLParser()
        config_data = parser.parse('''
        [app]
        name = "MyApp"
        debug = true

        [database]
        host = "localhost"
        port = 5432
        ''')
        toml_content = parser.dump({"key": "value"})
        ```

    <!-- Example Test:
    >>> from cfy.formats.toml_format import TOMLParser
    >>> parser = TOMLParser()
    >>> data = parser.parse('test = true\\nvalue = 42')
    >>> assert data["test"] == True
    >>> assert data["value"] == 42
    >>> toml_str = parser.dump({"key": "value"})
    >>> assert "key" in toml_str
    >>> assert "value" in toml_str
    -->
    """

    def __init__(self) -> None:
        """Initialize TOML parser with version-appropriate libraries."""
        self._tomllib: Any = None
        self._tomli_w: Any = None
        self._import_toml_libraries()

    def _import_toml_libraries(self) -> None:
        """Import TOML libraries with version-specific handling."""
        # For reading TOML files
        # Use built-in tomllib for Python 3.11+
        try:
            import tomllib

            self._tomllib = tomllib
        except ImportError as e:
            raise FileFormatError(
                "tomllib should be available in Python 3.11+, but import failed",
                details={
                    "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
                    "import_error": str(e),
                },
            ) from e

        # For writing TOML files
        try:
            import tomli_w

            self._tomli_w = tomli_w
        except ImportError as e:
            raise FileFormatError(
                "tomli-w is required for TOML writing support. "
                "Install it with: pip install tomli-w",
                details={"missing_dependency": "tomli-w", "import_error": str(e)},
            ) from e

    def parse(self, content: str) -> dict[str, Any]:
        """
        Parse TOML configuration content.

        Args:
            content: TOML content as string

        Returns:
            Parsed configuration data as dictionary

        Raises:
            FileFormatError: If TOML parsing fails

        Example:
            ```python
            parser = TOMLParser()
            toml_content = '''
            [app]
            name = "MyApp"
            debug = true
            version = "1.0.0"

            [database]
            host = "localhost"
            port = 5432
            ssl = false

            [[database.pools]]
            name = "primary"
            max_connections = 100
            '''
            config = parser.parse(toml_content)
            console.print(f"App name: {config['app']['name']}")
            console.print(f"Database pools: {len(config['database']['pools'])}")
            ```
        """
        if not content.strip():
            return {}

        try:
            # Convert string to bytes for tomllib/tomli
            content_bytes = content.encode("utf-8")

            if self._tomllib is None:
                raise FileFormatError("TOML library not available")
            if hasattr(self._tomllib, "loads"):
                # tomllib.loads() expects string
                data = self._tomllib.loads(content)
            else:
                # tomli.load() expects bytes
                data = self._tomllib.load(content_bytes)

            return data

        except Exception as e:
            # Handle different TOML library exceptions
            error_msg = str(e)
            line_number = None

            # Try to extract line number from error message
            if "line" in error_msg.lower():
                try:
                    # Look for patterns like "line 5" in error message
                    import re

                    match = re.search(r"line\s+(\d+)", error_msg, re.IGNORECASE)
                    if match:
                        line_number = int(match.group(1))
                except (ValueError, AttributeError):
                    pass

            raise FileFormatError(
                f"Invalid TOML format: {error_msg}",
                line_number=line_number,
                parse_error=str(e),
                details={"toml_error": str(e)},
            ) from e

    def dump(self, data: dict[str, Any]) -> str:
        """
        Dump configuration data to TOML format.

        Args:
            data: Configuration data to serialize

        Returns:
            TOML-formatted configuration string

        Raises:
            FileFormatError: If TOML serialization fails

        Example:
            ```python
            parser = TOMLParser()
            config_data = {
                "app": {
                    "name": "MyApp",
                    "version": "1.0.0",
                    "debug": False
                },
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "pools": [
                        {"name": "primary", "max_connections": 100},
                        {"name": "secondary", "max_connections": 50}
                    ]
                }
            }
            toml_content = parser.dump(config_data)
            console.print(toml_content)
            ```
        """
        try:
            # Convert to bytes and then back to string
            if self._tomli_w is None:
                raise FileFormatError("TOML writer library not available")
            toml_bytes = self._tomli_w.dumps(data)
            return toml_bytes
        except Exception as e:
            raise FileFormatError(
                f"Cannot serialize data to TOML: {e}", details={"serialization_error": str(e)}
            ) from e

    @property
    def format_name(self) -> str:
        """Get the format name."""
        return "TOML"

    @property
    def file_extensions(self) -> list[str]:
        """Get supported file extensions."""
        return [".toml"]
