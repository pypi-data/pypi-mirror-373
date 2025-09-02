from pydantic import BaseModel, Field
from typing import Dict

from .command import BaseCommand

class LoadLiquidParams(BaseModel):
    liquidId: str = Field(...)
    labwareId: str = Field(...)
    volumeByWell: Dict[str, int] = Field(...)

class LoadLiquidCommand(BaseCommand):
    commandType: str = Field(
        default="LoadLiquid"
    )
    params: LoadLiquidParams = Field(
        ...
    )
