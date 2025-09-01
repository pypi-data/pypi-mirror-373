from _typeshed import Incomplete
from bosa_server_plugins.cache.interface import CacheService as CacheService
from typing import TypeVar

T = TypeVar('T')

class RedisCacheService(CacheService):
    """Redis Cache Interface."""
    client: Incomplete
    def __init__(self, *, host: str | None = None, port: int | None = None, db: int = 0, password: str | None = None, tls_enabled: bool | None = None) -> None:
        """Initialize the connection pool.

        Prioritizes arguments over environment variables. If arguments are not provided,
        the environment variables are used.

        Args:
            host (str, optional): The host of the Redis server. Defaults to None.
            port (int, optional): The port of the Redis server. Defaults to None.
            db (int, optional): The database number. Defaults to 0.
            password (str, optional): The password of the Redis server. Defaults to None.
            tls_enabled (bool, optional): Whether to use TLS. Defaults to False.
        """
    def set(self, key: str, value: str, ttl: int | None = None) -> None:
        """Set a value with a TTL (Time To Live).

        Args:
            key (str): The key of the value.
            value (str): The value to be set.
            ttl (int, optional): The time to live of the value. Defaults to None.

        Returns:
            None
        """
    def get(self, key: str, clazz: type[T] | None = None) -> T | None:
        """Get a value from cache.

        Args:
            key (str): The key of the value.
            clazz (Type[T], optional): The class of the value. Defaults to None.

        Returns:
            T | None: The value, or None if not found.
        """
    def delete(self, key: str) -> None:
        """Delete a value from cache.

        Args:
            key (str): The key of the value.

        Returns:
            None
        """
