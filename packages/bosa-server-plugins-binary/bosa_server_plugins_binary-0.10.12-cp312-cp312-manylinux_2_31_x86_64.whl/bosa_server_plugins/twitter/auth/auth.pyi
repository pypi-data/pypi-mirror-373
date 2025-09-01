class TwitterClient:
    """Handles Twitter API authentication using bearer tokens."""
    def __new__(cls, token: str):
        """Creates a new instance of TwitterClient or returns the existing instance.

        This method initializes the Twitter API client with the provided bearer token
        if no instance exists. It ensures that only one instance of TwitterClient is created
        (singleton pattern).

        Args:
            cls: The class of the instance being created.
            token (str): The bearer token for authenticating with the Twitter API.

        Returns:
            TwitterClient: The singleton instance of TwitterClient.
        """
    def get_client(self):
        """Retrieves the Twitter API client.

        This method returns the initialized Twitter API client, which can be used
        to make requests to the Twitter API.

        Returns:
            tweepy.Client: The Twitter API client instance.
        """
