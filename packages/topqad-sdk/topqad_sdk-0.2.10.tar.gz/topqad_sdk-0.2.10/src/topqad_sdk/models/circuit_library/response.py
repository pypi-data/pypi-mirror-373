from typing import List, Optional
from pydantic import BaseModel, Field

from topqad_sdk.models import StatusEnum


class UploadCircuitResponse(BaseModel):
    """Model for confirmation of circuit upload."""

    circuit_path: str = Field(description="The path to the circuit file")
    circuit_name: Optional[str] = Field(description="The name of the circuit")
    description: Optional[str] = Field(description="Description of the circuit")
    status: StatusEnum = Field(description="The status of the circuit retrieval")
    message: Optional[str] = Field(
        description="Error message if problem retrieving the circuit"
    )


class CircuitInfo(BaseModel):
    """The circuit's metadata."""

    id: str = Field(description="The unique ID of the circuit")
    circuit_name: str = Field(description="The name of the circuit")
    description: Optional[str] = Field(
        default="", description="Description of the circuit"
    )
    is_public: Optional[bool] = Field(description="Whether the circuit is public")
    created_at: Optional[str] = Field(default="", description="Creation timestamp")


class ExampleCircuitInfoMinimal(BaseModel):
    """Minimal information about an example circuit.

    This model is used specifically for the retrieval of a list of all example files.
    """

    id: str = Field(description="The unique ID of the example circuit")
    circuit_name: str = Field(description="The name of the example circuit")


class RetrieveCircuitResponse(BaseModel):
    """Response model for circuit retrieval.

    Returns all of the circuits based on the request specifications.
    """

    status: str = Field(description="Status of the request, e.g., 'success'")
    circuits: List[ExampleCircuitInfoMinimal] = Field(
        description="List of uploaded circuits"
    )


class ExampleCircuitInfo(BaseModel):
    """Information about an example circuit.

    This model is used specifically for the retrieval of example files.
    """

    id: str = Field(description="The unique ID of the example circuit")
    circuit_name: str = Field(description="The name of the example circuit")
    circuit_path: str = Field(description="The path to the example circuit file")


class RetrieveCircuitByIdResponse(BaseModel):
    """Response model for retrieving a specific circuit by ID."""

    status: str = Field(description="Status of the request, e.g., 'success'")
    circuit: ExampleCircuitInfo = Field(description="Details of the requested circuit")
