"""
Pydantic models for single deployment API responses.

This module defines the data structures returned by the get_deployment endpoint,
which retrieves a single deployment by ID.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .get_deployments import AboutDeploymentMetadata, DataSource, UserPrompt


class GetDeploymentResponse(BaseModel):
    """
    Response model for retrieving a single deployment.

    Represents a deployment DTO with complete information about the deployment,
    including its configuration, associated resources, and metadata.

    Attributes:
        id: Unique deployment identifier
        pipeline_id: Unique identifier of the pipeline powering this deployment
        pipeline_name: Name of the pipeline associated with this deployment
        project_id: Unique identifier of the project containing this deployment
        deployment_name: Human-readable name of the deployment
        deployment_icon_url: Optional URL to the deployment's icon image
        deployment_icon_id: Optional unique identifier for the deployment icon
        description: Detailed description of what the deployment does
        tags: List of tags for categorizing and filtering deployments
        is_recommended: Whether this deployment is marked as recommended
        user_prompts: List of user prompts associated with this deployment
        deployment_prompt: Optional hardcoded prompt type for the deployment
        user_ids: List of user IDs that have access to this deployment
        group_ids: List of group IDs that have access to this deployment
        conversation_type: Type of conversation this deployment supports
        data_sources: List of data sources that the deployment can access
        pipeline_user_id: ID of the user who created the underlying pipeline
        about: Optional metadata for the About tab
    """

    id: UUID = Field(description="Gets the deployment ID.")
    pipeline_id: UUID = Field(
        alias="pipelineId",
        description="Gets the pipeline ID associated with this deployment.",
    )
    pipeline_name: Optional[str] = Field(
        None,
        alias="pipelineName",
        description="Gets the pipeline name associated with this deployment.",
    )
    project_id: UUID = Field(
        alias="projectId",
        description="Gets the project ID associated with this deployment.",
    )
    deployment_name: str = Field(
        alias="deploymentName", description="Gets the deployment name."
    )
    deployment_icon_url: Optional[str] = Field(
        None, alias="deploymentIconUrl", description="Gets the Deployment Icon URL."
    )
    deployment_icon_id: Optional[UUID] = Field(
        None, alias="deploymentIconId", description="Gets the Deployment Icon Id."
    )
    description: str = Field(description="Gets the deployment description.")
    tags: List[str] = Field(description="Gets the Tags.")
    is_recommended: bool = Field(
        alias="isRecommended",
        description="Gets a value indicating whether the deployment is recommended.",
    )
    user_prompts: List[UserPrompt] = Field(
        alias="userPrompts",
        description="Gets the user prompts associated with this deployment.",
    )
    deployment_prompt: Optional[str] = Field(
        None,
        alias="deploymentPrompt",
        description="Gets or sets the optional deployment prompt type.",
    )
    user_ids: Optional[List[UUID]] = Field(
        alias="userIds",
        description="Gets or sets the user IDs associated with this deployment.",
    )
    group_ids: Optional[List[UUID]] = Field(
        alias="groupIds",
        description="Gets or sets the group IDs associated with this deployment.",
    )
    conversation_type: str = Field(
        alias="conversationType",
        description="Gets or sets the conversation start type for this deployment.",
    )
    data_sources: List[DataSource] = Field(
        alias="dataSources",
        description="Gets the data sources associated with this deployment.",
    )
    pipeline_user_id: Optional[UUID] = Field(
        None,
        alias="pipelineUserId",
        description="Gets the ID of the user who created deployed agent.",
    )
    about: Optional[AboutDeploymentMetadata] = Field(
        None,
        description="Gets the deployment metadata for the 'About' section.",
    )
