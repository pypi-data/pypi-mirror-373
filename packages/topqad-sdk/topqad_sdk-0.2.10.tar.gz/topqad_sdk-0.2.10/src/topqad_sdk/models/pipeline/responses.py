from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field


from ..scheduler.responses import SchedulerSolutionResponse
from ..noise_profiler.responses import FTQCSolutionResponse
from ..optimizer.responses import OptimizerSolutionResponse
from ..pipeline.requests import PipelineRequest
from ..assembler.responses import PREReport
from ..assembler.assembler_reports import PREReports
from ..decomposer.responses import DecomposerSolutionResponse


class PipelineResponse(BaseModel):
    """Response model for pipeline status and messages."""

    pipeline_id: str = Field(description="The id of the pipeline")
    status: str = Field(description="The status of the pipeline")
    request_received_at: Optional[str] = Field(
        default=None, description="Timestamp when the request was received."
    )
    name: Optional[str] = Field(default=None, description="Name of the pipeline request.")
    description: Optional[str] = Field(
        default=None, description="Description of the pipeline request."
    )
    message: Optional[str] = Field(
        default=None,
        description="Error message if problem getting or submitting pipeline",
    )

    @property
    def as_dict(self):
        """Convert the model to a dictionary."""
        return self.model_dump()


class StepRetrievalError(BaseModel):
    """A response for a step in the pipeline that we are unable to retrieve."""

    status: Literal["unknown"] = Field(
        description="There was an error retrieving the step data"
    )


class PipelineStepSolutions(BaseModel):
    """The solutions from each step of the pipeline, used in the GET response."""

    decomposer: Optional[Union[DecomposerSolutionResponse, StepRetrievalError]] = Field(
        default=None,
        description="The status/solution of the decomposition step of the pipeline",
    )
    optimizer: Optional[Union[OptimizerSolutionResponse, StepRetrievalError]] = Field(
        default=None,
        description="The status/solution of the optimization step of the pipeline",
    )
    scheduler: Optional[Union[SchedulerSolutionResponse, StepRetrievalError]] = Field(
        default=None,
        description="The status/solution of the scheduling step of the pipeline",
    )
    emulator: Optional[Union[FTQCSolutionResponse, StepRetrievalError]] = Field(
        default=None,
        description="The status/solution of the fault-tolerant quantum computing "
        "emulation step of the pipeline",
    )
    pre: Optional[Union[PREReport, StepRetrievalError]] = Field(
        default=None,
        description="The physical resource estimation report data",
    )

    def solution_type(self, step_name):
        """Returns the type of the model associated with the given step name."""
        mapping = {
            "decomposer": DecomposerSolutionResponse,
            "optimizer": OptimizerSolutionResponse,
            "scheduler": SchedulerSolutionResponse,
            "emulator": FTQCSolutionResponse,
            "pre": PREReport,
        }
        try:
            return mapping[step_name]
        except KeyError:
            raise ValueError(
                f"Invalid step name '{step_name}'. "
                f"Valid step names are: {', '.join(mapping.keys())}."
            )


class PipelineSolutionResponse(PipelineResponse):
    """Response model containing the solutions and reports for the pipeline."""

    steps: PipelineStepSolutions = Field(
        description="The GET responses from each tool in this pipeline"
    )
    assembler_reports: Optional[List[PREReports]] = None
    input: PipelineRequest = Field(description="The input request for this pipeline")
