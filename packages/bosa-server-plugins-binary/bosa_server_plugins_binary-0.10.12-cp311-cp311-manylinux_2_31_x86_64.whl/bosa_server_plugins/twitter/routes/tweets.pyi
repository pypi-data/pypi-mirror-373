from _typeshed import Incomplete
from bosa_server_plugins.handler import Router as Router
from bosa_server_plugins.twitter.auth.auth import TwitterClient as TwitterClient
from bosa_server_plugins.twitter.helpers.connect import get_multiple_tweet as get_multiple_tweet, search_recent_tweets as search_recent_tweets
from bosa_server_plugins.twitter.helpers.tweets import build_tweet_thread as build_tweet_thread
from bosa_server_plugins.twitter.requests.tweets import GetThreadRequest as GetThreadRequest, GetTweetsRequest as GetTweetsRequest, TweetsRequest as TweetsRequest

class TweetRoutes:
    """Registers tweet-related endpoints to a FastAPI router.

    This class handles routing for Twitter operations such as searching for tweets
    using the Twitter API. It defines and binds the necessary endpoints when initialized.
    """
    router: Incomplete
    twitter_client: Incomplete
    def __init__(self, router: Router, twitter_client: TwitterClient) -> None:
        """Initializes the TweetRoutes with a FastAPI router and Twitter API authentication.

        Args:
            router (Router): The FastAPI APIRouter instance to register routes on.
            twitter_client (TwitterClient): The authentication object for accessing the Twitter API.
        """
