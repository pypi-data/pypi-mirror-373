from typing import Dict, List, Union
from . import Module

from ..commands.module import (ThermocyclerModuleCloseLidCommand, ThermocyclerModuleCloseLidParams,
                               ThermocyclerModuleOpenLidCommand, ThermocyclerModuleOpenLidParams,
                               ThermocyclerModuleSetBlockTempCommand, ThermocyclerModuleSetBlockTempParams,
                               ThermocyclerModuleSetLidTempCommand, ThermocyclerModuleSetLidTempParams,
                               ThermocyclerModuleWaitForBlockTempCommand, ThermocyclerModuleWaitForBlockTempParams,
                               ThermocyclerModuleWaitForLidTempCommand, ThermocyclerModuleWaitForLidTempParams,
                               ThermocyclerModuleDeactivateBlockCommand, ThermocyclerModuleDeactivateBlockParams,
                               ThermocyclerModuleDeactivateLidCommand, ThermocyclerModuleDeactivateLidParams,
                               ThermocyclerRunProfileCommand, ThermocyclerModuleRunProfileParams, ThermocyclerModuleRunProfileStep)

from  ..app.commands import ThermocyclerCommand, ProfileCycle, ProfileItem

# REMARK: The wait_for_temp params is only work on python script only, in the app, it is always set to be True and cannot be changed

