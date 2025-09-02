from pydantic import BaseModel

class ActionResult(BaseModel):
    """Model for an action result."""
    success: bool
    message: str
