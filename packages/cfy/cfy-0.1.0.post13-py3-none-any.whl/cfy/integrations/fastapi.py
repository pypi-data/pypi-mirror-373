"""
FastAPI integration utilities for PyConfig.

This module provides seamless integration between PyConfig and FastAPI applications,
including dependency injection, middleware, and lifecycle management.
"""

from collections.abc import Callable
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import TypeVar

from fastapi import Depends, FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.base import BaseConfiguration
from ..core.exceptions import ConfigurationLoadError, PyConfigError
from ..core.loader import ConfigurationLoader

T = TypeVar("T", bound=BaseConfiguration)


class ConfigDependency[T]:
    """
    FastAPI dependency for configuration injection.

    This class provides a reusable dependency that can be used to inject
    configuration objects into FastAPI route handlers and other dependencies.

    Example:
        ```python
        from cfy.integrations import ConfigDependency

        # Create dependency
        config_dep = ConfigDependency(MyAppConfig)

        # Use in route
        @app.get("/status")
        async def status(config: MyAppConfig = Depends(config_dep)):
            return {"database_url": config.database.url}
        ```

    <!-- Example Test:
    >>> from cfy.integrations.fastapi import ConfigDependency
    >>> from cfy.core.base import BaseConfiguration
    >>> class TestConfig(BaseConfiguration): pass
    >>> dep = ConfigDependency(TestConfig)
    >>> assert dep.config_class == TestConfig
    >>> assert callable(dep)
    -->
    """

    def __init__(
        self,
        config_class: type[T],
        loader: ConfigurationLoader | None = None,
        cache_enabled: bool = True,
    ) -> None:
        """
        Initialize configuration dependency.

        Args:
            config_class: Configuration model class to load
            loader: Optional custom configuration loader
            cache_enabled: Whether to cache the configuration instance
        """
        self.config_class = config_class
        self.loader = loader or ConfigurationLoader(app_name="fastapi_app")
        self.cache_enabled = cache_enabled
        self._cached_config: T | None = None

    def __call__(self) -> T:
        """
        Load and return configuration instance.

        Returns:
            Configuration instance

        Raises:
            ConfigurationLoadError: If configuration cannot be loaded
        """
        if self.cache_enabled and self._cached_config is not None:
            return self._cached_config

        try:
            config = self.loader.load(self.config_class)  # type: ignore[type-var]
            if self.cache_enabled:
                self._cached_config = config
            return config
        except Exception as e:
            raise ConfigurationLoadError(
                f"Failed to load configuration for FastAPI dependency: {e}",
                details={"config_class": self.config_class.__name__},
            ) from e

    def clear_cache(self) -> None:
        """
        Clear cached configuration instance.

        Example:
            ```python
            config_dep = ConfigDependency(MyConfig)
            config_dep.clear_cache()  # Force reload on next call
            ```
        """
        self._cached_config = None


def create_config_dependency(
    config_class: type[T], loader: ConfigurationLoader | None = None, cache_enabled: bool = True
) -> Callable[[], T]:
    """
    Factory function to create configuration dependencies.

    Args:
        config_class: Configuration model class
        loader: Optional custom configuration loader
        cache_enabled: Whether to cache configuration instances

    Returns:
        FastAPI dependency function

    Example:
        ```python
        from cfy.integrations import create_config_dependency

        # Create dependency
        get_config = create_config_dependency(MyAppConfig)

        # Use in route
        @app.get("/info")
        async def info(config: MyAppConfig = Depends(get_config)):
            return {"app_name": config.app_name}
        ```

    <!-- Example Test:
    >>> from cfy.integrations.fastapi import create_config_dependency
    >>> from cfy.core.base import BaseConfiguration
    >>> class TestConfig(BaseConfiguration): pass
    >>> dep = create_config_dependency(TestConfig)
    >>> assert callable(dep)
    -->
    """
    dependency = ConfigDependency(config_class, loader, cache_enabled)
    return dependency


def create_lifespan_handler(
    config_class: type[T],
    loader: ConfigurationLoader | None = None,
    startup_callback: Callable[[T], None] | None = None,
    shutdown_callback: Callable[[T], None] | None = None,
):
    """
    Create FastAPI lifespan handler with configuration loading.

    Args:
        config_class: Configuration model class
        loader: Optional custom configuration loader
        startup_callback: Optional callback called during startup with config
        shutdown_callback: Optional callback called during shutdown with config

    Returns:
        FastAPI lifespan context manager

    Example:
        ```python
        from cfy.integrations import create_lifespan_handler

        def on_startup(config: MyAppConfig):
            console.print(f"Starting {config.app_name}")

        def on_shutdown(config: MyAppConfig):
            console.print("Shutting down")

        lifespan = create_lifespan_handler(
            MyAppConfig,
            startup_callback=on_startup,
            shutdown_callback=on_shutdown
        )

        app = FastAPI(lifespan=lifespan)
        ```
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        try:
            config_loader = loader or ConfigurationLoader(app_name="fastapi_app")
            config = config_loader.load(config_class)

            # Store config in app state for access in routes
            app.state.config = config

            # Call startup callback if provided
            if startup_callback:
                startup_callback(config)

            yield

        except Exception as e:
            raise ConfigurationLoadError(
                f"Failed to load configuration during FastAPI startup: {e}",
                details={"config_class": config_class.__name__},
            ) from e
        finally:
            # Shutdown
            if shutdown_callback and hasattr(app.state, "config"):
                shutdown_callback(app.state.config)

    return lifespan


class FastAPIConfigMiddleware(BaseHTTPMiddleware):
    """
    Middleware for request-scoped configuration management.

    This middleware can reload configuration per request, useful for
    dynamic configuration scenarios or development environments.

    Example:
        ```python
        from cfy.integrations import FastAPIConfigMiddleware

        app.add_middleware(
            FastAPIConfigMiddleware,
            config_class=MyAppConfig,
            reload_on_request=True
        )
        ```
    """

    def __init__(
        self,
        app,
        config_class: type[BaseConfiguration],
        loader: ConfigurationLoader | None = None,
        reload_on_request: bool = False,
        config_header: str = "X-Config-Version",
    ) -> None:
        """
        Initialize configuration middleware.

        Args:
            app: FastAPI application instance
            config_class: Configuration model class
            loader: Optional custom configuration loader
            reload_on_request: Whether to reload config on each request
            config_header: Header name for config version tracking
        """
        super().__init__(app)
        self.config_class = config_class
        self.loader = loader or ConfigurationLoader(app_name="fastapi_app")
        self.reload_on_request = reload_on_request
        self.config_header = config_header
        self._config_cache: BaseConfiguration | None = None

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request with configuration context.

        Args:
            request: FastAPI request
            call_next: Next middleware or route handler

        Returns:
            Response with configuration context
        """
        try:
            # Load or get cached configuration
            if self.reload_on_request or self._config_cache is None:
                config = self.loader.load(self.config_class)
                if not self.reload_on_request:
                    self._config_cache = config
            else:
                config = self._config_cache

            # Add config to request state
            request.state.config = config

            # Process request
            response = await call_next(request)

            # Add config version header if available
            if hasattr(config, "__version__"):
                response.headers[self.config_header] = str(config.__version__)

            return response

        except Exception as e:
            # Log error but don't break request processing
            # In production, you might want to handle this differently
            request.state.config_error = str(e)
            return await call_next(request)


