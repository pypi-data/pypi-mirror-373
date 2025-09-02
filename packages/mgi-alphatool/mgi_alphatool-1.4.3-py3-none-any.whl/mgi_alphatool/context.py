import json
import os
import time
import uuid
import glob
import logging
from typing import Any, List, Union, Literal, Dict, Optional

import Levenshtein

from .handler.pipette import Pipette
from .handler.gripper import Gripper
from .liquid import Liquid
from .module import Module
from .module.temperature import TemperatureModule
from .module.thermocycler import ThermocyclerModule
from .module.magnetic import MagneticModule
from .module.heatershaker import HeaterShakerModule
from .module.transport import TransportModule

from .labware import Column, Labware, Well
from .labware.adapter import Adapter
from .labware.aluminumblock import AluminumBlock
from .labware.reservoir import Reservoir
from .labware.tiprack import TipRack
from .labware.tuberack import TubeRack
from .labware.wellplate import WellPlate
from .labware.trashbin import TrashBin

from .commands.command import Location
from .commands.pipette import LoadPipetteParams, LoadPipetteCommand
from .commands.module import LoadModuleParams, LoadModuleCommand
from .commands.labware import LoadLabwareParams, LoadLabwareCommand, MoveLabwareParams, MoveLabwareCommand
from .commands.wait import WaitForDurationParams, WaitForDurationCommand, WaitForResumeParams, WaitForResumeCommand

from .app.commands import MoveLabwareCommand as AppMoveLabwareCommand, PauseCommand
from .app.handle import (dedup_commands, 
                         concat_pcr_profile_steps, 
                         concat_pcr_profile_state_temp_steps,
                         concat_pcr_state_state_temp_steps, 
                         concat_pcr_profile_state_lid_steps,
                         concat_state_pcr_profile_lid_steps,
                         create_ordered_step_ids)

from .utils.cmd_func import concat_pcr_run_cmd, clean_cmd
from .utils.common import get_behind_slot, get_base_slot, get_front_slot
from .utils.validation import validate_mount
from .utils.exception import PlacementErr

from .robot import Robot

_MODULE_CLASSES = {
    "temperatureModuleV2": TemperatureModule,
    "thermocyclerModuleV2": ThermocyclerModule,
    "magneticModuleV2": MagneticModule,
    "heaterShakerModuleV1": HeaterShakerModule,
    "transportModuleSenderV1": TransportModule,
    "transportModuleReceiverV1": TransportModule
}

_LABWARE_CLASSES = {
    'tipRack': TipRack,
    'tubeRack': TubeRack,
    'adapter': Adapter,
    'wellPlate': WellPlate,
    'reservoir': Reservoir,
    'aluminumBlock': AluminumBlock,
    'trash': TrashBin
}

_MODULE_ID_MAP = {
    "temperatureModuleV2": 'temperatureModuleType',
    "thermocyclerModuleV2": 'thermocyclerModuleType',
    "magneticModuleV2": 'magneticModuleType',
    "heaterShakerModuleV1": 'heaterShakerModuleType',
    "transportModuleSenderV1": 'transportModuleType',
    "transportModuleReceiverV1": 'transportModuleType'
}

_PIPETTE_NAME = ['p200_multi', 'p200_single', 'p1000_single']
_MODULE_TYPES = list(_MODULE_CLASSES.keys())
_ROBOT_TYPES = ['alphatool']

_logged_warnings = set()
def warn_once(msg: str):
    if msg not in _logged_warnings:
        logging.warning(msg)
        _logged_warnings.add(msg)

