from typing import Union, Optional, Literal
from pydantic import BaseModel, Field
from ..decomposer.responses import DecomposerSolutionResponse
from ..optimizer.responses import OptimizerSolutionResponse
from ..scheduler.responses import SchedulerSolutionResponse
from ..compiler.requests import CompilerPipelineRequest


class StepRetrievalError(BaseModel):
    """A response for a step in the pipeline that we are unable to retrieve."""

    status: Literal["unknown"] = Field(
        description="There was an error retrieving the step data"
    )


class CompilerPipelineResponse(BaseModel):
    compiler_pipeline_id: str = Field(description="The id of the compiler pipeline")
    status: str = Field(description="The status of the pipeline")
    message: Optional[str] = Field(
        description="Error message if problem getting or submitting pipeline",
        default="",
    )


class CompilerPipelineStepSolutions(BaseModel):
    """The solutions from each step of the pipeline, used in the GET response"""

    decomposer: Optional[Union[DecomposerSolutionResponse, StepRetrievalError]] = Field(
        description="The status/solution of the decomposition step of the pipeline",
        default=None,
    )
    optimizer: Optional[Union[OptimizerSolutionResponse, StepRetrievalError]] = Field(
        description="The status/solution of the optimization step of the pipeline",
        default=None,
    )
    scheduler: Optional[Union[SchedulerSolutionResponse, StepRetrievalError]] = Field(
        description="The status/solution of the scheduling step of the pipeline",
        default=None,
    )

    @classmethod
    def solution_type(cls, step_name):
        """Returns the type of the model associated with the given step name"""
        mapping = {
            "decomposer": DecomposerSolutionResponse,
            "optimizer": OptimizerSolutionResponse,
            "scheduler": SchedulerSolutionResponse,
        }
        return mapping[step_name]


class CompilerPipelineSolutionResponse(CompilerPipelineResponse):
    steps: CompilerPipelineStepSolutions = Field(
        description="The GET responses from each tool in this pipeline"
    )
    input: CompilerPipelineRequest = Field(
        description="The input request for this pipeline"
    )
