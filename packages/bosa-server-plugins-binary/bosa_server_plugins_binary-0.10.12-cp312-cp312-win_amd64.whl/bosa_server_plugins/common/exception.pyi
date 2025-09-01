from bosa_core.exception import BosaException

class IntegrationExistsException(BosaException):
    """Exception raised when an integration already exists for a user and client."""
    def __init__(self, plugin_name: str, user_id: str) -> None:
        """Initialize the exception with the plugin name.

        Args:
            plugin_name (str): The name of the plugin that already exists.
            user_id (str): The user ID associated with the existing integration.
        """

class IntegrationDoesNotExistException(BosaException):
    """Raised when an integration or account does not exist for the requested connector."""
    def __init__(self, plugin_name: str, user_id: str = 'DEFAULT') -> None:
        '''Create the exception.

        Args:
            plugin_name (str): Connector / plugin name (e.g. "github").
            user_id (str): Account identifier or "DEFAULT" for the default account.
        '''
