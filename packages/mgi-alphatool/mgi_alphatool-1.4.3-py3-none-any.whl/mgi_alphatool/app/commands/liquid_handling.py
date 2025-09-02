from typing import List, Literal, Optional, Union
from pydantic import Field
from .base import BaseCommand

class TransferCommand(BaseCommand):
    stepType: str = Field(default="moveLiquid", description="The type of the step")
    stepName: str = Field(default="Pipetting", description="Name of the step")
    
    # Liquid settings
    liquid_id: Optional[str] = Field(default=None)
    liquid_param_name: Optional[str] = Field(default=None)

    # Basic transfer settings
    path: Literal["single", "multiDispense"] = Field(default="single", description="Path type for liquid transfer")
    volume: float = Field(..., description="Volume to transfer")
    pipette: str = Field(..., description="ID of pipette to use")
    tipRack: str = Field(..., description="Tip rack to use")
    changeTip: str = Field(..., description="When to change tips")
    
    # Source and destination
    aspirate_wells: List[str] = Field(..., description="Wells to aspirate from")
    dispense_wells: List[str] = Field(..., description="Wells to dispense to")
    aspirate_labware: str = Field(..., description="Labware to aspirate from")
    dispense_labware: str = Field(..., description="Labware to dispense to")
    aspirate_mmFromBottom: Optional[float] = Field(default=None, description="aspirate offset from bottom")
    dispense_mmFromBottom: Optional[float] = Field(default=None, description="dispense offset from bottom")

    # Tip handling
    dropTip_location: str = Field(..., description="Location to drop tip")
    preWetTip: bool = Field(default=False, description="Whether to pre-wet tip")
    preAspirate: bool = Field(default=False, description="Whether to pre-aspirate")
    preAspirateVolume: Optional[float] = Field(default=None, description="Pre-aspirate volume")
    
    # Flow control
    blowout_checkbox: bool = Field(default=False, description="Whether to perform blowout")
    blowout_location: Optional[str] = Field(default=None, description="Location to blowout")
    disposalVolume_volume: float = Field(default=0, description="Disposal volume")
    disposalVolume_checkbox: bool = Field(default=False, description="Whether to use disposal volume")
    disposalVolume_location: Optional[str] = Field(default=None, description="Location to blowout")
    aspirate_flowRate: Optional[float] = Field(default=None, description="Aspirate flow rate")
    dispense_flowRate: Optional[float] = Field(default=None, description="Dispense flow rate")

    # Air gap settings
    aspirate_airGap_volume: float = Field(default=30, description="Air gap volume for aspiration")
    aspirate_airGap_checkbox: bool = Field(default=False, description="Whether to use air gap during aspiration")
    dispense_airGap_volume: float = Field(default=30, description="Air gap volume for dispensing")
    dispense_airGap_checkbox: bool = Field(default=False, description="Whether to use air gap during dispensing")
    
    # Mixing settings
    aspirate_mix_checkbox: bool = Field(default=False, description="Whether to mix while aspirating")
    aspirate_mix_times: Optional[int] = Field(default=None, description="Number of mix repetitions while aspirating")
    aspirate_mix_volume: Optional[float] = Field(default=None, description="Volume to mix while aspirating")
    dispense_mix_checkbox: bool = Field(default=False, description="Whether to mix while dispensing")
    dispense_mix_times: Optional[int] = Field(default=None, description="Number of mix repetitions while dispensing")
    dispense_mix_volume: Optional[float] = Field(default=None, description="Volume to mix while dispensing")
    
    # nozzles
    
    # Delay settings
    aspirate_delay_seconds: Optional[Union[int, float]] = Field(default=None, description="Delay after aspiration")
    aspirate_delay_checkbox: bool = Field(default=False, description="Whether to delay after aspiration")
    aspirate_delay_mmFromBottom: Optional[float] = Field(default=None, description="aspirate delay offset from bottom")
    dispense_delay_seconds: Optional[Union[int, float]] = Field(default=None, description="Delay after dispensing")
    dispense_delay_checkbox: bool = Field(default=False, description="Whether to delay after dispensing")
    dispense_delay_mmFromBottom: Optional[float] = Field(default=None, description="dispense delay offset from bottom")

    # Well ordering
    aspirate_wells_grouped: bool = Field(default=False, description="Whether wells are grouped")
    aspirate_detect_checkbox: bool = Field(default=False, description="Whether to detect liquid level")
    aspirate_detect_mmsSpeed: Optional[float] = Field(default=None, description="Aspirate detect speed")
    aspirate_wellOrder_first: str = Field(default="t2b", description="First well ordering direction for aspiration")
    aspirate_wellOrder_second: str = Field(default="l2r", description="Second well ordering direction for aspiration")
    dispense_wellOrder_first: str = Field(default="t2b", description="First well ordering direction for dispensing")
    dispense_wellOrder_second: str = Field(default="l2r", description="Second well ordering direction for dispensing")
    
    # Touch tip settings
    aspirate_touchTip_checkbox: bool = Field(default=False, description="Whether to touch tip after aspiration")
    aspirate_touchTip_mmFromBottom: Optional[float] = Field(default=None, description="aspirate touch tip offset from bottom")
    dispense_touchTip_checkbox: bool = Field(default=False, description="Whether to touch tip after dispensing")
    dispense_touchTip_mmFromBottom: Optional[float] = Field(default=None, description="aspirate touch tip offset from bottom")

class MixCommand(BaseCommand):
    stepType: str = Field(default="mix", description="The type of the step")
    stepName: str = Field(default="Mix", description="Name of the step")

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
    dropTip_location: str = Field(..., description="Location to drop tip")
    
    # Mix offset setting
    mix_mmFromBottom: Optional[float] = Field(default=None, description="Mix offset from bottom")

    # Well ordering
    mix_wellOrder_first: str = Field(default="t2b", description="First well ordering direction")
    mix_wellOrder_second: str = Field(default="l2r", description="Second well ordering direction")
    
    # Touch tip and delay settings
    mix_touchTip_checkbox: bool = Field(default=False, description="Whether to touch tip after mixing")
    mix_touchTip_mmFromBottom: Optional[float] = Field(default=None, description="Touch tip offset from bottom")
    aspirate_delay_seconds: Union[int, float] = Field(default=1, description="Delay after aspiration")
    dispense_delay_seconds: Union[int, float] = Field(default=1, description="Delay after dispensing")
    aspirate_delay_checkbox: bool = Field(default=False, description="Whether to delay after aspiration")
    dispense_delay_checkbox: bool = Field(default=False, description="Whether to delay after dispensing") 

    preAspirate: bool = Field(default=False, description="Whether to pre-aspirate")
    preAspirateVolume: Optional[float] = Field(default=None, description="Pre-aspirate volume")