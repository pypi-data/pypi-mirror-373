from pydantic import BaseModel, Field

class InternalMarkerParams(BaseModel):
    commandType: str = Field(
        default="internal_mark"
    )
    class Config:
        extra = "allow"