from pydantic import BaseModel

class BosaToken(BaseModel):
    """Model for a BOSA Token."""
    token: str
    token_type: str
    expires_at: str
    is_revoked: bool
    user_id: str
    client_id: str
