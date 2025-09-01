from typing import Any

def serialize_cache_data(data: Any) -> str:
    """Serialize data for caching.

    Converts Python objects to JSON strings for cache storage.
    String values are stored as-is.

    Args:
        data (Any): The data to serialize.

    Returns:
        str: Serialized data as a string.
    """
def deserialize_cache_data(data: bytes | str) -> Any:
    """Deserialize data from cache.

    Handles special processing value and JSON deserialization.

    Args:
        data (bytes or str): The serialized data from cache.

    Returns:
        Any: Deserialized data or processing value.
    """
