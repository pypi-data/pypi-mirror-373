from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
)
from topqad_sdk.noiseprofiler.libprotocols.models import ProtocolSpecificationModel



class FTQCRequest(BaseModel):
    """FTQC Request Object."""

    protocols: list[ProtocolSpecificationModel] = Field(default_factory=list)
    model_config = ConfigDict(extra="ignore")
