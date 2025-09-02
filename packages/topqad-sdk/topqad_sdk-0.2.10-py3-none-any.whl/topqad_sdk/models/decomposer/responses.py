from typing import Optional
from pydantic import BaseModel, Field
from ..enums import StatusEnum


class DecomposerResponse(BaseModel):
    """Decomposer response model."""

    request_id: str = Field(description="Id of the Decomposer job request.")
    status: StatusEnum = Field(description="Current status of SK job.")
    request_received_at: Optional[str] = Field(
        description="Timestamp when the request was received.", default=None
    )
    name: Optional[str] = Field(description="Name of the request.", default="name")
    description: Optional[str] = Field(
        default=None, description="Description of the request."
    )



class DecomposerSolutionResponse(DecomposerResponse):
    """Decomposer Solution response model."""

    sk_circuit_path: Optional[str] = Field(
        default=None, description="Path of the SK circuit."
    )
    accumulated_error: Optional[float] = Field(
        default=None, description="Accumulated_error of the SK circuit."
    )
    elapsed_time: Optional[float] = Field(
        default=None, description="The elapsed time of the tool in seconds"
    )
    message: Optional[str] = Field(
        default=None, description="Error message when status is failed."
    )
