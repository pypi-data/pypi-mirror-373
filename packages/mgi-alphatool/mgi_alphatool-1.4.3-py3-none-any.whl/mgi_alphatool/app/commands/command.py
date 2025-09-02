import uuid
from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class BaseCommand(BaseModel):
    # Basic step information
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description=("The id of the saved step form")
    )

class PauseCommand(BaseCommand):
    stepType: str = Field(default="pause", description="The type of the step")
    stepName: str = Field(default="暂停", description="Name of the step") 
    moduleId: Optional[str] = Field(default=None, description="The ID of the module")
    pauseAction: Literal["untilTime", "untilTemperature", "untilResume"] = Field(..., description="Type of pause action")
    pauseSecond: Optional[int] = Field(default=None, description="Number of seconds to pause")
    pauseMinute: Optional[int] = Field(default=None, description="Number of minutes to pause")
    pauseMessage: str = Field(default="", description="Message to display during pause")
    pauseTemperature: Optional[int] = Field(default=None, description="Temperature to pause until")

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
    profileItemsById: dict = Field(default_factory=dict, description="Dictionary of profile items with either profileStep or profileCycle type")
    orderedProfileItems: List[str] = Field(default_factory=list, description="Ordered list of profile item IDs")

class ProfileItem(BaseCommand):
    type: str = Field(default="profileStep", description="The type of the step")
    title: str = Field(default="", description="The title of the step")
    temperature: str = Field(..., description="The target temperature of the step")
    durationMinutes: Optional[str] = Field(default=None, description="Number of minutes of the step")
    durationSeconds: Optional[str] = Field(default=None, description="Number of seconds of the step")

class MagneticModuleCommand(BaseCommand):
    stepType: str = Field(default="magnet", description="The type of the step")
    stepName: str = Field(default="施加磁场", description="Name of the step")
    moduleId: str = Field(..., description="The ID of the magnetic module")
    
    # Magnet settings
    magnetAction: Literal["engage", "disengage"] = Field(..., description="Action to take")
    engageHeight: Optional[float] = Field(default=None, description="Height to engage")

class TemperatureCommand(BaseCommand):
    stepType: str = Field(default="temperature", description="The type of the step")
    stepName: str = Field(default="温控", description="Name of the step")
    moduleId: str = Field(..., description="The ID of the temperature module")
    
    # Temperature settings
    setTemperature: bool = Field(default=False, description="Whether to set temperature")
    targetTemperature: Optional[str] = Field(default=None, description="Target temperature in Celsius")

