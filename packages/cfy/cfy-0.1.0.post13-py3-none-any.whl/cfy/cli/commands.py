"""
CLI commands for PyConfig configuration management.

This module provides the main CLI interface using Typer for interacting with
PyConfig configuration management features including validation, inspection,
and conversion between different configuration formats.
"""

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from ..core.base import BaseConfiguration
from ..core.loader import ConfigurationLoader
from ..formats.base import FileFormatManager
from ..security.secrets import SecretManager, mask_secret
from ..utils.performance import PerformanceMonitor

app = typer.Typer(
    name="pyconfig",
    help="PyConfig: Modern Python Configuration Management",
    add_completion=False,
    no_args_is_help=True,
)

console = Console()
performance_monitor = PerformanceMonitor()


@app.command()
def validate(
    schema_module: str = typer.Argument(
        ...,
        help="Python module path to configuration schema class (e.g., 'myapp.config:AppConfig')",
    ),
    config_files: list[Path] | None = typer.Option(
        None, "--config", "-c", help="Configuration files to validate"
    ),
    env_prefix: str | None = typer.Option(
        None, "--env-prefix", "-p", help="Environment variable prefix"
    ),
    secrets_dir: Path | None = typer.Option(
        None, "--secrets-dir", "-s", help="Directory containing secret files"
    ),
    show_values: bool = typer.Option(
        False, "--show-values", "-v", help="Show configuration values (secrets will be masked)"
    ),
    output_format: str = typer.Option(
        "table", "--format", "-f", help="Output format: table, json, yaml"
    ),
) -> None:
    """
    Validate configuration against a Pydantic schema.

    This command loads configuration from multiple sources and validates it
    against a user-defined Pydantic configuration schema.

    Example:
        pyconfig validate myapp.config:AppConfig --config config.yaml --env-prefix MYAPP_
    """
    try:
        with performance_monitor.measure("validate_command"):
            # Import and get the configuration class
            config_class = _import_config_class(schema_module)

            # Create loader with specified options
            loader = _create_loader(
                app_name="pyconfig",
                config_paths=config_files,
                env_prefix=env_prefix,
                secrets_dir=secrets_dir,
            )

            # Load and validate configuration
            try:
                config = loader.load(config_class)
                console.print("[green]✓[/green] Configuration validation successful!")

                if show_values:
                    _display_config(config, output_format, mask_secrets=True)

            except Exception as e:
                console.print(f"[red]✗[/red] Configuration validation failed: {e}")
                raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def inspect(
    schema_module: str = typer.Argument(
        ..., help="Python module path to configuration schema class"
    ),
    field: str | None = typer.Option(None, "--field", "-f", help="Inspect specific field"),
    show_sources: bool = typer.Option(
        False, "--sources", "-s", help="Show configuration sources and precedence"
    ),
    debug_precedence: bool = typer.Option(
        False, "--debug", "-d", help="Debug configuration precedence resolution"
    ),
) -> None:
    """
    Inspect configuration schema and current values.

    This command provides detailed information about configuration schema,
    field types, defaults, and current resolved values.

    Example:
        pyconfig inspect myapp.config:AppConfig --field database_url --sources
    """
    try:
        with performance_monitor.measure("inspect_command"):
            # Import configuration class
            config_class = _import_config_class(schema_module)

            # Create loader
            loader = _create_loader(app_name="pyconfig")

            if field:
                _inspect_field(config_class, field)
            else:
                _inspect_schema(config_class)

            if show_sources:
                _show_sources(loader)

            if debug_precedence:
                _debug_precedence(loader, config_class)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def convert(
    input_file: Path = typer.Argument(..., help="Input configuration file"),
    output_file: Path = typer.Argument(..., help="Output configuration file"),
    format_from: str | None = typer.Option(
        None, "--from", help="Input format (auto-detected if not specified)"
    ),
    format_to: str | None = typer.Option(
        None, "--to", help="Output format (auto-detected from extension if not specified)"
    ),
    pretty: bool = typer.Option(True, "--pretty/--no-pretty", help="Pretty format output"),
) -> None:
    """
    Convert configuration files between different formats.

    Supports conversion between JSON, YAML, and TOML formats with automatic
    format detection based on file extensions.

    Example:
        pyconfig convert config.yaml config.json
        pyconfig convert config.toml config.yaml --pretty
    """
    try:
        with performance_monitor.measure("convert_command"):
            format_manager = FileFormatManager()

            # Validate input file exists
            if not input_file.exists():
                console.print(f"[red]Error:[/red] Input file '{input_file}' does not exist")
                raise typer.Exit(1)

            # Load from input file
            console.print(f"Loading from {input_file}...")
            data = format_manager.parse_file(input_file)

            # Determine output format
            if format_to is None:
                if not output_file.suffix:
                    console.print("[red]Error:[/red] Cannot determine output format from extension")
                    raise typer.Exit(1)
                format_to = output_file.suffix[1:]  # Remove the dot

            # Save to output file
            console.print(f"Converting to {output_file}...")
            format_manager.write_file(data, output_file)

            console.print("[green]✓[/green] Conversion completed successfully!")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def generate_schema(
    schema_module: str = typer.Argument(
        ..., help="Python module path to configuration schema class"
    ),
    output_file: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file for JSON schema (prints to stdout if not specified)",
    ),
    title: str | None = typer.Option(None, "--title", help="Schema title"),
) -> None:
    """
    Generate JSON schema from Pydantic configuration class.

    This command generates a JSON Schema document from a Pydantic configuration
    class, useful for IDE support, documentation, and validation tools.

    Example:
        pyconfig generate-schema myapp.config:AppConfig --output schema.json
    """
    try:
        with performance_monitor.measure("generate_schema_command"):
            # Import configuration class
            config_class = _import_config_class(schema_module)

            # Generate JSON schema
            schema = config_class.model_json_schema()

            if title:
                schema["title"] = title

            # Output schema
            schema_json = json.dumps(schema, indent=2)

            if output_file:
                output_file.write_text(schema_json)
                console.print(f"[green]✓[/green] JSON schema written to {output_file}")
            else:
                console.print(schema_json)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def secrets(
    action: str = typer.Argument(..., help="Action: list, validate, mask"),
    secrets_dir: Path | None = typer.Option(
        None, "--secrets-dir", "-d", help="Directory containing secret files"
    ),
    pattern: str | None = typer.Option(
        None, "--pattern", "-p", help="Validation pattern for secrets"
    ),
) -> None:
    """
    Manage configuration secrets.

    This command provides utilities for managing sensitive configuration
    data including validation, masking, and security checks.

    Example:
        pyconfig secrets list --secrets-dir /var/run/secrets
        pyconfig secrets validate --pattern api_key
    """
    try:
        with performance_monitor.measure("secrets_command"):
            secret_manager = SecretManager()

            if action == "list":
                _list_secrets(secrets_dir)
            elif action == "validate":
                _validate_secrets(secret_manager, pattern)
            elif action == "mask":
                _mask_secrets_demo()
            else:
                console.print(f"[red]Error:[/red] Unknown action '{action}'")
                console.print("Available actions: list, validate, mask")
                raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def performance() -> None:
    """
    Show performance statistics for PyConfig operations.

    This command displays timing and usage statistics for various PyConfig
    operations to help identify performance bottlenecks.
    """
    try:
        stats = performance_monitor.get_all_stats()

        if not stats:
            console.print("[yellow]No performance data available[/yellow]")
            return

        table = Table(title="PyConfig Performance Statistics")
        table.add_column("Operation")
        table.add_column("Count", justify="right")
        table.add_column("Total Time", justify="right")
        table.add_column("Avg Time", justify="right")
        table.add_column("Min Time", justify="right")
        table.add_column("Max Time", justify="right")

        for operation, data in stats.items():
            table.add_row(
                operation,
                str(data["count"]),
                f"{data['total_time']:.3f}s",
                f"{data['avg_time']:.3f}s",
                f"{data['min_time']:.3f}s",
                f"{data['max_time']:.3f}s",
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


# Helper functions


def _import_config_class(module_path: str) -> type[BaseConfiguration]:
    """Import configuration class from module path."""
    try:
        module_name, class_name = module_path.split(":")
    except ValueError:
        raise ValueError(
            f"Invalid module path '{module_path}'. Expected format: 'module:ClassName'"
        )

    try:
        import importlib

        module = importlib.import_module(module_name)
        config_class = getattr(module, class_name)

        if not issubclass(config_class, BaseConfiguration):
            raise ValueError(f"Class {class_name} must inherit from BaseConfiguration")

        return config_class
    except ImportError as e:
        raise ImportError(f"Could not import module '{module_name}': {e}")
    except AttributeError:
        raise AttributeError(f"Class '{class_name}' not found in module '{module_name}'")


def _create_loader(
    app_name: str,
    config_paths: list[Path] | None = None,
    env_prefix: str | None = None,
    secrets_dir: Path | None = None,
) -> ConfigurationLoader:
    """Create configuration loader with specified options."""
    from typing import cast

    config_paths_union: list[str | Path] | None = cast(list[str | Path] | None, config_paths)
    loader = ConfigurationLoader(
        app_name=app_name,
        config_paths=config_paths_union,
        env_prefix=env_prefix,
    )

    return loader


def _display_config(
    config: BaseConfiguration, output_format: str, mask_secrets: bool = True
) -> None:
    """Display configuration in specified format."""
    if mask_secrets:
        config_data = config.to_dict(exclude_secrets=True)
    else:
        config_data = config.to_dict()

    if output_format == "json":
        json_data = JSON.from_data(config_data)
        console.print(json_data)
    elif output_format == "yaml":
        try:
            import yaml

            yaml_content = yaml.dump(config_data, default_flow_style=False, indent=2)
            syntax = Syntax(yaml_content, "yaml", theme="monokai", line_numbers=False)
            console.print(syntax)
        except ImportError:
            console.print("[red]Error:[/red] PyYAML not installed. Use 'json' format instead.")
    else:  # table format
        table = Table(title="Configuration Values")
        table.add_column("Field")
        table.add_column("Value")
        table.add_column("Type")

        for key, value in config_data.items():
            table.add_row(key, str(value), type(value).__name__)

        console.print(table)


def _inspect_field(config_class: type[BaseConfiguration], field_name: str) -> None:
    """Inspect specific configuration field."""
    # Create temporary instance to access field info
    try:
        temp_instance = config_class()
        field_info = temp_instance.get_field_info(field_name)

        if field_info is None:
            console.print(f"[red]Error:[/red] Field '{field_name}' not found")
            return

        panel_content = f"""
[bold]Field:[/bold] {field_name}
[bold]Type:[/bold] {field_info["type"]}
[bold]Required:[/bold] {field_info["is_required"]}
[bold]Default:[/bold] {field_info["default"]}
[bold]Description:[/bold] {field_info.get("description", "No description")}
[bold]Alias:[/bold] {field_info.get("alias", "None")}
        """.strip()

        panel = Panel(panel_content, title=f"Field: {field_name}")
        console.print(panel)

    except Exception as e:
        console.print(f"[red]Error creating temporary instance:[/red] {e}")


def _inspect_schema(config_class: type[BaseConfiguration]) -> None:
    """Inspect configuration schema."""
    table = Table(title=f"Configuration Schema: {config_class.__name__}")
    table.add_column("Field")
    table.add_column("Type")
    table.add_column("Required")
    table.add_column("Default")
    table.add_column("Description")

    for field_name, field_info in config_class.model_fields.items():
        table.add_row(
            field_name,
            str(field_info.annotation) if field_info.annotation else "Unknown",
            "Yes" if field_info.is_required() else "No",
            str(field_info.default) if field_info.default is not ... else "None",
            field_info.description or "No description",
        )

    console.print(table)


def _show_sources(loader: ConfigurationLoader) -> None:
    """Show configuration sources and their precedence."""
    source_names = loader.get_source_names()

    table = Table(title="Configuration Sources (Precedence Order)")
    table.add_column("Priority")
    table.add_column("Source")
    table.add_column("Status")

    for i, source_name in enumerate(source_names, 1):
        # Try to get source status
        sources_data = loader.load_individual_sources()
        status = "Available" if source_name in sources_data else "Not Available"

        table.add_row(str(i), source_name, status)

    console.print(table)


def _debug_precedence(loader: ConfigurationLoader, config_class: type[BaseConfiguration]) -> None:
    """Debug configuration precedence resolution."""
    debug_info = loader.debug_precedence(config_class)

    console.print("\n[bold]Configuration Precedence Debug:[/bold]")

    # Show individual sources
    console.print("\n[bold]Individual Sources:[/bold]")
    for source_name, source_data in debug_info["individual_sources"].items():
        if source_data:
            console.print(f"  [green]{source_name}:[/green] {len(source_data)} values")
        else:
            console.print(f"  [yellow]{source_name}:[/yellow] No values")

    # Show field precedence
    if "fields" in debug_info:
        console.print("\n[bold]Field Precedence Resolution:[/bold]")
        table = Table()
        table.add_column("Field")
        table.add_column("Final Value")
        table.add_column("Winning Source")
        table.add_column("All Sources")

        for field_name, field_info in debug_info["fields"].items():
            all_sources = ", ".join(field_info["source_values"].keys())
            table.add_row(
                field_name,
                str(field_info["final_value"]),
                field_info["winning_source"] or "Default",
                all_sources or "None",
            )

        console.print(table)


def _list_secrets(secrets_dir: Path | None) -> None:
    """List available secret files."""
    if not secrets_dir:
        console.print("[red]Error:[/red] --secrets-dir is required for 'list' action")
        return

    if not secrets_dir.exists():
        console.print(f"[red]Error:[/red] Secrets directory '{secrets_dir}' does not exist")
        return

    table = Table(title="Available Secrets")
    table.add_column("Secret Name")
    table.add_column("File Path")
    table.add_column("Size")
    table.add_column("Permissions")

    for secret_file in secrets_dir.iterdir():
        if secret_file.is_file():
            stat = secret_file.stat()
            permissions = oct(stat.st_mode)[-3:]

            table.add_row(
                secret_file.name,
                str(secret_file),
                f"{stat.st_size} bytes",
                permissions,
            )

    console.print(table)


def _validate_secrets(secret_manager: SecretManager, pattern: str | None) -> None:
    """Validate secrets against patterns."""
    available_patterns = secret_manager.list_secret_patterns()

    table = Table(title="Available Secret Validation Patterns")
    table.add_column("Pattern Name")
    table.add_column("Description")

    pattern_descriptions = {
        "api_key": "API keys (16+ alphanumeric/underscore/dash chars)",
        "token": "Tokens (20+ alphanumeric/dot/underscore/dash chars)",
        "password": "Passwords (8+ characters)",
        "uuid": "UUID format",
        "hex": "Hexadecimal format",
    }

    for pattern_name in available_patterns:
        description = pattern_descriptions.get(pattern_name, "Custom pattern")
        table.add_row(pattern_name, description)

    console.print(table)


def _mask_secrets_demo() -> None:
    """Demonstrate secret masking functionality."""
    demo_secrets = [
        ("api_key_12345678901234567890", "API Key"),
        ("password123", "Password"),
        ("jwt.token.here", "JWT Token"),
        ("short", "Short Secret"),
    ]

    table = Table(title="Secret Masking Demo")
    table.add_column("Type")
    table.add_column("Original Length")
    table.add_column("Masked Value")

    for secret, secret_type in demo_secrets:
        masked = mask_secret(secret)
        table.add_row(secret_type, str(len(secret)), masked)

    console.print(table)


if __name__ == "__main__":
    app()
