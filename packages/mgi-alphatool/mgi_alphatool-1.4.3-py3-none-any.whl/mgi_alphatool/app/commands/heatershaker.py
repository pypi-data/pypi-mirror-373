from typing import List, Literal, Optional
from pydantic import Field
from .base import BaseCommand

class HeaterShakerCommand(BaseCommand):
    stepType: str = Field(default="heaterShaker", description="The type of the step")
    stepName: str = Field(default="加热振荡", description="Name of the step")
    moduleId: str = Field(..., description="The ID of the heater-shaker module")
    
    # State settings
    latchOpen: bool = Field(default=False, description="Whether the latch is open")
    
    # Shaking settings
    setShake: bool = Field(default=False, description="Whether to enable shaking")
    targetSpeed: Optional[str] = Field(default=None, description="Target RPM for shaking")
    
    # Temperature settings
    setHeaterShakerTemperature: bool = Field(default=False, description="Whether to set temperature")
    targetHeaterShakerTemperature: Optional[str] = Field(default=None, description="Temperature")
    
    # Timer settings
    heaterShakerSetTimer: bool = Field(default=False, description="Whether to set a timer")
    heaterShakerTimerMinutes: Optional[str] = Field(default=None, description="Timer minutes")
    heaterShakerTimerSeconds: Optional[str] = Field(default=None, description="Timer seconds") 