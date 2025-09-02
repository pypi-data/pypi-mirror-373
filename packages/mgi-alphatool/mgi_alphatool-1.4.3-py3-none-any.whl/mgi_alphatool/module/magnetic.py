from typing import Union
from . import Module
from ..commands.module import (MagneticModuleEngageParams, 
                               MagneticModuleEngageCommand, 
                               MagneticModuleDisengageParams, 
                               MagneticModuleDisengageCommand)

from ..commands.wait import WaitForDurationParams, WaitForDurationCommand

from  ..app.commands import MagneticModuleCommand

class MagneticModule(Module):
    def __init__(self, id: str, name: str, slot: int, context: 'Context'):
        """Initialize the magnetic module.

        Args:
            id (str): The unique identifier for the module.
            name (str): The name of the module.
            slot (int): The location slot of the module.
            context (Context): The protocol context instance.
        """
        super().__init__(id, name, slot, context)
        self.__context = context
        self.__height = 0

    def set_height(self, height: Union[float, None] = None) -> 'MagneticModule':
        """Engage the magnetic module to a specified height.

        Args:
            height (float, optional): The engagement height. Defaults to None, which tries to use the labware's default height.

        Returns:
            MagneticModule: The current module instance.
        """
        # validate height
        if height is not None and (height < 0 or height > 20):
            raise ValueError("Height must be a positive number between 0 and 20")

        # try to find height from labware data
        if height is None:
            labware = self.context._get_labware_on_module(self)

            if labware:
                height = labware._get_default_mag_height()
        
        # raise error if still no height
        if height is None:
            raise TypeError("Missing required parameter: height")
        
        self.__context._append_command(WaitForDurationCommand(
            params=WaitForDurationParams(seconds=1)
        ))

        self.__context._append_command(MagneticModuleEngageCommand(
            params=MagneticModuleEngageParams(
                moduleId=self.id,
                height=height
            )
        ))
        self.__height = height
        
        self.__context._append_saved_step_form(
            MagneticModuleCommand(
                moduleId=self.id,
                engageHeight=str(height),
                magnetAction='engage'
            )
        )
        
        return self
    
    def engage(self, height: Union[float, None] = None) -> 'MagneticModule':
        """Alias of set_height function.

        Args:
            height (float, optional): The engagement height. Defaults to None, which tries to use the labware's default height.

        Returns:
            MagneticModule: The current module instance.
        """
        return self.set_height(height)

    def disengage(self) -> 'MagneticModule':
        """Disengage the magnetic module.

        Returns:
            MagneticModule: The current module instance.
        """
        self.__context._append_command(WaitForDurationCommand(
            params=WaitForDurationParams(seconds=1)
        ))

        self.__context._append_command(MagneticModuleDisengageCommand(
            params=MagneticModuleDisengageParams(
                moduleId=self.id
            )
        ))
        
        self.__context._append_saved_step_form(
            MagneticModuleCommand(
                moduleId=self.id,
                magnetAction='disengage',
                engageHeight=str(self.__height)
            )
        )
        
        return self