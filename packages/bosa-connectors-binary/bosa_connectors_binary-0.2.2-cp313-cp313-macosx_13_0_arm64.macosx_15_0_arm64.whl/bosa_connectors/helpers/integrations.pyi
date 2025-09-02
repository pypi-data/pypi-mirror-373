from _typeshed import Incomplete
from bosa_connectors.auth import ApiKeyAuthenticator as ApiKeyAuthenticator
from bosa_connectors.models.result import ActionResult as ActionResult
from typing import Any

class BosaIntegrationHelper:
    """Helper class for BOSA API integrations."""
    OAUTH2_FLOW_ENDPOINT: str
    INTEGRATION_USER_ENDPOINT: str
    INTEGRATION_CHECK_ENDPOINT: str
    DEFAULT_TIMEOUT: int
    api_base_url: Incomplete
    auth_scheme: Incomplete
    def __init__(self, api_base_url: str = 'https://api.bosa.id', api_key: str = 'bosa') -> None:
        '''Initializes the BosaIntegrationHelper with the provided API key.

        Args:
            api_base_url (str): The base URL for the BOSA API. Defaults to "https://api.bosa.id".
            api_key (str): The API key for authentication. Defaults to "bosa".
        '''
    def user_has_integration(self, app_name: str, token: str) -> bool:
        """Checks whether or not a user has an integration for a given app in this client.

        Args:
            app_name: The name of the app/connector to use
            token: The BOSA User Token

        Returns:
            True if the user has an integration for the given app
        """
    def initiate_integration(self, app_name: str, token: str, callback_uri: str) -> str:
        """Initiates a 3rd party integration for a user against a certain client.

        Args:
            app_name: The name of the app/connector to use
            token: The BOSA User Token
            callback_uri: The callback URL to be used for the integration

        Returns:
            The integration URL
        """
    def initiate_plugin_configuration(self, app_name: str, token: str, config: dict[str, Any]) -> ActionResult:
        """Initiates a plugin configuration for a given app/connector.

        Used to initiate a connector that requires a plugin configuration and may not
        support the OAuth2 flow.
        
        Args:
            app_name: The name of the app/connector to use
            token: The BOSA User Token
            config: The configuration for the integration

        Returns:
            Result that contains an error message (if any), and the success status.
        """
    def select_integration(self, app_name: str, token: str, user_identifier: str) -> ActionResult:
        """Selects a 3rd party integration for a user against a certain client.

        Args:
            token: The BOSA User Token
            app_name: The name of the app/connector to use
            user_identifier: User identifier to specify which integration to select

        Returns:
            Result that contains an error message (if any), and the success status.
        """
    def get_integration(self, app_name: str, token: str, user_identifier: str) -> dict:
        """Gets a 3rd party integration for a user against a certain client.

        Args:
            token: The BOSA User Token
            app_name: The name of the app/connector to use
            user_identifier: User identifier to specify which integration to get

        Returns:
            Result that contains an error message (if any), and the success status.
        """
    def remove_integration(self, app_name: str, token: str, user_identifier: str) -> ActionResult:
        """Removes a 3rd party integration for a user against a certain client.

        Args:
            app_name: The name of the app/connector to use
            token: The BOSA User Token
            user_identifier: User identifier to specify which integration to remove

        Returns:
            Result that contains an error message (if any), and the success status.
        """
