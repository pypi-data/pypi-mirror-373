import logging
from . import Handler

from typing import List, Literal, Union
from ..utils.common import flatten_wells
from ..utils.exception import PickUpTipsErr
from ..utils.validation import (validate_disposal, validate_location, 
                                validate_transfer_params, 
                                validate_mix_params, 
                                validate_wells, 
                                validate_tiprack, 
                                validate_mix_in_transfer_params, 
                                validate_delay, 
                                validate_air_gap, 
                                validate_multi_dispense_mode, 
                                validate_volume, 
                                validate_detect_liquid_speed,
                                validate_flow_rate,
                                validate_offset,
                                validate_position,
                                validate_touch_tip,
                                validate_pre_aspirate)

from ..labware import Labware, Well, Column
from ..labware.tiprack import TipRack
from ..labware.trashbin import TrashBin
from ..commands.pipette import (MoveToCommand, MoveToParams,
                               MoveToAreaCommand, MoveToAreaParams,
                               PickUpTipCommand, PickUpTipParams,
                               AspirateCommand, AspirateParams,
                               DispenseCommand, DispenseParams,
                               DispenseInplaceCommand, DispenseInplaceParams,
                               DropTipCommand, DropTipInPlaceCommand, DropTipParams,
                               BlowOutCommand, BlowOutParams,
                               TouchTipCommand, TouchTipParams,
                               MoveToAreaForDropTipCommand, MoveToAreaForDropTipParams)

from ..commands.mark import InternalMarkerParams
from ..app.commands import TransferCommand, MixCommand


