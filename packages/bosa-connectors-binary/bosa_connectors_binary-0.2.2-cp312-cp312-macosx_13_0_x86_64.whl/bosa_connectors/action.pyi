from bosa_connectors.action_response import ActionResponse as ActionResponse
from bosa_connectors.auth import BaseAuthenticator as BaseAuthenticator
from bosa_connectors.models.file import ConnectorFile as ConnectorFile
from bosa_connectors.module import BosaConnectorModule as BosaConnectorModule
from typing import Annotated, Any

class ActionExecutor:
    """Represents a specific action execution for a service.

    Example:
        # Direct execution with raw response
        data, status = github.action('list_pull_requests')            .params({'owner': 'GDP-ADMIN', 'repo': 'bosa'})            .execute()

        # Or with pagination support
        response = github.action('list_pull_requests')            .params({'owner': 'GDP-ADMIN', 'repo': 'bosa'})            .run()

        # Get data and handle pagination
        data = response.get_data()
        while response.has_next():
            response = response.next_page()
            data = response.get_data()
    """
    DEFAULT_MAX_ATTEMPTS: int
    DEFAULT_TIMEOUT: int
    def __init__(self, module: BosaConnectorModule, authenticator: BaseAuthenticator, action: str) -> None:
        """Initialize the action executor.

        Args:
            module: The connector module to execute against
            authenticator: The authenticator to use for requests
            action: The action name to execute
        """
    def params(self, params: dict[str, Any]) -> ActionExecutor:
        """Set additional parameters."""
    def account(self, account: Annotated[str | None, None]) -> ActionExecutor:
        """Set the user account for the action.

        deprecated:: future version
            The `account` method is deprecated and will be removed in future version.
            Use `identifier()` instead.
        """
    def identifier(self, identifier: str | None = None) -> ActionExecutor:
        """Set the user identifier for the action."""
    def headers(self, headers: dict[str, str]) -> ActionExecutor:
        """Set request headers."""
    def max_attempts(self, attempts: int) -> ActionExecutor:
        """Set maximum retry attempts."""
    def token(self, token: str | None) -> ActionExecutor:
        """Set the BOSA user token for this action."""
    def timeout(self, timeout: int | None) -> ActionExecutor:
        """Set the timeout for the request."""
    def execute(self) -> tuple[dict[str, Any] | ConnectorFile, int]:
        """Execute request and return raw response.

        Returns:
            Tuple of (response_data, status_code)
        """
    def run(self) -> ActionResponse:
        """Execute request and return paginated response.

        Returns an ActionResponse that supports pagination for list responses.
        For single item responses, pagination methods will return the same item.

        Returns:
            ActionResponse with pagination support
        """

class Action:
    """Base class for plugins to prepare action execution.

    Example:
        # Create a GitHub connector
        github = bosa.connect('github')

        # Execute with raw response
        data, status = github.action('list_pull_requests')            .params({'owner': 'GDP-ADMIN', 'repo': 'bosa'})            .execute()

        # Or with pagination support
        response = github.action('list_pull_requests')            .params({'owner': 'GDP-ADMIN', 'repo': 'bosa'})            .run()
    """
    def __init__(self, module: BosaConnectorModule, authenticator: BaseAuthenticator) -> None:
        """Initialize the action builder.

        Args:
            module: The connector module to use
            authenticator: The authenticator to use for requests
        """
    def action(self, action: str) -> ActionExecutor:
        """Create a new action executor for a service."""
