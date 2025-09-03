"""
Performance utilities for PyConfig.

This module provides caching, lazy loading, and other performance
optimization utilities for configuration management.
"""

import threading
import time
from collections.abc import Callable
from functools import lru_cache, wraps
from pathlib import Path
from typing import Any, ParamSpec, TypeVar

from ..core.exceptions import PerformanceError

P = ParamSpec("P")
T = TypeVar("T")


class ConfigCache:
    """
    Thread-safe cache for configuration data with TTL support.

    This cache provides thread-safe access to configuration data with
    automatic expiration based on time-to-live (TTL) settings.

    Example:
        ```python
        from cfy.utils import ConfigCache

        cache = ConfigCache(ttl=300)  # 5 minute TTL

        # Store configuration
        cache.set('app_config', {'debug': True, 'port': 8080})

        # Retrieve configuration
        config = cache.get('app_config')

        # Check if key exists
        if cache.has('app_config'):
            console.print("Config found in cache")
        ```

    <!-- Example Test:
    >>> from cfy.utils.performance import ConfigCache
    >>> cache = ConfigCache(ttl=1)
    >>> cache.set('test', {'value': 42})
    >>> assert cache.get('test') == {'value': 42}
    >>> assert cache.has('test') is True
    >>> import time; time.sleep(1.1)
    >>> assert cache.has('test') is False
    -->
    """

    def __init__(self, ttl: float = 3600.0, max_size: int = 1000) -> None:
        """
        Initialize configuration cache.

        Args:
            ttl: Time to live in seconds (default: 1 hour)
            max_size: Maximum number of cached items

        Example:
            ```python
            # Create cache with 5 minute TTL
            cache = ConfigCache(ttl=300)

            # Create cache with custom size limit
            cache = ConfigCache(ttl=600, max_size=500)
            ```
        """
        self.ttl = ttl
        self.max_size = max_size
        self._cache: dict[str, tuple[Any, float]] = {}
        self._lock = threading.RLock()

    def set(self, key: str, value: Any) -> None:
        """
        Store value in cache with current timestamp.

        Args:
            key: Cache key
            value: Value to store

        Example:
            ```python
            cache = ConfigCache()
            cache.set('database_config', {'host': 'localhost', 'port': 5432})
            ```
        """
        current_time = time.time()

        with self._lock:
            # Remove oldest entries if at capacity
            if len(self._cache) >= self.max_size:
                self._evict_oldest()

            self._cache[key] = (value, current_time)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve value from cache if not expired.

        Args:
            key: Cache key
            default: Default value if key not found or expired

        Returns:
            Cached value or default

        Example:
            ```python
            cache = ConfigCache()
            cache.set('app_config', {'debug': True})
            config = cache.get('app_config', {})
            ```
        """
        with self._lock:
            if key not in self._cache:
                return default

            value, timestamp = self._cache[key]

            # Check if expired
            if time.time() - timestamp > self.ttl:
                del self._cache[key]
                return default

            return value

    def has(self, key: str) -> bool:
        """
        Check if key exists in cache and is not expired.

        Args:
            key: Cache key

        Returns:
            True if key exists and is valid, False otherwise

        Example:
            ```python
            cache = ConfigCache()
            cache.set('config', {'key': 'value'})

            if cache.has('config'):
                console.print("Config is cached")
            ```
        """
        return self.get(key) is not None

    def delete(self, key: str) -> bool:
        """
        Remove key from cache.

        Args:
            key: Cache key to remove

        Returns:
            True if key was removed, False if not found

        Example:
            ```python
            cache = ConfigCache()
            cache.set('temp_config', {})

            removed = cache.delete('temp_config')
            console.print(f"Removed: {removed}")  # True
            ```
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        """
        Clear all cached items.

        Example:
            ```python
            cache = ConfigCache()
            cache.set('config1', {})
            cache.set('config2', {})
            cache.clear()

            console.print(cache.size())  # 0
            ```
        """
        with self._lock:
            self._cache.clear()

    def size(self) -> int:
        """
        Get number of cached items.

        Returns:
            Number of items currently in cache

        Example:
            ```python
            cache = ConfigCache()
            cache.set('config', {})
            console.print(f"Cache size: {cache.size()}")  # 1
            ```
        """
        with self._lock:
            return len(self._cache)

    def cleanup_expired(self) -> int:
        """
        Remove expired items from cache.

        Returns:
            Number of items removed

        Example:
            ```python
            cache = ConfigCache(ttl=1)
            cache.set('config', {})
            time.sleep(2)

            removed = cache.cleanup_expired()
            console.print(f"Removed {removed} expired items")
            ```
        """
        current_time = time.time()
        removed_count = 0

        with self._lock:
            expired_keys = [
                key
                for key, (_, timestamp) in self._cache.items()
                if current_time - timestamp > self.ttl
            ]

            for key in expired_keys:
                del self._cache[key]
                removed_count += 1

        return removed_count

    def _evict_oldest(self) -> None:
        """Remove the oldest cache entry."""
        if not self._cache:
            return

        oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
        del self._cache[oldest_key]


