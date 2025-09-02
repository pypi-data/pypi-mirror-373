from pydantic import BaseModel
from uuid import UUID

class ThirdPartyIntegrationAuthBasic(BaseModel):
    """Basic model for a third party integration authentication."""
    id: UUID
    client_id: UUID
    user_id: UUID
    connector: str
    user_identifier: str
    selected: bool

class BosaUser(BaseModel):
    """Model for a BOSA User."""
    id: UUID
    client_id: UUID
    identifier: str
    secret_preview: str
    is_active: bool
    integrations: list[ThirdPartyIntegrationAuthBasic]

class CreateUserResponse(BaseModel):
    """Model for a BOSA User creation response."""
    id: UUID
    identifier: str
    secret: str
    secret_preview: str
    is_active: bool
