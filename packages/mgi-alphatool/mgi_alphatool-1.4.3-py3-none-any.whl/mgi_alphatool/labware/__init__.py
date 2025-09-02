from typing import Any, Dict, Union, List, Tuple, Optional
from ..liquid import Liquid
from ..commands.liquid import LoadLiquidCommand, LoadLiquidParams

class Well():
    def __init__(self, id: str, max_vol: float, parent: 'Labware', context: 'Context'):
        """Initialize a well in labware.

        Args:
            id (str): Identifier for the well.
            parent (Labware): Parent labware containing the well.
        """
        self.__id = id
        self.__context = context
        self.__volume = 0
        self.__max_volume = max_vol
        self.__liquid: Optional[Liquid] = None
        self.__parent = parent

    @property
    def id(self) -> str:
        """Get the well ID.

        Returns:
            str: The well ID.
        """
        return self.__id
    
    def _get_parent(self) -> 'Labware':
        """Get the parent labware.

        Returns:
            Labware: The parent labware.
        """
        return self.__parent

    def fill_liquid(self, liquid: Liquid, volume: float):
        """Fill liquid to the well with a specified volume during initial setup.

        Args:
            liquid (Liquid): The liquid to add to the well.
            volume (float): Volume of liquid to add in microliters.

        Raises:
            ValueError: If adding the volume would exceed the well's maximum capacity.

        Note:
            This method is intended for initial setup of the labware before running a protocol.
            Do not use this to simulate liquid transfers during protocol execution.
        """
        self._fill_liquid(liquid, volume)

        self.__context._append_command(
            LoadLiquidCommand(
                params=LoadLiquidParams(
                liquidId=liquid.id,
                labwareId=self._get_parent().id,
                volumeByWell={self.id: volume}
            )))
        return self
    
    def _fill_liquid(self, liquid: Liquid, volume: float):
        """Fill liquid to the well with a specified volume during initial setup.

        Args:
            liquid (Liquid): The liquid to add to the well.
            volume (float): Volume of liquid to add in microliters.

        Raises:
            ValueError: If adding the volume would exceed the well's maximum capacity.

        Note:
            This method is intended for initial setup of the labware before running a protocol.
            Do not use this to simulate liquid transfers during protocol execution.
        """
        self.__liquid = liquid
        self.__volume += volume
        if self.__volume > self.__max_volume:
            raise ValueError(f"Cannot add {volume}uL - would exceed well maximum volume of {self.__max_volume}uL")
        
        return self
    
    # def reduce_liquid(self, volume: float) -> float:
    #     """Remove liquid from the well.

    #     Args:
    #         volume (float): Volume of liquid to remove in microliters.

    #     Returns:
    #         float: The actual volume removed, which may be less than requested if insufficient liquid is present.
    #     """
    #     if self.__liquid is None:
    #         return 0

    #     removed = min(volume, self.__volume)
    #     self.__volume -= removed
    #     if self.__volume == 0:
    #         self.__liquid = None
 
class Column():
    def __init__(self, id: int, parent: 'Labware', context: 'Context'):
        """Initialize a column in labware.

        Args:
            id (int): Identifier for the column.
            parent (Labware): Parent labware containing the column.
        """
        self.__id = id
        self.__parent = parent
        self.__context = context
        self._wells: Dict[str, Well] = {}

    @property
    def id(self) -> str:
        """Get the column ID.

        Returns:
            str: The column ID.
        """
        return self.__id

    def _get_parent(self) -> 'Labware':
        """Get the parent labware containing this column.

        Returns:
            Labware: The parent labware instance.
        """
        return self.__parent

    def _add_well(self, well: Well):
        """Add a well to this column.

        Args:
            well (Well): The well instance to add to this column.
        """
        self._wells[well.id] = well

    def __iter__(self):
        """Make the column iterable over its wells.

        Returns:
            Iterator[Well]: Iterator over the wells in this column.
        """
        return iter(self._wells.values())

    def __getitem__(self, index: int) -> Well:
        """Get a well by its index in the column.

        Args:
            index (int): The index of the well to retrieve.

        Returns:
            Well: The well at the specified index.

        Raises:
            IndexError: If the index is out of range.
        """
        wells_list = list(self._wells.values())
        if index < 0:
            index += len(wells_list)
        if index < 0 or index >= len(wells_list):
            raise IndexError("Well index out of range.")
        return wells_list[index]

    def __len__(self):
        """Get the number of wells in this column.

        Returns:
            int: The number of wells.
        """
        return len(self._wells)
    
    def wells(self) -> List[Well]:
        """Get all wells in the column.

        Returns:
            List[Well]: List of wells.
        """
        return list(self._wells.values())
    
    def fill_liquid(self, liquid: Liquid, volume: float) -> None:
        """Fill all wells in the column with a specified volume of liquid during initial setup.

        Args:
            volume (float): Volume of liquid to fill in each well.
        
        Note:
            This method is intended for initial setup of the labware before running a protocol.
            Do not use this to simulate liquid transfers during protocol execution.
        """
        for well in self._wells.values():
            well._fill_liquid(liquid, volume)
    
        self.__context._append_command(
            LoadLiquidCommand(
                params=LoadLiquidParams(
                liquidId=liquid.id,
                labwareId=self._get_parent().id,
                volumeByWell={well.id: volume for well in self._wells.values()}
            )))

