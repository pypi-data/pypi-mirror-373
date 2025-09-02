"""Types for the get_pipelines_config API response.

This module defines data structures for the pipelines configuration list endpoint,
including pipeline configurations with their deployment details, execution statistics,
version information, and metadata.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class PipelineExecutionStats(BaseModel):
    """Statistics about pipeline executions.

    Attributes:
        success_count: Number of successful executions
        failure_count: Number of failed executions
    """

    success_count: int = Field(
        alias="successCount", description="Number of successful executions"
    )
    failure_count: int = Field(
        alias="failureCount", description="Number of failed executions"
    )


class PipelineVersion(BaseModel):
    """Represents a version of a pipeline.

    Attributes:
        pipeline_id: The unique identifier of the pipeline
        major_version: Major version number
        minor_version: Minor version number
        version_number: Full version number as string
        is_draft_version: Whether this is a draft version
        is_latest: Whether this is the latest version
        steps: Pipeline steps (optional)
        alignment: Layout alignment of the pipeline
        description: Version description (optional)
        version_name: Name of the version (optional)
        is_deprecated: Whether this version is deprecated
        id: Unique identifier for this version
        tenant_id: Tenant identifier
        project_id: Project identifier
        created_at: Creation timestamp
        updated_at: Last update timestamp
        user_id: User identifier who created this version
    """

    pipeline_id: str = Field(
        alias="pipelineId", description="The unique identifier of the pipeline"
    )
    major_version: int = Field(alias="majorVersion", description="Major version number")
    minor_version: int = Field(alias="minorVersion", description="Minor version number")
    version_number: str = Field(
        alias="versionNumber", description="Full version number as string"
    )
    is_draft_version: bool = Field(
        alias="isDraftVersion", description="Whether this is a draft version"
    )
    is_latest: bool = Field(
        alias="isLatest", description="Whether this is the latest version"
    )
    steps: Optional[Any] = Field(None, description="Pipeline steps")
    alignment: str = Field(description="Layout alignment of the pipeline")
    description: Optional[str] = Field(None, description="Version description")
    version_name: Optional[str] = Field(
        alias="versionName", default=None, description="Name of the version"
    )
    is_deprecated: bool = Field(
        alias="isDeprecated", description="Whether this version is deprecated"
    )
    id: str = Field(description="Unique identifier for this version")
    tenant_id: str = Field(alias="tenantId", description="Tenant identifier")
    project_id: str = Field(alias="projectId", description="Project identifier")
    created_at: datetime = Field(alias="createdAt", description="Creation timestamp")
    updated_at: datetime = Field(alias="updatedAt", description="Last update timestamp")
    user_id: Optional[str] = Field(
        alias="userId",
        default=None,
        description="User identifier who created this version",
    )


class DeploymentAssignment(BaseModel):
    """Represents a deployment assignment.

    This is a placeholder for deployment assignment data structure.
    """

    pass


class Deployment(BaseModel):
    """Represents a deployment configuration.

    Attributes:
        pipeline_id: The pipeline identifier this deployment belongs to
        name: Name of the deployment
        description: Description of the deployment
        pipeline: Pipeline details (optional)
        deployment_user_prompts: User prompts for deployment (optional)
        deployment_prompt: Deployment prompt (optional)
        project_id: Project identifier
        is_recommended: Whether this deployment is recommended
        tags: List of tags associated with the deployment
        deployment_type: Type of deployment
        conversation_type: Type of conversation
        about: About information (optional)
        is_deployed_via_assistants: Whether deployed via assistants
        assignments: List of deployment assignments
        supported_input_modes: List of supported input modes
        id: Unique identifier for the deployment
        tenant_id: Tenant identifier
        created_at: Creation timestamp
        updated_at: Last update timestamp
        user_id: User identifier who created the deployment
    """

    pipeline_id: str = Field(
        alias="pipelineId",
        description="The pipeline identifier this deployment belongs to",
    )
    name: str = Field(description="Name of the deployment")
    description: str = Field(description="Description of the deployment")
    pipeline: Optional[Any] = Field(None, description="Pipeline details")
    deployment_user_prompts: Optional[Any] = Field(
        alias="deploymentUserPrompts",
        default=None,
        description="User prompts for deployment",
    )
    deployment_prompt: Optional[str] = Field(
        alias="deploymentPrompt", default=None, description="Deployment prompt"
    )
    project_id: str = Field(alias="projectId", description="Project identifier")
    is_recommended: bool = Field(
        alias="isRecommended", description="Whether this deployment is recommended"
    )
    tags: List[str] = Field(
        default_factory=list, description="List of tags associated with the deployment"
    )
    deployment_type: str = Field(
        alias="deploymentType", description="Type of deployment"
    )
    conversation_type: str = Field(
        alias="conversationType", description="Type of conversation"
    )
    about: Optional[Any] = Field(None, description="About information")
    is_deployed_via_assistants: bool = Field(
        alias="isDeployedViaAssistants", description="Whether deployed via assistants"
    )
    assignments: List[DeploymentAssignment] = Field(
        default_factory=list, description="List of deployment assignments"
    )
    supported_input_modes: List[str] = Field(
        alias="supportedInputModes", description="List of supported input modes"
    )
    id: str = Field(description="Unique identifier for the deployment")
    tenant_id: str = Field(alias="tenantId", description="Tenant identifier")
    created_at: datetime = Field(alias="createdAt", description="Creation timestamp")
    updated_at: datetime = Field(alias="updatedAt", description="Last update timestamp")
    user_id: Optional[str] = Field(
        alias="userId",
        default=None,
        description="User identifier who created the deployment",
    )


class AgentTrigger(BaseModel):
    """Represents an agent trigger configuration.

    Attributes:
        email_id: Email identifier for the trigger
        allowed_type: Type of allowed values
        allowed_values: Comma-separated allowed values
        pipeline_id: Pipeline identifier
        data_source_id: Data source identifier (optional)
        store_connector_id: Store connector identifier
        email_action: Email action to perform
        forward_to: Forward destination (optional)
        id: Unique identifier for the trigger
        tenant_id: Tenant identifier
        project_id: Project identifier
        created_at: Creation timestamp
        updated_at: Last update timestamp
        user_id: User identifier who created the trigger
    """

    email_id: str = Field(
        alias="emailId", description="Email identifier for the trigger"
    )
    allowed_type: str = Field(alias="allowedType", description="Type of allowed values")
    allowed_values: str = Field(
        alias="allowedValues", description="Comma-separated allowed values"
    )
    pipeline_id: str = Field(alias="pipelineId", description="Pipeline identifier")
    data_source_id: Optional[str] = Field(
        alias="dataSourceId", default=None, description="Data source identifier"
    )
    store_connector_id: Optional[str] = Field(
        alias="storeConnectorId", default=None, description="Store connector identifier"
    )
    email_action: str = Field(
        alias="emailAction", description="Email action to perform"
    )
    forward_to: Optional[str] = Field(
        alias="forwardTo", default=None, description="Forward destination"
    )
    id: str = Field(description="Unique identifier for the trigger")
    tenant_id: str = Field(alias="tenantId", description="Tenant identifier")
    project_id: str = Field(alias="projectId", description="Project identifier")
    created_at: datetime = Field(alias="createdAt", description="Creation timestamp")
    updated_at: datetime = Field(alias="updatedAt", description="Last update timestamp")
    user_id: Optional[str] = Field(
        alias="userId",
        default=None,
        description="User identifier who created the trigger",
    )


class PipelineConfigItem(BaseModel):
    """Represents a single pipeline configuration item.

    Attributes:
        deployment_id: Deployment identifier (optional)
        deployment_name: Name of the deployment
        deployment_description: Description of the deployment
        user_keys: User keys (optional)
        group_keys: Group keys (optional)
        agent_icon: Agent icon (optional)
        external: Whether this is an external pipeline
        active_version_id: ID of the active version
        name: Name of the pipeline
        execution_name: Execution name for the pipeline
        description: Description of the pipeline
        video_link: Link to video documentation
        agent_icon_id: Agent icon identifier (optional)
        agent_unicode_icon: Unicode icon for the agent
        versions: List of pipeline versions
        execution_stats: Execution statistics
        industry: Industry category
        sub_industries: Sub-industry categories (optional)
        agent_details: Agent details (optional)
        agent_details_tags: Agent details tags (optional)
        active_version: The active version details
        backup_pipeline_id: Backup pipeline ID (optional)
        deployment: Deployment configuration (optional)
        library_agent_id: Library agent ID (optional)
        library_imported_hash: Hash of imported library
        library_imported_version: Version of imported library
        is_deleted: Whether this pipeline is deleted (optional)
        agent_trigger: Agent trigger configuration (optional)
        api_key_id: API key identifier (optional)
        is_seeded: Whether this pipeline is seeded
        behaviours: Behaviours configuration (optional)
        department_id: Department identifier (optional)
        department: Department information (optional)
        id: Unique identifier for the pipeline
        tenant_id: Tenant identifier
        project_id: Project identifier
        created_at: Creation timestamp
        updated_at: Last update timestamp
        user_id: User identifier who created the pipeline
    """

    deployment_id: Optional[str] = Field(
        alias="deploymentId", default=None, description="Deployment identifier"
    )
    deployment_name: str = Field(
        alias="deploymentName", description="Name of the deployment"
    )
    deployment_description: str = Field(
        alias="deploymentDescription", description="Description of the deployment"
    )
    user_keys: Optional[Any] = Field(
        alias="userKeys", default=None, description="User keys"
    )
    group_keys: Optional[Any] = Field(
        alias="groupKeys", default=None, description="Group keys"
    )
    agent_icon: Optional[Any] = Field(
        alias="agentIcon", default=None, description="Agent icon"
    )
    external: bool = Field(description="Whether this is an external pipeline")
    active_version_id: str = Field(
        alias="activeVersionId", description="ID of the active version"
    )
    name: str = Field(description="Name of the pipeline")
    execution_name: str = Field(
        alias="executionName", description="Execution name for the pipeline"
    )
    description: str = Field(description="Description of the pipeline")
    video_link: str = Field(
        alias="videoLink", description="Link to video documentation"
    )
    agent_icon_id: Optional[str] = Field(
        alias="agentIconId", default=None, description="Agent icon identifier"
    )
    agent_unicode_icon: str = Field(
        alias="agentUnicodeIcon", description="Unicode icon for the agent"
    )
    versions: List[PipelineVersion] = Field(description="List of pipeline versions")
    execution_stats: Optional[PipelineExecutionStats] = Field(
        alias="executionStats", default=None, description="Execution statistics"
    )
    industry: str = Field(description="Industry category")
    sub_industries: Optional[Any] = Field(
        alias="subIndustries", default=None, description="Sub-industry categories"
    )
    agent_details: Optional[Any] = Field(
        alias="agentDetails", default=None, description="Agent details"
    )
    agent_details_tags: Optional[Any] = Field(
        alias="agentDetailsTags", default=None, description="Agent details tags"
    )
    active_version: PipelineVersion = Field(
        alias="activeVersion", description="The active version details"
    )
    backup_pipeline_id: Optional[str] = Field(
        alias="backupPipelineId", default=None, description="Backup pipeline ID"
    )
    deployment: Optional[Deployment] = Field(
        None, description="Deployment configuration"
    )
    library_agent_id: Optional[str] = Field(
        alias="libraryAgentId", default=None, description="Library agent ID"
    )
    library_imported_hash: str = Field(
        alias="libraryImportedHash", description="Hash of imported library"
    )
    library_imported_version: str = Field(
        alias="libraryImportedVersion", description="Version of imported library"
    )
    is_deleted: Optional[bool] = Field(
        alias="isDeleted", default=None, description="Whether this pipeline is deleted"
    )
    agent_trigger: Optional[AgentTrigger] = Field(
        alias="agentTrigger", default=None, description="Agent trigger configuration"
    )
    api_key_id: Optional[str] = Field(
        alias="apiKeyId", default=None, description="API key identifier"
    )
    is_seeded: bool = Field(
        alias="isSeeded", description="Whether this pipeline is seeded"
    )
    behaviours: Optional[Any] = Field(None, description="Behaviours configuration")
    department_id: Optional[str] = Field(
        alias="departmentId", default=None, description="Department identifier"
    )
    department: Optional[Any] = Field(None, description="Department information")
    id: str = Field(description="Unique identifier for the pipeline")
    tenant_id: str = Field(alias="tenantId", description="Tenant identifier")
    project_id: str = Field(alias="projectId", description="Project identifier")
    created_at: datetime = Field(alias="createdAt", description="Creation timestamp")
    updated_at: datetime = Field(alias="updatedAt", description="Last update timestamp")
    user_id: Optional[str] = Field(
        alias="userId",
        default=None,
        description="User identifier who created the pipeline",
    )


class GetPipelinesConfigResponse(BaseModel):
    """Response model for the get_pipelines_config endpoint.

    Attributes:
        items: List of pipeline configuration items
        total_count: Total count of pipeline configurations
    """

    items: List[PipelineConfigItem] = Field(
        description="List of pipeline configuration items"
    )
    total_count: int = Field(
        alias="totalCount", description="Total count of pipeline configurations"
    )
