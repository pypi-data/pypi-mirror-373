from bosa_server_plugins.twitter.auth.auth import TwitterClient as TwitterClient
from bosa_server_plugins.twitter.helpers.connect import get_multiple_tweet as get_multiple_tweet, get_users as get_users, search_recent_tweets as search_recent_tweets
from bosa_server_plugins.twitter.requests.tweets import GetThreadRequest as GetThreadRequest, GetTweetsRequest as GetTweetsRequest, TweetsRequest as TweetsRequest
from bosa_server_plugins.twitter.requests.users import GetUsersRequest as GetUsersRequest

def build_tweet_thread(twitter_client: TwitterClient, request: GetThreadRequest) -> dict:
    """Builds a thread of tweets from a given tweet ID.

    Args:
        twitter_client (TwitterClient): Authentication for the Twitter API.
        request (GetThreadRequest): Contains the tweet ID to start the thread.

    Returns:
        dict: A dictionary of tweets in the thread, including the original tweet and replies, or an error response.
    """
