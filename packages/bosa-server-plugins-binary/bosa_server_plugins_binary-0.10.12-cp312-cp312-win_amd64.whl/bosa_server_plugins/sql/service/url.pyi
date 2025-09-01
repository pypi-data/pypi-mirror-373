from bosa_server_plugins.sql.config import SqlConfig as SqlConfig
from typing import Any

class SqlUrlService:
    """Service for handling SQL database connection URLs."""
    @staticmethod
    def encode_credentials(credential: str) -> str:
        """Encodes credentials for safe use in URLs.

        Args:
            credential: The credential string to encode.

        Returns:
            The URL-encoded credential string.
        """
    @staticmethod
    def encode_url_credentials(url: str) -> str:
        """Encodes credentials in a provided URL to handle special characters.

        Args:
            url: The database URL that may contain unencoded credentials.

        Returns:
            The URL with properly encoded credentials.
        """
    @staticmethod
    def build_url_from_config(configuration: SqlConfig) -> str:
        """Builds a database URL from configuration.

        Args:
            configuration: The SQL configuration object.

        Returns:
            The properly formatted database URL with encoded credentials.
        """
    @staticmethod
    def build_safe_url(url: str) -> str:
        """Builds a safe database URL by encoding any problematic credentials.

        This is a convenience method for when you have a URL string that may
        contain unencoded credentials with special characters.

        Args:
            url: The database URL string.

        Returns:
            The URL with safely encoded credentials.
        """
    @staticmethod
    def parse_url_for_hash(url: str) -> dict[str, Any]:
        """Parses a URL to extract components for configuration hashing.

        Args:
            url: The database URL to parse.

        Returns:
            Dictionary containing parsed URL components with decoded credentials.
        """
    @staticmethod
    def build_configuration_hash(configuration: SqlConfig) -> str:
        """Builds a configuration hash from SQL configuration.

        The configuration hash is a unique string identifying the SQL configuration,
        built as: driver:host:port:user:database

        Args:
            configuration: The SQL configuration object.

        Returns:
            The configuration hash string.
        """
