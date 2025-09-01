from bosa_core.exception import BosaException

class GraphQLError(BosaException):
    """Exception for GraphQL errors."""
    def __init__(self, message: str, extra_dict: dict = None) -> None:
        """Initialize the GraphQLError exception.

        Args:
            message (str): The error message.
            extra_dict (dict, optional): Additional information to include in the exception.
        """
