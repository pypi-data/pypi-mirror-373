from _typeshed import Incomplete
from bosa_connectors.action import Action as Action
from bosa_connectors.action_response import ActionResponse as ActionResponse
from bosa_connectors.auth import ApiKeyAuthenticator as ApiKeyAuthenticator
from bosa_connectors.helpers.authenticator import BosaAuthenticator as BosaAuthenticator
from bosa_connectors.helpers.integrations import BosaIntegrationHelper as BosaIntegrationHelper
from bosa_connectors.models.file import ConnectorFile as ConnectorFile
from bosa_connectors.models.result import ActionResult as ActionResult
from bosa_connectors.models.token import BosaToken as BosaToken
from bosa_connectors.models.user import BosaUser as BosaUser, CreateUserResponse as CreateUserResponse
from bosa_connectors.module import BosaConnectorError as BosaConnectorError, BosaConnectorModule as BosaConnectorModule
from typing import Annotated, Any

class BosaConnector:
    """Main connector class that manages all BOSA connector modules."""
    DEFAULT_TIMEOUT: int
    DEFAULT_MAX_ATTEMPTS: int
    OAUTH2_FLOW_ENDPOINT: str
    INTEGRATION_CHECK_ENDPOINT: str
    api_base_url: Incomplete
    auth_scheme: Incomplete
    bosa_authenticator: Incomplete
    bosa_integration_helper: Incomplete
    def __init__(self, api_base_url: str = 'https://api.bosa.id', api_key: str = 'bosa') -> None:
        """Initialization."""
    def get_available_modules(self) -> list[str]:
        """Scan and cache all available connector modules.

        Returns:
            List of available modules
        """
    def create_bosa_user(self, identifier: str) -> CreateUserResponse:
        """Create a BOSA User in the scope of BOSA API.

        Args:
            identifier: BOSA Username

        Returns:
            BOSA User Data with the secret
        """
    def authenticate_bosa_user(self, identifier: str, secret: str) -> BosaToken:
        """Triggers the authentication of the BOSA User in the scope of BOSA API.

        Args:
            identifier: BOSA Username
            secret: BOSA Password

        Returns:
            BOSA User Token
        """
    def initiate_connector_auth(self, app_name: str, token: str, callback_uri: str) -> str:
        """Triggers the OAuth2 flow for a connector for this API Key and User Token.

        Args:
            app_name: The name of the app/connector to use
            token: The BOSA User Token
            callback_uri: The callback URL to be used for the integration

        Returns:
            The redirect URL to be used for the integration
        """
    def initiate_plugin_configuration(self, app_name: str, token: str, config: dict[str, Any]) -> ActionResult:
        """Initiates a plugin configuration for a given app/connector.

        Args:
            app_name: The name of the app/connector to use
            token: The BOSA User Token
            config: The configuration for the integration

        Returns:
            Result that contains an error message (if any), and the success status.
        """
    def get_user_info(self, token: str) -> BosaUser:
        """Gets the user information for a given token.

        Args:
            token: The BOSA User Token

        Returns:
            BOSA User
        """
    def user_has_integration(self, app_name: str, token: str) -> bool:
        """Checks whether or not a user has an integration for a given app in this client.

        Args:
            app_name: The name of the app/connector to use
            token: The BOSA User Token

        Returns:
            True if the user has an integration for the given app
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
            app_name: The name of the app/connector to use
            token: The BOSA User Token
            user_identifier: User identifier to specify which integration to get

        Returns:
            The integration data as a dictionary
        """
    def remove_integration(self, app_name: str, token: str, user_identifier: str) -> ActionResult:
        """Removes a 3rd party integration for a user against a certain client.

        Args:
            token: The BOSA User Token
            app_name: The name of the app/connector to use
            user_identifier: User identifier to specify which integration to remove

        Returns:
            Result that contains an error message (if any), and the success status.
        """
    def get_connector(self, app_name: str) -> BosaConnectorModule:
        """Get or create an instance of a connector module.

        Args:
            app_name: The name of the app/connector to use

        Returns:
            BosaConnectorModule: The connector module
        """
    def refresh_connector(self, app_name: str) -> None:
        """Refresh the connector module."""
    def connect(self, app_name: str) -> Action:
        """Connect to a specific module and prepare for action execution.

        Creates an Action instance for the specified connector..

        Example:
            # Create action builders for different connectors
            github = bosa.connect('github')
            gdrive = bosa.connect('google_drive') # This is just an example

        Args:
            app_name: The name of the app/connector to use (eg: 'github', 'google_drive', etc)

        Returns:
            Action: A new Action instance for the specified connector
        """
    def execute(self, app_name: str, action: str, *, identifier: str | None = None, account: Annotated[str | None, None] = None, max_attempts: int = ..., input_: dict[str, Any] = None, token: str | None = None, headers: dict[str, str] | None = None, timeout: int | None = ..., **kwargs) -> tuple[dict[str, Any] | ConnectorFile, int]:
        """Execute an action on a specific module and return raw response.

        The method supports both ways of passing parameters:
        1. As a dictionary: execute(app_name, action, params_dict)
        2. As keyword arguments: execute(app_name, action, param1=value1, param2=value2)

        Args:
            app_name: The name of the app/connector to use
            action: The action to execute
            input_: Optional input data for the action
            token: The BOSA User Token
            identifier: Optional user integration account identifier
            account: Optional user integration account identifier (deprecated, remove this in the future)
            headers: Optional headers to include in the request
            max_attempts: The number of times the request can be retried for. Default is 0 (does not retry). Note that
                the backoff factor is 2^(N - 1) with the basic value being 1 second (1, 2, 4, 8, 16, 32, ...).
                Maximum number of retries is 10 with a maximum of 64 seconds per retry.
            timeout: Optional timeout for the request in seconds. Default is 30 seconds.
            **kwargs: Optional keyword arguments

        Returns:
            Tuple of (response, status_code) where response is the API response and status_code is the HTTP status code
        """
    def run(self, app_name: str, action: str, *, identifier: str | None = None, account: Annotated[str | None, None] = None, max_attempts: int = ..., input_: dict[str, Any] = None, token: str | None = None, headers: dict[str, str] | None = None, timeout: int | None = ..., **kwargs) -> ActionResponse:
        """Execute an action on a specific module and return paginated response.

        The method supports both ways of passing parameters:
        1. As a dictionary: execute(app_name, action, input_dict)
        2. As keyword arguments: execute(app_name, action, param1=value1, param2=value2)

        Args:
            app_name: The name of the app/connector to use
            action: The action to execute
            input_: Optional input data for the action
            token: The BOSA User Token
            identifier: Optional user identifier to use for the request
            account: Optional user identifier to use for the request (deprecated, remove this in the future)
            headers: Optional headers to include in the request
            max_attempts: The number of times the request can be retried for. Default is 0 (does not retry). Note that
                the backoff factor is 2^(N - 1) with the basic value being 1 second (1, 2, 4, 8, 16, 32, ...).
                Maximum number of retries is 10 with a maximum of 64 seconds per retry.
            timeout: Optional timeout for the request in seconds. Default is 30 seconds.
            **kwargs: Optional keyword arguments

        Returns:
            ActionResponse: Response wrapper with pagination support
        """
