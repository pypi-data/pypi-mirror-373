from typing import List, Optional

from ...types._api_version import ApiVersion
from ...types.api.project import ProjectItem
from .._request_handler import AsyncRequestHandler
from .base_project import BaseProject


class AsyncProject(BaseProject):
    def __init__(self, request_handler: AsyncRequestHandler):
        super().__init__(request_handler)

    async def get_projects(
        self, correlation_id: Optional[str] = None
    ) -> List[ProjectItem]:
        """
        Retrieve a list of all projects accessible to the authenticated user.

        This method fetches comprehensive information about all projects that the
        current user has access to, including project metadata, creation details,
        and status information.

        Args:
            correlation_id (str, optional): A unique identifier for request tracing
                and logging. If not provided, one will be automatically generated.

        Returns:
            List[ProjectItem]: A list of ProjectItem objects containing project
                information. Returns an empty list if no projects are accessible
                or found.

        Raises:
            AiriaAPIError: If the API request fails, including cases where:
                - Authentication fails (401)
                - Access is forbidden (403)
                - Server errors (5xx)

        Example:
            ```python
            from airia import AiriaAsyncClient

            client = AiriaAsyncClient(api_key="your_api_key")

            # Get all accessible projects
            projects = await client.project.get_projects()

            for project in projects:
                print(f"Project: {project.name}")
                print(f"ID: {project.id}")
                print(f"Description: {project.description}")
                print(f"Created: {project.created_at}")
                print("---")
            ```

        Note:
            The returned projects are filtered based on the authenticated user's
            permissions. Users will only see projects they have been granted
            access to.
        """
        request_data = self._pre_get_projects(
            correlation_id=correlation_id, api_version=ApiVersion.V1.value
        )
        resp = await self._request_handler.make_request("GET", request_data)

        if "items" not in resp or len(resp["items"]) == 0:
            return []

        return [ProjectItem(**item) for item in resp["items"]]

    async def get_project(
        self, project_id: str, correlation_id: Optional[str] = None
    ) -> ProjectItem:
        """
        Retrieve detailed information for a specific project.

        This method fetches comprehensive information about a single project,
        including all associated resources, metadata, and configuration details.

        Args:
            project_id (str): The unique identifier (GUID) of the project to retrieve.
            correlation_id (str, optional): A unique identifier for request tracing
                and logging. If not provided, one will be automatically generated.

        Returns:
            ProjectItem: A ProjectItem object containing complete project
                information including pipelines, models, data sources, and metadata.

        Raises:
            AiriaAPIError: If the API request fails, including cases where:
                - Project not found (404)
                - Authentication fails (401)
                - Access is forbidden (403)
                - Server errors (5xx)

        Example:
            ```python
            from airia import AiriaAsyncClient

            client = AiriaAsyncClient(api_key="your_api_key")

            # Get a specific project by ID
            project = await client.project.get_project("12345678-1234-1234-1234-123456789abc")

            print(f"Project: {project.name}")
            print(f"Description: {project.description}")
            print(f"Pipelines: {len(project.pipelines)}")
            print(f"Created: {project.created_at}")
            ```

        Note:
            The project must be accessible to the authenticated user.
            Users will only be able to retrieve projects they have been granted
            access to.
        """
        request_data = self._pre_get_project(
            project_id=project_id,
            correlation_id=correlation_id,
            api_version=ApiVersion.V1.value,
        )
        resp = await self._request_handler.make_request("GET", request_data)

        return ProjectItem(**resp)
