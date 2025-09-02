import uuid
from pydantic import BaseModel, Field

class BaseCommand(BaseModel):
    # Basic step information
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description=("The id of the saved step form")
    )
    stepDetails: str = Field(default="", description="Additional step details") 