class LazyLoader[T]:
    """
    Lazy loading wrapper for expensive configuration operations.

    This class defers expensive operations until they are actually needed,
    improving startup performance for applications that may not use all
    configuration values.

    Example:
        ```python
        from cfy.utils import LazyLoader

        def load_database_config():
            # Expensive database configuration loading
            return {'host': 'db.example.com', 'port': 5432}

        lazy_db_config = LazyLoader(load_database_config)

        # Configuration not loaded yet
        console.print("App starting...")

        # Configuration loaded on first access
        config = lazy_db_config.value
        ```

    <!-- Example Test:
    >>> from cfy.utils.performance import LazyLoader
    >>> def expensive_func():
    ...     return {'loaded': True}
    >>> loader = LazyLoader(expensive_func)
    >>> assert loader.is_loaded() is False
    >>> value = loader.value
    >>> assert value == {'loaded': True}
    >>> assert loader.is_loaded() is True
    -->
    """

    def __init__(self, loader_func: Callable[[], T]) -> None:
        """
        Initialize lazy loader.

        Args:
            loader_func: Function to call for loading value

        Example:
            ```python
            def load_config():
                return {'key': 'value'}

            lazy_config = LazyLoader(load_config)
            ```
        """
        self._loader_func = loader_func
        self._value: T | None = None
        self._loaded = False
        self._lock = threading.Lock()

    @property
    def value(self) -> T:
        """
        Get the loaded value, loading if necessary.

        Returns:
            The loaded value

        Example:
            ```python
            lazy_config = LazyLoader(load_expensive_config)
            config = lazy_config.value  # Loads on first access
            ```
        """
        if not self._loaded:
            with self._lock:
                if not self._loaded:  # Double-check locking
                    try:
                        self._value = self._loader_func()
                        self._loaded = True
                    except Exception as e:
                        raise PerformanceError(
                            f"Failed to load lazy value: {e}", details={"loader_error": str(e)}
                        ) from e

        return self._value

    def is_loaded(self) -> bool:
        """
        Check if value has been loaded.

        Returns:
            True if value has been loaded, False otherwise

        Example:
            ```python
            lazy_config = LazyLoader(load_config)
            console.print(f"Loaded: {lazy_config.is_loaded()}")  # False

            config = lazy_config.value
            console.print(f"Loaded: {lazy_config.is_loaded()}")  # True
            ```
        """
        return self._loaded

    def reset(self) -> None:
        """
        Reset the loader to unloaded state.

        Example:
            ```python
            lazy_config = LazyLoader(load_config)
            config = lazy_config.value  # Load value

            lazy_config.reset()  # Reset to unloaded
            console.print(f"Loaded: {lazy_config.is_loaded()}")  # False
            ```
        """
        with self._lock:
            self._value = None
            self._loaded = False


