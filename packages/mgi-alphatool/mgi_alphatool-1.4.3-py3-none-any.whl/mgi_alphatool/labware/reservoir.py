from . import Labware

class Reservoir(Labware):
    def __init__(self, id: str, labware_name: str, slot: int, definition: dict, context: 'Context'):
        super().__init__(id, labware_name, slot, definition, context)