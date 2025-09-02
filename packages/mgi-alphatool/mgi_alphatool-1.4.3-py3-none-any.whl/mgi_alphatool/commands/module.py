from typing import List
from pydantic import BaseModel, Field

from .command import BaseCommand, Location

class LoadModuleParams(BaseModel):
    model: str = Field(...)
    location: Location = Field(...)
    moduleId: str = Field(...)

class LoadModuleCommand(BaseCommand):
    commandType: str = Field(default="loadModule")
    params: LoadModuleParams = Field(...)

##### Magnetic Module #####
class MagneticModuleEngageParams(BaseModel):
    moduleId: str = Field(...)
    height: float = Field(...)

class MagneticModuleEngageCommand(BaseCommand):
    commandType: str = Field(default="magneticModule/engage")
    params: MagneticModuleEngageParams = Field(...)

class MagneticModuleDisengageParams(BaseModel):
    moduleId: str = Field(...)

class MagneticModuleDisengageCommand(BaseCommand):
    commandType: str = Field(default="magneticModule/disengage")
    params: MagneticModuleDisengageParams = Field(...)

##### HeaterShaker #####
class HeaterShakerModuleCloseLatchParams(BaseModel):
    moduleId: str = Field(...)

class HeaterShakerModuleOpenLatchParams(BaseModel):
    moduleId: str = Field(...)

class HeaterShakerModuleCloseLatchCommand(BaseCommand):
    commandType: str = Field(default="heaterShaker/closeLabwareLatch")
    params: HeaterShakerModuleCloseLatchParams = Field(...)

class HeaterShakerModuleOpenLatchCommand(BaseCommand):
    commandType: str = Field(default="heaterShaker/openLabwareLatch")
    params: HeaterShakerModuleOpenLatchParams = Field(...)

class HeaterShakerModuleSetShakeSpeedParams(BaseModel):
    moduleId: str = Field(...)
    rpm: int = Field(...)

class HeaterShakerModuleSetShakeSpeedCommand(BaseCommand):
    commandType: str = Field(default="heaterShaker/setAndWaitForShakeSpeed")
    params: HeaterShakerModuleSetShakeSpeedParams = Field(...)

class HeaterShakerModuleDeactivateShakerParams(BaseModel):
    moduleId: str = Field(...)

class HeaterShakerModuleDeactivateShakerCommand(BaseCommand):
    commandType: str = Field(default="heaterShaker/deactivateShaker")
    params: HeaterShakerModuleDeactivateShakerParams = Field(...)

class HeaterShakerModuleDeactivateHeaterParams(BaseModel):
    moduleId: str = Field(...)

class HeaterShakerModuleDeactivateHeaterCommand(BaseCommand):
    commandType: str = Field(default="heaterShaker/deactivateHeater")
    params: HeaterShakerModuleDeactivateHeaterParams = Field(...)

class HeaterShakerModuleSetTempParams(BaseModel):
    moduleId: str = Field(...)
    celsius: int = Field(...)

class HeaterShakerModuleSetTempCommand(BaseCommand):
    commandType: str = Field(default="heaterShaker/setTargetTemperature")
    params: HeaterShakerModuleSetTempParams = Field(...)

class HeaterShakerModuleWaitForTempParams(BaseModel):
    moduleId: str = Field(...)
    celsius: int = Field(...)

class HeaterShakerModuleWaitForTempCommand(BaseCommand):
    commandType: str = Field(default="heaterShaker/waitForTemperature")
    params: HeaterShakerModuleWaitForTempParams = Field(...)

##### Temperature #####
class TemperatureModuleSetTempParams(BaseModel):
    moduleId: str = Field(...)
    celsius: int = Field(...)

class TemperatureModuleSetTempCommand(BaseCommand):
    commandType: str = Field(default="temperatureModule/setTargetTemperature")
    params: TemperatureModuleSetTempParams = Field(...)

class TemperatureModuleDeactivateParams(BaseModel):
    moduleId: str = Field(...)

class TemperatureModuleDeactivateCommand(BaseCommand):
    commandType: str = Field(default="temperatureModule/deactivate")
    params: TemperatureModuleDeactivateParams = Field(...)

