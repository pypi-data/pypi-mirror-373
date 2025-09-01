from _typeshed import Incomplete
from bosa_server_plugins.handler import Router as Router
from bosa_server_plugins.twitter.auth.auth import TwitterClient as TwitterClient
from bosa_server_plugins.twitter.requests.users import GetUsersRequest as GetUsersRequest

class UserRoutes:
    """Class to define user-related routes for the Twitter API."""
    router: Incomplete
    twitter_client: Incomplete
    def __init__(self, router: Router, twitter_client: TwitterClient) -> None:
        """Initialize UserRoutes with a router and an authentication token.

        Args:
            router (Router): The router instance to register the routes.
            twitter_client (TwitterClient): The authentication object for accessing the Twitter API.
        """
