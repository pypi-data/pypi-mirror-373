from pydantic import BaseModel, Field
from typing import Literal, Optional

from .command import BaseCommand

class LoadPipetteParams(BaseModel):
    pipetteName: str = Field(...)
    mount: Literal['left', 'right'] = Field(...)
    pipetteId: str = Field(...)

class LoadPipetteCommand(BaseCommand):
    commandType: str = Field(
        default="loadPipette"
    )
    params: LoadPipetteParams = Field(
        ...
    )

##### Transfer #####
class PickUpTipParams(BaseModel):
    pipetteId: str = Field(...)
    labwareId: str = Field(...)
    wellName: str = Field(...)

class PickUpTipCommand(BaseCommand):
    commandType: str = Field(
        default="pickUpTip",
    )
    params: PickUpTipParams = Field(
        ...
    )

class TransferWellOffset(BaseModel):
    z: float = 1
    x: float = 0
    y: float = 0

class TransferWellLocation(BaseModel):
    origin: Literal["bottom", "top"] = "bottom"
    offset: TransferWellOffset = Field(default=TransferWellOffset())

class AspirateWellLocation(TransferWellLocation):
    detectLiquid: Optional[bool] = Field(default=None)
    detectSpeed: Optional[float] = Field(default=None)

class AspirateParams(BaseModel):
    pipetteId: str = Field(...)
    volume: float = Field(...)
    labwareId: str = Field(...)
    wellName: str = Field(...)
    flowRate: float = Field(default=500)
    wellLocation: AspirateWellLocation = Field(
        default=AspirateWellLocation()
    )

    class Config:
        extra = "allow"

class AspirateCommand(BaseCommand):
    commandType: str = Field(
        default="aspirate",
    )
    params: AspirateParams = Field(
        ...
    )
    
class DispenseParams(BaseModel):
    pipetteId: str = Field(...)
    volume: float = Field(...)
    labwareId: str = Field(...)
    wellName: str = Field(...)
    flowRate: float = Field(default=1000)
    wellLocation: TransferWellLocation = Field(
        default=TransferWellLocation()
    )

    class Config:
        extra = "allow"

class DispenseCommand(BaseCommand):
    commandType: str = Field(
        default="dispense",
    )
    params: DispenseParams = Field(
        ...
    )

class DispenseInplaceParams(BaseModel):
    pipetteId: str = Field(...)
    volume: float = Field(...)
    flowRate: float = Field(default=1000)

class DispenseInplaceCommand(BaseCommand):
    commandType: str = Field(
        default="dispenseInPlace",
    )
    params: DispenseInplaceParams = Field(
        ...
    )

class DropTipParams(BaseModel):
    pipetteId: str = Field(...)
    
    class Config:
        extra = "allow"

class DropTipCommand(BaseCommand):
    commandType: str = Field(
        default="dropTip",
    )
    params: DropTipParams = Field(
        ...
    )

class DropTipInPlaceCommand(BaseCommand):
    commandType: str = Field(
        default="dropTipInPlace",
    )
    params: DropTipParams = Field(
        ...
    )

##### Touch Tip #####
class TouchTipParams(BaseModel):
    pipetteId: str = Field(...)
    labwareId: str = Field(...)
    wellName: str = Field(...)
    wellLocation: TransferWellLocation = Field(
        default=TransferWellLocation()
    )

    class Config:
        extra = "allow"

class TouchTipCommand(BaseCommand):
    commandType: str = Field(
        default="touchTip",
    )
    params: TouchTipParams = Field(
        ...
    )

##### Blow out #####
class BlowOutParams(BaseModel):
    pipetteId: str = Field(...)
    flowRate: float = Field(default=10)

    class Config:
        extra = "allow"

class BlowOutCommand(BaseCommand):
    commandType: str = Field(
        default="blowOutInPlace",
    )
    params: BlowOutParams = Field(
        ...
    )

##### Move #####
class MoveToParams(BaseModel):
    pipetteId: str = Field(...)
    labwareId: str = Field(...)
    wellName: str = Field(...)
    wellLocation: TransferWellLocation = Field(
        default=TransferWellLocation()
    )

class MoveToCommand(BaseCommand):
    commandType: str = Field(
        default="moveToWell",
    )
    params: MoveToParams = Field(
        ...
    )

class MoveToAreaParams(BaseModel):
    pipetteId: str = Field(...)
    addressableAreaName: str = Field(...)
    offset: TransferWellOffset = Field(default=TransferWellOffset())

class MoveToAreaCommand(BaseCommand):
    commandType: str = Field(
        default="moveToAddressableArea",
    )
    params: MoveToAreaParams = Field(
        ...
    )

class MoveToAreaForDropTipParams(BaseModel):
    pipetteId: str = Field(...)
    addressableAreaName: str = Field(default="fixedTrash")
    alternateDropLocation: bool = Field(default=True)
    offset: TransferWellOffset = Field(default=TransferWellOffset(x=0, y=0, z=0))

class MoveToAreaForDropTipCommand(BaseCommand):
    commandType: str = Field(
        default="moveToAddressableAreaForDropTip",
    )
    params: MoveToAreaForDropTipParams = Field(
        ...
    )
