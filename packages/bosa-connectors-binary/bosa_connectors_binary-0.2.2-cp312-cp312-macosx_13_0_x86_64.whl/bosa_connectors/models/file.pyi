from pydantic import BaseModel

class ConnectorFile(BaseModel):
    """Model for a file in a BOSA Connector request or response."""
    file: bytes
    filename: str | None
    content_type: str | None
    headers: dict[str, str] | None
