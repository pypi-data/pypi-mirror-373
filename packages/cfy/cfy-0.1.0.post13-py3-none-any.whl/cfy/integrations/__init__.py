"""
Integration utilities for PyConfig with popular frameworks.

This module provides integration helpers for using PyConfig with various
Python frameworks and libraries including FastAPI, Flask, and others.
"""

from .fastapi import (
    ConfigDependency,
    FastAPIConfigMiddleware,
    create_config_dependency,
    create_lifespan_handler,
    get_config,
    setup_config_middleware,
)

__all__ = [
    "ConfigDependency",
    "create_config_dependency",
    "create_lifespan_handler",
    "FastAPIConfigMiddleware",
    "get_config",
    "setup_config_middleware",
]
