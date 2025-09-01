from pydantic import BaseModel

class ErrorResponse(BaseModel):
    """Error response entity."""
    message: str
    source: str
    reference_id: str