class Labware():
    def __init__(self, id: str, name: str, slot: Union[int, str, 'Module', 'Labware'], definition: dict, context: 'Context'):
        """initialization.

        Args:
            id (str): labware id
            name (str): labware name
            slot (Any): location
            definition (dict): details of labware
            context (Context): context instance
        """
        self.__id = id
        self.__name = name
        self.__slot = slot
        self.__definition = definition
        self.__context = context
        self._columns: Dict[int, Column] = {}
        self._wells: Dict[str, Well] = {}
        self._generate_wells_and_columns()
        self._max_row, self._max_col = self._get_max_row_col()
        self._is_irregular_well = any(len(row) != len(self.__definition['ordering'][0]) for row in self.__definition['ordering'][1:])
        self._height = self.__definition['dimensions']['zDimension']

    # TODO: add a method to get the rows

    @property
    def id(self) -> str:
        """Get the labware ID.

        Returns:
            str: Labware ID.
        """
        return self.__id
    
    def _get_name(self) -> str:
        """Get the labware name.

        Returns:
            str: Labware name.
        """
        return self.__name
    
    def _get_context(self) -> 'Context':
        """Get the context.

        Returns:
            Context: The context.
        """
        return self.__context

    def _get_definition(self) -> dict:
        """Get the labware definition dictionary.

        Returns:
            dict: The complete labware definition.
        """
        return self.__definition
    
    def _generate_wells_and_columns(self):
        """create wells and columns.
        """
        well_ids = sorted(
            self.__definition['wells'],
            key=lambda wid: (int(''.join(filter(str.isdigit, wid))), ''.join(filter(str.isalpha, wid)))
        )
        for well_id in well_ids:
            col_num = int(''.join(filter(str.isdigit, well_id))) - 1
            if col_num not in self._columns:
                self._columns[col_num] = Column(col_num, self, self.__context)
            well = Well(well_id, self._get_definition()['wells'][well_id]['totalLiquidVolume'], self, self.__context)
            self._columns[col_num]._add_well(well)
            self._wells[well_id] = well
    
    def _get_max_row_col(self) -> Tuple[str, int]:
        """get the maximum row and column.

        Returns:
            Tuple[str, int]: the max row (A-H) and column (1-12)
        """
        max_row = ''
        max_col = 0

        for well_id in self._wells.keys():
            # Extract row and column
            row = ''.join(filter(str.isalpha, well_id))
            col = int(''.join(filter(str.isdigit, well_id)))
            
            # Update max row, max col
            max_row = row if row > max_row else max_row
            max_col = col if col > max_col else max_col

        return max_row, max_col

    def __getitem__(self, key: Union[str, int, slice, Tuple[Union[str, int], ...]]) -> Union[Well, Column, List[Well], List[Column]]:
        if isinstance(key, str):
            if key.isdigit():
                if len(key) >= len(self._columns):
                    raise IndexError()
                return self._columns[int(key)]
            return self._wells[key]
        
        elif isinstance(key, int):
            if key >= len(self._columns):
                raise IndexError()
            return self._columns[key]
        
        elif isinstance(key, slice):
            if isinstance(key.start, str) and isinstance(key.stop, str):
                return self._get_wells_by_range(key.start, key.stop)
            
            return [self._columns[i] for i in range(key.start or 0, (key.stop or self._max_col))]
        
        elif isinstance(key, tuple):
            return self._get_multiple_wells_or_columns(key)
        
        else:
            raise TypeError("Key must be a string, int, slice, or tuple of strings or ints")
    
    def _get_wells_by_range(self, start: str, stop: str) -> List[Well]:
        """Get a range of wells between two well positions.

        Args:
            start (str): Starting well position (e.g., 'A1').
            stop (str): Ending well position (e.g., 'H12').

        Returns:
            List[Well]: List of wells within the specified range.
        """
        # source_labware["A1":"A8"]
        start_row = ''.join(filter(str.isalpha, start))
        start_col = int(''.join(filter(str.isdigit, start)))
        stop_row = ''.join(filter(str.isalpha, stop))
        stop_col = int(''.join(filter(str.isdigit, stop)))

        wells = []
        for col in range(start_col, stop_col + 1):
            for row in range(ord('A'), ord(self._max_row) + 1):
                if col == start_col and chr(row) < start_row:
                    continue
                if col == stop_col and chr(row) > stop_row:
                    continue
                well_id = f"{chr(row)}{col}"
                if well_id in self._wells:
                    wells.append(self._wells[well_id])
        return wells

    def _get_multiple_wells_or_columns(self, keys: Tuple[Union[str, int], ...]) -> List[Union[Well, Column]]:
        """Get multiple wells or columns by their keys.

        Args:
            keys (Tuple[Union[str, int], ...]): Tuple of well IDs or column indices.

        Returns:
            List[Union[Well, Column]]: List of requested wells or columns.

        Raises:
            ValueError: If an invalid well key is provided.
            TypeError: If an invalid key type is provided.
        """
        # source_labware["A1":"H12"]
        result = []
        for key in keys:
            if isinstance(key, str):
                if key.isdigit():
                    result.append(self._columns[int(key)])
                elif key in self._wells:
                    result.append(self._wells[key])
                else:
                    raise ValueError(f"Invalid well key: {key}")
            elif isinstance(key, int):
                result.append(self._columns[key])
            else:
                raise TypeError(f"Invalid key type: {type(key)}. Must be str or int.")
        return result

    def _is_tiprack(self) -> bool:
        """Check if the labware is a tip rack.

        Returns:
            bool: True if the labware is a tip rack, False otherwise.
        """
        return self.__definition['parameters']['isTiprack']
    
    def wells(self) -> List[Well]:
        """Get all wells in the labware.

        Returns:
            List[Well]: List of all wells.
        """
        return list(self._wells.values())
    
    def columns(self) -> List[Column]:
        """Get all columns in the labware.

        Returns:
            List[Column]: List of all columns.
        """
        return list(self._columns.values())
    
    def _set_slot(self, slot) -> None:
        """Set the slot location for this labware.

        Args:
            slot (Union[int, Module, Labware]): The slot to assign this labware to.
        """
        self.__slot = slot
    
    def _get_slot(self) -> Union[int, str, 'Module', 'Labware']:
        """Get the slot location of this labware.

        Returns:
            Union[int, Module, Labware]: The current slot assignment.
        """
        return self.__slot

    def _get_height(self) -> float:
        """Get the height dimension of the labware.

        Returns:
            float: The height (z-dimension) of the labware.
        """
        return self._height
    
    def _is_irregular(self) -> bool:
        """Check if the labware has an irregular well pattern.

        Returns:
            bool: True if the well pattern is irregular, False otherwise.
        """
        return self._is_irregular_well

    def fill_liquid(self, liquid: Liquid, volume: float) -> None:
        """Fill all wells in the labware with a specified volume of liquid during initial setup.

        Args:
            liquid (Liquid): The liquid to add to the wells.
            volume (float): Volume of liquid to fill in each well.
        
        Note:
            This method is intended for initial setup of the labware before running a protocol.
            Do not use this to simulate liquid transfers during protocol execution.
        """            
        for well in self._wells.values():
            well._fill_liquid(liquid, volume)
        
        self.__context._append_command(
            LoadLiquidCommand(
                params=LoadLiquidParams(
                liquidId=liquid.id,
                labwareId=self.id,
                volumeByWell={well.id: volume for well in self._wells.values()}
            )))