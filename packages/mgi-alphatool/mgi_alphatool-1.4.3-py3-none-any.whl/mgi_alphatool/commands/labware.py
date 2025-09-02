from pydantic import BaseModel, Field

from .command import BaseCommand, Location

class LoadLabwareParams(BaseModel):
    displayName: str = Field(..., description="The display name of the labware")
    labwareId: str = Field(..., description="The unique identifier for the labware")
    loadName: str = Field(..., description="The load name of the labware")
    namespace: str = Field(..., description="The namespace of the labware")
    version: int = Field(..., description="The version of the labware")
    location: Location = Field(..., description="The location details of the labware")

class LoadLabwareCommand(BaseCommand):
    commandType: str = Field(
        default="loadLabware"
    )
    params: LoadLabwareParams = Field(
        ...
    )

class MoveLabwareParams(BaseModel):
    labwareId: str = Field(..., description="The unique identifier for the labware")
    strategy: str = Field(..., description="The way to move the labware")
    newLocation: Location = Field(..., description="The location details of the labware")

class MoveLabwareCommand(BaseCommand):
    commandType: str = Field(
        default="moveLabware"
    )
    params: MoveLabwareParams = Field(
        ...
    )