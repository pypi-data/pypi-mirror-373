from typing import Any, TypeVar

T = TypeVar('T')

class CacheService:
    """Cache interface template."""
    @staticmethod
    def build_key(namespace: str, *args: Any) -> str:
        """Build cache key.

        Args:
            namespace (str): The namespace of the cache
            *args (Any): The arguments of the cache

        Returns:
            str: The cache key
        """
    def set(self, key: str, value: str, ttl: int | None = None):
        """Set a value with a TTL (Time To Live).

        Args:
            key (str): The key of the cache
            value (str): The value of the cache
            ttl (int, optional): The TTL of the cache. Defaults to None.
        """
    def get(self, key: str, clazz: type[T] | None = None) -> T | None:
        """Get a value from cache.

        Args:
            key (str): The key of the cache
            clazz (Type[T], optional): The class of the cache. Defaults to None.

        Returns:
            T | None: The value of the cache
        """
    def delete(self, key: str) -> None:
        """Delete a value from cache.

        Args:
            key (str): The key of the cache
        """
