from typing import Optional
import uuid
from pydantic import BaseModel, Field, model_validator, field_validator

class BaseCommand(BaseModel):
    commandType: str = Field(
        ...,
        description=(
            "Specific command type that determines data requirements and "
            "execution behavior"
        ),
    )
    key: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description=(
            "An identifier representing this command as a step in a protocol."
            " A command's `key` will be unique within a given run, but stable"
            " across all runs that perform the same exact procedure. Thus,"
            " `key` be used to compare/match commands across multiple runs"
            " of the same protocol."
        ),
    )

class Location(BaseModel):
    moduleId: Optional[str] = Field(None, description="The ID of the module")
    labwareId: Optional[str] = Field(None, description="The ID of the labware(adapter)") 
    slotName: Optional[str] = Field(None, description="The slot number")

    @field_validator('slotName', mode='before')
    def convert_slotName_to_str(cls, v):
        if isinstance(v, int):
            return str(v)
        return v

    @model_validator(mode='after')
    def check_one_field(cls, values):
        moduleId = values.moduleId
        slotName = values.slotName
        labwareId = values.labwareId
        if not (moduleId or slotName or labwareId):
            raise ValueError("Location must have either moduleId or slotName or labwareId defined")
        return values
    
    def json(self, **kwargs):
        return super().model_dump(exclude_none=True, **kwargs)