from .connector import BosaConnector as BosaConnector
from .helpers.model_request_generator import create_request_model as create_request_model
from _typeshed import Incomplete
from langchain_core.tools import BaseTool
from pydantic import BaseModel as BaseModel

class BosaConnectorToolError(Exception):
    """Base exception for BOSA connector errors."""

class BOSAConnectorToolGenerator:
    """Tool Generator for BOSA Connectors.

    This class generates tools based on OpenAPI schemas for various services.

    Attributes:
        api_base_url (str): The base URL for the API.
        api_key (str): The API key for authentication.
        info_path (str): The path to the API information endpoint.
        DEFAULT_TIMEOUT (int): Default timeout for API requests.
        app_name (str): The name of the application.
        schema_data (dict): The schema data for the services.

    Methods:
        generate_tools(): Generates tools for the specified services.
    """
    api_base_url: str
    api_key: str
    INFO_PATH: str
    DEFAULT_TIMEOUT: int
    app_name: str
    schema_data: dict
    EXCLUDED_ENDPOINTS: Incomplete
    def __init__(self, api_base_url: str, api_key: str, app_name: str) -> None:
        """Initialize the tool generator with API base URL, info path, and app name.

        Args:
            api_base_url (str): The base URL for the API.
            api_key (str): The API key for authentication.
            app_name (str): The name of the application.
        """
    def generate_tools(self) -> list[BaseTool]:
        """Generate tools based on the BOSA API OpenAPI schemas.

        Returns:
            Dict[str, Type[BaseTool]]: A dictionary of generated tool classes.
        """
