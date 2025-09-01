from typing import Callable, TypeVar

T = TypeVar('T', bound=Callable)

def public(func: T) -> T:
    """Decorator to mark an endpoint as an endpoint that requires no authentication.

    Args:
        func: The function to decorate

    Returns:
        The decorated function
    """
def exclude_from_mcp(func: T) -> T:
    """Decorator to mark an endpoint as an endpoint that should be excluded from MCP.

    Args:
        func: The function to decorate

    Returns:
        The decorated function
    """