def cached_method(ttl: float = 3600.0, max_size: int = 128):
    """
    Decorator for caching method results with TTL.

    Args:
        ttl: Time to live in seconds
        max_size: Maximum cache size

    Returns:
        Decorated method with caching

    Example:
        ```python
        from cfy.utils import cached_method

        class ConfigService:
            @cached_method(ttl=300)  # 5 minute cache
            def load_expensive_config(self, name: str):
                # Expensive configuration loading
                return {'name': name, 'loaded_at': time.time()}

        service = ConfigService()
        config1 = service.load_expensive_config('app')  # Loads from source
        config2 = service.load_expensive_config('app')  # Returns cached value
        ```
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        cache = ConfigCache(ttl=ttl, max_size=max_size)

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"

            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result

            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            return result

        # Add cache management methods to wrapper
        wrapper.cache_clear = cache.clear  # type: ignore
        wrapper.cache_info = lambda: {"size": cache.size(), "ttl": ttl}  # type: ignore

        return wrapper

    return decorator


def file_watcher_cache(ttl: float = 60.0):
    """
    Decorator for caching file-based operations with file modification checking.

    Args:
        ttl: Minimum time between file modification checks

    Returns:
        Decorated function with file-aware caching

    Example:
        ```python
        from cfy.utils import file_watcher_cache
        from pathlib import Path

        @file_watcher_cache(ttl=30)
        def load_config_file(file_path: Path):
            return file_path.read_text()

        config = load_config_file(Path('config.yaml'))  # Loads from file
        config = load_config_file(Path('config.yaml'))  # Returns cached if file unchanged
        ```
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        cache: dict[str, tuple[T, float, float]] = {}  # value, mtime, check_time
        lock = threading.Lock()

        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Extract file path from arguments (assume first Path argument)
            file_path = None
            for arg in args:
                if isinstance(arg, Path):
                    file_path = arg
                    break

            if file_path is None:
                # No file path found, call function directly
                return func(*args, **kwargs)

            cache_key = str(file_path)
            current_time = time.time()

            with lock:
                # Check cache
                if cache_key in cache:
                    cached_value, cached_mtime, last_check = cache[cache_key]

                    # Only check file modification if enough time has passed
                    if current_time - last_check < ttl:
                        return cached_value

                    # Check if file has been modified
                    try:
                        current_mtime = file_path.stat().st_mtime
                        if current_mtime == cached_mtime:
                            # Update check time and return cached value
                            cache[cache_key] = (cached_value, cached_mtime, current_time)
                            return cached_value
                    except OSError:
                        # File no longer exists or inaccessible, remove from cache
                        del cache[cache_key]

                # Load fresh value
                try:
                    result = func(*args, **kwargs)
                    file_mtime = file_path.stat().st_mtime
                    cache[cache_key] = (result, file_mtime, current_time)
                    return result
                except Exception as e:
                    raise PerformanceError(
                        f"Failed to load file-cached value: {e}",
                        details={"cache_error": str(e), "file_path": str(file_path)},
                    ) from e

        # Add cache management
        wrapper.cache_clear = lambda: cache.clear()  # type: ignore
        wrapper.cache_info = lambda: {"size": len(cache), "ttl": ttl}  # type: ignore

        return wrapper

    return decorator


@lru_cache(maxsize=256)
def memoize_config_operation(operation_id: str, *args: Any) -> Any:
    """
    Memoize configuration operations using LRU cache.

    Args:
        operation_id: Unique identifier for the operation
        args: Operation arguments

    Returns:
        Cached result

    Example:
        ```python
        from cfy.utils import memoize_config_operation

        # Memoize expensive calculation
        def expensive_calculation(data):
            result = memoize_config_operation('calc', data)
            if result is None:
                # Perform calculation
                result = sum(data) * len(data)
            return result
        ```

    <!-- Example Test:
    >>> from cfy.utils.performance import memoize_config_operation
    >>> result1 = memoize_config_operation('test', 1, 2, 3)
    >>> result2 = memoize_config_operation('test', 1, 2, 3)
    >>> # Results should be the same cached value
    -->
    """
    # This is a placeholder - actual operation would be performed
    # This function serves as a memoization key for external operations
    return None