class TransferCommand(BaseCommand):
    stepType: str = Field(default="moveLiquid", description="The type of the step")
    stepName: str = Field(default="移液", description="Name of the step")
    
    # Basic transfer settings
    path: str = Field(default="single", description="Path type for liquid transfer")
    volume: float = Field(..., description="Volume to transfer")
    pipette: str = Field(..., description="ID of pipette to use")
    tipRack: str = Field(..., description="Tip rack to use")
    changeTip: str = Field(..., description="When to change tips")
    stepDetails: str = Field(default="", description="Additional step details")
    
    # Source and destination
    aspirate_wells: List[str] = Field(..., description="Wells to aspirate from")
    dispense_wells: List[str] = Field(..., description="Wells to dispense to")
    aspirate_labware: str = Field(..., description="Labware to aspirate from")
    dispense_labware: str = Field(..., description="Labware to dispense to")
    
    # Tip handling
    dropTip_location: str = Field(..., description="Location to drop tip")
    preWetTip: bool = Field(default=False, description="Whether to pre-wet tip")
    
    # Flow control
    blowout_checkbox: bool = Field(default=False, description="Whether to perform blowout")
    disposalVolume_volume: float = Field(default=30, description="Disposal volume")
    disposalVolume_checkbox: bool = Field(default=False, description="Whether to use disposal volume")
    
    # Air gap settings
    aspirate_airGap_volume: float = Field(default=30, description="Air gap volume for aspiration")
    aspirate_airGap_checkbox: bool = Field(default=False, description="Whether to use air gap during aspiration")
    dispense_airGap_volume: float = Field(default=30, description="Air gap volume for dispensing")
    dispense_airGap_checkbox: bool = Field(default=False, description="Whether to use air gap during dispensing")
    
    # Mixing settings
    aspirate_mix_checkbox: bool = Field(default=False, description="Whether to mix while aspirating")
    dispense_mix_checkbox: bool = Field(default=False, description="Whether to mix while dispensing")
    
    # Delay settings
    aspirate_delay_seconds: float = Field(default=1, description="Delay after aspiration")
    aspirate_delay_checkbox: bool = Field(default=False, description="Whether to delay after aspiration")
    dispense_delay_seconds: float = Field(default=1, description="Delay after dispensing")
    dispense_delay_checkbox: bool = Field(default=False, description="Whether to delay after dispensing")
    
    # Well ordering
    aspirate_wells_grouped: bool = Field(default=False, description="Whether wells are grouped")
    aspirate_detect_checkbox: bool = Field(default=False, description="Whether to detect liquid level")
    aspirate_wellOrder_first: str = Field(default="t2b", description="First well ordering direction for aspiration")
    aspirate_wellOrder_second: str = Field(default="l2r", description="Second well ordering direction for aspiration")
    dispense_wellOrder_first: str = Field(default="t2b", description="First well ordering direction for dispensing")
    dispense_wellOrder_second: str = Field(default="l2r", description="Second well ordering direction for dispensing")
    
    # Touch tip settings
    aspirate_touchTip_checkbox: bool = Field(default=False, description="Whether to touch tip after aspiration")
    dispense_touchTip_checkbox: bool = Field(default=False, description="Whether to touch tip after dispensing")

class MixCommand(BaseCommand):
    stepType: str = Field(default="mix", description="The type of the step")
    stepName: str = Field(default="混合", description="Name of the step")
    stepDetails: str = Field(default="", description="Additional step details")

    # Basic mix settings
    times: int = Field(..., description="Number of mix repetitions")
    volume: float = Field(..., description="Volume to mix")
    wells: List[str] = Field(..., description="Wells to mix in")
    labware: str = Field(..., description="Labware containing wells")
    
    # Pipette settings
    pipette: str = Field(..., description="ID of pipette to use")
    tipRack: str = Field(..., description="Tip rack to use")
    changeTip: str = Field(..., description="When to change tips")
    
    # Flow settings
    aspirate_flowRate: float = Field(..., description="Aspirate flow rate")
    dispense_flowRate: float = Field(..., description="Dispense flow rate")
    blowout_checkbox: bool = Field(default=False, description="Whether to perform blowout")
    
    # Additional settings
    stepDetails: str = Field(default="", description="Additional step details")
    dropTip_location: str = Field(..., description="Location to drop tip")
    
    # Well ordering
    mix_wellOrder_first: str = Field(default="t2b", description="First well ordering direction")
    mix_wellOrder_second: str = Field(default="l2r", description="Second well ordering direction")
    
    # Touch tip and delay settings
    mix_touchTip_checkbox: bool = Field(default=False, description="Whether to touch tip after mixing")
    aspirate_delay_seconds: float = Field(default=1, description="Delay after aspiration")
    dispense_delay_seconds: float = Field(default=1, description="Delay after dispensing")
    aspirate_delay_checkbox: bool = Field(default=False, description="Whether to delay after aspiration")
    dispense_delay_checkbox: bool = Field(default=False, description="Whether to delay after dispensing")

class MoveLabwareCommand(BaseCommand):
    stepType: str = Field(default="moveLabware", description="The type of the step")
    stepName: str = Field(default="移板", description="Name of the step")
    
    # Move settings
    labware: str = Field(..., description="The unique identifier for the labware")
    newLocation: str = Field(..., description="The new location of the labware")
    useGripper: bool = Field(..., description="Whether to use the gripper for moving the labware")