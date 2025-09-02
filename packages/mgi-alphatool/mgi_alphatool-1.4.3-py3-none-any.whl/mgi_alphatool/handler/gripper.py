from . import Handler

from typing import Literal, Union
from ..labware import Column, Labware, Well
from ..module import Module
from ..commands.command import Location
from ..commands.labware import MoveLabwareParams, MoveLabwareCommand
from ..app.commands import MoveLabwareCommand as AppMoveLabwareCommand

class Gripper(Handler):
    def __init__(self, id: str, name: str, mount: str, context: 'Context'):
        super().__init__(id, name, mount, context)

    def move_labware(self, labware: Labware, 
                     location: Union[int, Module, Labware]) -> 'Gripper':
        """Move labware to a new location using the gripper.

        Args:
            labware (Labware): The labware to move.
            location (Union[int, Module, Labware]): Target location (deck slot, module, or labware).
        """
        if isinstance(location, (Module, Labware)):
            new_loc = Location(moduleId=location.id) if isinstance(location, Module) else Location(labwareId=location.id)
            labware._set_slot(location._get_slot())
        else:
            new_loc = Location(slotName=str(location))
            labware._set_slot(location)

        self._get_context()._append_command(MoveLabwareCommand(
            params=MoveLabwareParams(
                labwareId=labware.id,
                strategy='usingGripper',
                newLocation=new_loc
            )
        ))

        self._get_context()._append_saved_step_form(AppMoveLabwareCommand(
            useGripper=True,
            labware=labware.id,
            newLocation=str(location) if isinstance(location, int) else location.id
        ))

        return self