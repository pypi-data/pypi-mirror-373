from . import Labware

class WellPlate(Labware):
    def __init__(self, id: str, labware_name: str, slot: int, definition: dict, context: 'Context'):
        super().__init__(id, labware_name, slot, definition, context)
        self.labware = None
    
    def _get_default_mag_height(self):
        return self._get_definition()['parameters'].get('magneticModuleEngageHeight', None)
    
    def load_labware(self, labware_name):
        """Load labware onto the wellplate (most likely a lid).

        Args:
            labware_name (str): Name of the labware to load.

        Returns:
            Labware: The loaded labware.
        """
        self.labware = self._get_context().load_labware(labware_name, self)
        return self.labware