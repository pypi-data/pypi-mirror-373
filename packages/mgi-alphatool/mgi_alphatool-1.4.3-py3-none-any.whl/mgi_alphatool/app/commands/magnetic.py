from typing import List, Literal, Optional
from pydantic import Field
from .base import BaseCommand

class MagneticModuleCommand(BaseCommand):
    stepType: str = Field(default="magnet", description="The type of the step")
    stepName: str = Field(default="Magnetic", description="Name of the step")
    moduleId: str = Field(..., description="The ID of the magnetic module")
    
    # Magnet settings
    magnetAction: Literal["engage", "disengage"] = Field(..., description="Action to take")
    engageHeight: Optional[str] = Field(default=None, description="Height to engage")