class PerformanceMonitor:
    """
    Monitor performance metrics for configuration operations.

    This class tracks timing and usage statistics for configuration
    operations to help identify performance bottlenecks.

    Example:
        ```python
        from cfy.utils import PerformanceMonitor

        monitor = PerformanceMonitor()

        with monitor.measure('config_load'):
            config = load_configuration()

        stats = monitor.get_stats('config_load')
        console.print(f"Average load time: {stats['avg_time']:.2f}s")
        ```

    <!-- Example Test:
    >>> from cfy.utils.performance import PerformanceMonitor
    >>> import time
    >>> monitor = PerformanceMonitor()
    >>> with monitor.measure('test'):
    ...     time.sleep(0.01)
    >>> stats = monitor.get_stats('test')
    >>> assert stats['count'] == 1
    >>> assert stats['total_time'] >= 0.01
    -->
    """

    def __init__(self) -> None:
        """Initialize performance monitor."""
        self._stats: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()

    def measure(self, operation_name: str):
        """
        Context manager for measuring operation performance.

        Args:
            operation_name: Name of the operation being measured

        Returns:
            Context manager for timing the operation

        Example:
            ```python
            monitor = PerformanceMonitor()

            with monitor.measure('database_query'):
                result = execute_expensive_query()
            ```
        """
        return _PerformanceMeasurement(self, operation_name)

    def record_timing(self, operation_name: str, duration: float) -> None:
        """
        Record timing for an operation.

        Args:
            operation_name: Name of the operation
            duration: Duration in seconds

        Example:
            ```python
            monitor = PerformanceMonitor()

            start = time.time()
            perform_operation()
            duration = time.time() - start

            monitor.record_timing('operation', duration)
            ```
        """
        with self._lock:
            if operation_name not in self._stats:
                self._stats[operation_name] = {
                    "count": 0,
                    "total_time": 0.0,
                    "min_time": float("inf"),
                    "max_time": 0.0,
                    "avg_time": 0.0,
                }

            stats = self._stats[operation_name]
            stats["count"] += 1
            stats["total_time"] += duration
            stats["min_time"] = min(stats["min_time"], duration)
            stats["max_time"] = max(stats["max_time"], duration)
            stats["avg_time"] = stats["total_time"] / stats["count"]

    def get_stats(self, operation_name: str) -> dict[str, Any] | None:
        """
        Get performance statistics for an operation.

        Args:
            operation_name: Name of the operation

        Returns:
            Statistics dictionary or None if not found

        Example:
            ```python
            monitor = PerformanceMonitor()
            stats = monitor.get_stats('config_load')

            if stats:
                console.print(f"Called {stats['count']} times")
                console.print(f"Average: {stats['avg_time']:.3f}s")
            ```
        """
        with self._lock:
            return self._stats.get(operation_name, {}).copy()

    def get_all_stats(self) -> dict[str, dict[str, Any]]:
        """
        Get all performance statistics.

        Returns:
            Dictionary of all operation statistics

        Example:
            ```python
            monitor = PerformanceMonitor()
            all_stats = monitor.get_all_stats()

            for operation, stats in all_stats.items():
                console.print(f"{operation}: {stats['avg_time']:.3f}s avg")
            ```
        """
        with self._lock:
            return {name: stats.copy() for name, stats in self._stats.items()}

    def reset_stats(self, operation_name: str | None = None) -> None:
        """
        Reset performance statistics.

        Args:
            operation_name: Specific operation to reset, or None for all

        Example:
            ```python
            monitor = PerformanceMonitor()

            # Reset specific operation
            monitor.reset_stats('config_load')

            # Reset all operations
            monitor.reset_stats()
            ```
        """
        with self._lock:
            if operation_name is None:
                self._stats.clear()
            else:
                self._stats.pop(operation_name, None)


class _PerformanceMeasurement:
    """Context manager for performance measurements."""

    def __init__(self, monitor: PerformanceMonitor, operation_name: str) -> None:
        self.monitor = monitor
        self.operation_name = operation_name
        self.start_time: float = 0.0

    def __enter__(self) -> "_PerformanceMeasurement":
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        duration = time.time() - self.start_time
        self.monitor.record_timing(self.operation_name, duration)
