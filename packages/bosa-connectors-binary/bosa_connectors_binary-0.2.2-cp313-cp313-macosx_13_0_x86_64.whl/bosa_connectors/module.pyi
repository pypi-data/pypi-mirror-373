from _typeshed import Incomplete
from bosa_connectors.auth import BaseAuthenticator as BaseAuthenticator
from bosa_connectors.models.file import ConnectorFile as ConnectorFile
from pydantic import BaseModel as BaseModel
from typing import Annotated, Any

class BosaConnectorError(Exception):
    """Base exception for BOSA connector errors."""

class BosaConnectorModule:
    """Base class for all BOSA connector modules."""
    app_name: str
    DEFAULT_TIMEOUT: int
    MAX_RETRY: int
    MAX_BACKOFF_SECONDS: int
    INFO_PATH: str
    EXCLUDED_ENDPOINTS: Incomplete
    @staticmethod
    def is_retryable_error(status_code: int) -> bool:
        """Check if the status code indicates a retryable error (429 or 5xx).

        Args:
            status_code: HTTP status code to check

        Returns:
            bool: True if the error is retryable
        """
    api_base_url: Incomplete
    info_path: Incomplete
    def __init__(self, app_name: str, api_base_url: str = 'https://api.bosa.id', info_path: str = ...) -> None:
        """Initialize a new connector module.

        This constructor should only be called by BosaConnector.
        """
    def get_actions(self) -> list[tuple[str, str, str]]:
        """Return list of available actions for this module."""
    def get_action_parameters(self, action: str):
        """Get flattened parameter information for an action.

        Args:
            action: The action endpoint

        Returns:
            List of parameter info dicts with name, type, and required fields.
            Nested objects are flattened using dot notation, e.g.:
                object.attr1, object.attr2, object.attr3.attr21
        """
    def validate_request(self, action: str, params: dict[str, Any]) -> tuple[dict[str, Any] | None, dict[str, str]]:
        """Validate and clean request parameters.

        Args:
            action: The action endpoint
            params: Dict of parameter values

        Returns:
            Tuple of (cleaned_params, error_details) where error_details is empty if validation passed
        """
    def execute(self, action: str, max_attempts: int, input_: dict = None, token: str | None = None, account: Annotated[str | None, None] = None, identifier: str | None = None, authenticator: BaseAuthenticator | None = None, headers: dict[str, str] | None = None, timeout: int | None = ...) -> tuple[dict[str, Any] | ConnectorFile, int]:
        """Execute an action with validated parameters and return typed response.

        Args:
            action: The action to execute
            max_attempts: Maximum number of attempts for failed requests (429 or 5xx errors). Must be at least 1.
                  Will be capped at MAX_RETRY (10) to prevent excessive retries.
            input_: Optional dictionary of parameters
            token: Optional BOSA User Token. If not provided, will use the default token
            account: Optional user account to use for the request (deprecated, remove this in the future)
            identifier: Optional user identifier to use for the request
            authenticator: Optional authenticator to use for the request
            headers: Optional headers to include in the request

        The method supports both ways of passing parameters:
        1. As a dictionary: execute(action, params_dict)
        2. As keyword arguments: execute(action, param1=value1, param2=value2)

        Raises:
            ValueError: If action is invalid, parameters are invalid, or max_attempts is less than 1
        """
