from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

from .requests import ProtocolSpecificationModel


class StatusEnum(str, Enum):
    """Status of a circuit job."""

    waiting = "waiting"
    done = "done"
    executing = "executing"
    failed = "failed"


class FTQCResponse(BaseModel):
    """FTQC response model."""

    request_id: str = Field(description="Id of the ftqc circuit job request.")
    status: StatusEnum = Field(description="Current status of circuit job.")
    request_received_at: str = Field(
        description="Timestamp when the request was received."
    )
    name: str = Field(description="Name of the request.")
    description: Optional[str] = Field(
        default=None, description="Description of the request."
    )

    @property
    def as_dict(self):
        """Convert the model to a dictionary with the option to exclude None values."""
        return self.model_dump(exclude_none=True)


class FTQCSolutionResponse(FTQCResponse):
    """FTQC solution response model."""

    protocols: Optional[list[ProtocolSpecificationModel]] = Field(default=None)
    message: Optional[str] = Field(
        default=None, description="Error message when status is failed."
    )
    elapsed_time: Optional[float] = Field(
        default=None, description="The elapsed time of the tool in seconds"
    )
