from .response import ApiResponse as ApiResponse
from enum import Enum
from typing import Any, Callable, TypeVar

class HttpMethod(Enum):
    """HTTP methods supported by the router."""
    GET = ...
    POST = ...
    PUT = ...
    PATCH = ...
    DELETE = ...
    HEAD = ...
    OPTIONS = ...
T = TypeVar('T')
RouteHandler = Callable[..., T]
Routes = dict[str, dict[HttpMethod, RouteHandler[Any]]]

class Router:
    """Handler for plugin routes with support for all HTTP methods."""
    def __init__(self) -> None:
        """Constructor."""
    def add_route(self, method: HttpMethod, path: str, handler: RouteHandler[T]) -> None:
        """Register a route with its handler function.

        Args:
            method: The HTTP method for this route
            path: The URL path for the route
            handler: The function that will handle this route
        """
    def route(self, path: str, methods: HttpMethod | list[HttpMethod]) -> Callable[[RouteHandler[T]], RouteHandler[ApiResponse[T, Any]]]:
        '''Decorator for registering route handlers.

        Args:
            path: The URL path for the route
            methods: HTTP method(s) for this route

        Example:
            @router.route("/users", HttpMethod.GET)
            async def get_users():
                ...

            @router.route("/users", [HttpMethod.POST, HttpMethod.PUT])
            async def create_or_update_user():
                ...
        '''
    def get(self, path: str) -> Callable[[RouteHandler[T]], RouteHandler[ApiResponse[T, Any]]]:
        """Decorator for GET routes."""
    def post(self, path: str) -> Callable[[RouteHandler[T]], RouteHandler[ApiResponse[T, Any]]]:
        """Decorator for POST routes."""
    def put(self, path: str) -> Callable[[RouteHandler[T]], RouteHandler[ApiResponse[T, Any]]]:
        """Decorator for PUT routes."""
    def patch(self, path: str) -> Callable[[RouteHandler[T]], RouteHandler[ApiResponse[T, Any]]]:
        """Decorator for PATCH routes."""
    def delete(self, path: str) -> Callable[[RouteHandler[T]], RouteHandler[ApiResponse[T, Any]]]:
        """Decorator for DELETE routes."""
    def get_routes(self) -> list[tuple[HttpMethod, str, RouteHandler[Any]]]:
        """Get all registered routes.

        Returns:
            List of tuples containing (method, path, handler)
        """
