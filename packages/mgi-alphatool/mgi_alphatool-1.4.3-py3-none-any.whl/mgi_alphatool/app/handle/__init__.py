from typing import List, Dict, Any

def dedup_commands(commands: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Remove duplicate adjacent commands from a command list.
    
    A command is considered a duplicate if it has all fields except id matching
    the previous command in the list. Only module commands (magnet, temperature, etc.)
    are checked for duplicates.
    
    Args:
        commands: Dictionary mapping command IDs to command parameters
        
    Returns:
        Dictionary of commands with adjacent duplicates removed
    """
    # Define module command types as a frozen set for immutability
    _MODULE_COMMAND_TYPES = {'magnet', 'temperature', 'heaterShaker', 'thermocycler'}
    
    unique_commands = {}
    previous_id = None
    
    for current_id, current_command in commands.items():
        # Skip duplicate check if no previous command or current command is not a module command
        if not previous_id or current_command.get('stepType') not in _MODULE_COMMAND_TYPES:
            unique_commands[current_id] = current_command
            previous_id = current_id
            continue
            
        # Get previous command and compare all fields except id
        previous_command = commands[previous_id]
        current_without_id = {k: v for k, v in current_command.items() if k != 'id'}
        previous_without_id = {k: v for k, v in previous_command.items() if k != 'id'}
        
        # Only add command if it differs from previous
        if current_without_id != previous_without_id:
            unique_commands[current_id] = current_command
            previous_id = current_id
            
    return unique_commands

def concat_pcr_profile_steps(commands: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Concatenate consecutive PCR profile steps in app commands.
    
    This function processes PCR profile commands and merges consecutive profile steps.
    If a command has profile settings and follows another profile command, its profiles
    will be merged into the previous command's profiles.
    
    Args:
        commands: Dictionary mapping command IDs to command parameters
        
    Returns:
        Dictionary of processed commands with merged PCR profiles
    """
    processed_commands = {}
    previous_command_id = None
    
    for current_id, current_command in commands.items():
        # Skip if command has no profile settings
        has_no_profile = not current_command.get('profileItemsById')
        if has_no_profile:
            processed_commands[current_id] = current_command
            previous_command_id = current_id
            continue

        # Check if we can merge with previous PCR profile command
        is_previous_profile = (previous_command_id and 
                             processed_commands[previous_command_id].get('profileItemsById'))
        
        if is_previous_profile:
            # Merge profile items and ordered items into previous command
            processed_commands[previous_command_id]['profileItemsById'].update(
                current_command['profileItemsById']
            )
            processed_commands[previous_command_id]['orderedProfileItems'].extend(
                current_command['orderedProfileItems']
            )
        else:
            # Start new profile command sequence
            processed_commands[current_id] = current_command
            previous_command_id = current_id
            
    return processed_commands

def concat_pcr_profile_state_temp_steps(commands: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Concatenate consecutive PCR profile steps in app commands.
    
    This function processes PCR profile commands and merges temperature settings from consecutive steps.
    If a command has temperature settings and follows a PCR profile command, its temperatures will be
    added as "hold" temperatures to the previous profile command.
    
    Args:
        commands: Dictionary mapping command IDs to command parameters
        
    Returns:
        Dictionary of processed commands with merged temperature settings
    """
    processed_commands = {}
    previous_command_id = None
    
    for current_id, current_command in commands.items():
        # Skip if command has no temperature settings
        has_no_temps = not (current_command.get('blockTargetTemp') or 
                            current_command.get('lidTargetTemp'))
        if has_no_temps:
            processed_commands[current_id] = current_command
            previous_command_id = current_id
            continue

        # Check if we can merge with previous PCR profile command
        is_previous_pcr = (previous_command_id and 
                          processed_commands[previous_command_id].get('profileItemsById'))
        
        if is_previous_pcr:
            # Add block temperature if present
            if block_temp := current_command.get('blockTargetTemp'):
                processed_commands[previous_command_id]['blockTargetTempHold'] = block_temp
                processed_commands[previous_command_id]['blockIsActiveHold'] = True

            # Add lid temperature if present  
            if lid_temp := current_command.get('lidTargetTemp'):
                processed_commands[previous_command_id]['lidTargetTempHold'] = lid_temp
                processed_commands[previous_command_id]['lidIsActiveHold'] = True
        else:
            # Start new command sequence
            processed_commands[current_id] = current_command
            previous_command_id = current_id
            
    return processed_commands

def concat_pcr_profile_state_lid_steps(commands: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Concatenate consecutive PCR profile steps in app commands.
    
    This function processes PCR profile commands and merges lid open settings from consecutive steps.
    If a command has lid open settings and follows a PCR profile command, its lid open settings will be
    added as "hold" settings to the previous profile command.
    
    Args:
        commands: Dictionary mapping command IDs to command parameters
        
    Returns:
        Dictionary of processed commands with merged lid open settings
    """
    
    processed_commands = {}
    previous_command_id = None

    for current_id, current_command in commands.items():
        # Skip if not a thermocycler state command
        if not current_command.get('thermocyclerFormType') == 'thermocyclerState':
            processed_commands[current_id] = current_command
            previous_command_id = current_id
            continue

        # Check if we can merge with previous thermocyclerProfile command
        is_previous_step_match = (previous_command_id and \
                             processed_commands[previous_command_id].get('thermocyclerFormType') == 'thermocyclerProfile')
        
        if is_previous_step_match:
            processed_commands[previous_command_id]['lidOpen'] = current_command.get('lidOpen')
            processed_commands[previous_command_id]['lidOpenHold'] = current_command.get('lidOpen')
        else:
            processed_commands[current_id] = current_command
            previous_command_id = current_id
    
    return processed_commands

def concat_state_pcr_profile_lid_steps(commands: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    processed_commands = {}
    previous_command_id = None

    for current_id, current_command in commands.items():
        if not current_command.get('thermocyclerFormType') == 'thermocyclerProfile':
            processed_commands[current_id] = current_command
            previous_command_id = current_id
            continue

        is_previous_step_match = (previous_command_id and \
                             processed_commands[previous_command_id].get('thermocyclerFormType') == 'thermocyclerState' and \
                             processed_commands[previous_command_id].get('lidOpen') == False)
        
        if is_previous_step_match:
            processed_commands.pop(previous_command_id)
        
        processed_commands[current_id] = current_command
        previous_command_id = current_id
    
    return processed_commands

def concat_pcr_state_state_temp_steps(commands: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Concatenate consecutive PCR state steps in app commands.
    
    This function processes PCR state commands and merges temperature settings from consecutive steps.
    If a command has temperature settings and follows another PCR state command, its temperatures will
    update any unset temperatures in the previous command.
    
    Args:
        commands: Dictionary mapping command IDs to command parameters
        
    Returns:
        Dictionary of processed commands with merged temperature settings
    """
    processed_commands = {}
    previous_command_id = None
    
    for current_id, current_command in commands.items():
        # Skip if not a thermocycler state command
        if not current_command.get('thermocyclerFormType') == 'thermocyclerState':
            processed_commands[current_id] = current_command
            previous_command_id = current_id
            continue

        # Check if we can merge with previous PCR state command
        is_previous_state_match = (previous_command_id and \
                             processed_commands[previous_command_id].get('thermocyclerFormType') == 'thermocyclerState')
        
        if is_previous_state_match:
            # Update block temperature if previous is None and current exists
            if (processed_commands[previous_command_id].get('blockTargetTemp') is None and \
                current_command.get('blockTargetTemp')):

                processed_commands[previous_command_id]['blockTargetTemp'] = current_command.get('blockTargetTemp')
                processed_commands[previous_command_id]['blockIsActive'] = True

            # Update lid temperature if previous is None and current exists
            if (processed_commands[previous_command_id].get('lidTargetTemp') is None and \
                current_command.get('lidTargetTemp')):
                processed_commands[previous_command_id]['lidTargetTemp'] = current_command.get('lidTargetTemp')
                processed_commands[previous_command_id]['lidIsActive'] = True
        else:
            # Start new command sequence
            processed_commands[current_id] = current_command
            previous_command_id = current_id
            
    return processed_commands

def create_ordered_step_ids(commands: Dict[str, Dict[str, Any]]) -> List[str]:
    """Create a list of ordered step IDs based on the command order.
    
    This function creates a list of step IDs in the order they appear in the commands dictionary.
    
    Args:
        commands: Dictionary mapping command IDs to command parameters
        
    Returns:
        List of ordered step IDs
    """
    return list(commands.keys())
