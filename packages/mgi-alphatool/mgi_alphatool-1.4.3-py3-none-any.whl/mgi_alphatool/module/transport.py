from . import Module
from ..commands.module import (TransportHomeParams, TransportHomeCommand,
                               TransportSendParams, TransportSendCommand)

class TransportModule(Module):
    def __init__(self, id: str, name: str, slot: int, context: 'Context'):
        """Initialize the transport module.

        Args:
            id (str): The unique identifier for the module.
            name (str): The name of the module.
            slot (int): The location slot of the module.
            context (Context): The protocol context instance.
        """
        super().__init__(id, name, slot, context)
        self.__context = context
    
    def send(self):
        """Sending out the labware on the conveyor belt. 
        """
        self.__context._append_command(TransportSendCommand(
            params=TransportHomeParams(
                moduleId=self.id
            )
        ))
        return self

    def home(self):
        """Reset the conveyor belt.
        """
        self.__context._append_command(TransportHomeCommand(
            params=TransportSendParams(
                moduleId=self.id
            )
        ))
        return self
    