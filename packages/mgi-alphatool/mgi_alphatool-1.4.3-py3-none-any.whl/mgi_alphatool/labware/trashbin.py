from typing import Union
from . import Labware

class TrashBin(Labware):
    def __init__(self, 
                 id: str, 
                 labware_name: str, 
                 slot: Union[int, str], 
                 definition: dict, 
                 context: 'Context'):
        super().__init__(id, labware_name, slot, definition, context)