class Pipette(Handler):
    def __init__(self, id: str, name: str, mount: str, context: 'Context'):
        super().__init__(id, name, mount, context)
        self.__has_tip = False
        self._current_tip_location = None
        self._current_return_tip = False
        self.n_channel = 1 if self.is_single_channel() else 8

    def __process_wells_and_cols(
            self,
            wells: Union[List[Well],List[Column]]
        ) -> List[Well]:
        """convert the column into well.

        Args:
            wells (Union[List[Well],List[Column]]): input wells or columns

        Returns:
            List[Well]: output wells
        """
        
        # Process wells or columns based on pipette type
        processed = []
        for w in wells:

            if isinstance(w, Column):
                # For multi-channel pipettes, keep columns intact
                # For single-channel pipettes, expand columns to individual wells
                processed.extend([w] if not self.is_single_channel() else w.wells())
            else:
                # if is well, keep it unchange
                processed.append(w)
        return processed
 
    def __execute_transfer(
            self,
            volume: int,
            source_wells: List[Well],
            dest_wells: List[Well],
            tiprack: Union[TipRack, Column, Well, List[Well], List[Column]],
            use_new_tip: str,
            return_tip: bool,
            aspirate_position: Literal['top', 'bottom'],
            aspirate_offset: tuple,
            dispense_position: Literal['top', 'bottom'],
            dispense_offset: tuple,
            aspirate_flow_rate: float,
            dispense_flow_rate: float,
            pre_wet: bool,
            pre_aspirate: float,
            aspirate_touch_tip: bool,
            aspirate_touch_tip_position: Literal['top', 'bottom'],
            aspirate_touch_tip_offset: tuple,
            dispense_touch_tip: bool,
            dispense_touch_tip_position: Literal['top', 'bottom'],
            dispense_touch_tip_offset: tuple,
            detect_liquid_speed: float,
            mix_before_aspirate: Union[tuple, None],
            mix_after_dispense: Union[tuple, None],
            air_gap_after_aspirate: float, 
            air_gap_before_drop_tip: float,
            delay_after_aspirate: int,
            delay_after_aspirate_position: Literal['top', 'bottom'],
            delay_after_aspirate_offset: tuple,
            delay_after_dispense: int,
            delay_after_dispense_position: Literal['top', 'bottom'],
            delay_after_dispense_offset: tuple,
            multi_dispense_mode: False,
            disposal: float,
            disposal_location: Literal['source', 'trash_bin'],
        ) -> None:

        """Executes the liquid transfer process based on the provided parameters."""
        n_src_wells = len(source_wells)
        n_dest_wells = len(dest_wells)

        if isinstance(tiprack, TipRack):
            _tiprack = tiprack
        elif isinstance(tiprack, (Well, Column)):
            _tiprack = tiprack._get_parent()
        elif isinstance(tiprack, list):
            _tiprack = tiprack[0]._get_parent()
        
        max_volume = (_tiprack or self._current_tip_location._get_parent())._get_max_volume()

        def _transfer_chunk(vol: Union[int, float], 
                            max_vol: Union[int, float], 
                            src: Union[Well, Column], 
                            dest: Union[Well, Column, List[Union[Well, Column]]]):
            
            # if dest is a list, then it is in multi-dispense mode
            # then aspirate vol*len(dest)
            volume_remaining = vol

            if pre_wet:
                self.aspirate(volume=min(vol, max_volume), 
                              location=src, 
                              position=aspirate_position,
                              offset=aspirate_offset, 
                              flow_rate=aspirate_flow_rate)
                
                self.dispense(volume=min(vol, max_volume), 
                              location=src, 
                              position=aspirate_position,
                              offset=aspirate_offset, 
                              flow_rate=dispense_flow_rate)
            
            if mix_before_aspirate:
                self.mix(repetitions=mix_before_aspirate[0], 
                          volume=mix_before_aspirate[1], 
                          wells=src, 
                          use_new_tip='never', 
                          return_tip=return_tip,
                          aspirate_position=aspirate_position,
                          aspirate_offset=aspirate_offset,
                          dispense_position=aspirate_position,
                          dispense_offset=aspirate_offset)
            
            if isinstance(dest, (Well, Column)):
                dest = [dest]
                
            while volume_remaining > 0:
                volume_chunk = min(volume_remaining, max_vol)

                if air_gap_after_aspirate:
                    volume_chunk = min(max_vol-air_gap_after_aspirate, volume_remaining)
                
                if pre_aspirate:
                    self.aspirate(volume=pre_aspirate,
                                  location=src,
                                  position='top',
                                  offset=(0,0,5))
                
                if multi_dispense_mode and disposal > 0:
                    extra_disposal_volume = disposal
                else:
                    extra_disposal_volume = 0

                self.aspirate(volume=(volume_chunk*len(dest))+extra_disposal_volume,
                              location=src, 
                              position=aspirate_position,
                              offset=aspirate_offset, 
                              flow_rate=aspirate_flow_rate,
                              detect_liquid_speed=detect_liquid_speed)

                if delay_after_aspirate:
                    self.move_to(src, delay_after_aspirate_position, delay_after_aspirate_offset)
                    self._get_context()._pause(delay_after_aspirate)

                if aspirate_touch_tip:
                    self.touch_tip(position=aspirate_touch_tip_position, offset=aspirate_touch_tip_offset)

                if air_gap_after_aspirate:
                    # call the internal function to grant more parameter control (position)
                    # dispense the air gap before dispense the liquid
                    # TODO: need to handle air gap case in multi-dispense mode?
                    self.air_gap(air_gap_after_aspirate)
                    self.dispense(volume=air_gap_after_aspirate,
                                  location=dest[0] if isinstance(dest, list) else dest,
                                  position='top',
                                  offset=(0,0,5),
                                  flow_rate=dispense_flow_rate)

                for d in dest:

                    # Check if d is the last destination well
                    is_last_dest = (d == dest[-1])
                    if is_last_dest and pre_aspirate > 0:
                        extra_pre_aspirate_volume = pre_aspirate
                    else:
                        extra_pre_aspirate_volume = 0

                    if isinstance(d._get_parent(), TrashBin):
                        self.dispense(volume_chunk+extra_pre_aspirate_volume, d._get_parent(), flow_rate=dispense_flow_rate)
                    else:
                        self.dispense(volume_chunk+extra_pre_aspirate_volume, d, position=dispense_position, offset=dispense_offset, flow_rate=dispense_flow_rate)
                    
                    if delay_after_dispense:
                        self.move_to(d, delay_after_dispense_position, delay_after_dispense_offset)
                        self._get_context()._pause(delay_after_dispense)
                    
                    if dispense_touch_tip:
                        self.touch_tip(position=dispense_touch_tip_position, offset=dispense_touch_tip_offset)
            
                    if mix_after_dispense:
                        self.mix(repetitions=mix_after_dispense[0], volume=mix_after_dispense[1], 
                                wells=d, 
                                use_new_tip='never', 
                                return_tip=return_tip,
                                aspirate_position=dispense_position,
                                aspirate_offset=dispense_offset,
                                dispense_position=dispense_position,
                                dispense_offset=dispense_offset)
                
                if multi_dispense_mode and disposal > 0:
                    self.dispense(volume=extra_disposal_volume,
                                  location=src if disposal_location == 'source' else self._get_context().trash_bin,
                                  position=aspirate_position,
                                  offset=aspirate_offset,
                                  flow_rate=dispense_flow_rate)
                
                volume_remaining -= volume_chunk

        if n_src_wells == n_dest_wells:
            for idx, (src, dest) in enumerate(zip(source_wells, dest_wells)):
                if use_new_tip == 'always' and self.has_tip():
                    
                    if air_gap_before_drop_tip:
                        self.air_gap(air_gap_after_aspirate)
                    if return_tip:
                        self.return_tip()
                    else:
                        self.drop_tip()
                    
                    self.pick_up_tip(tiprack[idx] if isinstance(tiprack, list) else tiprack)

                if not self.has_tip():
                    self.pick_up_tip(tiprack[idx] if isinstance(tiprack, list) else tiprack)    

                _transfer_chunk(volume, max_volume, src, dest)

        elif n_src_wells == 1 or (n_src_wells == 1 and isinstance(source_wells[0], Column) and not self.is_single_channel()):
            
            # Create chunks list first
            chunks = []
            if multi_dispense_mode:
                n_wells_can_dispense = int(max_volume / volume)
                for i in range(0, n_dest_wells, n_wells_can_dispense):
                    dest_wells_chunk = dest_wells[i:i+n_wells_can_dispense]
                    chunks.append(dest_wells_chunk)
            else:
                chunks = dest_wells

            # Process each chunk
            for idx, chunk in enumerate(chunks):
                if use_new_tip == 'always' and self.has_tip():
                    if air_gap_before_drop_tip:
                        self.air_gap(air_gap_after_aspirate)
                    
                    if return_tip:
                        self.return_tip()
                    else:
                        self.drop_tip()
                        
                    self.pick_up_tip(tiprack[idx] if isinstance(tiprack, list) else tiprack)
                
                if not self.has_tip():
                    self.pick_up_tip(tiprack[idx] if isinstance(tiprack, list) else tiprack)
                
                _transfer_chunk(volume, max_volume, source_wells[0], chunk)
  
        elif n_dest_wells == 1 or (n_dest_wells == 1 and isinstance(dest_wells[0], Column) and not self.is_single_channel()):
            if isinstance(tiprack, list):
                pass

            for idx, src in enumerate(source_wells):
                if use_new_tip == 'always' and self.has_tip():

                    if air_gap_before_drop_tip:
                        self.air_gap(air_gap_after_aspirate)
                        
                    if return_tip:
                        self.return_tip()
                    else:
                        self.drop_tip()
                        
                    self.pick_up_tip(tiprack[idx] if isinstance(tiprack, list) else tiprack)
                
                if not self.has_tip():
                    self.pick_up_tip(tiprack[idx] if isinstance(tiprack, list) else tiprack)

                _transfer_chunk(volume, max_volume, src, dest_wells[0])
                
    def transfer(self, 
                 volume: float, 
                 source_wells: Union[List[Well], Well, List[Column], Column, Labware], 
                 dest_wells: Union[List[Well], Well, List[Column], Column, Labware, TrashBin], 
                 tiprack: Union[TipRack, Well, Column, List[Well], List[Column], None] = None, 
                 use_new_tip: Literal['once', 'always', 'never'] = 'once',
                 return_tip: bool = False,
                 aspirate_position: Literal['top', 'bottom'] = 'bottom',
                 aspirate_offset: tuple = (0,0,1),
                 dispense_position: Literal['top', 'bottom'] = 'bottom',
                 dispense_offset: tuple = (0,0,1),
                 aspirate_flow_rate: float = 150,
                 dispense_flow_rate: float = 300,
                 pre_wet: bool = False,
                 pre_aspirate: float = 0,
                 aspirate_touch_tip: bool = False,
                 aspirate_touch_tip_position: Literal['top', 'bottom'] = 'bottom',
                 aspirate_touch_tip_offset: tuple = (0,0,1),
                 dispense_touch_tip: bool = False,
                 dispense_touch_tip_position: Literal['top', 'bottom'] = 'bottom',
                 dispense_touch_tip_offset: tuple = (0,0,1),
                 detect_liquid_speed: float = 0,
                 mix_before_aspirate: Union[tuple, None] = None,
                 mix_after_dispense: Union[tuple, None] = None,
                 air_gap_after_aspirate: float = 0,
                 air_gap_before_drop_tip: float = 0,
                 delay_after_aspirate: int = 0,
                 delay_after_aspirate_position: Literal['top', 'bottom'] = 'bottom',
                 delay_after_aspirate_offset: tuple = (0,0,1),
                 delay_after_dispense: int = 0,
                 delay_after_dispense_position: Literal['top', 'bottom'] = 'bottom',
                 delay_after_dispense_offset: tuple = (0,0,1),
                 multi_dispense_mode: bool= False,
                 disposal: float = 0,
                 disposal_location: Literal['source', 'trash_bin'] = 'source',
                 ) -> 'Pipette':
        """Transfer liquid from source to destination wells.

        This method facilitates the transfer of a specified volume of liquid from source wells to destination wells using a pipette.
        It supports various options for tip usage, liquid handling, and transfer customization.

        Args:
            volume (float): The volume of liquid to transfer.
            source_wells (Union[List[Well], Well, List[Column], Column, Labware]): Source wells/columns to transfer from. If Labware is passed, all wells in the labware will be used.
            dest_wells (Union[List[Well], Well, List[Column], Column, Labware, TrashBin]): Destination wells/columns or trash bin to transfer to.
            tiprack (Union[TipRack, Well, Column, List[Well], List[Column], None], optional): Tip rack (Supports TipRack, Well, Column) for picking up tips. If None, attempts automatic selection. Defaults to None.
            use_new_tip (str, optional): When to use new tips - 'once' (first transfer), 'always' (each transfer), 'never' (reuse tip). Defaults to 'once'. If selected 'never' and there is no tip on the pipette, the pipette will pick up the tip first.
            return_tip (bool, optional): Return tips to tiprack instead of trash when dropping. Defaults to False.
            aspirate_position (str, optional): Position for aspirate - 'top' or 'bottom'. Defaults to 'bottom'.
            aspirate_offset (tuple, optional): (x,y,z) offset in mm from bottom of source well. Defaults to (0,0,1).
            dispense_position (str, optional): Position for dispense - 'top' or 'bottom'. Defaults to 'bottom'.
            dispense_offset (tuple, optional): (x,y,z) offset in mm from bottom of destination well. Defaults to (0,0,1).
            aspirate_flow_rate (float, optional): Aspirate flow rate in uL/s. Defaults to 150.
            dispense_flow_rate (float, optional): Dispense flow rate in uL/s. Defaults to 300.
            pre_wet (bool, optional): Pre-wet tip by aspirating and dispensing before transfer. Defaults to False.
            pre_aspirate (float, optional): Pre-aspirate volume in uL. Defaults to 0.
            aspirate_touch_tip (bool, optional): Touch tip to well side after aspiration. Defaults to False.
            aspirate_touch_tip_position (str, optional): Position for aspirate touch tip - 'top' or 'bottom'. Defaults to 'bottom'.
            aspirate_touch_tip_offset (tuple, optional): (x,y,z) offset in mm for aspirate touch tip. Defaults to (0,0,1).
            dispense_touch_tip (bool, optional): Touch tip to well side after dispensing. Defaults to False.
            dispense_touch_tip_position (str, optional): Position for dispense touch tip - 'top' or 'bottom'. Defaults to 'bottom'.
            dispense_touch_tip_offset (tuple, optional): (x,y,z) offset in mm for dispense touch tip. Defaults to (0,0,1).
            detect_liquid_speed (float, optional): Detect liquid speed in mm/s. Defaults to 0 means no detection.
            mix_before_aspirate (tuple, optional): (repetitions, volume) for mixing before aspirating. Defaults to None.
            mix_after_dispense (tuple, optional): (repetitions, volume) for mixing after dispensing. Defaults to None.
            air_gap_after_aspirate (float, optional): Air volume to aspirate after liquid to prevent drips. Defaults to 0.
            air_gap_before_drop_tip (float, optional): Air volume to aspirate before dropping tip. Defaults to 0.
            delay_after_aspirate (int, optional): Seconds to wait after aspirating. Defaults to 0.
            delay_after_aspirate_position (str, optional): Position for delay after aspirating - 'top' or 'bottom'. Defaults to 'bottom'.
            delay_after_aspirate_offset (tuple, optional): (x,y,z) offset in mm for delay after aspirating. Defaults to (0,0,1).
            delay_after_dispense (int, optional): Seconds to wait after dispensing. Defaults to 0.
            delay_after_dispense_position (str, optional): Position for delay after dispensing - 'top' or 'bottom'. Defaults to 'bottom'.
            delay_after_dispense_offset (tuple, optional): (x,y,z) offset in mm for delay after dispensing. Defaults to (0,0,1).
            multi_dispense_mode (bool, optional): If True, the pipette will aspirate once and dispense to multiple destination wells at the same time. Only suitable for one to many transfer. Defaults to False.
            disposal (float, optional): Volume to dispose after dispensing. Defaults to 0. Only works when multi_dispense_mode is True.
            disposal_location (str, optional): Location to dispose - 'source' or 'trash_bin'. Defaults to 'source'. Only works when multi_dispense_mode is True.
            
        Returns:
            Pipette: The pipette instance for method chaining.

        Note:
            - For mix parameters, provide a tuple of (repetitions, volume)
            - Offsets are measured in millimeters relative to well positions
            - Air gaps help prevent cross-contamination and dripping
        """
        source_wells = [source_wells] if isinstance(source_wells, (Well, Column)) else source_wells
        dest_wells = [dest_wells] if isinstance(dest_wells, (Well, Column)) else dest_wells

        if isinstance(source_wells, Labware):
            # by default return column, not well since single channel pipette can access column but 8 channel pipette cannot access well
            # source_wells = source_wells.wells()
            source_wells = source_wells.columns()
        if isinstance(dest_wells, Labware):
            # dest_wells = dest_wells.wells()
            dest_wells = dest_wells.columns()

        source_wells = flatten_wells(source_wells)
        dest_wells = flatten_wells(dest_wells)

        # validation parameters
        validate_transfer_params(self, source_wells, dest_wells)
        validate_wells(source_wells)
        validate_wells(dest_wells)

        # validate offset
        validate_offset(aspirate_offset, "aspirate_offset")
        validate_offset(dispense_offset, "dispense_offset")
        validate_offset(aspirate_touch_tip_offset, "aspirate_touch_tip_offset")
        validate_offset(dispense_touch_tip_offset, "dispense_touch_tip_offset")
        validate_offset(delay_after_aspirate_offset, "delay_after_aspirate_offset")
        validate_offset(delay_after_dispense_offset, "delay_after_dispense_offset")

        # validate flow rate
        validate_flow_rate(aspirate_flow_rate, "aspirate_flow_rate")
        validate_flow_rate(dispense_flow_rate, "dispense_flow_rate")

        # validate position
        validate_position(aspirate_position, "aspirate_position")
        validate_position(dispense_position, "dispense_position")
        validate_position(aspirate_touch_tip_position, "aspirate_touch_tip_position")
        validate_position(dispense_touch_tip_position, "dispense_touch_tip_position")
        validate_position(delay_after_aspirate_position, "delay_after_aspirate_position")
        validate_position(delay_after_dispense_position, "delay_after_dispense_position")

        # Validate mix_before and mix_after
        validate_mix_in_transfer_params(mix_before_aspirate, "mix_before")
        validate_mix_in_transfer_params(mix_after_dispense, "mix_after")

        # Validate delay_after_aspirate and delay_after_dispense
        validate_delay(delay_after_aspirate, "delay_after_aspirate")
        validate_delay(delay_after_dispense, "delay_after_dispense")

        # Validate touch tip offset
        validate_touch_tip(aspirate_touch_tip_offset, "aspirate_touch_tip_offset")
        validate_touch_tip(dispense_touch_tip_offset, "dispense_touch_tip_offset")

        validate_pre_aspirate(pre_aspirate, "pre_aspirate")
        validate_disposal(disposal, "disposal")

        # Validate option
        if use_new_tip not in ['once', 'always', 'never']:
            raise ValueError("Invalid value for use_new_tip. Expected 'once', 'always', or 'never'.")
        
        if disposal_location not in ['source', 'trash_bin']:
            raise ValueError("Invalid value for disposal_location. Expected 'source' or 'trash_bin'.")
    
        # try to get the tiprack from deck
        # if no need to change tip and there is a tip on the pipette, skip the tip check
        if use_new_tip == 'never' and self.has_tip():
            _tiprack= self._current_tip_location._get_parent()
        else:
            if isinstance(tiprack, TipRack):
                _tiprack = tiprack
            elif isinstance(tiprack, Well) or isinstance(tiprack, Column):
                _tiprack = tiprack._get_parent()
            elif isinstance(tiprack, list):
                _tiprack = tiprack[0]._get_parent()
            elif tiprack is None:
                tiprack = self._get_context()._auto_get_tiprack(volume=volume, n_tip=self.n_channel)
                _tiprack = tiprack
            else:
                raise ValueError("Invalid tiprack type. Expected TipRack, Well, or Column.")
        
        if _tiprack is None:
            raise ValueError("Tiprack must be provided when using new tips and no tiprack is loaded on the deck.")

        # Validate air gap volumes
        max_volume = (_tiprack and _tiprack._get_max_volume()) or (self._current_tip_location and self._current_tip_location._get_parent()._get_max_volume())
        validate_air_gap(air_gap_after_aspirate, max_volume, "air_gap_after_aspirate")
        validate_air_gap(air_gap_before_drop_tip, max_volume, "air_gap_before_drop_tip")

        # preprocessing the well list
        source_wells = self.__process_wells_and_cols(source_wells)
        dest_wells = self.__process_wells_and_cols(dest_wells)

        # validate tiprack param if it is a list
        # no. of tip must be equal to no. of dest wells/columns
        if isinstance(tiprack, list):
            if len(dest_wells) > 1:
                if len(tiprack) != len(dest_wells):
                    raise ValueError("Number of tips must be equal to number of destination wells.")
            elif len(source_wells) > 1:
                if len(tiprack) != len(source_wells):
                    raise ValueError("Number of tips must be equal to number of source wells.")
            else:
                raise ValueError("Number of tips must be equal to number of destination wells or source wells.")

        # validate multi dispense mode
        try:
            if multi_dispense_mode:
                validate_multi_dispense_mode(source_wells, dest_wells, max_volume, volume)
        except ValueError as e:
            # warn user that multi dispense mode is not supported and will ignore this time
            logging.warning(f"Warning: Multi-dispense mode is not supported. Will be ignored this time. {e}")
            multi_dispense_mode=False

        # add the marker command
        self._get_context()._append_command(InternalMarkerParams(
            use_new_tip=use_new_tip,
            pipette_id=self.id
        ))

        # once: need to replace tip only at the beginning (if possible)
        # always: replace the tip for each transfer
        if (use_new_tip == 'once' or use_new_tip == 'always') and self.has_tip():
            # this is for the last transfer or mix command. if last command mentioned return tip, then return tip now.
            self.drop_tip(self._current_tip_location if self._current_return_tip else None)

        # always record the last transfer is return tip or not
        self._current_return_tip = return_tip

        # run the command
        self.__execute_transfer(volume, source_wells, dest_wells, 
                                _tiprack if tiprack is None else tiprack, 
                                use_new_tip, return_tip,
                                aspirate_position,
                                aspirate_offset,
                                dispense_position,
                                dispense_offset,
                                aspirate_flow_rate,
                                dispense_flow_rate,
                                pre_wet, 
                                pre_aspirate,
                                aspirate_touch_tip, aspirate_touch_tip_position, aspirate_touch_tip_offset, 
                                dispense_touch_tip, dispense_touch_tip_position, dispense_touch_tip_offset,
                                detect_liquid_speed,
                                mix_before_aspirate, mix_after_dispense,
                                air_gap_after_aspirate, air_gap_before_drop_tip,
                                delay_after_aspirate, delay_after_aspirate_position, delay_after_aspirate_offset,
                                delay_after_dispense, delay_after_dispense_position, delay_after_dispense_offset,
                                multi_dispense_mode,
                                disposal, disposal_location
                                )
        
        if disposal_location == 'source':
            _disposal_location = 'source_well'
        elif disposal_location == 'trash_bin':
            _disposal_location = self._get_context()._get_trash_bin().id.split(":")[0]+':trashBin'

        _drop_tip_location = self._get_context()._get_trash_bin().id.split(":")[0]+':trashBin'

        self._get_context()._append_saved_step_form(
            TransferCommand(
                volume=volume,
                pipette=self.id,
                tipRack=_tiprack.id.split(":")[-1],
                preWetTip=pre_wet,

                preAspirate=pre_aspirate>0,
                preAspirateVolume=pre_aspirate if pre_aspirate>0 else None,

                aspirate_wells=[self.__get_well_name(well) for well in source_wells],
                dispense_wells=[self.__get_well_name(well) for well in dest_wells],
                aspirate_labware=source_wells[0]._get_parent().id,
                dispense_labware=dest_wells[0]._get_parent().id,
                dropTip_location=_drop_tip_location,

                aspirate_mmFromBottom=aspirate_offset[2] if aspirate_position=='bottom' else None,
                dispense_mmFromBottom=dispense_offset[2] if aspirate_position=='bottom' else None,

                aspirate_mix_checkbox=bool(mix_before_aspirate),
                aspirate_mix_times=mix_before_aspirate[0] if mix_before_aspirate else None,
                aspirate_mix_volume=mix_before_aspirate[1] if mix_before_aspirate else None,
                dispense_mix_checkbox=bool(mix_after_dispense),
                dispense_mix_times=mix_after_dispense[0] if mix_after_dispense else None,
                dispense_mix_volume=mix_after_dispense[1] if mix_after_dispense else None,
                
                changeTip=use_new_tip,
                
                aspirate_airGap_volume=air_gap_after_aspirate,
                aspirate_airGap_checkbox=air_gap_after_aspirate > 0,
                dispense_airGap_volume=air_gap_before_drop_tip,
                dispense_airGap_checkbox=air_gap_before_drop_tip > 0,
                aspirate_delay_seconds=max(delay_after_aspirate, 0),
                aspirate_delay_checkbox=delay_after_aspirate > 0,
                dispense_delay_seconds=max(delay_after_dispense, 0),
                dispense_delay_checkbox=delay_after_dispense > 0,
                aspirate_delay_mmFromBottom=delay_after_aspirate_offset[2] if delay_after_aspirate_position == 'bottom' else None,
                dispense_delay_mmFromBottom=delay_after_dispense_offset[2] if delay_after_aspirate_position == 'bottom' else None,

                aspirate_touchTip_checkbox=aspirate_touch_tip,
                dispense_touchTip_checkbox=dispense_touch_tip,
                aspirate_touchTip_mmFromBottom=aspirate_touch_tip_offset[2] if aspirate_touch_tip_position=='bottom' else None,
                dispense_touchTip_mmFromBottom=dispense_touch_tip_offset[2] if dispense_touch_tip_position=='bottom' else None,

                aspirate_wells_grouped=False,
                aspirate_detect_checkbox=detect_liquid_speed > 0,
                aspirate_detect_mmsSpeed=detect_liquid_speed if detect_liquid_speed > 0 else None,

                aspirate_flowRate=aspirate_flow_rate,
                dispense_flowRate=dispense_flow_rate,

                path="single" if not multi_dispense_mode else "multiDispense",
                disposalVolume_volume=disposal,
                disposalVolume_checkbox=disposal > 0,
                disposalVolume_location=_disposal_location,
            )
        )

        self._get_context()._await_drop_tip_before_next_pipette_command(self._get_mount())

        return self

    def __get_well_name(self, location: Union[Well, Column]) -> str:
        """Extract well name from location, handling both Well and Column types."""
        if isinstance(location, Column):
            return location.wells()[0].id
        return location.id

    def mix(self,
            repetitions: int,
            volume: float,
            wells: Union[List[Well], List[Column], Well, Column, None] = None,
            tiprack: Union[TipRack, None] = None,
            use_new_tip: Literal['once', 'always', 'never'] = 'once',
            return_tip: bool = False,
            aspirate_position: Literal['top', 'bottom'] = 'bottom',
            aspirate_offset: tuple = (0,0,1),
            dispense_position: Literal['top', 'bottom'] = 'bottom',
            dispense_offset: tuple = (0,0,1),
            pre_aspirate: float = 0,
            delay_after_aspirate: int = 0,
            delay_after_dispense: int = 0,
            touch_tip: bool = False,
            touch_tip_position: Literal['top', 'bottom'] = 'top',
            touch_tip_offset: tuple = (0,0,0),
            aspirate_flow_rate: float = 150,
            dispense_flow_rate: float = 300,
            ) -> 'Pipette':
        """Mix liquid in specified wells. Performs a mixing operation by repeatedly aspirating and dispensing liquid in the given wells.

        Args:
            repetitions (int): Number of times to repeat the mix operation.
            volume (float): Volume in microliters (µL) to aspirate and dispense.
            wells (Union[List[Well], List[Column], Well, Column], optional): Target wells for mixing.
                Can be a single Well/Column or a list. Defaults to current location.
            tiprack (Union[TipRack, None], optional): Tip rack to use. If None, auto-selected.
            use_new_tip (str, optional): When to use new tips - 'once', 'always', or 'never'.
                'once': New tip at start only
                'always': New tip for each well
                'never': Reuse existing tip
                Defaults to 'once'.
            return_tip (bool, optional): Return tip after mixing. Defaults to False.
            aspirate_position (str, optional): Position for aspirate - 'top' or 'bottom'. Defaults to 'bottom'.
            aspirate_offset (tuple, optional): (x,y,z) offset in mm for aspirate. Defaults to (0,0,1).
            dispense_position (str, optional): Position for dispense - 'top' or 'bottom'. Defaults to 'bottom'.
            dispense_offset (tuple, optional): (x,y,z) offset in mm for dispense. Defaults to (0,0,1).
            pre_aspirate (float, optional): Volume to pre-aspirate. Defaults to 0 meaning no pre-aspirate.
            delay_after_aspirate (int, optional): Seconds to wait after aspirating. Defaults to 0.
            delay_after_dispense (int, optional): Seconds to wait after dispensing. Defaults to 0.
            touch_tip (bool, optional): Touch tip to well side after mixing. Defaults to False.
            touch_tip_position (str, optional): Position for touch tip - 'top' or 'bottom'. Defaults to 'top'.
            touch_tip_offset (tuple, optional): (x,y,z) offset in mm for touch tip. Defaults to (0,0,0).
            aspirate_flow_rate (float, optional): Aspirate flow rate in uL/s. Defaults to 150.
            dispense_flow_rate (float, optional): Dispense flow rate in uL/s. Defaults to 300.
           
        Returns:
            Pipette: The pipette instance.
        """
        # Get current location if no wells specified
        if wells is None:
            wells = self._get_context()._get_arm_location()

        # Convert single well/column to list
        if isinstance(wells, (Well, Column)):
            wells = [wells]
        
        # Convert labware to well list
        if isinstance(wells, Labware):
            # wells = wells.wells()
            wells = wells.columns()

        # Flatten and validate wells
        wells = flatten_wells(wells)

        validate_mix_params(self, wells)
        validate_wells(wells)
        validate_pre_aspirate(pre_aspirate, "pre_aspirate")
        validate_touch_tip(touch_tip_offset, "touch_tip_offset")

        validate_delay(delay_after_aspirate, "delay_after_aspirate")
        validate_delay(delay_after_dispense, "delay_after_dispense")

        wells = self.__process_wells_and_cols(wells)
        
        # try to get the tiprack from deck
        # if no need to change tip and there is a tip on the pipette, skip the tip check
        if use_new_tip == 'never' and self.has_tip():
            _tiprack = self._current_tip_location._get_parent()
        else:
            if tiprack is None:
                _tiprack = self._get_context()._auto_get_tiprack(volume=volume, n_tip=self.n_channel)    
            elif isinstance(tiprack, Well) or isinstance(tiprack, Column):
                _tiprack = tiprack._get_parent()
            elif isinstance(tiprack, TipRack):
                _tiprack = tiprack
            else:
                raise ValueError("Invalid tiprack type. Expected TipRack, Well, or Column.")

        # add the marker command
        self._get_context()._append_command(InternalMarkerParams(
            use_new_tip=use_new_tip,
            pipette_id=self.id
        ))

        # once: need to replace tip only at the beginning (if possible)
        # always: replace the tip for each transfer
        if (use_new_tip == 'once' or use_new_tip == 'always') and self.has_tip():
            self.drop_tip(self._current_tip_location if self._current_return_tip else None)

        self._current_return_tip = return_tip
        
        for well in wells:
            # Handle tip management
            # Ensure we have a fresh tip if needed            
            if use_new_tip == 'always' and self.has_tip():
                if return_tip:
                    self.return_tip()
                else:
                    self.drop_tip()

            if not self.has_tip():
                self.pick_up_tip(_tiprack)

            if pre_aspirate > 0:
                self.aspirate(volume=pre_aspirate, location=well, 
                              position='top',
                              offset=(0,0,5), 
                              flow_rate=aspirate_flow_rate)

            # Perform mixing
            for _ in range(repetitions):
                self.aspirate(volume=volume, location=well, 
                              position=aspirate_position,
                              offset=aspirate_offset, 
                              flow_rate=aspirate_flow_rate)
                
                if delay_after_aspirate:
                    self._get_context()._pause(delay_after_aspirate)


                # check if the last iteration of the loop
                extra_volume = 0
                if _ == repetitions - 1 and pre_aspirate > 0:
                    extra_volume = pre_aspirate
                
                self.dispense(volume=volume + extra_volume, location=well, 
                              position=dispense_position,
                              offset=dispense_offset, 
                              flow_rate=dispense_flow_rate)
                
                if delay_after_dispense:
                    self._get_context()._pause(delay_after_dispense)

            # Optional post-mix steps
            if touch_tip:
                self.touch_tip(position=touch_tip_position, offset=touch_tip_offset)
            
        self._get_context()._await_drop_tip_before_next_pipette_command(self._get_mount())

        self._get_context()._append_saved_step_form(
            MixCommand(
                times=repetitions,
                wells=[self.__get_well_name(w) for w in wells],
                volume=volume,
                labware=wells[0]._get_parent().id,
                pipette=self.id,
                tipRack=_tiprack.id.split(":")[-1],
                changeTip=use_new_tip,
                dropTip_location=self._get_context()._get_trash_bin().id.split(":")[0]+':trashBin',
                mix_touchTip_checkbox=touch_tip,
                aspirate_delay_seconds=max(delay_after_aspirate, 1),
                dispense_delay_seconds=max(delay_after_dispense, 1),
                aspirate_delay_checkbox=delay_after_aspirate > 0,
                dispense_delay_checkbox=delay_after_dispense > 0,
                aspirate_flowRate=aspirate_flow_rate,
                dispense_flowRate=dispense_flow_rate,
                mix_mmFromBottom=aspirate_offset[2] if aspirate_position=='bottom' else None,
                mix_touchTip_mmFromBottom=touch_tip_offset[2] if touch_tip_position=='bottom' else None,
                preAspirate=pre_aspirate>0,
                preAspirateVolume=pre_aspirate if pre_aspirate>0 else None
            )
        )

        return self
    
    def aspirate(self, volume: float, 
                 location: Union[Well, Column]=None,
                 flow_rate: float = 5,
                 position: Literal['top','bottom'] = 'bottom',
                 offset: tuple = (0,0,1),
                 detect_liquid_speed: float = 0,
                 **kwargs) -> 'Pipette':
        """Aspirate liquid from a specified location. This method performs an aspiration of a specified volume from a given well or column.

        Args:
            volume (float): The volume in microliters (µL) to aspirate.
            location (Union[Well, Column], optional): The well or column from which to aspirate. Defaults to current location if not specified.
            float_rate (float, optional): The aspirate speed. Defaults to 5 ul/s
            offset (tuple, optional): A tuple of (x,y,z) offsets in millimeters from the reference position. Defaults to (0,0,1).
            detect_liquid_speed (float, optional): Detect liquid speed in mm/s. Defaults to 0 means no detection.
            **kwargs: Additional keyword arguments to pass to the internal aspirate function.

        Returns:
            Pipette: The pipette instance.
        """
        validate_volume(volume, "volume")
        validate_detect_liquid_speed(detect_liquid_speed, "detect_liquid_speed")
        validate_offset(offset, "offset")
        validate_flow_rate(flow_rate, "flow_rate")
        validate_position(position, "position")

        return self.__aspirate(volume=volume,
                        location=location,
                        flow_rate=flow_rate,
                        position=position,
                        offset=offset,
                        detect_liquid_speed=detect_liquid_speed,
                        **kwargs
                        )
    
    def __aspirate(self, volume: float, 
                 location: Union[Well, Column, None]=None,
                 flow_rate: float = 5,
                 position: Literal['top','bottom'] = 'bottom',
                 offset: tuple = (0,0,1),
                 detect_liquid_speed: float = 0,
                 **kwargs) -> 'Pipette':
        """internal function of aspirate."""
        location = self.__get_validated_location(location)
        
        if not self.has_tip():
            raise ValueError("Need to pick up tips first before aspiration.")

        validate_location(self, location)
            
        self._get_context()._append_command(AspirateCommand(
            params=AspirateParams(
                pipetteId=self.id, 
                volume=volume, 
                labwareId=location._get_parent().id, 
                wellName=self.__get_well_name(location),
                flowRate=flow_rate,
                wellLocation=self.__create_well_location(position, offset),
                detectLiquid=detect_liquid_speed > 0,
                detectSpeed=detect_liquid_speed if detect_liquid_speed > 0 else None,
                **kwargs
                )))
        
        self._get_context()._set_arm_location(location)
        return self
        
    def dispense(self, volume: float, 
                 location: Union[Well, Column, TrashBin]= None,
                 flow_rate: float = 10,
                 position: Literal['top','bottom'] = 'bottom',
                 offset: tuple = (0,0,1),
                 **kwargs) -> 'Pipette':
        """Dispense liquid into a specified location. This method performs a dispensation of a specified volume into a given well or column.

        Args:
            volume (float): The volume in microliters (µL) to dispense.
            location (Union[Well, Column, TrashBin], optional): The well or column to dispense into. If TrashBin is passed, it will dispense the liquid to the trash bin. Defaults to the current location if not specified.
            float_rate (float): The dispense speed. Defaults to 10 ul/s
            position (Literal['top', 'bottom'], optional): The position within the well. Wether the 'top' of the well or 'bottom' of the well. Defaults to 'bottom'.
            offset (tuple, optional): A tuple of (x,y,z) offsets in millimeters from the reference position. Defaults to (0,0,1).

        Returns:
            Pipette: The pipette instance.
        """
        validate_volume(volume, "volume")
        validate_offset(offset, "offset")
        validate_flow_rate(flow_rate, "flow_rate")
        validate_position(position, "position")

        return self.__dispense(volume=volume,
                           location=location, 
                           flow_rate=flow_rate,
                           position=position,
                           offset=offset,
                           **kwargs)
    
    def __dispense(self, volume: float, 
                 location: Union[Well, Column, TrashBin, None]= None,
                 flow_rate: float = 10,
                 position: Literal['top','bottom'] = 'bottom',
                 offset: tuple = (0,0,1),
                 **kwargs) -> 'Pipette':
        """internal function of dispense.
        """
        location = self.__get_validated_location(location)
        
        if not self.has_tip():
            raise ValueError("Need to pick up tips first before dispensation.")
        
        validate_location(self, location)
        
        if isinstance(location, TrashBin):
            self.move_to(location, 'top', (0,0,5))
            self._get_context()._append_command(DispenseInplaceCommand(
                params=DispenseInplaceParams(
                    pipetteId=self.id, 
                    volume=volume
                )
            ))

        else:
            self._get_context()._append_command(DispenseCommand(
                params=DispenseParams(pipetteId=self.id, 
                    volume=volume, 
                    labwareId=location._get_parent().id, 
                    wellName=self.__get_well_name(location),
                    flowRate=flow_rate,
                    wellLocation=self.__create_well_location(position, offset),
                    **kwargs
                    )))
        
            self._get_context()._set_arm_location(location)
        return self
    
    def pick_up_tip(self, location: Union[TipRack, Well, Column, None] = None) -> 'Pipette':
        """Pick up a tip from the specified location. This method picks up a tip from a given TipRack, Well, or Column. If no location is provided, it attempts to automatically select a TipRack.

        Args:
            location (Union[TipRack, Well, Column], optional): The location to pick up a tip from. Can be a TipRack, Well, or Column. Defaults to None for automatic selection.

        Returns:
            Pipette: The pipette instance.
        """
        self._get_context()._append_command(InternalMarkerParams(
            use_new_tip='always',
            pipette_id=self.id
        ))

        if self.has_tip():
            raise PickUpTipsErr("Pipette already has a tip on it. Please drop the tip before picking up a new one.")
        
        # check if another pipette already has a tip (since having tip on two pipettes at the same time is not allowed)
        if self._get_context()._is_both_pipettes_have_tips():
            raise PickUpTipsErr("Cannot pick up tip - another pipette already has a tip on it.")
        
        if isinstance(location, (Well,Column)):
            validate_location(self, location)
            tiprack = location._get_parent()
        elif isinstance(location, TipRack):
            tiprack = location
        else:
            tiprack = self._get_context()._auto_get_tiprack(n_tip=self.n_channel)

        # validate if tiprack provided or found
        validate_tiprack(tiprack)

        # Get tip location and well name
        if isinstance(location, (Well, Column)):
            tiprack._set_used_tip(location)
            self._current_tip_location = location
        else:
            self._current_tip_location = tiprack._get_new_tip(self.n_channel, self._get_context()._get_pick_up_tip_order())

        well_name = self.__get_well_name(self._current_tip_location)

        self._get_context()._append_command(PickUpTipCommand(
            params=PickUpTipParams(
                pipetteId=self.id, 
                labwareId=self._current_tip_location._get_parent().id, 
                wellName=well_name)
        ))
        
        self.__has_tip = True
        self._get_context()._set_arm_location(location)
        return self

    def drop_tip(self, location: Union[Well, Column, None] = None) -> 'Pipette':
        """Drop the tip from the pipette. This method drops the current tip. If a location is specified, the tip is dropped there; otherwise, it is dropped into the trash.

        Args:
            location (Union[Well, Column], optional): The location to drop the tip. Defaults to None, which drops the tip into the trash.
        
        Returns:
            Pipette: The pipette instance.

        Raises:
            ValueError: If the specified location is not part of a tip rack.
        """
        if not self.has_tip():
            # logging.warning("Warning: No tip is attached to the pipette. Will ignore this command.")
            return 

        if location is not None:
            # Validate that location is part of a tip rack
            parent = location._get_parent()
            if not isinstance(parent, TipRack):
                raise ValueError("Tips can only be dropped into tip racks or trash. The specified location is not part of a tip rack.")
            
            self.move_to(location,'bottom',(0,0,10))
            self._get_context()._append_command(DropTipInPlaceCommand(params=DropTipParams(pipetteId=self.id)))
        else:
            # drop tip to trash bin
            self._get_context()._append_command(MoveToAreaForDropTipCommand(params=MoveToAreaForDropTipParams(pipetteId=self.id)))
            self._get_context()._append_command(DropTipInPlaceCommand(params=DropTipParams(pipetteId=self.id)))
            self._get_context()._set_arm_location(self._get_context().trash_bin)

        self.__has_tip = False
        self._current_tip_location = None
        return self
    
    def return_tip(self) -> 'Pipette':
        """Return the current tip to its original location in the tiprack. This is an alias function of pipette.drop_tip(tip_location).

        Returns:
            Pipette: The pipette instance.
        """
        self.drop_tip(self._current_tip_location)

    def touch_tip(self, 
                  location: Union[Well, Column] = None,
                  position: Literal['top', 'bottom'] = 'top',
                  offset: tuple = (0,0,0)) -> 'Pipette':
        """Touch the pipette tip to the side of a well or column. This method performs a touch tip action, which can help remove droplets from the tip. If no location is specified, the action is performed at the current location.

        Args:
            location (Union[Well, Column], optional): The well or column to touch the tip. Defaults to None for performing the action in place.
            position (str, optional): The position within the well. Wether the 'top' of the well or 'bottom' of the well. Defaults to 'top'.
            offset (int, optional): The x, y, z offset in millimeters for the touch tip operation. Defaults to (0,0,0).

        Returns:
            Pipette: pipette instance
        """
        validate_position(position, "position")
        validate_offset(offset, "offset")
        validate_touch_tip(offset, "offset")

        if location is not None:
            self.move_to(location, position, offset)
        
        if not self.has_tip():
            raise RuntimeError("No tip is attached to the pipette. Please pick up the tip first.")

        loc = self._get_context()._get_arm_location()
        if isinstance(loc, Column):
            loc = loc.wells()[0]

        self._get_context()._append_command(TouchTipCommand(
            params=TouchTipParams(
                pipetteId=self.id,
                labwareId=loc._get_parent().id,
                wellName=loc.id,
                wellLocation=self.__create_well_location(position, offset)
                )))
        
        return self
    
    def air_gap(self, volume):
        """Aspirates air into the pipette tip in place to create an air gap.

        Args:
            volume (float): The volume of air to aspirate, typically in microliters (µL).
        
        Returns:
            Pipette: The pipette instance after the air gap action.
        """
        if not self.has_tip():
            raise RuntimeError("No tip is attached to the pipette. Please pick up the tip first.")

        if not self._get_context()._get_arm_location():
            raise RuntimeError("Cannot locate the current location. Please provide the location params or use move_to command to tell the robot the current location.")

        tiprack = self._current_tip_location._get_parent()
        validate_air_gap(volume, tiprack._get_max_volume(), "volume")

        loc = self._get_context()._get_arm_location()
        if isinstance(loc, Column):
            well_name = loc.wells()[0].id
        elif isinstance(loc, Well):
            well_name = loc.id

        self._get_context()._append_command(AspirateCommand(
            params=AspirateParams(
                pipetteId=self.id, 
                volume=volume, 
                labwareId=loc._get_parent().id, 
                wellName=well_name,
                wellLocation=self.__create_well_location("top", (0,0,5))
                )))
    
    def home(self) -> 'Pipette':
        """Home the pipette. This method moves the pipette to the trash bin and drop tips.

        Returns:
            Pipette: The pipette instance after homing.
        """
        # drop tip include move to trash bin
        # call move to function to gurantee the pipette will go to trash bin if drop tip command is ignored
        # self.move_to(self._get_context().trash_bin)
        # self._get_context()._append_command(InternalMarkerParams(
        #     use_new_tip='always',
        #     pipette_id=self.id()
        # ))

        self.drop_tip(self._current_tip_location if self._current_return_tip else None)
        return self

    def move_to(self, location: Union[Well, Column, TrashBin],
                position: Literal['top', 'bottom'] = 'top',
                offset: tuple = (0,0,5)) -> 'Pipette':
        """Move the pipette to a specified location. This method moves the pipette to the given well or column or trash bin location.

        Args:
            location (Union[Well, Column, TrashBin]): The target well or column to move to. Also support the moving to the trash bin.
            position (str, optional): The position within the well. Wether the 'top' of the well or 'bottom' of the well. Defaults to 'top'.
            offset (int, optional): The x, y, z offset in millimeters from the specified position. Defaults to (0,0,5).
        
        Returns:
            Pipette: The pipette instance after moving.
        """
        validate_location(self, location)

        if isinstance(location, TrashBin):
            self._get_context()._append_command(MoveToAreaCommand(
                params=MoveToAreaParams(pipetteId=self.id,
                                        addressableAreaName='fixedTrash',
                                        offset={'x':offset[0],'y':offset[1],'z':offset[2]})))
        else:
            self._get_context()._append_command(MoveToCommand(
                params=MoveToParams(pipetteId=self.id,
                                    labwareId=location._get_parent().id,
                                    wellName=self.__get_well_name(location),
                                    wellLocation=self.__create_well_location(position, offset)))
            )
        
        self._get_context()._set_arm_location(location)
        return self

    def rise(self, 
             position: Literal['top', 'bottom'] = 'top', 
             offset: tuple = (0,0,10)):
        """Rise the pipette to a specified height inplace.

        Args:
            position (str, optional): The position within the well. Wether the 'top' of the well or 'bottom' of the well. Defaults to 'top'.
            offset (tuple, optional): The z, y, x offset in millimeters from the specified position. Defaults to (0,0,10).
        """
        self.move_to(self._get_context()._get_arm_location(), position, offset)

    def is_single_channel(self):
        """Return true if the pipette is single-channel, false otherwise (multi-channel)

        Returns:
            bool: is single-channel pipette
        """
        return True if self._get_name().endswith('_single') else False
    
    def has_tip(self) -> bool:
        """Check if the pipette has a tip currently.
        
        Returns:
            bool: True if the pipette has a tip, False otherwise.
        """
        return self.__has_tip

    def __create_well_location(self, position: str, offset: tuple) -> dict:
        """Create a well location dictionary with position and offset."""
        return {
            "origin": position,
            "offset": {
                "x": offset[0],
                "y": offset[1],
                "z": offset[2]
            }
        }

    def __get_validated_location(self, location: Union[Well, Column, TrashBin, None]) -> Union[Well, Column, TrashBin]:
        """Get and validate location, using current location if None provided."""
        if location is None:
            location = self._get_context()._get_arm_location()
            if location is None:
                raise RuntimeError("Cannot locate current location. Please provide location or use move_to command.")
        validate_location(self, location)
        return location