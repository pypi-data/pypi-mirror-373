"""
Base file format parser interfaces and manager.

This module defines the abstract interface for file format parsers and
provides a unified manager for parsing configuration files in different formats.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Protocol

from ..core.exceptions import FileFormatError


class FileFormatParser(Protocol):
    """
    Protocol for configuration file format parsers.

    This protocol defines the interface that all file format parsers must
    implement for parsing and dumping configuration data.
    """

    def parse(self, content: str) -> dict[str, Any]:
        """
        Parse configuration content from string.

        Args:
            content: Configuration file content as string

        Returns:
            Parsed configuration data as dictionary

        Raises:
            FileFormatError: If parsing fails
        """
        ...

    def dump(self, data: dict[str, Any]) -> str:
        """
        Dump configuration data to string format.

        Args:
            data: Configuration data to dump

        Returns:
            Configuration data serialized as string

        Raises:
            FileFormatError: If dumping fails
        """
        ...


class BaseFileFormatParser(ABC):
    """
    Abstract base class for file format parsers.

    This class provides a common base for all concrete file format parser
    implementations, ensuring consistent error handling and interface.
    """

    @abstractmethod
    def parse(self, content: str) -> dict[str, Any]:
        """
        Parse configuration content from string.

        Args:
            content: Configuration file content as string

        Returns:
            Parsed configuration data as dictionary

        Raises:
            FileFormatError: If parsing fails
        """
        pass

    @abstractmethod
    def dump(self, data: dict[str, Any]) -> str:
        """
        Dump configuration data to string format.

        Args:
            data: Configuration data to dump

        Returns:
            Configuration data serialized as string

        Raises:
            FileFormatError: If dumping fails
        """
        pass

    @property
    @abstractmethod
    def format_name(self) -> str:
        """
        Get the name of this format.

        Returns:
            Format name (e.g., "JSON", "YAML", "TOML")
        """
        pass

    @property
    @abstractmethod
    def file_extensions(self) -> list[str]:
        """
        Get supported file extensions for this format.

        Returns:
            List of supported file extensions (including the dot)
        """
        pass


class FileFormatManager:
    """
    Manager for multiple file format parsers.

    This class provides a unified interface for parsing configuration files
    in various formats. It automatically detects the format based on file
    extensions and delegates to the appropriate parser.

    Example:
        ```python
        from cfy import FileFormatManager
        from pathlib import Path

        manager = FileFormatManager()

        # Parse different formats automatically
        yaml_config = manager.parse_file(Path("config.yaml"))
        toml_config = manager.parse_file(Path("config.toml"))
        json_config = manager.parse_file(Path("config.json"))

        # Write configuration to file
        manager.write_file(config_data, Path("output.yaml"))
        ```

    <!-- Example Test:
    >>> from cfy.formats.base import FileFormatManager
    >>> manager = FileFormatManager()
    >>> assert isinstance(manager, FileFormatManager)
    >>> extensions = manager.get_supported_extensions()
    >>> assert ".json" in extensions
    >>> assert ".yaml" in extensions
    -->
    """

    def __init__(self) -> None:
        """Initialize file format manager with default parsers."""
        self.parsers: dict[str, BaseFileFormatParser] = {}
        self._register_default_parsers()

    def _register_default_parsers(self) -> None:
        """Register default file format parsers."""
        # Import parsers here to avoid circular imports
        from .json_format import JSONParser
        from .toml_format import TOMLParser
        from .yaml_format import YAMLParser

        # Register parsers for their supported extensions
        self.register_parser(JSONParser())
        self.register_parser(YAMLParser())
        self.register_parser(TOMLParser())

    def register_parser(self, parser: BaseFileFormatParser) -> None:
        """
        Register a file format parser.

        Args:
            parser: Parser instance to register

        Example:
            ```python
            manager = FileFormatManager()
            custom_parser = CustomFormatParser()
            manager.register_parser(custom_parser)
            ```
        """
        for extension in parser.file_extensions:
            self.parsers[extension.lower()] = parser

    def unregister_parser(self, extension: str) -> bool:
        """
        Unregister a file format parser by extension.

        Args:
            extension: File extension to unregister (with or without dot)

        Returns:
            True if parser was found and removed, False otherwise

        Example:
            ```python
            manager = FileFormatManager()
            removed = manager.unregister_parser(".yaml")
            if removed:
                console.print("YAML parser removed")
            ```
        """
        ext = extension if extension.startswith(".") else f".{extension}"
        if ext.lower() in self.parsers:
            del self.parsers[ext.lower()]
            return True
        return False

    def get_parser(self, file_path: Path) -> BaseFileFormatParser:
        """
        Get appropriate parser for a file based on its extension.

        Args:
            file_path: Path to the file

        Returns:
            Parser instance for the file format

        Raises:
            FileFormatError: If no parser is available for the file extension

        Example:
            ```python
            manager = FileFormatManager()
            parser = manager.get_parser(Path("config.yaml"))
            assert parser.format_name == "YAML"
            ```
        """
        extension = file_path.suffix.lower()
        if extension not in self.parsers:
            raise FileFormatError(
                f"No parser available for file extension: {extension}",
                file_path=str(file_path),
                details={"extension": extension, "available": list(self.parsers.keys())},
            )
        return self.parsers[extension]

    def parse_file(self, file_path: Path) -> dict[str, Any]:
        """
        Parse configuration file automatically detecting format.

        Args:
            file_path: Path to configuration file

        Returns:
            Parsed configuration data

        Raises:
            FileFormatError: If file cannot be read or parsed

        Example:
            ```python
            manager = FileFormatManager()
            config = manager.parse_file(Path("config.yaml"))
            console.print(f"Loaded config: {config}")
            ```
        """
        if not file_path.exists():
            raise FileFormatError(
                f"Configuration file does not exist: {file_path}", file_path=str(file_path)
            )

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            raise FileFormatError(
                f"Failed to read file {file_path}: {e}",
                file_path=str(file_path),
                details={"read_error": str(e)},
            )

        parser = self.get_parser(file_path)
        return parser.parse(content)

    def parse_content(self, content: str, format_name: str) -> dict[str, Any]:
        """
        Parse configuration content with explicit format specification.

        Args:
            content: Configuration content as string
            format_name: Format name (e.g., "json", "yaml", "toml")

        Returns:
            Parsed configuration data

        Raises:
            FileFormatError: If format is not supported or parsing fails

        Example:
            ```python
            manager = FileFormatManager()
            yaml_content = "debug: true\nport: 8080"
            config = manager.parse_content(yaml_content, "yaml")
            ```
        """
        # Find parser by format name
        parser = None
        for registered_parser in set(self.parsers.values()):
            if registered_parser.format_name.lower() == format_name.lower():
                parser = registered_parser
                break

        if parser is None:
            available_formats = [p.format_name for p in set(self.parsers.values())]
            raise FileFormatError(
                f"No parser available for format: {format_name}",
                details={"format": format_name, "available": available_formats},
            )

        return parser.parse(content)

    def write_file(self, data: dict[str, Any], file_path: Path) -> None:
        """
        Write configuration data to file with format detection.

        Args:
            data: Configuration data to write
            file_path: Target file path (format determined by extension)

        Raises:
            FileFormatError: If format is not supported or writing fails

        Example:
            ```python
            manager = FileFormatManager()
            config_data = {"debug": True, "port": 8080}
            manager.write_file(config_data, Path("output.yaml"))
            ```
        """
        parser = self.get_parser(file_path)

        try:
            content = parser.dump(data)

            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write content to file
            file_path.write_text(content, encoding="utf-8")

        except Exception as e:
            raise FileFormatError(
                f"Failed to write file {file_path}: {e}",
                file_path=str(file_path),
                details={"write_error": str(e)},
            )

    def dump_content(self, data: dict[str, Any], format_name: str) -> str:
        """
        Dump configuration data to string with explicit format specification.

        Args:
            data: Configuration data to dump
            format_name: Target format name (e.g., "json", "yaml", "toml")

        Returns:
            Configuration data serialized as string

        Raises:
            FileFormatError: If format is not supported or dumping fails

        Example:
            ```python
            manager = FileFormatManager()
            config_data = {"debug": True, "port": 8080}
            yaml_content = manager.dump_content(config_data, "yaml")
            console.print(yaml_content)
            ```
        """
        # Find parser by format name
        parser = None
        for registered_parser in set(self.parsers.values()):
            if registered_parser.format_name.lower() == format_name.lower():
                parser = registered_parser
                break

        if parser is None:
            available_formats = [p.format_name for p in set(self.parsers.values())]
            raise FileFormatError(
                f"No parser available for format: {format_name}",
                details={"format": format_name, "available": available_formats},
            )

        return parser.dump(data)

    def get_supported_extensions(self) -> list[str]:
        """
        Get list of all supported file extensions.

        Returns:
            List of supported file extensions

        Example:
            ```python
            manager = FileFormatManager()
            extensions = manager.get_supported_extensions()
            console.print(f"Supported formats: {extensions}")
            ```
        """
        return list(self.parsers.keys())

    def get_supported_formats(self) -> list[str]:
        """
        Get list of all supported format names.

        Returns:
            List of supported format names

        Example:
            ```python
            manager = FileFormatManager()
            formats = manager.get_supported_formats()
            console.print(f"Supported formats: {formats}")
            ```
        """
        return list({parser.format_name for parser in self.parsers.values()})

    def is_supported(self, file_path: Path) -> bool:
        """
        Check if a file format is supported.

        Args:
            file_path: Path to check

        Returns:
            True if the file format is supported

        Example:
            ```python
            manager = FileFormatManager()
            if manager.is_supported(Path("config.yaml")):
                console.print("YAML format is supported")
            ```
        """
        extension = file_path.suffix.lower()
        return extension in self.parsers
