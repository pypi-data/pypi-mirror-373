from typing import List, Literal, Optional
from pydantic import Field
from .base import BaseCommand

class TemperatureCommand(BaseCommand):
    stepType: str = Field(default="temperature", description="The type of the step")
    stepName: str = Field(default="Temperature", description="Name of the step")
    moduleId: str = Field(..., description="The ID of the temperature module")
    
    # Temperature settings
    setTemperature: str = Field(default='false', description="Whether to set temperature")
    targetTemperature: Optional[str] = Field(default=None, description="Target temperature in Celsius")