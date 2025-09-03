import humps
import requests
from typing import Optional

from gen_ai_hub import GenAIHubProxyClient
from gen_ai_hub.proxy import get_proxy_client

from .models.pipeline import (
    CreatePipelineRequest,
    PipelineIdResponse,
    GetPipelinesResponse,
    GetPipelineStatusResponse,
    BasePipelineResponse
)

# Constants
PATH_DOCUMENT_GROUNDING = "/lm/document-grounding/pipelines"


class PipelineAPIClient:
    """The Pipelines API creates and manages vector stores based on documents from user data repositories:
    S3, SFTP, and Microsoft SharePoint.
    Each pipeline represents a configured end-to-end process including the following steps:
    - Fetches documents from a supported data source
    - Preprocesses and chunks the document content, and generates semantic embeddings.
      Semantic embeddings are multidimensional representations of textual information.
    - Stores semantic embeddings into the HANA Vector Store

    The Pipeline API is compatible with the following data repositories:
    - Microsoft SharePoint
    - AWS S3
    - SFTP

    The Pipelines API has additional methods which might be added later here:
    - Get Pipeline Executions
    - Get Documents of a Pipeline

    see https://api.sap.com/api/DOCUMENT_GROUNDING_API/resource/Pipelines

    Args:
        proxy_client: The proxy client to use for making requests.
    """

    def __init__(
            self,
            proxy_client: Optional[GenAIHubProxyClient] = None,
    ):
        """
        Initializes the PipelineAPIClient
        Args:
            proxy_client: optional proxy client to use for requests
        """
        self.proxy_client = proxy_client or get_proxy_client(proxy_version="gen-ai-hub")
        self.rest_client = self.proxy_client.ai_core_client.rest_client
        self.path = PATH_DOCUMENT_GROUNDING

    def create_pipeline(self, pipeline_request: CreatePipelineRequest) -> PipelineIdResponse:
        """Create a document vectorization pipeline
        Args:
            pipeline_request: The object containing the pipeline configuration.
        Returns:
            PipelineIdResponse object containing the ID of the created pipeline.
        """
        response = self.rest_client.post(path=self.path, body=pipeline_request.model_dump(exclude_none=True))
        response = humps.camelize(response)  # rest_client (ai api sdk) returns snake_case responses
        return PipelineIdResponse(**response)

    def get_pipelines(self, top: Optional[int] = None, skip: Optional[int] = None, count: Optional[bool] = None) \
            -> GetPipelinesResponse:
        """Get all pipelines."""
        params = {}
        if top is not None:
            params['top'] = top
        if skip is not None:
            params['skip'] = skip
        if count is not None:
            params['count'] = count
        response = self.rest_client.get(path=self.path, params=params)
        return GetPipelinesResponse(**response)

    def get_pipeline_by_id(self, pipeline_id: str) -> BasePipelineResponse:
        """Get details of a pipeline by pipeline id."""
        response = self.rest_client.get(path=f"{self.path}/{pipeline_id}")
        return BasePipelineResponse(**response)

    def delete_pipeline_by_id(self, pipeline_id: str) -> requests.Response:
        """Delete a pipeline by pipeline id."""
        response = self.rest_client.delete(path=f"{self.path}/{pipeline_id}")
        if response == "":  # rest_client (ai api sdk) returns empty string for 204 No Content
            response = requests.Response()
            response.status_code = 204
        return response

    def get_pipeline_status(self, pipeline_id: str) -> GetPipelineStatusResponse:
        """Get pipeline status by pipeline id."""
        response = self.rest_client.get(path=f"{self.path}/{pipeline_id}/status")
        response = humps.camelize(response)  # rest_client (ai api sdk) returns snake_case responses
        return GetPipelineStatusResponse(**response)
