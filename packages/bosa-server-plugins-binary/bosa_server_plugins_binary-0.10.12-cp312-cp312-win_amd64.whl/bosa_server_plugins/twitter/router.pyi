from bosa_server_plugins.handler import Router as Router
from bosa_server_plugins.twitter.auth.auth import TwitterClient as TwitterClient
from bosa_server_plugins.twitter.routes.tweets import TweetRoutes as TweetRoutes
from bosa_server_plugins.twitter.routes.users import UserRoutes as UserRoutes

class TwitterApiRoutes:
    """Defines and registers Twitter-related API routes with a FastAPI router.

    This class is responsible for initializing and organizing all Twitter endpoint
    routes, such as tweet search or thread retrieval, using the provided Twitter API token.
    """
    router: Router
    twitter_client: TwitterClient
    def __init__(self, router: Router, twitter_client: TwitterClient) -> None:
        """Initializes the TwitterApiRoutes with a FastAPI router and Twitter API authentication.

        This constructor sets up the routing for Twitter-related endpoints by
        initializing sub-routes such as TweetRoutes.

        Args:
            router (Router): The FastAPI router where routes will be registered.
            twitter_client (TwitterClient): The authentication object for accessing the Twitter API.
        """
