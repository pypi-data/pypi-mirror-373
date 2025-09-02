from typing import Union
from pydantic import BaseModel, Field

from .command import BaseCommand

class WaitForDurationParams(BaseModel):
    seconds: Union[int, float] = Field(..., description="The duration to wait, in seconds")
    message: str = Field("", description="An optional message to display during the wait")

class WaitForDurationCommand(BaseCommand):
    commandType: str = Field(
        default="waitForDuration",
        description="Command type for WaitForDurationCommand"
    )
    params: WaitForDurationParams = Field(
        ...,
        description="Parameters specific to the waitForDuration command"
    )

class WaitForResumeParams(BaseModel):
    message: str = Field("", description="An optional message to display during the wait")

class WaitForResumeCommand(BaseCommand):
    commandType: str = Field(
        default="waitForResume",
        description="Command type for WaitForResumeCommand"
    )
    params: WaitForResumeParams = Field(
        ...,
        description="Parameters specific to the waitForDuration command"
    )