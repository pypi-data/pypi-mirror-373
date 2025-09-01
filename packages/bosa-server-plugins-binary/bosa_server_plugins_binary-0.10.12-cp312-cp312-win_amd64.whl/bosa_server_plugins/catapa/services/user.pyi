from bosa_core import ConfigService as ConfigService
from bosa_core.authentication.plugin.service import ThirdPartyIntegrationService as ThirdPartyIntegrationService
from bosa_server_plugins.catapa.auth.auth import CatapaCredentials as CatapaCredentials
from bosa_server_plugins.catapa.services.base import CatapaServiceBase as CatapaServiceBase
from typing import Any

class CatapaUserInfoService(CatapaServiceBase):
    """Service class for Catapa user info API."""
    def __init__(self, credentials: CatapaCredentials, config: ConfigService, third_party_integration_service: ThirdPartyIntegrationService) -> None:
        """Initialize the Catapa user info service with credentials.

        Args:
            credentials (CatapaCredentials): The credentials for the service
            config (ConfigService): The config service
            third_party_integration_service (ThirdPartyIntegrationService): Service for updating integrations
        """
    def get_user_info(self) -> dict[str, Any]:
        """Get user information from Catapa API.

        Returns:
            User: User information from /users/me endpoint
        """
