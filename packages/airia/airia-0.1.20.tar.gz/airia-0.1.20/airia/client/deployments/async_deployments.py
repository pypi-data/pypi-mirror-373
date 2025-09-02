from typing import List, Optional

from ...types._api_version import ApiVersion
from ...types.api.deployments import GetDeploymentResponse, GetDeploymentsResponse
from .._request_handler import AsyncRequestHandler
from .base_deployments import BaseDeployments


class AsyncDeployments(BaseDeployments):
    def __init__(self, request_handler: AsyncRequestHandler):
        super().__init__(request_handler)

    async def get_deployments(
        self,
        tags: Optional[List[str]] = None,
        is_recommended: Optional[bool] = None,
        project_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V2.value,
    ) -> GetDeploymentsResponse:
        """
        Retrieve a paged list of deployments asynchronously.

        This method fetches deployments from the Airia platform with optional filtering
        by tags and recommendation status. The response includes detailed information
        about each deployment including associated pipelines, data sources, and user prompts.

        Args:
            tags: Optional list of tags to filter deployments by
            is_recommended: Optional filter by recommended status
            project_id: Optional filter by project id
            correlation_id: Optional correlation ID for request tracing
            api_version: API version to use (defaults to V2)

        Returns:
            GetDeploymentsResponse: Paged response containing deployment items and total count

        Raises:
            AiriaAPIError: If the API request fails
            ValueError: If an invalid API version is provided

        Example:
            ```python
            client = AiriaAsyncClient(api_key="your-api-key")
            deployments = await client.deployments.get_deployments(
                tags=["production", "nlp"],
                is_recommended=True
            )
            print(f"Found {deployments.total_count} deployments")
            for deployment in deployments.items:
                print(f"- {deployment.deployment_name}")
            ```
        """
        request_data = self._pre_get_deployments(
            tags=tags,
            is_recommended=is_recommended,
            correlation_id=correlation_id,
            api_version=api_version,
        )

        response = await self._request_handler.make_request("GET", request_data)

        if project_id is not None:
            response["items"] = [
                item for item in response["items"] if item["projectId"] == project_id
            ]

        return GetDeploymentsResponse(**response)

    async def get_deployment(
        self,
        deployment_id: str,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V1.value,
    ) -> GetDeploymentResponse:
        """
        Retrieve a single deployment by ID asynchronously.

        This method fetches a specific deployment from the Airia platform using its
        unique identifier. The response includes complete information about the deployment
        including associated pipelines, data sources, user prompts, and configuration settings.

        Args:
            deployment_id: The unique identifier of the deployment to retrieve
            correlation_id: Optional correlation ID for request tracing
            api_version: API version to use (defaults to V1)

        Returns:
            GetDeploymentResponse: Complete deployment information

        Raises:
            AiriaAPIError: If the API request fails or deployment is not found
            ValueError: If an invalid API version is provided

        Example:
            ```python
            client = AiriaAsyncClient(api_key="your-api-key")
            deployment = await client.deployments.get_deployment("deployment-id-123")
            print(f"Deployment: {deployment.deployment_name}")
            print(f"Description: {deployment.description}")
            print(f"Project: {deployment.project_id}")
            ```
        """
        request_data = self._pre_get_deployment(
            deployment_id=deployment_id,
            correlation_id=correlation_id,
            api_version=api_version,
        )

        response = await self._request_handler.make_request("GET", request_data)

        return GetDeploymentResponse(**response)