class TemperatureModuleWaitForTempParams(BaseModel):
    moduleId: str = Field(...)
    celsius: int = Field(...)

class TemperatureModuleWaitForTempCommand(BaseCommand):
    commandType: str = Field(default="temperatureModule/waitForTemperature")
    params: TemperatureModuleWaitForTempParams = Field(...)

##### Thermocycler #####
class ThermocyclerModuleOpenLidParams(BaseModel):
    moduleId: str = Field(...)

class ThermocyclerModuleCloseLidParams(BaseModel):
    moduleId: str = Field(...)

class ThermocyclerModuleOpenLidCommand(BaseModel):
    commandType: str = Field(default="thermocycler/openLid")
    params: ThermocyclerModuleOpenLidParams = Field(...)

class ThermocyclerModuleCloseLidCommand(BaseModel):
    commandType: str = Field(default="thermocycler/closeLid")
    params: ThermocyclerModuleCloseLidParams = Field(...)

class ThermocyclerModuleSetBlockTempParams(BaseModel):
    moduleId: str = Field(...)
    celsius: int = Field(...)

class ThermocyclerModuleSetBlockTempCommand(BaseCommand):
    commandType: str = Field(default="thermocycler/setTargetBlockTemperature")
    params: ThermocyclerModuleSetBlockTempParams = Field(...)

class ThermocyclerModuleSetLidTempParams(BaseModel):
    moduleId: str = Field(...)
    celsius: int = Field(...)

class ThermocyclerModuleSetLidTempCommand(BaseCommand):
    commandType: str = Field(default="thermocycler/setTargetLidTemperature")
    params: ThermocyclerModuleSetLidTempParams = Field(...)

class ThermocyclerModuleWaitForBlockTempParams(BaseModel):
    moduleId: str = Field(...)

class ThermocyclerModuleWaitForBlockTempCommand(BaseCommand):
    commandType: str = Field(default="thermocycler/waitForBlockTemperature")
    params: ThermocyclerModuleWaitForBlockTempParams = Field(...)

class ThermocyclerModuleWaitForLidTempParams(BaseModel):
    moduleId: str = Field(...)

class ThermocyclerModuleWaitForLidTempCommand(BaseCommand):
    commandType: str = Field(default="thermocycler/waitForLidTemperature")
    params: ThermocyclerModuleWaitForLidTempParams = Field(...)

class ThermocyclerModuleDeactivateBlockParams(BaseModel):
    moduleId: str = Field(...)

class ThermocyclerModuleDeactivateBlockCommand(BaseCommand):
    commandType: str = Field(default="thermocycler/deactivateBlock")
    params: ThermocyclerModuleDeactivateBlockParams = Field(...)

class ThermocyclerModuleDeactivateLidParams(BaseModel):
    moduleId: str = Field(...)

class ThermocyclerModuleDeactivateLidCommand(BaseCommand):
    commandType: str = Field(default="thermocycler/deactivateLid")
    params: ThermocyclerModuleDeactivateLidParams = Field(...)

class ThermocyclerModuleRunProfileStep(BaseModel):
    holdSeconds: int
    celsius: int

class ThermocyclerModuleRunProfileParams(BaseModel):
    moduleId: str = Field(...)
    profile: List[ThermocyclerModuleRunProfileStep] = Field(...)
    blockMaxVolumeUl: int = Field(...)

class ThermocyclerRunProfileCommand(BaseCommand):
    commandType: str = Field(default="thermocycler/runProfile")
    params: ThermocyclerModuleRunProfileParams = Field(...)

##### Transport #####
class TransportSendParams(BaseModel):
    moduleId: str = Field(...)

class TransportSendCommand(BaseCommand):
    commandType: str = Field(default="transportModule/send")
    params: TransportSendParams = Field(...)

class TransportHomeParams(BaseModel):
    moduleId: str = Field(...)

class TransportHomeCommand(BaseCommand):
    commandType: str = Field(default="transportModule/home")
    params: TransportHomeParams = Field(...)