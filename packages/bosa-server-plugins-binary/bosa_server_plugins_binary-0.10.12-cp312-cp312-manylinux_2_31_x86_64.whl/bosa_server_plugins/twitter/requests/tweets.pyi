from bosa_server_plugins.handler import BaseRequestModel as BaseRequestModel

class TweetsRequest(BaseRequestModel):
    """Request model for searching."""
    query: str
    end_time: str | None
    start_time: str | None
    sort_order: str | None
    lang: str | None
    max_results: int | None
    tweet_fields: list[str] | None
    expansions: list[str] | None
    media_fields: list[str] | None
    since_id: str | None
    until_id: str | None
    next_token: str | None
    place_fields: list[str] | None
    poll_fields: list[str] | None
    user_fields: list[str] | None
    def to_search_recent_params(self) -> dict:
        """Convert the request attributes to a dictionary for searching recent tweets."""

class GetTweetsRequest(BaseRequestModel):
    """Request model for retrieving multiple tweets by their IDs."""
    ids: list[str]
    expansions: list[str] | None
    media_fields: list[str] | None
    place_fields: list[str] | None
    poll_fields: list[str] | None
    tweet_fields: list[str] | None
    user_fields: list[str] | None
    def to_lookup_tweets_params(self) -> dict:
        """Convert the request attributes to a dictionary for lookup tweets."""

class GetThreadRequest(BaseRequestModel):
    """Request model for retrieving multiple tweets by their IDs."""
    id: str
