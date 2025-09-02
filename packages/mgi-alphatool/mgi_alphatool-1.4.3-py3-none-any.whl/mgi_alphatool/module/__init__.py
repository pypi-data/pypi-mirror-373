from ..labware import Labware
from ..labware.adapter import Adapter

class Module:
    def __init__(self, id: str, name: str, slot: int, context: 'Context'):
        """Abstract class for a module.

        Args:
            id (str): The unique identifier for the module.
            name (str): The name of the module.
            slot (int): The location slot of the module.
            context (Context): The protocol context instance.
        """
        self.__id = id
        self.__name = name
        self.__slot = slot
        self.__context = context
        self.labware = None

    def load_labware(self, labware_name: str) -> Labware:
        """Load labware onto the module.

        Args:
            labware_name (str): The name of the labware to load.

        Returns:
            Labware: The loaded labware instance.
        """
        lw =  self.__context.load_labware(labware_name, self)
        self.labware = lw
        return lw
    
    def load_adapter(self, adapter_name: str) -> Adapter:
        """Load an adapter onto the module. Alias of load_labware() for adapter.

        Args:
            adapter_name (str): The name of the adapter to load.

        Returns:
            Adapter: The loaded adapter instance.
        """
        return self.load_labware(adapter_name)
    
    @property
    def id(self) -> str:
        """Get the module ID.

        Returns:
            str: The module's unique identifier.
        """
        return self.__id
    
    def _get_name(self) -> str:
        return self.__name
    
    def _set_slot(self, slot) -> None:
        self.__slot = slot
    
    def _get_slot(self) -> int:
        return self.__slot