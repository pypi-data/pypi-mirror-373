import re
from typing import List, Union

from .exception import LocationErr

from ..labware.trashbin import TrashBin
from ..labware import Labware, Well, Column
from .common import get_n_wells, is_only_first_row

def validate_transfer_params(pipette: "Pipette", 
                             source_wells: Union[List[Well], List[Column]], 
                             dest_wells: Union[List[Well], List[Column]]) -> None:
    """validate the parameter of transfer

    Args:
        source_wells (Union[List[Well], List[Column]]): source wells
        dest_wells (Union[List[Well], List[Column]]): destination wells
    """

    # get the length of the wells
    n_src_wells = get_n_wells(source_wells)
    n_dest_wells = get_n_wells(dest_wells)

    # Single-channel validation
    if pipette.is_single_channel():
        if not (n_src_wells == n_dest_wells or n_src_wells == 1 or n_dest_wells == 1):
            raise ValueError("For single-channel pipette, transfer must be 1 to many, many to 1, or N to N.")
        return
        
    # Multi-channel validation
    if not ((n_src_wells % 8 == 0 or is_only_first_row(source_wells)) and 
            (n_dest_wells % 8 == 0 or is_only_first_row(dest_wells))):
        raise ValueError("For multi-channel pipette, well counts must be divisible by 8.")
    
    src_valid = n_src_wells / 8 == 1 or (len(source_wells) == 1 and is_only_first_row(source_wells))
    dest_valid = n_dest_wells / 8 == 1 or (len(dest_wells) == 1 and is_only_first_row(dest_wells))
    
    if not (n_src_wells == n_dest_wells or src_valid or dest_valid):
        raise ValueError("Transfer must be 1 to many, many to 1, or N to N (where N is divisible by 8).")

def validate_mix_params(pipette: "Pipette", wells: Union[List[Well], List[Column]]) -> None:
    """vlidate the parameters of mix

    Args:
        wells (Union[List[Well], List[Column]]): wells for mixing
    """
    n_wells = get_n_wells(wells)

    if not pipette.is_single_channel():
        if not (n_wells % 8 == 0 or is_only_first_row(wells)):
            raise ValueError("For multi-channel pipette, the number of wells must be divisible by 8")
        
def validate_wells(wells: List[Well]):
    """check is the wells in the list come from the same location(labware)

    Args:
        wells (List[Well]): wells in the list
    """
    if len(set(well._get_parent() for well in wells)) != 1:
        raise ValueError("All wells must in the same labware")

def validate_tiprack(tiprack: Union["TipRack", None]):
    """check is the tiprack provided.

    Args:
        tiprack (TipRack): tiprack instance
    """
    if tiprack is None:
        raise ValueError("Tiprack should be provided useless there is only one tiprack type loaded.")

    if not tiprack._is_tiprack():
        raise ValueError("Please provide the valid tiprack instance.")

def validate_mix_in_transfer_params(mix_param: Union[tuple, None], param_name: str) -> None:
    """Validate the mix_before and mix_after parameters.

    Args:
        mix_param (Union[tuple, None]): The mix parameter to validate.
        param_name (str): The name of the parameter ('mix_before' or 'mix_after').

    Raises:
        ValueError: If the mix parameter is invalid.
    """
    if mix_param is not None:
        if not isinstance(mix_param, (tuple, list)) or len(mix_param) != 2:
            raise ValueError(f"{param_name} must be a tuple or list of two elements")
        if not isinstance(mix_param[0], int) or mix_param[0] <= 0:
            raise ValueError(f"First element of {param_name} must be a positive integer (number of repetitions)")
        if not isinstance(mix_param[1], (int, float)) or mix_param[1] <= 0:
            raise ValueError(f"Second element of {param_name} must be a positive number (volume)")

def validate_delay(delay: Union[int, float], param_name: str) -> None:
    """Validate the delay parameters.

    Args:
        delay (int): The delay value to validate.
        param_name (str): The name of the parameter.

    Raises:
        ValueError: If the delay parameter is invalid.
    """
    if not isinstance(delay, (int, float)) or delay < 0:
        raise ValueError(f"{param_name} must be a non-negative number")

def validate_multi_dispense_mode(source_wells: List[Union[Well, Column]],
                                 dest_wells: List[Union[Well, Column]],
                                 max_volume: int,
                                 volume: int) -> None:
    n_src_wells = len(source_wells)
    n_dest_wells = len(dest_wells)
    if n_src_wells != 1 or n_dest_wells < 2:
        raise ValueError(
            f"Multi-dispense mode requires exactly 1 source well/column and more than 1 destination well/column(s)."
            f"Got {n_src_wells} source well/column(s) and {n_dest_wells} destination well/column(s)."
        )
    
    if max_volume / volume < 2:
        raise ValueError(
            f"Multi-dispense mode is not supported as the max volume of tip is too small."
            f"Got max volume of tip {max_volume} and volume {volume}."
        )

def validate_air_gap(air_gap: float,
                        max_volume: int, 
                        param_name: str):
    """Validate the air gap parameters.

    Args:
        air_gap (float): The air gap volume to validate.
        max_volume (int): The maximum volume capacity of the tip.
        param_name (str): The name of the parameter.

    Raises:
        ValueError: If the air gap parameter is invalid or exceeds the maximum tip volume.
    """
    if not isinstance(air_gap, (int, float)) or air_gap < 0:
        raise ValueError(f"Invalid value for {param_name}. Must be a non-negative number.")
    
    if air_gap >= max_volume:
        raise ValueError(f"The volume of air gap should not be larger then the maximum volume of tip.")

