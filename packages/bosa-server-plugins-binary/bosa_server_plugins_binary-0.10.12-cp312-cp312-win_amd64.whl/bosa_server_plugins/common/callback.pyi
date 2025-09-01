from _typeshed import Incomplete
from bosa_server_plugins.cache.interface import CacheService as CacheService
from typing import Awaitable, Callable, TypeVar, overload

T = TypeVar('T')
CALLBACK_URL_CACHE_KEY_FORMAT: str
DEFAULT_TIMEOUT: int
DEFAULT_MAX_RETRIES: int
DEFAULT_BASE_DELAY: float
logger: Incomplete

@overload
def with_callbacks() -> Callable[[Callable[..., Awaitable[tuple[T, list[str]]]]], Callable[..., Awaitable[T]]]: ...
@overload
def with_callbacks() -> Callable[[Callable[..., tuple[T, list[str]]]], Callable[..., T]]: ...
def save_callback_urls(cache_service: CacheService, cache_key: str, urls: list[str]) -> None:
    """Save callback URLs to cache."""
def delete_callback_urls(cache_service: CacheService, cache_key: str) -> None:
    """Delete callback URLs from cache."""
def get_callback_urls(cache_service: CacheService, cache_key: str) -> list[str]:
    """Get callback URLs from cache."""
