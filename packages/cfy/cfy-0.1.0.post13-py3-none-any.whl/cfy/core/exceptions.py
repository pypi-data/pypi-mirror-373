"""
Custom exceptions for PyConfig configuration management library.

This module defines comprehensive exception classes for handling various error conditions
that can occur during configuration loading, validation, and processing.
"""

from typing import Any


class PyConfigError(Exception):
    """
    Base exception class for all PyConfig errors.

    This is the parent class for all custom exceptions in the PyConfig library.
    It provides a consistent interface for error handling and reporting.

    Example:
        ```python
        try:
            config = loader.load()
        except PyConfigError as e:
            logger.error(f"Configuration error: {e}")
        ```
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """
        Initialize the base configuration error.

        Args:
            message: Human-readable error message
            details: Optional dictionary containing additional error context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationLoadError(PyConfigError):
    """
    Raised when configuration loading fails from any source.

    This error occurs when the configuration loader cannot successfully load
    configuration data from one or more sources due to file access issues,
    parsing errors, or validation failures.

    Example:
        ```python
        try:
            config = loader.load(MyAppConfig)
        except ConfigurationLoadError as e:
            console.print(f"Failed to load config: {e.message}")
            console.print(f"Failed sources: {e.failed_sources}")
        ```
    """

    def __init__(
        self,
        message: str,
        failed_sources: list[str] | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize configuration load error.

        Args:
            message: Human-readable error message
            failed_sources: List of configuration sources that failed to load
            details: Additional context about the failure
        """
        super().__init__(message, details)
        self.failed_sources = failed_sources or []


class ConfigurationValidationError(PyConfigError):
    """
    Raised when loaded configuration data fails validation.

    This error occurs when configuration data is successfully loaded but does not
    meet the validation requirements defined in the configuration schema.

    Example:
        ```python
        try:
            config = MyAppConfig(**config_data)
        except ConfigurationValidationError as e:
            console.print(f"Validation failed: {e.message}")
            for error in e.validation_errors:
                console.print(f"  - {error}")
        ```
    """

    def __init__(
        self,
        message: str,
        validation_errors: list[str] | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize configuration validation error.

        Args:
            message: Human-readable error message
            validation_errors: List of specific validation error messages
            details: Additional validation context
        """
        super().__init__(message, details)
        self.validation_errors = validation_errors or []


class FileFormatError(PyConfigError):
    """
    Raised when file parsing fails due to format issues.

    This error occurs when a configuration file cannot be parsed due to
    syntax errors, unsupported format, or malformed data.

    Example:
        ```python
        try:
            data = format_manager.parse_file(Path("config.yaml"))
        except FileFormatError as e:
            console.print(f"Format error in {e.file_path}: {e.message}")
            console.print(f"Line {e.line_number}: {e.parse_error}")
        ```
    """

    def __init__(
        self,
        message: str,
        file_path: str | None = None,
        line_number: int | None = None,
        parse_error: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize file format error.

        Args:
            message: Human-readable error message
            file_path: Path to the file that failed to parse
            line_number: Line number where parsing failed (if available)
            parse_error: Original parsing error message
            details: Additional parsing context
        """
        super().__init__(message, details)
        self.file_path = file_path
        self.line_number = line_number
        self.parse_error = parse_error


class CLIParsingError(PyConfigError):
    """
    Raised when CLI argument parsing fails.

    This error occurs when command-line arguments cannot be parsed or
    when invalid arguments are provided to the CLI parser.

    Example:
        ```python
        try:
            overrides = cli_parser.parse_args()
        except CLIParsingError as e:
            console.print(f"CLI parsing failed: {e.message}")
            console.print(f"Invalid arguments: {e.invalid_args}")
        ```
    """

    def __init__(
        self,
        message: str,
        invalid_args: list[str] | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize CLI parsing error.

        Args:
            message: Human-readable error message
            invalid_args: List of invalid command-line arguments
            details: Additional parsing context
        """
        super().__init__(message, details)
        self.invalid_args = invalid_args or []


class SecretError(PyConfigError):
    """
    Raised when secret management operations fail.

    This error occurs when secrets cannot be loaded, validated, or processed
    due to security constraints or access issues.

    Example:
        ```python
        try:
            secret = secret_manager.load_secret("api_key")
        except SecretError as e:
            console.print(f"Secret loading failed: {e.message}")
            console.print(f"Secret type: {e.secret_type}")
        ```
    """

    def __init__(
        self, message: str, secret_type: str | None = None, details: dict[str, Any] | None = None
    ) -> None:
        """
        Initialize secret management error.

        Args:
            message: Human-readable error message
            secret_type: Type of secret that failed (e.g., "api_key", "password")
            details: Additional security context
        """
        super().__init__(message, details)
        self.secret_type = secret_type


class SecurityError(PyConfigError):
    """
    Raised when security-related operations fail.

    This error occurs when security constraints are violated, secrets
    cannot be loaded, or when security policies are not met.

    Example:
        ```python
        try:
            secret_manager = SecretManager()
            secret = secret_manager.get_secret_env('MISSING_SECRET')
        except SecurityError as e:
            console.print(f"Security error: {e.message}")
            console.print(f"Security details: {e.details}")
        ```
    """

    def __init__(
        self,
        message: str,
        security_type: str | None = None,
        file_path: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize security error.

        Args:
            message: Human-readable error message
            security_type: Type of security issue (e.g., "permission", "validation")
            file_path: Path to file that caused security issue (if applicable)
            details: Additional security context
        """
        super().__init__(message, details)
        self.security_type = security_type
        self.file_path = file_path


class PerformanceError(PyConfigError):
    """
    Raised when performance-related operations fail.

    This error occurs when performance constraints are violated, caching
    fails, or when performance optimization operations encounter issues.

    Example:
        ```python
        try:
            lazy_loader = LazyLoader(expensive_operation)
            result = lazy_loader.value
        except PerformanceError as e:
            console.print(f"Performance error: {e.message}")
            console.print(f"Performance details: {e.details}")
        ```
    """

    def __init__(
        self,
        message: str,
        operation_type: str | None = None,
        performance_metric: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize performance error.

        Args:
            message: Human-readable error message
            operation_type: Type of operation that failed (e.g., "caching", "lazy_loading")
            performance_metric: Performance metric that was violated (if applicable)
            details: Additional performance context
        """
        super().__init__(message, details)
        self.operation_type = operation_type
        self.performance_metric = performance_metric


class ConfigurationSourceError(PyConfigError):
    """
    Raised when a specific configuration source encounters an error.

    This error occurs when an individual configuration source (file, environment,
    CLI) fails to provide data due to access issues or processing errors.

    Example:
        ```python
        try:
            data = source.load_data()
        except ConfigurationSourceError as e:
            console.print(f"Source '{e.source_name}' failed: {e.message}")
            console.print(f"Source type: {e.source_type}")
        ```
    """

    def __init__(
        self,
        message: str,
        source_name: str | None = None,
        source_type: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize configuration source error.

        Args:
            message: Human-readable error message
            source_name: Name of the source that failed
            source_type: Type of source (e.g., "file", "environment", "cli")
            details: Additional source-specific context
        """
        super().__init__(message, details)
        self.source_name = source_name
        self.source_type = source_type