def validate_location(pipette: "Pipette", location: Union[Well, Column, Labware, TrashBin]):
    """Validate is the location type match the pipette type.

    Args:
        location (Union[Well, Column, Labware, TrashBin]): location (well or column instance)

    Raises:
        LocationErr: mismatched location and pipette.
    """
    if isinstance(location, TrashBin):
        return  True
    
    if not isinstance(location, (Column, Well, Labware)):
        raise ValueError("Location must be a well, column, labware or trash bin instance.")

    if pipette.is_single_channel() and isinstance(location, Column):
        raise LocationErr("Unable to locate column for a single-channel pipette.")
    
    if not pipette.is_single_channel() and isinstance(location, Well):
        raise LocationErr("Unable to locate well for a multi-channel pipette.")
    
    # check if anything on top of the labware
    target = location if isinstance(location, Labware) else location._get_parent()
    labware_on_top = pipette._get_context()._get_labware_on_location(target)
    if labware_on_top is not None:
        raise ValueError("There are labware on top of the location. Please remove the labware first.")
    
    # TODO: find a better way to check if the irregular labware is compatible with the pipette
    # p200 multi channel pipette cannot be used with irregular labware
    # if self._get_name() == 'p200_multi' and location._get_parent()._is_irregular():
    #     raise ValueError("P200 multi channel pipette cannot be used with irregular labware.")
    
    # check collosion when using p200 single channel pipette (8ch in single channel mode)
    if pipette._get_name() == 'p200_single':
        if not isinstance(location, TrashBin):
            pipette._get_context()._check_collision(location)

def validate_mount(mount: str, arm_mount: dict) -> None:
    """Validate mount position and availability.

    Args:
        mount: The mount position to validate
        
    Raises:
        ValueError: If mount is invalid or occupied
    """
    if mount not in ['left', 'right']:
        raise ValueError(f'Invalid mount: "{mount}". Must be either "left" or "right"')
        
    if arm_mount[mount] is not None:
        raise ValueError(
            f'Mount "{mount}" is already occupied.'
        )

def validate_volume(volume: float, param_name: str) -> None:
    """Validate the volume parameters.

    Args:
        volume (float): The volume to validate.
        param_name (str): The name of the parameter.
    """
    if not isinstance(volume, (int, float)) or volume <= 0:
        raise ValueError(f"Invalid value for {param_name}. Must be a positive number.")

def validate_detect_liquid_speed(detect_liquid_speed: Union[int, float], param_name: str) -> None:
    """Validate the detect liquid speed parameters.

    Args:
        detect_liquid_speed (float): The detect liquid speed to validate.
        param_name (str): The name of the parameter.
    """
    if not isinstance(detect_liquid_speed, (int, float)):
        raise ValueError(f"Invalid value for {param_name}. Must be a number.")
    if detect_liquid_speed != 0 and (detect_liquid_speed < 2 or detect_liquid_speed > 50):
        raise ValueError(f"Invalid value for {param_name}. Must be either 0 or between 2-50.")

def validate_offset(offset: tuple, param_name: str) -> None:
    """Validate the offset parameters.

    Args:
        offset (tuple): The offset (x,y,z) tuple to validate.
        param_name (str): The name of the parameter.
    """
    if not isinstance(offset, tuple) or len(offset) != 3:
        raise ValueError(f"Invalid value for {param_name}. Must be a tuple of 3 numbers (x,y,z).")

def validate_position(position: str, param_name: str) -> None:
    """Validate the position parameters.

    Args:
        position (str): The position to validate.
        param_name (str): The name of the parameter.
    """
    if position not in ['top', 'bottom']:
        raise ValueError(f"Invalid value for {param_name}. Must be either 'top' or 'bottom'.")

def validate_flow_rate(flow_rate: float, param_name: str) -> None:
    """Validate the flow rate parameters.

    Args:
        flow_rate (float): The flow rate to validate. Must be between 60-800.
        param_name (str): The name of the parameter.
    """
    if not isinstance(flow_rate, (int, float)):
        raise ValueError(f"Invalid value for {param_name}. Must be a number.")
    # if flow_rate < 60 or flow_rate > 800:
    #     raise ValueError(f"Invalid value for {param_name}. Must be between 60-800.")

def validate_touch_tip(touch_tip_offset: tuple, param_name: str) -> None:
    """Validate the touch tip offset parameters.

    Args:
        touch_tip_offset (tuple): The touch tip offset (x,y,z) tuple to validate.
        param_name (str): The name of the parameter.
    """
    # Validate z range
    z = touch_tip_offset[2]
    if not isinstance(z, (int, float)):
        raise ValueError(f"Invalid z value in {param_name}. Must be a number.")
    if z < 0 or z > 235:
        raise ValueError(f"Invalid z value in {param_name}. Must be between 0-235.")

def validate_pre_aspirate(pre_aspirate: float, param_name: str) -> None:
    """Validate the pre aspirate parameters.

    Args:
        pre_aspirate (float): The pre aspirate to validate. Must be 0 or between 1-20.
        param_name (str): The name of the parameter.
    """
    if not isinstance(pre_aspirate, (int, float)):
        raise ValueError(f"Invalid value for {param_name}. Must be a number.")
    if pre_aspirate != 0 and (pre_aspirate < 1 or pre_aspirate > 20):
        raise ValueError(f"Invalid value for {param_name}. Must be either 0 or between 1-20.")

def validate_disposal(disposal: float, param_name: str) -> None:
    """Validate the disposal parameters.

    Args:
        disposal (float): The disposal volume to validate.
        param_name (str): The name of the parameter.
    """
    if not isinstance(disposal, (int, float)):
        raise ValueError(f"Invalid value for {param_name}. Must be a number.")
    if disposal < 0:
        raise ValueError(f"Invalid value for {param_name}. Must be a non-negative number.")