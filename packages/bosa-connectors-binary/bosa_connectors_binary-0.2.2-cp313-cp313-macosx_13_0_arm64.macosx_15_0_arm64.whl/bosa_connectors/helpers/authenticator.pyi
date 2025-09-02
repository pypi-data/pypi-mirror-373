from _typeshed import Incomplete
from bosa_connectors.auth import ApiKeyAuthenticator as ApiKeyAuthenticator
from bosa_connectors.models.token import BosaToken as BosaToken
from bosa_connectors.models.user import BosaUser as BosaUser, CreateUserResponse as CreateUserResponse

class BosaAuthenticator:
    """Authenticator for BOSA API."""
    DEFAULT_TIMEOUT: int
    api_base_url: Incomplete
    auth_scheme: Incomplete
    def __init__(self, api_base_url: str = 'https://api.bosa.id', api_key: str = 'bosa') -> None:
        '''Initialize the BosaAuthenticator with the provided API key.

        Args:
            api_base_url (str): The base URL for the BOSA API. Defaults to "https://api.bosa.id".
            api_key (str): The API key for authentication. Defaults to "bosa".
        '''
    def register(self, identifier: str) -> CreateUserResponse:
        """Register a BOSA User in the scope of BOSA API.

        Args:
            identifier: BOSA Username

        Returns:
            BOSA User Data with the secret
        """
    def authenticate(self, identifier: str, secret: str) -> BosaToken:
        """Authenticate a BOSA User in the scope of BOSA API.

        Args:
            identifier: BOSA Username
            secret: BOSA Password

        Returns:
            BOSA User Token
        """
    def get_user(self, token: str) -> BosaUser:
        """Get the current user from BOSA API.

        Args:
            token: The BOSA User Token

        Returns:
            BOSA User
        """
