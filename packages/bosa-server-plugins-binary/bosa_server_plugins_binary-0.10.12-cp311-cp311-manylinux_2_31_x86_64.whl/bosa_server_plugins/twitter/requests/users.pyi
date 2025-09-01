from bosa_server_plugins.handler import BaseRequestModel as BaseRequestModel

class GetUsersRequest(BaseRequestModel):
    """Request model for searching user by ID(s) / username(s).

    This model allows the user to specify either user ID(s) or username(s) to retrieve user information(s).
    It enforces that at least one of the two fields must be provided to successfully make a request.

    Note:
        - Only one of the four fields must be provided to successfully make a request.
        - If multiple fields are provided, the request will throw an error.
    """
    id: str | None
    ids: list[str] | None
    username: str | None
    usernames: list[str] | None
    user_fields: list[str] | None
    expansions: list[str] | None
    tweet_fields: list[str] | None
    @classmethod
    def validate_fields(cls, data):
        """Validates whether only one of the four fields is provided."""
    @classmethod
    def validate_user_fields(cls, value):
        """Validates user_fields and removes duplicates."""
    @classmethod
    def validate_expansions(cls, value):
        """Validates expansions and removes duplicates."""
    @classmethod
    def validate_tweet_fields(cls, value):
        """Validates tweet_fields and removes duplicates."""
