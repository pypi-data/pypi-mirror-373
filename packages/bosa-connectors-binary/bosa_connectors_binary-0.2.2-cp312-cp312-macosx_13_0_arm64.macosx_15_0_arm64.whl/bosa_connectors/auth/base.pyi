import abc
from abc import ABC, abstractmethod

class BaseAuthenticator(ABC, metaclass=abc.ABCMeta):
    """Base authenticator for BOSA API."""
    @abstractmethod
    def authenticate(self):
        """Authenticates the request.

        Raises:
            AuthenticationError: If authentication fails.
        """
