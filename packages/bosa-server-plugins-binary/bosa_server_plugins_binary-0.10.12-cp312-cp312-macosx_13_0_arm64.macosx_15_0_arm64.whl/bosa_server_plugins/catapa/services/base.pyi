from _typeshed import Incomplete
from bosa_core import ConfigService as ConfigService
from bosa_core.authentication.plugin.service import ThirdPartyIntegrationService as ThirdPartyIntegrationService
from bosa_server_plugins.catapa.auth.auth import CatapaCredentials as CatapaCredentials
from typing import Any

class CatapaServiceBase:
    """Base class for Catapa API services."""
    DEFAULT_TIMEOUT: int
    credentials: Incomplete
    config: Incomplete
    third_party_integration_service: Incomplete
    def __init__(self, credentials: CatapaCredentials, config: ConfigService, third_party_integration_service: ThirdPartyIntegrationService) -> None:
        """Initialize the Catapa service with credentials.

        Args:
            credentials (CatapaCredentials): The credentials for the service
            config (ConfigService, optional): The config service for getting client credentials
            third_party_integration_service (ThirdPartyIntegrationService): Service for updating integrations
        """
    @property
    def base_url(self) -> str:
        """Get the base URL from config."""
    @property
    def api_version(self) -> str:
        """Get the default API version from config."""
    @staticmethod
    def is_oauth_endpoint(endpoint: str) -> bool:
        """Check if the endpoint is an OAuth endpoint."""
    @staticmethod
    def is_token_related_error(error_message: str) -> bool:
        """Check if the error message is related to token."""
    def refresh_token(self) -> dict[str, Any]:
        """Refresh the integration tokens.

        Args:
            existing_integration (ThirdPartyIntegrationAuth): The existing integration to refresh

        Returns:
            Dict[str, Any]: The refresh result with new token information

        Raises:
            requests.RequestException: If the refresh token fails
        """
