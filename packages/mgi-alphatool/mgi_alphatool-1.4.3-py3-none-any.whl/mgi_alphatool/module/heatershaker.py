import logging
from . import Module
from ..commands.module import (HeaterShakerModuleOpenLatchParams,HeaterShakerModuleOpenLatchCommand,
                               HeaterShakerModuleCloseLatchParams, HeaterShakerModuleCloseLatchCommand,
                               HeaterShakerModuleSetShakeSpeedParams, HeaterShakerModuleSetShakeSpeedCommand,
                               HeaterShakerModuleSetTempParams, HeaterShakerModuleSetTempCommand,
                               HeaterShakerModuleDeactivateHeaterParams, HeaterShakerModuleDeactivateHeaterCommand,
                               HeaterShakerModuleDeactivateShakerParams, HeaterShakerModuleDeactivateShakerCommand,
                               HeaterShakerModuleWaitForTempParams, HeaterShakerModuleWaitForTempCommand)

from ..commands.wait import WaitForDurationParams, WaitForDurationCommand

from ..app.commands import HeaterShakerCommand, PauseCommand

class HeaterShakerModule(Module):
    def __init__(self, id: str, name: str, slot: int, context: 'Context'):
        """Initialize the heater shaker module.

        Args:
            id (str): The unique identifier for the module.
            name (str): The name of the module.
            slot (int): The location slot of the module.
            context (Context): The protocol context instance.
        """
        super().__init__(id, name, slot, context)
        self.__context = context
        self.__latch_open = True
        
    def set_shaker(self, rpm: int) -> 'HeaterShakerModule':
        """Set the RPM of the shaker module.

        Args:
            rpm (int): Revolutions per minute for the shaker. Valid range: 100 rpm - 2000 rpm

        Returns:
            HeaterShakerModule: The current module instance.
        """
        if rpm < 100 or rpm > 2000:
            raise ValueError(f"Invalid RPM value: {rpm}. Valid range: 100 rpm - 2000 rpm")

        self.__context._append_command(WaitForDurationCommand(
            params=WaitForDurationParams(seconds=1)
        ))

        if self.__latch_open:
            logging.info("Shaker latch is not closed. Will auto close the latch first before shaking.")
            self.close_latch()
            # raise ValueError("Shaker latch is not closed. Please close the latch first before shaking.")

        self.__context._append_command(
            HeaterShakerModuleSetShakeSpeedCommand(
                params=HeaterShakerModuleSetShakeSpeedParams(
                moduleId=self.id,
                rpm=rpm
            )))
        
        self.__context._append_saved_step_form(
            HeaterShakerCommand(
                moduleId=self.id,
                setShake=True,
                latchOpen=self.__latch_open,
                targetSpeed=str(rpm),
                setHeaterShakerTemperature=False,
                heaterShakerSetTimer=False
            )
        )
        
        return self
    
    def set_heater(self, celsius: int, wait_for_temp:bool =True) -> 'HeaterShakerModule':
        """Set the temperature of the heater module.

        Args:
            celsius (int): Target temperature in Celsius. Valid range: 4°C-90°C.
            wait_for_temp (bool, optional): Wait until the target temperature is achieved. Defaults to True.

        Returns:
            HeaterShakerModule: The current module instance.
        """
        if celsius < 0 or celsius > 90:
            raise ValueError(f"Invalid temperature: {celsius}. Valid range: 4°C-90°C.")

        self.__context._append_command(WaitForDurationCommand(
            params=WaitForDurationParams(seconds=1)
        ))

        self.__context._append_command(HeaterShakerModuleSetTempCommand(
            params=HeaterShakerModuleSetTempParams(
                moduleId=self.id,
                celsius=celsius
            )
        ))

        self.__context._append_saved_step_form(
            HeaterShakerCommand(
                moduleId=self.id,
                setShake=False,
                latchOpen=self.__latch_open,
                setHeaterShakerTemperature=True,
                targetHeaterShakerTemperature=str(celsius),
                heaterShakerSetTimer=False
            )
        )

        if wait_for_temp:
            self.__context._append_command(HeaterShakerModuleWaitForTempCommand(
                params=HeaterShakerModuleWaitForTempParams(
                    moduleId=self.id,
                    celsius=celsius
                )
            ))

            self.__context._append_saved_step_form(
                PauseCommand(
                    pauseAction="untilTemperature",
                    pauseTemperature=str(celsius),
                    moduleId=self.id
                )
            )


        return self

    def open_latch(self) -> 'HeaterShakerModule':
        """Open the latch of the module.

        Returns:
            HeaterShakerModule: The current module instance.
        """

        self.__context._append_command(WaitForDurationCommand(
            params=WaitForDurationParams(seconds=1)
        ))

        self.__context._append_command(HeaterShakerModuleOpenLatchCommand(
            params=HeaterShakerModuleOpenLatchParams(
                moduleId=self.id,
            )
        ))
        self.__latch_open = True

        self.__context._append_saved_step_form(
            HeaterShakerCommand(
                moduleId=self.id,
                latchOpen=True,
                setShake=False,
                setHeaterShakerTemperature=False,
                heaterShakerSetTimer=False
            )
        )

        return self
    
    def close_latch(self) -> 'HeaterShakerModule':
        """Close the latch of the module.

        Returns:
            HeaterShakerModule: The current module instance.
        """
        self.__context._append_command(WaitForDurationCommand(
            params=WaitForDurationParams(seconds=1)
        ))

        self.__context._append_command(HeaterShakerModuleCloseLatchCommand(
            params=HeaterShakerModuleCloseLatchParams(
                moduleId=self.id,
            )
        ))
        self.__latch_open = False

        self.__context._append_saved_step_form(
            HeaterShakerCommand(
                moduleId=self.id,
                latchOpen=False,
                setShake=False,
                setHeaterShakerTemperature=False,
                heaterShakerSetTimer=False
            )
        )
        
        return self
       
    def disengage_heater(self) -> 'HeaterShakerModule':
        """Disengage the heater of the module.

        Returns:
            HeaterShakerModule: The current module instance.
        """
        self.__context._append_command(WaitForDurationCommand(
            params=WaitForDurationParams(seconds=1)
        ))

        self.__context._append_command(HeaterShakerModuleDeactivateHeaterCommand(
            params=HeaterShakerModuleDeactivateHeaterParams(
                moduleId=self.id,
            )
        ))

        self.__context._append_saved_step_form(
            HeaterShakerCommand(
                moduleId=self.id,
                latchOpen=self.__latch_open,
                setShake=False,
                setHeaterShakerTemperature=False,
                heaterShakerSetTimer=False
            )
        )

        return self

    def disengage_shaker(self) -> 'HeaterShakerModule':
        """Disengage the shaker of the module.

        Returns:
            HeaterShakerModule: The current module instance.
        """
        self.__context._append_command(WaitForDurationCommand(
            params=WaitForDurationParams(seconds=1)
        ))
        
        self.__context._append_command(HeaterShakerModuleDeactivateShakerCommand(
            params=HeaterShakerModuleDeactivateShakerParams(
                moduleId=self.id,
            )
        ))

        self.__context._append_saved_step_form(
            HeaterShakerCommand(
                moduleId=self.id,
                latchOpen=self.__latch_open,
                setShake=False,
                setHeaterShakerTemperature=False,
                heaterShakerSetTimer=False
            )
        )
        return self

    def disengage(self) -> 'HeaterShakerModule':
        """Disengage both heater and shaker.

        Returns:
            HeaterShakerModule: The current module instance.
        """
        self.disengage_heater()
        self.disengage_shaker()
        return self
        