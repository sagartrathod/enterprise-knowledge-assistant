from pydantic import BaseModel, ConfigDict

class BaseResponseSchema(BaseModel):
    """Global configuration to automatically serialize native asyncpg records / objects."""
    model_config = ConfigDict(from_attributes=True)

class MessageResponse(BaseResponseSchema):
    status: str = "success"
    message: str