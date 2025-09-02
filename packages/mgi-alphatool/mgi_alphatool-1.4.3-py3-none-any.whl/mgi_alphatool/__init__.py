from typing import Literal
from .context import Context
from .handler.gripper import Gripper
from .handler.pipette import Pipette
from .liquid import Liquid
from .labware import Labware
from .module import Module

def init(robot_type: str = 'alphatool', 
         deck_type: Literal['standard', 'ext1'] = 'standard',
         pick_up_tip_order: Literal['top_to_bottom', 'bottom_to_top'] = 'top_to_bottom') -> Context:
    """Initialize the protocol context. This function sets up the protocol context based on the alphatool.

    Args:
        robot_type (str): Type of robot to use (e.g. 'alphatool')
        deck_type (Literal['standard', 'ext1']): Type of deck to use (e.g. 'standard' or 'ext1')
        pick_up_tip_order (Literal['top_to_bottom', 'bottom_to_top']): Order of tip picking up,
            'top_to_bottom' means pick up tips from top left to bottom right,
            'bottom_to_top' means pick up tips from bottom left to top right.

    Returns:
        Context: The initialized protocol context.
    """
    if robot_type != 'alphatool':
        raise ValueError(f"Unsupported robot type: {robot_type}. Must be 'alphatool'.")
    if deck_type not in ['standard', 'ext1']:
        raise ValueError(f"Unsupported deck type: {deck_type}. Must be 'standard' or 'ext1'.")

    return Context(robot_type=robot_type, deck_type=deck_type, pick_up_tip_order=pick_up_tip_order)