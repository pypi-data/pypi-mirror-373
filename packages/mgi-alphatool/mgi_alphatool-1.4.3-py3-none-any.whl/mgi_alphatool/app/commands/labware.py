from pydantic import Field
from .base import BaseCommand

class MoveLabwareCommand(BaseCommand):
    stepType: str = Field(default="moveLabware", description="The type of the step")
    stepName: str = Field(default="移板", description="Name of the step")
    
    # Move settings
    labware: str = Field(..., description="The unique identifier for the labware")
    newLocation: str = Field(..., description="The new location of the labware")
    useGripper: bool = Field(..., description="Whether to use the gripper for moving the labware") 