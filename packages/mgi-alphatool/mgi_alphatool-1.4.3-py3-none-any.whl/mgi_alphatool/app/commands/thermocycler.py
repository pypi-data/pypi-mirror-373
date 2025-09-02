from typing import List, Literal, Optional
from pydantic import Field
from .base import BaseCommand

class ProfileItem(BaseCommand):
    type: str = Field(default="profileStep", description="The type of the step")
    title: str = Field(default="", description="The title of the step")
    temperature: str = Field(..., description="The target temperature of the step")
    durationMinutes: str = Field(default="0", description="Number of minutes of the step")
    durationSeconds: str = Field(default="0", description="Number of seconds of the step")
    index: int = Field(default=1, description="The index of the step")

class ProfileCycle(BaseCommand):
    type: str = Field(default="profileCycle", description="The type of the step")
    steps: List[ProfileItem] = Field(..., description="The set of profile item step")
    repetitions: str = Field(..., description="The repetitions of the cycle")
    index: int = Field(default=1, description="The index of the step")

class ThermocyclerCommand(BaseCommand):
    stepType: str = Field(default="thermocycler", description="The type of the step")
    stepName: str = Field(default="热循环仪", description="Name of the step")
    moduleId: str = Field(..., description="The ID of the thermocycler module")
    
    # Form settings
    thermocyclerFormType: Literal["thermocyclerProfile", "thermocyclerState"] = Field(
        default="thermocyclerProfile", 
        description="Type of thermocycler form"
    )

    # Lid control
    lidOpen: bool = Field(default=False, description="Whether the lid is open")
    lidOpenHold: bool = Field(default=False, description="Whether to hold lid open state")
    lidIsActive: bool = Field(default=False, description="Whether the lid temperature control is active")
    lidIsActiveHold: bool = Field(default=False, description="Whether to hold lid temperature")
    lidTargetTemp: Optional[str] = Field(default=None, description="Target lid temperature")
    lidTargetTempHold: Optional[str] = Field(default=None, description="Target temperature to hold lid at")

    # Block control
    blockIsActive: bool = Field(default=False, description="Whether the block temperature control is active")
    blockIsActiveHold: bool = Field(default=False, description="Whether to hold block temperature")
    blockTargetTemp: Optional[str] = Field(default=None, description="Target block temperature")
    blockTargetTempHold: Optional[str] = Field(default=None, description="Target temperature to hold block at")

    # Profile settings
    profileVolume: Optional[str] = Field(default=None, description="Volume for thermocycling")
    profileTargetLidTemp: Optional[str] = Field(default=None, description="Target lid temperature")
    profileItemsById: Optional[dict] = Field(default_factory=dict, description="Set of profile items with either profileStep or profileCycle type")
    orderedProfileItems: Optional[List[str]] = Field(default_factory=list, description="Ordered list of profile item IDs") 