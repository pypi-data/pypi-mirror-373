from typing import Optional

from pydantic import BaseModel

from topqad_sdk.noiseprofiler.libprotocols.models import (
    ProtocolSpecificationModel,
)


class ProtocolSpecificationListModel(BaseModel):
    protocols: list[ProtocolSpecificationModel]


# simulation parameters
class BackendSimulationParametersModel(BaseModel):
    num_workers: int


class SimulationRunInformation(BaseModel):
    system: str
    python_version: str
    noiseprofiler_version: str
    execution_time: int
    report_generation_time: str


class RequestResponseModel(BaseModel):
    protocols: list[ProtocolSpecificationModel]
    backend_simulation_parameters: Optional[BackendSimulationParametersModel] = None
    simulation_run_information: Optional[SimulationRunInformation] = None
