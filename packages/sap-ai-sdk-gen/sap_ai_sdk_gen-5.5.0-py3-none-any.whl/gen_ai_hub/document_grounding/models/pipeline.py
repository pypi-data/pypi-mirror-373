from typing import List, Optional, Union, Annotated, Literal
from pydantic import BaseModel, Field

# --- Models for Pipeline API ---

class MetaData(BaseModel):
    destination: str

class SharePointSite(BaseModel):
    name: str
    includePaths: Optional[List[str]] = None

class SharePointConfig(BaseModel):
    site: SharePointSite

class MSSharePointConfiguration(BaseModel):
    destination: str
    sharePoint: SharePointConfig

class CommonConfiguration(BaseModel):
    destination: str

class MSSharePointPipelineCreateRequest(BaseModel):
    type: Literal["MSSharePoint"] = "MSSharePoint"
    configuration: MSSharePointConfiguration
    metadata: Optional[MetaData] = None

class S3PipelineCreateRequest(BaseModel):
    type: Literal["S3"] = "S3"
    configuration: CommonConfiguration
    metadata: Optional[MetaData] = None

class SFTPPipelineCreateRequest(BaseModel):
    type: Literal["SFTP"] = "SFTP"
    configuration: CommonConfiguration
    metadata: Optional[MetaData] = None

CreatePipelineRequest = Union[
    MSSharePointPipelineCreateRequest,
    S3PipelineCreateRequest,
    SFTPPipelineCreateRequest
]

class PipelineIdResponse(BaseModel):
    pipelineId: str

class BasePipelineResponse(BaseModel):
    id: str
    type: str
    metadata: Optional[MetaData] = None

class MSSharePointConfigurationGetResponse(BaseModel):
    destination: str
    sharePoint: SharePointConfig

class MSSharePointPipelineGetResponse(BasePipelineResponse):
    type: Literal["MSSharePoint"] = "MSSharePoint"
    configuration: MSSharePointConfigurationGetResponse

class S3PipelineGetResponse(BasePipelineResponse):
    type: Literal["S3"] = "S3"
    configuration: CommonConfiguration

class SFTPPipelineGetResponse(BasePipelineResponse):
    type: Literal["SFTP"] = "SFTP"
    configuration: CommonConfiguration

GetPipelineResponse = Annotated[
    MSSharePointPipelineGetResponse | S3PipelineGetResponse | SFTPPipelineGetResponse,
    Field(discriminator="type")
]

class GetPipelinesResponse(BaseModel):
    count: Optional[int]
    resources: List[GetPipelineResponse]

class GetPipelineStatusResponse(BaseModel):
    lastStarted: Optional[str]
    status: Optional[str]
