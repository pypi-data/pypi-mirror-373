"""
cfy: Config For You - Modern Python Configuration Management

A comprehensive, generic configuration management library for Python 3.12+ that provides
extensible utilities and patterns for building type-safe, multi-source configuration systems.
"""

from .cli.parser import CLIParser
from .core.base import BaseConfiguration
from .core.loader import ConfigurationLoader
from .core.sources import ConfigurationSources
from .formats.base import FileFormatManager
from .security.secrets import SecretManager
from .utils.interpolation import ConfigInterpolator, interpolate_config, interpolate_string

__version__ = "0.1.0"

__all__ = [
    "BaseConfiguration",
    "CLIParser",
    "ConfigInterpolator",
    "ConfigurationLoader",
    "ConfigurationSources",
    "FileFormatManager",
    "SecretManager",
    "interpolate_config",
    "interpolate_string",
]
