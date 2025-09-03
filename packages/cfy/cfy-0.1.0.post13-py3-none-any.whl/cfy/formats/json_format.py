"""
JSON format parser for configuration files.

This module provides JSON parsing capabilities for PyConfig,
handling JSON configuration files with proper error reporting.
"""

import json
from typing import Any

from ..core.exceptions import FileFormatError
from .base import BaseFileFormatParser


class JSONParser(BaseFileFormatParser):
    """
    JSON configuration file parser.

    This parser handles standard JSON configuration files with
    comprehensive error reporting and validation.

    Example:
        ```python
        from cfy.formats import JSONParser

        parser = JSONParser()
        config_data = parser.parse('{"debug": true, "port": 8080}')
        json_content = parser.dump({"key": "value"})
        ```

    <!-- Example Test:
    >>> from cfy.formats.json_format import JSONParser
    >>> parser = JSONParser()
    >>> data = parser.parse('{"test": true, "value": 42}')
    >>> assert data["test"] == True
    >>> assert data["value"] == 42
    >>> json_str = parser.dump({"key": "value"})
    >>> assert "key" in json_str
    >>> assert "value" in json_str
    -->
    """

    def parse(self, content: str) -> dict[str, Any]:
        """
        Parse JSON configuration content.

        Args:
            content: JSON content as string

        Returns:
            Parsed configuration data as dictionary

        Raises:
            FileFormatError: If JSON parsing fails

        Example:
            ```python
            parser = JSONParser()
            config = parser.parse('{"database": {"host": "localhost", "port": 5432}}')
            console.print(f"Database host: {config['database']['host']}")
            ```
        """
        if not content.strip():
            return {}

        try:
            data = json.loads(content)

            # Ensure we return a dictionary
            if not isinstance(data, dict):
                raise FileFormatError(
                    f"JSON configuration must be an object, got {type(data).__name__}",
                    details={"content_type": type(data).__name__, "content": str(data)[:100]},
                )

            return data

        except json.JSONDecodeError as e:
            raise FileFormatError(
                f"Invalid JSON format: {e.msg}",
                line_number=e.lineno,
                parse_error=str(e),
                details={
                    "line": e.lineno,
                    "column": e.colno,
                    "position": e.pos,
                    "error_msg": e.msg,
                },
            ) from e
        except Exception as e:
            raise FileFormatError(f"Unexpected error parsing JSON: {e}", parse_error=str(e)) from e

    def dump(self, data: dict[str, Any]) -> str:
        """
        Dump configuration data to JSON format.

        Args:
            data: Configuration data to serialize

        Returns:
            JSON-formatted configuration string

        Raises:
            FileFormatError: If JSON serialization fails

        Example:
            ```python
            parser = JSONParser()
            config_data = {
                "app": {"name": "MyApp", "version": "1.0.0"},
                "database": {"host": "localhost", "port": 5432}
            }
            json_content = parser.dump(config_data)
            console.print(json_content)
            ```
        """
        try:
            return json.dumps(
                data, indent=2, ensure_ascii=False, separators=(",", ": "), sort_keys=False
            )
        except TypeError as e:
            raise FileFormatError(
                f"Cannot serialize data to JSON: {e}", details={"serialization_error": str(e)}
            ) from e
        except Exception as e:
            raise FileFormatError(
                f"Unexpected error dumping JSON: {e}", details={"dump_error": str(e)}
            ) from e

    @property
    def format_name(self) -> str:
        """Get the format name."""
        return "JSON"

    @property
    def file_extensions(self) -> list[str]:
        """Get supported file extensions."""
        return [".json"]