class ThermocyclerModule(Module):
    def __init__(self, id: str, name: str, slot: int, context: 'Context'):
        """Initialize the thermocycler module.

        Args:
            id (str): The unique identifier for the module.
            name (str): The name of the module.
            slot (int): The location slot of the module.
            context (Context): The protocol context instance.
        """
        super().__init__(id, name, slot, context)
        self.__context = context
        self.__lid_open = True
        self.__block_temp = None
        self.__lid_temp = None

    def open_lid(self) -> 'ThermocyclerModule':
        """Open the lid of the thermocycler.

        Returns:
            ThermocyclerModule: The current module instance.
        """
        command = ThermocyclerModuleOpenLidCommand(
            params=ThermocyclerModuleOpenLidParams(
                moduleId=self.id,
            )
        )
        self.__context._append_command(command)

        self.__context._append_saved_step_form(
            ThermocyclerCommand(
                thermocyclerFormType='thermocyclerState',
                moduleId=self.id,
                lidOpen=True
            )
        )
        self.__lid_open = True
        return self
     
    def close_lid(self) -> 'ThermocyclerModule':
        """Close the lid of the thermocycler.

        Returns:
            ThermocyclerModule: The current module instance.
        """
        command = ThermocyclerModuleCloseLidCommand(
            params=ThermocyclerModuleCloseLidParams(
                moduleId=self.id,
            )
        )
        self.__context._append_command(command)

        self.__context._append_saved_step_form(
            ThermocyclerCommand(
                thermocyclerFormType='thermocyclerState',
                moduleId=self.id,
                lidOpen=False
            )
        )
        self.__lid_open = False
        return self
       
    def set_lid_temp(self, celsius: int, wait_for_temp:bool=True) -> 'ThermocyclerModule':
        """Set the lid temperature.

        Args:
            celsius (int): Temperature of the lid in Celsius. Valid range is 35°C-110°C.
            wait_for_temp (bool, optional): Whether to wait for the lid temperature to be reached. Defaults to True.

        Returns:
            ThermocyclerModule: The current module instance.
        """

        if celsius < 35 or celsius > 110:
            raise ValueError(f"Invalid lid temperature: {celsius}. Valid range is 35°C-110°C.")

        command = ThermocyclerModuleSetLidTempCommand(
            params=ThermocyclerModuleSetLidTempParams(
                moduleId=self.id,
                celsius=celsius
            )
        )
        self.__context._append_command(command)

        self.__context._append_saved_step_form(
            ThermocyclerCommand(
                thermocyclerFormType='thermocyclerState',
                moduleId=self.id,
                lidOpen=self.__lid_open,
                lidIsActive=True,
                lidTargetTemp=str(celsius)
            )
        )
        self.__lid_temp = celsius

        if wait_for_temp:
            command = ThermocyclerModuleWaitForLidTempCommand(
                params=ThermocyclerModuleWaitForLidTempParams(
                    moduleId=self.id,
                )
            )
            self.__context._append_command(command)
        
            # TODO: add wait app command

        return self
       
    def set_block_temp(self, celsius: int, wait_for_temp:bool=True) -> 'ThermocyclerModule':
        """Set the block temperature.

        Args:
            celsius (int): Temperature of the block in Celsius. Valid range is 4°C-110°C.
            wait_for_temp (bool, optional): Whether to wait for the block temperature to be reached. Defaults to True.
            
        Returns:
            ThermocyclerModule: The current module instance.
        """
        if celsius < 4 or celsius > 110:
            raise ValueError(f"Invalid block temperature: {celsius}. Valid range is 4°C-110°C.")

        command = ThermocyclerModuleSetBlockTempCommand(
            params=ThermocyclerModuleSetBlockTempParams(
                moduleId=self.id,
                celsius=celsius
            )
        )
        self.__context._append_command(command)

        self.__context._append_saved_step_form(
            ThermocyclerCommand(
                thermocyclerFormType='thermocyclerState',
                moduleId=self.id,
                lidOpen=self.__lid_open,
                blockIsActive=True,
                blockTargetTemp=str(celsius)
            )
        )
        self.__block_temp = celsius

        if wait_for_temp:
            command = ThermocyclerModuleWaitForBlockTempCommand(
                params=ThermocyclerModuleWaitForBlockTempParams(
                    moduleId=self.id,
                )
            )
            self.__context._append_command(command)

            # TODO: add wait app command

        return self

    def disengage_block(self) -> 'ThermocyclerModule':
        """Disengage the block.

        Returns:
            ThermocyclerModule: The current module instance.
        """
        command = ThermocyclerModuleDeactivateBlockCommand(
            params=ThermocyclerModuleDeactivateBlockParams(
                moduleId=self.id,
            )
        )
        self.__context._append_command(command)

        # disable block
        self.__context._append_saved_step_form(
            ThermocyclerCommand(
                thermocyclerFormType='thermocyclerState',
                moduleId=self.id,
                lidOpen=self.__lid_open,
                blockIsActive=False,
                lidIsActive=True if self.__lid_temp else False
            )
        )
        self.__block_temp = None

        return self
    
    def disengage_lid(self) -> 'ThermocyclerModule':
        """Disengage the lid.

        Returns:
            ThermocyclerModule: The current module instance.
        """
        command = ThermocyclerModuleDeactivateLidCommand(
            params=ThermocyclerModuleDeactivateLidParams(
                moduleId=self.id,
            )
        )
        self.__context._append_command(command)

        # disabel lid
        self.__context._append_saved_step_form(
            ThermocyclerCommand(
                thermocyclerFormType='thermocyclerState',
                moduleId=self.id,
                lidOpen=self.__lid_open,
                lidIsActive=False,
                blockIsActive=True if self.__block_temp else False
            )
        )
        self.__lid_temp = None

        return self

    def disengage(self) -> 'ThermocyclerModule':
        """Disengage both lid and block.

        Returns:
            ThermocyclerModule: The current module instance.
        """
        self.disengage_block()
        self.disengage_lid()
        return self
       
    def run(self, steps: Union[List[Dict], Dict], cycle: int=1, volume: int=0) -> 'ThermocyclerModule':
        """Run the thermocycler profile.

        Args:
            steps (Union[List[Dict], Dict]): The profile steps to run.
            cycle (int, optional): Number of cycles. Defaults to 1.
            volume (int, optional): Block maximum volume in microliters. Defaults to 0.

        Returns:
            ThermocyclerModule: The current module instance.
        """
        _steps = []

        if isinstance(steps, dict):
            steps = [steps]

        for _ in range(cycle):
            for s in steps:
                if s['celsius'] < 4 or s['celsius'] > 99:
                    raise ValueError(f"Invalid temperature: {s['celsius']}. Valid range is 4°C-99°C.")
                _steps.append(ThermocyclerModuleRunProfileStep(celsius=s['celsius'],
                                                               holdSeconds=s['seconds']))
        command = ThermocyclerRunProfileCommand(
            params=ThermocyclerModuleRunProfileParams(
                moduleId=self.id,
                profile=_steps,
                blockMaxVolumeUl=volume
            )
        )
        
        self.__context._append_command(command)

        profile_items = list()
        for idx, step in enumerate(steps):
            item = ProfileItem(
                title=str(idx+1),
                temperature=str(step["celsius"]),
                durationSeconds=str(step["seconds"])
            )
            profile_items.append(item)
        profile_cycle = ProfileCycle(steps=profile_items, repetitions=str(cycle))

        self.__context._append_saved_step_form(
            ThermocyclerCommand(
                thermocyclerFormType='thermocyclerProfile',
                moduleId=self.id,
                lidOpen=self.__lid_open,
                blockIsActive=False,
                lidIsActive=False,
                # blockTargetTemp=str(self.__block_temp) if self.__block_temp else None,
                # lidTargetTemp=str(self.__lid_temp) if self.__lid_temp else None,
                profileTargetLidTemp=str(self.__lid_temp) if self.__lid_temp else None,
                profileVolume=str(volume) if volume else "0",
                orderedProfileItems=[profile_cycle.id],
                profileItemsById={profile_cycle.id: profile_cycle}
            )
        )

        return self