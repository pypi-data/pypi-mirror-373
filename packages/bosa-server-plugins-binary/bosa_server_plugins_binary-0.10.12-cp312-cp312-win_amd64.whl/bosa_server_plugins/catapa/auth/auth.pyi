from abc import ABC
from bosa_core.authentication.plugin.repository.models import ThirdPartyIntegrationAuth as ThirdPartyIntegrationAuth
from typing import Any

class CatapaCredentials(ABC):
    """Catapa authentication scheme."""
    access_token: str
    refresh_token: str
    tenant: str
    integration: ThirdPartyIntegrationAuth | None
    def __init__(self, access_token: str, refresh_token: str, tenant: str, integration: object | None = None) -> None:
        """Initialize Catapa authentication scheme.

        Args:
            access_token (str): The access token
            refresh_token (str): The refresh token
            tenant (str): The tenant ID
            integration(ThirdPartyIntegrationAuth): The integration object for refresh operations (optional)
        """
    def get_headers(self) -> dict[str, str]:
        """Get the headers for API requests.

        Returns:
            Dict[str, str]: The headers with Authorization and Tenant
        """
    def get_auth_data(self) -> dict[str, Any]:
        """Get the auth data for token storage.

        Returns:
            Dict[str, Any]: The auth data
        """
