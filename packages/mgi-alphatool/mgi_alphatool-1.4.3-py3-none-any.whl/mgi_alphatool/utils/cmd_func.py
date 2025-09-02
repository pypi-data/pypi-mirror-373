
from typing import Dict, List

def clean_cmd(commands: List[Dict]) -> List[Dict]:
    """Clean the commands."""
    return [command for command in commands if command['commandType'] != 'internal_mark']

def concat_pcr_run_cmd(commands: List[Dict]) -> List[Dict]:
    """Concatenate consecutive PCR run commands into a single command.

    Args:
        commands (List[Dict]): List of protocol commands to process

    Returns:
        List[Dict]: List of commands with consecutive PCR runs merged
    """
    result = []
    i = 0
    
    while i < len(commands):
        cmd = commands[i]
        
        # Non-PCR commands are added directly
        if cmd['commandType'] != 'thermocycler/runProfile':
            result.append(cmd)
            i += 1
            continue
            
        # Collect consecutive PCR profiles with same parameters
        profiles = [cmd['params']['profile']]
        next_cmd = commands[i + 1] if i + 1 < len(commands) else None
        while (next_cmd and 
                next_cmd['commandType'] == 'thermocycler/runProfile' and
                next_cmd['params']['moduleId'] == cmd['params']['moduleId'] and 
                next_cmd['params']['blockMaxVolumeUl'] == cmd['params']['blockMaxVolumeUl']):
            profiles.append(next_cmd['params']['profile'])
            i += 1
            next_cmd = commands[i + 1] if i + 1 < len(commands) else None
        
        # Combine profiles into single command
        merged_cmd = {
            'commandType': 'thermocycler/runProfile',
            'key': cmd['key'],
            'params': {
                'moduleId': cmd['params']['moduleId'],
                'profile': [step for p in profiles for step in p],
                'blockMaxVolumeUl': cmd['params']['blockMaxVolumeUl']
            }
        }
        result.append(merged_cmd)
        i += 1
        
    return result