@lru_cache(maxsize=128)
def get_config(config_class: type[T], loader: ConfigurationLoader | None = None) -> T:
    """
    Cached configuration getter for FastAPI routes.

    This is a simple helper function that can be used directly
    in FastAPI routes without dependency injection.

    Args:
        config_class: Configuration model class
        loader: Optional custom configuration loader

    Returns:
        Configuration instance

    Example:
        ```python
        from cfy.integrations import get_config

        @app.get("/status")
        async def status():
            config = get_config(MyAppConfig)
            return {"status": "ok", "version": config.version}
        ```

    <!-- Example Test:
    >>> from cfy.integrations.fastapi import get_config
    >>> from cfy.core.base import BaseConfiguration
    >>> class TestConfig(BaseConfiguration): pass
    >>> config = get_config(TestConfig)
    >>> assert isinstance(config, TestConfig)
    -->
    """
    config_loader = loader or ConfigurationLoader(app_name="fastapi_app")
    return config_loader.load(config_class)


def setup_config_middleware(
    app: FastAPI,
    config_class: type[BaseConfiguration],
    loader: ConfigurationLoader | None = None,
    reload_on_request: bool = False,
    config_header: str = "X-Config-Version",
) -> None:
    """
    Utility function to setup configuration middleware.

    Args:
        app: FastAPI application instance
        config_class: Configuration model class
        loader: Optional custom configuration loader
        reload_on_request: Whether to reload config on each request
        config_header: Header name for config version tracking

    Example:
        ```python
        from cfy.integrations import setup_config_middleware

        app = FastAPI()
        setup_config_middleware(app, MyAppConfig)
        ```
    """
    app.add_middleware(
        FastAPIConfigMiddleware,
        config_class=config_class,
        loader=loader,
        reload_on_request=reload_on_request,
        config_header=config_header,
    )


# Additional utility functions for common FastAPI patterns


def create_health_check(config_dependency: Callable[[], BaseConfiguration]) -> Callable:
    """
    Create a health check endpoint that validates configuration.

    Args:
        config_dependency: Configuration dependency function

    Returns:
        FastAPI route handler for health checks

    Example:
        ```python
        from cfy.integrations import create_health_check, create_config_dependency

        get_config = create_config_dependency(MyAppConfig)
        health_check = create_health_check(get_config)

        app.get("/health")(health_check)
        ```
    """

    async def health_check(config: BaseConfiguration = Depends(config_dependency)):
        try:
            # Basic configuration validation
            config_dict = config.model_dump()
            return {
                "status": "healthy",
                "config_loaded": True,
                "config_fields": len(config_dict),
                "timestamp": config_dict.get("timestamp"),
            }
        except Exception as e:
            return {"status": "unhealthy", "config_loaded": False, "error": str(e)}

    return health_check


def create_config_info_endpoint(
    config_dependency: Callable[[], BaseConfiguration], include_secrets: bool = False
) -> Callable:
    """
    Create an endpoint that returns configuration information.

    Args:
        config_dependency: Configuration dependency function
        include_secrets: Whether to include secret values (masked)

    Returns:
        FastAPI route handler for config info

    Warning:
        Be careful with include_secrets=True in production environments.

    Example:
        ```python
        from cfy.integrations import create_config_info_endpoint

        get_config = create_config_dependency(MyAppConfig)
        config_info = create_config_info_endpoint(get_config)

        app.get("/config")(config_info)
        ```
    """

    async def config_info(config: BaseConfiguration = Depends(config_dependency)):
        try:
            if include_secrets:
                # Return full config with secrets masked
                config_dict = config.model_dump()
                # You might want to implement secret masking here
                return {"config": config_dict, "secrets_included": True}
            else:
                # Return config without secret fields
                config_dict = config.model_dump(exclude={"secrets", "password", "key", "token"})
                return {"config": config_dict, "secrets_included": False}
        except Exception as e:
            raise PyConfigError(
                f"Failed to serialize configuration: {e}",
                details={"config_class": type(config).__name__},
            ) from e

    return config_info
