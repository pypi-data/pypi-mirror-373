# from typing import List, Literal, Union

# from ..labware import Labware, Well, Column
# from ..labware.trashbin import TrashBin

class Handler:
    def __init__(self, id: str, name: str, mount: str, context: 'Context'):
        self._id = id
        self._name = name
        self._mount = mount
        self._context = context

    @property
    def id(self) -> str:
        """Get the module ID.

        Returns:
            str: The pipette's unique identifier.
        """
        return self._id

    def _get_name(self) -> str:
        return self._name
    
    def _get_context(self) -> 'Context':
        return self._context

    def _get_mount(self) -> str:
        return self._mount

    # def home(self) -> 'Handler':
    #     """Home the handler. This is a placeholder method that should be implemented by subclasses.

    #     Raises:
    #         NotImplementedError: This is a placeholder method that must be implemented by subclasses.
    #     """
    #     raise NotImplementedError("move_to() must be implemented by subclass")
    
    # def move_to(self, location: Union[Well, Column, TrashBin, Labware],
    #             position: Literal['top', 'bottom'] = 'top',
    #             offset: int = 5) -> 'Handler':
    #     """Move to a specified location. This is a placeholder method that should be implemented by subclasses.

    #     Args:
    #         location (Union[Well, Column, TrashBin]): The target location to move to.
    #         position (str, optional): The position within the well. Whether the 'top' of the well or 'bottom' of the well. Defaults to 'top'.
    #         offset (int, optional): The vertical offset in millimeters from the specified position. Positive values move up, negative values move down. Defaults to 5 mm.

    #     Returns:
    #         Handler: The handler instance.

    #     Raises:
    #         NotImplementedError: This is a placeholder method that must be implemented by subclasses.
    #     """
    #     raise NotImplementedError("move_to() must be implemented by subclass")