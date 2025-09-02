from pydantic import BaseModel
from typing import Any

def create_request_model(endpoint_name: str, schema: dict, service_prefix: str = 'BOSA', requires_auth: bool = False) -> type[BaseModel]:
    '''Create a Pydantic model for the request schema.

    Args:
        endpoint_name (str): The name of the endpoint.
        schema (dict): The schema definition for the endpoint.
        service_prefix (str, optional): The prefix for the service. Defaults to "BOSA".
        requires_auth (bool, optional): Whether the endpoint requires authentication. Defaults to False.

    Returns:
        Type[BaseModel]: The generated Pydantic model.
    '''

class _RequestModelBuilder:
    """Per-call builder that holds $defs and model cache to resolve refs safely."""
    def __init__(self) -> None: ...
    def set_definitions(self, defs: dict[str, dict[str, Any]]) -> None:
        """Set the definitions for this build scope and reset the cache.

        Args:
            defs: The definitions to set.
        """
    def resolve_field_type(self, field_schema: dict[str, Any]) -> Any:
        """Resolve a JSON Schema field definition into a Python type annotation.

        Supports $ref, anyOf (including nullables), and array item resolution.

        Args:
            field_schema: The field schema to resolve.

        Returns:
            The resolved field type.
        """
    def build_model_for_def(self, def_key: str) -> type[BaseModel]:
        """Create or retrieve a Pydantic model for a $defs entry.

        Args:
            def_key: The key of the $defs entry to build.

        Returns:
            The Pydantic model for the $defs entry.
        """
