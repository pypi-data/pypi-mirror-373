from _typeshed import Incomplete
from bosa_connectors.auth.base import BaseAuthenticator as BaseAuthenticator

class ApiKeyAuthenticator(BaseAuthenticator):
    """Injects API Key Headers to BOSA API for Authentication."""
    API_KEY_HEADER: str
    api_key: Incomplete
    def __init__(self, api_key: str) -> None:
        """Initializes the ApiKeyAuthenticator with the provided API key.

        Args:
            api_key (str): The API key for authentication.
        """
    def authenticate(self):
        """Authenticates the request.

        Raises:
            AuthenticationError: If authentication fails.
        """
