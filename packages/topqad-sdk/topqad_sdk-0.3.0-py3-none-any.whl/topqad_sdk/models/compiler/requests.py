from typing import Union, Optional
from pydantic import BaseModel, Field, field_validator


class CompilerPipelineRequest(BaseModel):
    circuit_path: str = Field(description="Circuit used in pipeline")
    global_error_budget: float = Field(
        description="Global error budget (must be > 0 and < 1)",
        gt=0.0,
        lt=1.0,
    )
    timeout: str = Field(description="Timeout.", default="0")
    bypass_optimization: Optional[bool] = Field(
        description="Flag to determine whether or not to bypass optimization and use basis conversion only",
        default=False,
    )
    generate_schedule: Optional[bool] = Field(
        description="Flag of whether or not to generate schedule file in scheduler",
        default=False,
    )

    @field_validator("timeout")
    @classmethod
    def timeout_must_be_numeric(cls, v):
        try:
            float(v)
            return v
        except ValueError:
            raise ValueError("timeout must be a numeric string")


class CompilerPipelineModel(CompilerPipelineRequest):
    compiler_pipeline_id: str = Field(description="Id of the pipeline")
    user_token: Optional[str] = Field(
        description="The user id token used in the pipeline"
    )
