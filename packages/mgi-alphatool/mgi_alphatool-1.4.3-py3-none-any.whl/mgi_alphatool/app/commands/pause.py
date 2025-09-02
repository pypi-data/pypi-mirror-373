from typing import Literal, Optional
from pydantic import Field
from .base import BaseCommand

class PauseCommand(BaseCommand):
    stepType: str = Field(default="pause", description="The type of the step")
    stepName: str = Field(default="Pause", description="Name of the step") 
    moduleId: Optional[str] = Field(default=None, description="The ID of the module")
    pauseAction: Literal["untilTime", "untilTemperature", "untilResume"] = Field(..., description="Type of pause action")
    pauseSecond: Optional[str] = Field(default=None, description="Number of seconds to pause")
    pauseMinute: Optional[str] = Field(default=None, description="Number of minutes to pause")
    pauseHour: Optional[str] = Field(default=None, description="Number of hours to pause")
    pauseMessage: str = Field(default="", description="Message to display during pause")
    pauseTemperature: Optional[str] = Field(default=None, description="Temperature to pause until") 