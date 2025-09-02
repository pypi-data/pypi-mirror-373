from typing import List, Literal, Tuple, Union
from . import Column, Labware, Well
from ..utils.exception import InsufficientTipsErr

class TipRack(Labware):
    def __init__(self, id: str, labware_name: str, slot: int, definition: dict, context: 'Context'):
        super().__init__(id, labware_name, slot, definition, context)
        self.__row_order = [chr(i) for i in range(ord('A'), ord(self._max_row) + 1)] # A, B, C, D, E, F, G, H
        self.__total_tips = len(self._wells)
        self.__tip_status = {well: False for well in self._wells}  # False means unused

    def _get_new_tip(self, count: int = 1, pick_up_tip_order: Literal['top_to_bottom', 'bottom_to_top'] = 'top_to_bottom') -> Union[str, List[str]]:
        """get the new tip based on the tip count

        Args:
            count (int, optional): number of tip to pick. Defaults to 1.
            pick_up_tip_order (Literal['top_to_bottom', 'bottom_to_top'], optional): The order to pick up tips - either from top to bottom of the tiprack or bottom to top. Defaults to 'top_to_bottom'.
        Returns:
            Union[str, List[str]]: list of tip name
        """
        try:
            if count not in [1, 8]:
                raise ValueError("Tip count must be either 1 (single channel) or 8 (multi channel).")

            if self._get_used_tip_count() >= self.__total_tips:
                raise InsufficientTipsErr()

            if not self._is_has_tip(count):
                raise InsufficientTipsErr()
            
            return self._get_single_tip(pick_up_tip_order) if count == 1 else self._get_column_tips()
            
        except InsufficientTipsErr:
            # # keep this function as user may pass a empty tiprack to the pick_up_tip function explicitly
            # # try to use the same tiprack on the deck
            # print('Insufficient tips. Try to load other tipracks on deck...')
            # labware_list = self.__context._get_same_type_labware(self)
            # # Sort labware list by used tip count (most used tips first)
            # labware_list.sort(key=lambda x: x._get_used_tip_count(), reverse=True)
            # if labware_list:
            #     for l in labware_list:
            #         if l._is_has_tip(count):
            #             return l._get_new_tip(count)

            raise InsufficientTipsErr()
    
    def _is_has_tip(self, n_tip):
        """is still has n tip to pick 

        Args:
            n_tip (int): number of tip to pick. either 1 or 8

        Returns:
            bool: true or false
        """
        for col in range(1, self._max_col + 1):
            if n_tip == 1:
                # if at least one tip is unused, return true
                if any(not self.__tip_status[f"{row}{col}"] for row in self.__row_order):
                    return True
            else:
                # if all tips in single column are unused, return true
                column_tips = [f"{row}{col}" for row in self.__row_order[:n_tip]]
                if all(not self.__tip_status[tip] for tip in column_tips):
                    return True
        return False

    def _get_single_tip(self, search_order: Literal['top_to_bottom', 'bottom_to_top'] ='top_to_bottom') -> Tuple['TipRack', str]:
        """Get a single unused tip from the tiprack.

        This method searches through the tiprack in the specified order to find the first unused tip.
        It marks the tip as used and returns its location.

        Args:
            search_order (Literal['top_to_bottom', 'bottom_to_top'], optional): The order to search for tips - either from 
                top to bottom of the tiprack or bottom to top. Defaults to 'top_to_bottom'.

        Raises:
            InsufficientTipsErr: If no unused tips are available in the tiprack.

        Returns:
            Well: The well location containing the unused tip that was found.
        """
        for col in range(1, self._max_col + 1):
            rows = self.__row_order if search_order == 'top_to_bottom' else reversed(self.__row_order)
            for row in rows:
                tip = f"{row}{col}"
                if tip in self.__tip_status and not self.__tip_status[tip]:                    
                    self.__tip_status[tip] = True
                    return self[tip]
        raise InsufficientTipsErr()

    def _get_column_tips(self) -> Tuple['TipRack', str]:
        """get 8 tips

        Raises:
            InsufficientTipsErr: error

        Returns:
            tuple: self instance, first tip name
        """
        for col in range(1, self._max_col + 1):
            column_tips = [f"{row}{col}" for row in self.__row_order if f"{row}{col}" in self.__tip_status]
            if len(column_tips) == 8 and all(not self.__tip_status[tip] for tip in column_tips):
                for tip in column_tips:
                    self.__tip_status[tip] = True
                
                # Extract column number from first tip (e.g. get 1 from 'A1')
                # -1 for index start from 0
                col_num = int(''.join(filter(str.isdigit, column_tips[0])))-1
                return self[col_num]
        raise InsufficientTipsErr()
    
    def _get_max_volume(self) -> int:
        """Get the maximum volume of the tip

        Returns:
            int: volume of liquid in ul
        """
        return int(self._get_definition()["wells"]["A1"]['totalLiquidVolume'])
    
    def _get_used_tip_count(self):
        """get number of used tips

        Returns:
            int: number of used tips
        """
        return sum(val is True for val in self.__tip_status.values())
    
    def _set_used_tip(self, location: Union[Well, Column]):
        """set the status of tip to be used

        Args:
            location (Union[Well, Column]): location of tips
        """
        if isinstance(location, Well):
            self.__tip_status[location.id] = True
        elif isinstance(location, Column):
            for well in location.wells():
                self.__tip_status[well.id] = True
    
    def reset_tip_status(self):
        """reset the status of all tips to be unused
        """
        self.__tip_status = {well: False for well in self._wells}