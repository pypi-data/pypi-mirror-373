from bosa_server_plugins.cache.interface import CacheService as CacheService
from bosa_server_plugins.cache.redis import RedisCacheService as RedisCacheService

__all__ = ['CacheService', 'RedisCacheService']
