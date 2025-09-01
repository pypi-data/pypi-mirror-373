from _typeshed import Incomplete
from bosa_core.authentication.client.service import ClientAwareService as ClientAwareService
from bosa_core.authentication.plugin.repository.models import ThirdPartyIntegrationAuth as ThirdPartyIntegrationAuth
from bosa_core.authentication.plugin.service import ThirdPartyIntegrationService as ThirdPartyIntegrationService
from bosa_core.authentication.token.service import VerifyTokenService as VerifyTokenService
from bosa_server_plugins.cache import CacheService as CacheService

class IntegrationHelper:
    """Helper class for integration operations."""
    DEFAULT_TOKEN_LENGTH: int
    DEFAULT_STATE_TTL: Incomplete
    token_length: int
    state_ttl: int
    connector_name: str
    cache: CacheService
    third_party_integration_service: ThirdPartyIntegrationService
    token_service: VerifyTokenService
    client_aware_service: ClientAwareService
    def __init__(self, connector_name: str, cache: CacheService, third_party_integration_service: ThirdPartyIntegrationService, token_service: VerifyTokenService, client_aware_service: ClientAwareService, token_length: int = ..., state_ttl: int = ...) -> None:
        """Initialize the integration helper with required services.

        Args:
            connector_name: The name of the connector
            cache: The cache service
            third_party_integration_service: The third-party integration service
            token_service: The token service
            client_aware_service: The client-aware service
            token_length: The length of the token
            state_ttl: The TTL of the state
        """
    def create_state_hash(self, args: dict[str, str], callback_url: str) -> str:
        """Creates a state hash that will be validated by our app to ensure security.

        Side-effect: This will also save to cache using cache_service for as long as the
        state_ttl duration.

        Args:
            args: the args to be encoded in the state
            callback_url: the callback url for later use when use has successfully given access.

        Returns:
            State string that comprises the following: args and state_code. State-code is guaranteed to be
            URL-Safe.
        """
    def decode_state(self, state: str) -> dict:
        """Decodes the state.

        Args:
            state: The state to decode.

        Returns:
            dict: The decoded state.
        """
    def validate_state(self, args: dict[str, str]) -> str:
        """Checks whether or the state exists. If it does, means that the state is valid.

        Side-effect: Once validated, we will delete the state from the cache.

        Args:
            args: the args to be validated

        Returns:
            str: the callback URL
        """
    def get_integration_by_name(self, user_identifier: str, token: str, api_key: str) -> ThirdPartyIntegrationAuth | None:
        """Get integration by name for a specific connector.

        Args:
            user_identifier: The user identifier to get integration for
            token: The bearer token (without 'Bearer ' prefix)
            api_key: The API key for client authentication

        Returns:
            The integration object if found

        Raises:
            NotFoundException: If integration is not found
        """
    def validate_can_get_integration(self, x_api_key: str) -> None:
        """Validates if the API key is allowed to get integration.

        Args:
            x_api_key: The API key to validate

        Raises:
            UnauthorizedException: If the API key is not valid
        """