class Context:
    def __init__(self, robot_type: str, 
                 deck_type: str,
                 pick_up_tip_order: Literal['top_to_bottom', 'bottom_to_top']):
        """Initialize the Context with robot and deck configurations.
        
        Args:
            robot_type (str): The type of robot to use, such as 'alphatool'.
            deck_type (str): The type of deck to use, such as 'alphatool_standard'.
            pick_up_tip_order (str): The order in which to pick up tips, either 'top_to_bottom' or 'bottom_to_top'.
            
        Raises:
            ValueError: If the specified robot_type is not supported.
        """        
        # TODO: option of trash location
            
        if robot_type not in _ROBOT_TYPES:
            raise ValueError(f"Unsupported robot type: {robot_type}. Must be one of: {', '.join(_ROBOT_TYPES)}")

        self.__robot_type = robot_type
        self.__deck_type = deck_type
        self.__commands: List[dict] = []
        self.__drop_tip_before_next_pipette_command = {"left": False, "right": False}
        self.__pick_up_tip_order = pick_up_tip_order

        # saved step form
        self.__saved_step_form: Dict[str, dict] = {}
        self.__module_location_update: Dict[str] = {}
        self.__pipette_location_update: Dict[str] = {}
        self.__labware_location_update: Dict[str, Union[str, int]] = {"fixedTrash": "12"} if self.__deck_type == 'standard' else {}

        cur_ts = int(time.time() * 1000)
        self.__json = {
            "metadata":{
                "protocolName": "py_protocol",
                "author": "alab Studio",
                "description": "py_protocol",
                "created": cur_ts,
                "lastModified": 0,
                "tags": [],
                "tipOrder": "t2b" if self.__pick_up_tip_order == 'top_to_bottom' else 'b2t',
                "category": None,
                "subcategory": None
            },
            "robot": {
                "model": "AlphaTool Standard",
                "deckId": "alphatool_"+self.__deck_type,
                "robotType": "MGI AlphaTool"
            },
            "liquidSchemaId": "mgiLiquidSchemaV1",
            "liquids": {},
            "commandAnnotationSchemaId": "mgiCommandAnnotationSchemaV1",
            "commandAnnotations": [],
            "designerApplication": {
                "name": "mgi/protocol-designer",
                "version": "1.0.0",
                "data": {
                    "_internalAppBuildDate": "",
                    "pipetteTiprackAssignments": {},
                    "ingredients": {},
                    "ingredLocations": {},
                    "dismissedWarnings": {
                        "form": {},
                        "timeline": {}
                    },
                    "defaultValues": {
                        "blowout_mmFromTop": 0,
                        "touchTip_mmFromTop": -1,
                        "aspirate_mmFromBottom": 1,
                        "dispense_mmFromBottom": 0.5
                    },
                    "savedStepForms": {
                        "__INITIAL_DECK_SETUP_STEP__": {
                            "id": "__INITIAL_DECK_SETUP_STEP__",
                            "stepType": "manualIntervention",
                            "labwareOrder": {},
                            "moduleLocationUpdate": self.__module_location_update,
                            "labwareLocationUpdate": self.__labware_location_update,
                            "pipetteLocationUpdate": self.__pipette_location_update
                        }
                    },
                    "orderedStepIds": [],
                }
            },
            "labwareDefinitionSchemaId": "mgiLabwareSchemaV2",
            "labwareDefinitions": {},
            "commandSchemaId": "mgiCommandSchemaV8",
            "commands": None
        }

        self.__custom_labware_list: Dict[str, dict] = {}
        self.__labware_name_list: List[str] = []
        self.__labware_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'data/labware')
        self.__labware_json_files = glob.glob(os.path.join(self.__labware_dir, "*.json"))
        for file_path in self.__labware_json_files:
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            self.__labware_name_list.append(file_name)
        
        self.__instrument_list: List[Union[Labware, Module]] = []
        self.__liquids_list: List[Liquid] = []

        # store the current arm state
        self.__arm_location: Optional[Union[Well, Column, TrashBin]] = None
        self.__arm_mount: Dict[str, Optional[Union[Pipette, Gripper]]] = {'left': None, 'right': None}

        # init trash bin
        if self.__deck_type == 'standard':
            self.trash_bin = self.load_labware('mgi_1_trash_1100ml_fixed', 12)
        elif self.__deck_type == 'ext1':
            self.trash_bin = self._load_ext_labware('mgi_1_trash_ext1_fixed', 'ext1')
        self.__instrument_list.append(self.trash_bin)

    def load_gripper(self) -> Gripper:
        """Load a gripper onto the specified mount.

        Returns:
            Gripper: The loaded gripper instance.
        """
        gripper_id = str(uuid.uuid4())
        g = Gripper(gripper_id, 'gripper', '', self)
        return g

    def load_pipette(self, pipette_name: str, mount: Literal['left', 'right']) -> Pipette:
        """Load a pipette onto the specified mount. This method loads a pipette for use in the protocol, validating the pipette name and mount position.

        Args:
            pipette_name (str): The name of the pipette (e.g., 'p1000_single').
            mount (str): The mount position, either 'left' or 'right'.

        Returns:
            Pipette: The loaded pipette instance.
        """
        validate_mount(mount, self.__arm_mount)

        pipette_id = str(uuid.uuid4())
        pipette_name = self.__validate_and_revise(pipette_name, _PIPETTE_NAME)

        self._append_command(
            LoadPipetteCommand(
            params=LoadPipetteParams(
                pipetteName=pipette_name,
                mount=mount,
                pipetteId=pipette_id
                )
            ))
        
        self.__pipette_location_update[pipette_id] = mount
        
        p = Pipette(pipette_id, pipette_name, mount, self)
        self.__arm_mount[mount] = p
        return p

    def load_liquid(self, liquid_name: str, description: str = '') -> Liquid:
        """Load a liquid for use in the protocol.

        Args:
            liquid_name (str): The name of the liquid to be loaded.
            description (str, optional): A description of the liquid. Defaults to an empty string.

        Returns:
            Liquid: The loaded liquid instance.
        """
        id = str(len(self.__json['designerApplication']['data']['ingredients']))
        self.__json['designerApplication']['data']['ingredients'][id] = {
            "name": liquid_name,
            "description": description,
            "serialize": False,
            "liquidGroupId": id
        }

        l = Liquid(id=id, name=liquid_name, desc=description, context=self)
        self.__liquids_list.append(l)
        return l
    
    def load_module(self, module_type: str, location: int) -> Union[TemperatureModule, ThermocyclerModule, MagneticModule, HeaterShakerModule, TransportModule]:
        """Load a module onto the specified deck slot. This method loads a specified module for use in the protocol, validating the module type and location.

        Args:
            module_type (str): The type of module to load. Options include 'temperatureModuleV2', 'thermocyclerModuleV2', 'magneticModuleV2', 'heaterShakerModuleV1', 'transportModuleSenderV1', 'transportModuleReceiverV1'.
            location (int): The slot ID (1-12) where the module will be placed.

        Returns:
            Union[TemperatureModule, ThermocyclerModule, MagneticModule, HeaterShakerModule, TransportModule]: The loaded module instance.
        """
        if module_type not in _MODULE_TYPES:
            raise ValueError(f"Unknown module name. Got: {module_type}. Please make sure that module names are correct.")
        
        # Check if location is already occupied
        if any(instrument._get_slot() == location for instrument in self.__instrument_list):
            raise PlacementErr(f"Slot {location} is already occupied by another labware or module.")

        if location < 1 or location > 12:
            raise ValueError(f"Invalid slot number: {location}. Slot number must be between 1 and 12.")
        
        if location in [6,7]:
            warn_once(f"Placing module on slot 6,7 is not recommended due to the wire routing on the deck.")

        if module_type == 'thermocyclerModuleV2' and location != 10:
            raise PlacementErr(f"Thermocycler module must be placed on slot 10.")
        
        if module_type == 'transportModuleSenderV1' and location != 11:
            raise PlacementErr(f"Transport sender module must be placed on slot 11.")
        
        if module_type == 'transportModuleReceiverV1' and location != 3:
            raise PlacementErr(f"Transport receiver module must be placed on slot 3.")
        
        module_name = _MODULE_ID_MAP[module_type]
        module_id = f"{str(uuid.uuid4())}:{module_name}"
        module_type = self.__validate_and_revise(module_type, _MODULE_TYPES)
        
        self._append_command(LoadModuleCommand(
            params=LoadModuleParams(
                model=module_type,
                location=Location(slotName=str(location)),
                moduleId=module_id
                )
            ))
        
        # for app ui
        self.__module_location_update[module_id] = str(location) if module_name != 'thermocyclerModuleType' else 'span9_10'
        
        module =  _MODULE_CLASSES[module_type](module_id, module_name, location, self)
        self.__instrument_list.append(module)

        return module
    
    def _load_ext_labware(self, labware_name: str, location: str='ext1') -> Labware:
        """Load a labware onto the specified location (extension 1).

        Args:
            labware_name (str): The name of the labware
            location (str): The location of the labware

        Returns:
            Labware: The loaded labware instance.
        """
        # validate the labware name
        labware_name = self.__validate_and_revise(labware_name, self.__labware_name_list)
        
        # load json file        
        labware_definition = self.__load_labware_json(labware_name)

        version = labware_definition['version']
        namespace = labware_definition['namespace']
        display_cat = labware_definition['metadata']['displayCategory']
        labware_full_name = f"{namespace}/{labware_name}/{version}"
        labware_id = f"{str(uuid.uuid4())}:{labware_full_name}"

        # add definiton json to output json
        self.__json['labwareDefinitions'][labware_full_name] = labware_definition

        # create labware instance  
        labware = _LABWARE_CLASSES.get(display_cat, Labware)(
            labware_id, labware_name, location, labware_definition, self
        )

        return labware

    def load_labware(self, 
                     labware_name: str, 
                     location: Union[int, Module, Labware]) -> Labware:
        """Load a labware onto the specified location. This method loads a labware for use in the protocol, validating the labware name and target location. The location can be a deck slot ID, a module instance, or another labware instance.

        Args:
            labware_name (str): The name of the labware
            location (Union[int, Module, Labware]): The target location for the labware. 
                - If int: Slot ID (1-12) on the deck.
                - If Module: The module instance where the labware will be placed.
                - If Labware: Another labware instance on which this labware will be placed.

        Returns:
            Labware: The loaded labware instance.
        """
        if labware_name not in self.__labware_name_list:
            raise ValueError(f"Unknown labware name: {labware_name}. Please make sure that labware names are correct.")

        # Check if location is already occupied
        if isinstance(location, int):
            if any(instrument._get_slot() == location for instrument in self.__instrument_list):
                raise ValueError(f"Attempting to load {labware_name} to slot {location} but it is already occupied by another labware or module.")
            if location < 1 or location > 12:
                raise ValueError(f"Invalid slot number: {location}. Slot number must be between 1 and 12.")

        elif isinstance(location, (Module, Labware)):
            if self._get_labware_on_location(location) is not None:
                raise ValueError(f"{type(location).__name__} already has a labware on it.")

        # validate the labware name
        labware_name = self.__validate_and_revise(labware_name, self.__labware_name_list)
        
        # load json file        
        labware_definition = self.__load_labware_json(labware_name)
        labware_name = labware_definition['parameters']['loadName']

        version = labware_definition['version']
        namespace = labware_definition['namespace']
        display_name = labware_definition['metadata']['displayName']
        display_cat = labware_definition['metadata']['displayCategory']
        labware_full_name = f"{namespace}/{labware_name}/{version}"
        labware_id = f"{str(uuid.uuid4())}:{labware_full_name}"

        # add definiton json to output json
        self.__json['labwareDefinitions'][labware_full_name] = labware_definition

        # if is trash, no need to write into app json
        if display_cat != 'trash':
            self.__labware_location_update[labware_id] = location.id if isinstance(location, (Module, Labware)) else str(location)

        if isinstance(location, int):
            _loc = Location(slotName=str(location))    
        elif isinstance(location, Module):
            _loc = Location(moduleId=location.id)
        elif isinstance(location, Labware):
            _loc = Location(labwareId=location.id)
            
        # save command and update the deck
        # skip trash bin
        if display_cat != 'trash':
            self._append_command(
                LoadLabwareCommand(
                    params=LoadLabwareParams(
                        displayName=display_name,
                        labwareId=labware_id,
                        loadName=labware_name,
                        namespace=namespace,
                        version=version,
                        location=_loc
                    )
                )
            )
 
        # create labware instance  
        labware = _LABWARE_CLASSES.get(display_cat, Labware)(
            labware_id, labware_name, location, labware_definition, self
        )
        
        self.__instrument_list.append(labware)

        if display_cat == 'tipRack':
            # If this is a tip rack, associate it with any pipettes mounted on either arm
            # by mapping the pipette IDs to this tip rack's full name in the JSON config

            if not isinstance(self.__arm_mount['left'], Pipette) and not isinstance(self.__arm_mount['right'], Pipette):
                raise ValueError("No pipette is mounted. Please mount a pipette first before loading tiprack.")

            for mount in ['left', 'right']:
                if mount in self.__arm_mount and isinstance(self.__arm_mount[mount], Pipette):
                    pipette_id = self.__arm_mount[mount].id
                    if pipette_id not in self.__json['designerApplication']['data']['pipetteTiprackAssignments']:
                        self.__json['designerApplication']['data']['pipetteTiprackAssignments'][pipette_id] = labware_full_name
                    else:
                        self.__json['designerApplication']['data']['pipetteTiprackAssignments'][pipette_id] += ','+labware_full_name
        return labware
    
    def move_labware(self, labware: Labware,
                     location: Union[int, Module, Labware]) -> Labware:
        """Move the labware to the specified location manually.

        This method moves an existing labware to a new location, which can be a deck slot,
        a module, or another labware.

        Args:
            labware (Labware): The labware instance to move.
            location (Union[int, Module, Labware]): The target location for the labware.
                - If int: Slot ID (1-12) on the deck.
                - If Module: The module instance to place the labware on.
                - If Labware: Another labware instance to place this labware on.

        Returns:
            Labware: The moved labware instance.

        Raises:
            ValueError: If the target location is already occupied.
            TypeError: If the location type is not supported.
        """
        if isinstance(location, (Module, Labware)):
            if location.labware is not None and location.labware == labware:
                logging.info(f"Labware {labware._get_name()} is already on {location._get_name()}. Ignore this move.")
                return 

        # check if occupied
        if isinstance(location, (Module, Labware)):
            if location.labware is not None:
                raise ValueError(f"Slot on {location._get_name()} is already occupied. Please unload the existing instrument first.")
        
        if isinstance(location, int):
            if self._get_instrument_by_slot(location) is not None:
                raise ValueError(f"Slot {location._get_name()} is already occupied. Please unload the existing instrument first.")

        # remove from the old location
        old_slot = labware._get_slot()
        if isinstance(old_slot, (Labware, Module)):
            old_slot.labware = None

        # add to the new location
        if isinstance(location, Module):
            new_loc = Location(moduleId=location.id)
            labware._set_slot(location)
            location.labware = labware

        elif isinstance(location, Labware):
            new_loc = Location(labwareId=location.id)
            labware._set_slot(location)
            location.labware = labware

        elif isinstance(location, int):
            new_loc = Location(slotName=str(location))
            labware._set_slot(location)

        self._append_command(MoveLabwareCommand(
            params=MoveLabwareParams(
                labwareId=labware.id,
                strategy='manualMoveWithPause',
                newLocation=new_loc)
            )
        )

        self._append_saved_step_form(AppMoveLabwareCommand(
            useGripper=False,
            labware=labware.id,
            newLocation=str(location) if isinstance(location, int) else location.id
        ))
    
    def _get_instrument_by_slot(self, slot: int) -> Union[Module, Labware, None]:
        for i in self.__instrument_list:
            if i._get_slot() == slot:
                return i
        return None
  
    def pause(self, seconds: int=0, wait_for_resume: bool=False) -> None:
        """Pause the protocol execution. This method pauses the protocol for a specified duration or until a manual resume.

        Args:
            seconds (int, optional): The number of seconds to pause. Defaults to 0. Ignored if `wait_for_resume` is True. If not specified, `wait_for_resume` is automatically set to True.
            wait_for_resume (bool, optional): If True, the protocol will wait for a manual resume action. Defaults to False.
        """
        self._pause(seconds, wait_for_resume, is_add_app_cmd=True)
    
    def _pause(self, seconds: int=0, wait_for_resume: bool=False, is_add_app_cmd=False) -> None:
        """Pause the protocol execution. This method pauses the protocol for a specified duration or until a manual resume.

        Args:
            seconds (int, optional): The number of seconds to pause. Defaults to 0. Ignored if `wait_for_resume` is True. If not specified, `wait_for_resume` is automatically set to True.
            wait_for_resume (bool, optional): If True, the protocol will wait for a manual resume action. Defaults to False.
        """
        # If seconds is not specified (0), automatically set wait_for_resume to True
        if seconds == 0:
            wait_for_resume = True
            
        if wait_for_resume:
            command = WaitForResumeCommand(
                params=WaitForResumeParams()
            )
        else:
            command = WaitForDurationCommand(
                params=WaitForDurationParams(seconds=seconds)
            )

        self._append_command(command)

        if is_add_app_cmd:
            # app command
            self._append_saved_step_form(
                PauseCommand(
                    pauseAction='untilResume' if wait_for_resume else 'untilTime',
                    pauseSecond=None if wait_for_resume else str(seconds)
                )   
            )

    def _get_trash_bin(self) -> Labware:
        return self.trash_bin

    def export(self, save_dir: Optional[str] = None) -> str:
        """Export the protocol to a JSON string or file.

        Args:
            save_dir (str, optional): Path where the JSON file should be saved. If None, the JSON is only returned
                as a string without saving to disk. Defaults to None.

        Returns:
            str: The protocol JSON as a string.

        Raises:
            ValueError: If the specified save directory path is invalid or doesn't exist.
            PermissionError: If the specified save directory is not writable.
        """
        # drop tip and move to trash bin at the end of the protocol for all pipettes
        for _, p in self.__arm_mount.items():
            if isinstance(p, Pipette) and p.has_tip():
                p.home()

        # post process (command part)
        self.__json['commands'] = [c.dict(exclude_none=True) for c in self.__commands]
        self.__json['commands'] = concat_pcr_run_cmd(self.__json['commands'])
        self.__json['commands'] = clean_cmd(self.__json['commands'])

        # post process (app part)
        app_commands = {k:v.dict(exclude_none=True) for k,v in self.__saved_step_form.items()}
        app_commands = dedup_commands(app_commands)
        app_commands = concat_pcr_profile_steps(app_commands)
        app_commands = concat_pcr_profile_state_temp_steps(app_commands)
        app_commands = concat_pcr_state_state_temp_steps(app_commands)
        app_commands = concat_pcr_profile_state_lid_steps(app_commands)
        app_commands = concat_state_pcr_profile_lid_steps(app_commands)
        ordered_step_ids = create_ordered_step_ids(app_commands)
        self.__json['designerApplication']['data']['savedStepForms'].update(app_commands)
        self.__json['designerApplication']['data']['orderedStepIds'] = ordered_step_ids

        cmd_json = json.dumps(self.__json)
        # save to file
        if save_dir:
            # Check if the directory is valid
            directory = os.path.dirname(save_dir) or '.'

            if not os.path.exists(directory):
                raise ValueError(f"Directory {directory} does not exist.")
            if not os.path.isdir(directory):
                raise ValueError(f"Path {directory} is not a directory.")
            if not os.access(directory, os.W_OK):
                raise PermissionError(f"Directory {directory} is not writable.")
            
            with open(save_dir, 'w') as f:
                f.write(cmd_json)
        
        return cmd_json

    def __load_labware_json(self, labware_name: str) -> dict:
        """Load the labware metadata/definition from JSON.

        Args:
            labware_name (str): Name of the labware

        Returns:
            dict: Labware definition

        Raises:
            ValueError: If JSON is invalid
        """
        # Check custom labware first
        if labware_name in self.__custom_labware_list:
            return self.__custom_labware_list[labware_name]

        # Load from file
        try:
            json_path = os.path.join(self.__labware_dir, f"{labware_name}.json")
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise ValueError(f"Error loading labware {labware_name}: {str(e)}")
        
    def __validate_and_revise(self, item, valid_list) -> str:
        """check if the item is in valid list, if not, replace with the most similar item.

        Args:
            item (str): item name
            valid_list (list[str]): list of strings

        Raises:
            FileNotFoundError: item not found

        Returns:
            str: validate item name
        """
        def most_similar_string(a, b):
            """find the similar string from b given a

            Args:
                a (str): string
                b (list[str]): list of strings

            Returns:
                str: most similar string in b
            """
            return min(b, key=lambda x: Levenshtein.distance(a, x))
        
        if item not in valid_list:
            revised_item = most_similar_string(item, valid_list)
            raise FileNotFoundError(f"Unsupported item: {item}, do you mean: {revised_item}?")
        
        return item

    def _get_labware_on_location(self, location: Union[Module, Labware]) -> Optional[Labware]:
        """Get the labware instance that is placed on the given location (module/labware).

        This method recursively checks for any labware placed on the given location.
        For example, if an adapter is placed on a module, and a plate is placed on that adapter,
        this will return the plate.

        Args:
            location (Union[Module, Labware]): The module or labware to check for labware on top

        Returns:
            Optional[Labware]: The labware instance placed on the module/labware, or None if no labware found
        """
        for instrument in self.__instrument_list:
            if isinstance(instrument, Labware) and instrument._get_slot() == location:
                # Recursively check if there's labware on this labware
                labware_on_top = self._get_labware_on_location(instrument)
                return labware_on_top if labware_on_top else instrument
        return None
     
    def _get_same_type_labware(self, labware: Labware) -> List[Labware]:
        """Get labwares of the same type as the given labware.

        Args:
            labware (Labware): Reference labware instance.

        Returns:
            List[Labware]: List of matching labware instances.
        """
        return [l for l in self.__instrument_list if l._get_name() == labware._get_name() and l != labware]
    
    def _auto_get_tiprack(self, volume: Union[int, float, None]=None, n_tip: Union[int, None]=None) -> Union[TipRack, None]:
        """Get the most suitable tiprack based on volume and number of tips needed.
        
        Args:
            volume: Target volume needed. If provided, finds tiprack with closest max volume.
            n_tip: Number of tips needed (1 or 8). If provided, checks tip availability.
            
        Returns:
            Most suitable TipRack, or None if no tipracks found.
        """
        # Get available tipracks sorted by most used first (to maximize tip usage)
        tipracks = sorted([l for l in self.__instrument_list if isinstance(l, TipRack)], 
                         key=lambda x: x._get_used_tip_count(), reverse=True)
        
        # Return None if no tipracks found
        if not tipracks:
            return None
            
        # If no volume specified, find first tiprack with enough tips
        # if no n_tip specified, just return the first tiprack
        if volume is None:
            if n_tip:
                # Return first tiprack that has enough tips available
                return next((t for t in tipracks if t._is_has_tip(n_tip)), None)

            return tipracks[0]
            
        # With volume specified, find tiprack with closest max volume
        if n_tip:
            # Filter to only tipracks with enough tips available if n_tip specified
            available = [t for t in tipracks if t._is_has_tip(n_tip)]
        else:
            available = tipracks

        # Return tiprack with volume capacity closest to target volume
        return min(available, key=lambda t: abs(t._get_max_volume() - volume))


    # def _get_labware_compatibility(self) -> dict:
    #     """
    #     Get the compatibility list for each labware and module.

    #     Returns:
    #         dict: Compatibility list for labware and modules.
    #     """
    #     result = {}
    #     for file_path in self.__labware_json_files:
    #         with open(file_path, 'r') as f:
    #             data = json.load(f)
    #             load_name = data['parameters']['loadName']
                
    #             # Extract compatibility information
    #             labware_compat = data.get('stackingOffsetWithLabware', {})
    #             module_compat = data.get('stackingOffsetWithModule', {})
                
    #             if labware_compat or module_compat:
    #                 result[load_name] = {}
    #                 if labware_compat:
    #                     result[load_name]['available_adapters'] = list(labware_compat.keys())
    #                 if module_compat:
    #                     result[load_name]['available_modules'] = list(module_compat.keys())
        
    #     return result
    
    def _append_command(self, command: Any) -> None:
        for mount in ['left', 'right']:
            if self.__drop_tip_before_next_pipette_command[mount]:
                self.__drop_tip_before_next_pipette_command[mount] = False

                # Skip dropping tip for internal marks that specify never using new tip
                is_skip_drop = (command.commandType == 'internal_mark' and 
                              getattr(command, 'use_new_tip', None) == 'never' and
                              getattr(command, 'pipette_id', None) == self.__arm_mount[mount].id)
                
                # drop the tips if the next command is not either transfer or mix with never use new tip param.
                # also check if the next command is drop tip command, if so, skip drop tip to prevent dropping tip twice.
                if not is_skip_drop and 'droptip' not in command.commandType.lower() and 'moveto' not in command.commandType.lower():
                    self.__arm_mount[mount].drop_tip(self.__arm_mount[mount]._current_tip_location if self.__arm_mount[mount]._current_return_tip else None)

        self.__commands.append(command)
        
    def _append_saved_step_form(self, command: Any) -> None:
        self.__saved_step_form[command.id] = command
    
    def _set_arm_location(self, location: Union[Well, Column, TrashBin]) -> None:
        self.__arm_location = location
    
    def _get_arm_location(self) -> Union[Well, Column, TrashBin, None]:
        return self.__arm_location
    
    def add_custom_labware(self, file_paths: Union[str, List[str]]):
        """
        Adds custom labware definitions to the protocol from JSON definition files.

        Args:
            file_paths (Union[str, List[str]]): Path or list of paths to JSON labware definition files.
                Each file must contain required fields: metadata, wells, parameters, version, namespace.

        Raises:
            FileNotFoundError: If any of the specified files cannot be found.
            ValueError: If any file contains invalid JSON or is missing required fields.

        The JSON files must define labware with:
        - metadata: General labware information
        - wells: Well definitions and coordinates 
        - parameters: Including loadName for referencing the labware
        - version: Schema version
        - namespace: Labware namespace
        """
        file_paths = [file_paths] if isinstance(file_paths, str) else file_paths
        
        for path in file_paths:
            if not os.path.isfile(path):
                raise FileNotFoundError(f"Metadata file not found: {path}")
            
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    metadata = json.load(file)
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON in file: {path}")
            
            # Validate required fields
            if not all(field in metadata for field in ['metadata', 'wells', 'parameters', 'version', 'namespace']):
                raise ValueError(f"Missing required field(s) in file: {path}")
            
            load_name = metadata['parameters']['loadName']
            self.__labware_name_list.append(load_name)
            self.__custom_labware_list[load_name] = metadata
    
    def _check_collision(self, location: Union[Well, Column]) -> None:
        """Check for potential collisions when accessing a location.
        
        This function checks if there are any collision risks when trying to access a given location,
        particularly with labware or modules in slots behind the target location.

        Args:
            location (Union[Well, Column]): The location to check for collision risks.

        Raises:
            ValueError: If there is a collision risk from a module or taller labware in the slot behind.
        """
        # Get the actual deck slot number for the location
        slot = get_base_slot(location._get_parent())
        behind_slot = get_behind_slot(slot)
        front_slot = get_front_slot(slot)

        # Calculate heights of labware stacks
        current_height = 0
        current = location._get_parent()
        while isinstance(current, Labware):
            current_height += current._get_height()
            current = current._get_slot()

        # Check collision based on tip order
        if self.__pick_up_tip_order == 'top_to_bottom':
            warning_slots = [1, 5, 9]
            item = self._get_instrument_by_slot(behind_slot)

        else:  # bottom_to_top
            warning_slots = [4, 8, 12]
            item = self._get_instrument_by_slot(front_slot)

        if slot in warning_slots:
            warn_once(f"Using single channel mode with 8 channel pipette on slot {slot} may lead to collision due to the physical limitation.")
            return

        if item is None:
            return

        # TODO: check if module is blocking
        # Modules always block access
        # if isinstance(item, Module):
        #     raise ValueError(f"Cannot access slot {slot} - blocked by module in slot {check_slot}")

        # Calculate height of blocking item
        blocking_height = 0
        blocking = item
        while isinstance(blocking, Labware):
            blocking_height += blocking._get_height()
            blocking = blocking._get_slot()

        # TODO: temporary disable this check
        # if current_height <= blocking_height:
        #     raise ValueError(f"Cannot access slot {slot} - blocked by taller labware in slot {check_slot}")

    def _is_both_pipettes_have_tips(self) -> bool:
        """Check if both mounts are pipettes and one of them have tips attached.
        
        Returns:
            bool: True if both mount are pipettes and one of them have tips, False otherwise.
        """
        pipettes = [p for p in (self.__arm_mount['left'], self.__arm_mount['right']) 
                   if isinstance(p, Pipette)]
        
        # if there are 2 pipettes and one of them has a tip, return True
        return len(pipettes) == 2 and any(p.has_tip() for p in pipettes)
    
    def _await_drop_tip_before_next_pipette_command(self, mount: Literal['left', 'right']) -> None:
        """Await drop tip before next pipette command.
        
        Args:
            pipette (Pipette): The pipette to await drop tip for.
        """
        self.__drop_tip_before_next_pipette_command[mount] = True

    def _get_pick_up_tip_order(self) -> Literal['top_to_bottom', 'bottom_to_top']:
        """Get the pick up tip order.
        
        Returns:
            Literal['top_to_bottom', 'bottom_to_top']: The pick up tip order.
        """
        return self.__pick_up_tip_order
    
    def submit(self, ip: str, port: int = 41950, skip_init: bool = False) -> None:
        """Submit the protocol to the machine for execution.

        This method connects to a machine at the specified IP address and port, then sends
        the protocol for execution. The protocol can optionally skip the initialization
        phase if the machine is already initialized.

        Args:
            ip (str): The IP address of the target robot to connect to.
            port (int, optional): The port number to connect to on the robot. 
                Defaults to 41950.
            skip_init (bool, optional): If True, skips the robot initialization phase.
                Only use this if you're certain the robot is already initialized.
                Defaults to False.
        """
        robot = Robot(ip, port)
        robot.submit(self.export(), skip_init=skip_init)