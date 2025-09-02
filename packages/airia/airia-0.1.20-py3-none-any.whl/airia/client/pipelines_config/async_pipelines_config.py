from typing import Optional

from ...types._api_version import ApiVersion
from ...types.api.pipelines_config import (
    PipelineConfigResponse,
    ExportPipelineDefinitionResponse,
    GetPipelinesConfigResponse,
)
from .._request_handler import AsyncRequestHandler
from .base_pipelines_config import BasePipelinesConfig


class AsyncPipelinesConfig(BasePipelinesConfig):
    def __init__(self, request_handler: AsyncRequestHandler):
        super().__init__(request_handler)

    async def get_pipeline_config(
        self, pipeline_id: str, correlation_id: Optional[str] = None
    ) -> PipelineConfigResponse:
        """
        Retrieve configuration details for a specific pipeline.

        This method fetches comprehensive information about a pipeline including its
        deployment details, execution statistics, version information, and metadata.

        Args:
            pipeline_id (str): The unique identifier of the pipeline to retrieve
                configuration for.
            correlation_id (str, optional): A unique identifier for request tracing
                and logging. If not provided, one will be automatically generated.

        Returns:
            PipelineConfigResponse: A response object containing the pipeline
                configuration.

        Raises:
            AiriaAPIError: If the API request fails, including cases where:
                - The pipeline_id doesn't exist (404)
                - Authentication fails (401)
                - Access is forbidden (403)
                - Server errors (5xx)

        Example:
            ```python
            from airia import AiriaAsyncClient

            client = AiriaAsyncClient(api_key="your_api_key")

            # Get pipeline configuration
            config = await client.pipelines_config.get_pipeline_config(
                pipeline_id="your_pipeline_id"
            )

            print(f"Pipeline: {config.agent.name}")
            print(f"Description: {config.agent.agent_description}")
            ```

        Note:
            This method only retrieves configuration information and does not
            execute the pipeline. Use execute_pipeline() to run the pipeline.
        """
        request_data = self._pre_get_pipeline_config(
            pipeline_id=pipeline_id,
            correlation_id=correlation_id,
            api_version=ApiVersion.V1.value,
        )
        resp = await self._request_handler.make_request("GET", request_data)

        return PipelineConfigResponse(**resp)

    async def export_pipeline_definition(
        self, pipeline_id: str, correlation_id: Optional[str] = None
    ) -> ExportPipelineDefinitionResponse:
        """
        Export the complete definition of a pipeline including all its components.

        This method retrieves a comprehensive export of a pipeline definition including
        metadata, agent configuration, data sources, prompts, tools, models, memories,
        Python code blocks, routers, and deployment information.

        Args:
            pipeline_id (str): The unique identifier of the pipeline to export
                definition for.
            correlation_id (str, optional): A unique identifier for request tracing
                and logging. If not provided, one will be automatically generated.

        Returns:
            ExportPipelineDefinitionResponse: A response object containing the complete
                pipeline definition export.

        Raises:
            AiriaAPIError: If the API request fails, including cases where:
                - The pipeline_id doesn't exist (404)
                - Authentication fails (401)
                - Access is forbidden (403)
                - Server errors (5xx)

        Example:
            ```python
            from airia import AiriaAsyncClient

            client = AiriaAsyncClient(api_key="your_api_key")

            # Export pipeline definition
            export = await client.pipelines_config.export_pipeline_definition(
                pipeline_id="your_pipeline_id"
            )

            print(f"Pipeline: {export.agent.name}")
            print(f"Export version: {export.metadata.export_version}")
            print(f"Data sources: {len(export.data_sources or [])}")
            print(f"Tools: {len(export.tools or [])}")
            ```

        Note:
            This method exports the complete pipeline definition which can be used
            for backup, version control, or importing into other environments.
        """
        request_data = self._pre_export_pipeline_definition(
            pipeline_id=pipeline_id,
            correlation_id=correlation_id,
            api_version=ApiVersion.V1.value,
        )
        resp = await self._request_handler.make_request("GET", request_data)

        return ExportPipelineDefinitionResponse(**resp)

    async def get_pipelines_config(
        self, project_id: Optional[str] = None, correlation_id: Optional[str] = None
    ) -> GetPipelinesConfigResponse:
        """
        Retrieve a list of pipeline configurations, optionally filtered by project ID.

        This method fetches a list of pipeline configurations including their
        deployment details, execution statistics, version information, and metadata.
        The results can be filtered by project ID to retrieve only pipelines
        belonging to a specific project.

        Args:
            project_id (str, optional): The unique identifier of the project to filter
                pipelines by. If not provided, pipelines from all accessible projects
                will be returned.
            correlation_id (str, optional): A unique identifier for request tracing
                and logging. If not provided, one will be automatically generated.

        Returns:
            GetPipelinesConfigResponse: A response object containing the list of
                pipeline configurations and the total count.

        Raises:
            AiriaAPIError: If the API request fails, including cases where:
                - Authentication fails (401)
                - Access is forbidden (403)
                - Server errors (5xx)

        Example:
            ```python
            from airia import AiriaAsyncClient

            client = AiriaAsyncClient(api_key="your_api_key")

            # Get all pipeline configurations
            pipelines = await client.pipelines_config.get_pipelines_config()
            print(f"Total pipelines: {pipelines.total_count}")
            for pipeline in pipelines.items:
                print(f"Pipeline: {pipeline.name}")
                print(f"Execution name: {pipeline.execution_name}")
                if pipeline.execution_stats:
                    print(f"Success count: {pipeline.execution_stats.success_count}")

            # Get pipelines for a specific project
            project_pipelines = await client.pipelines_config.get_pipelines_config(
                project_id="your_project_id"
            )
            print(f"Project pipelines: {project_pipelines.total_count}")
            ```

        Note:
            This method retrieves pipeline configuration information only. To execute
            a pipeline, use the execute_pipeline() method with the appropriate
            pipeline identifier.
        """
        request_data = self._pre_get_pipelines_config(
            project_id=project_id,
            correlation_id=correlation_id,
            api_version=ApiVersion.V1.value,
        )
        resp = await self._request_handler.make_request("GET", request_data)

        return GetPipelinesConfigResponse(**resp)
