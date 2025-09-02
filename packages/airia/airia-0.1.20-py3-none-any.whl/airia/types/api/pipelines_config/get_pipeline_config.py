"""Types for the get_pipeline_config API response.

This module defines comprehensive data structures for pipeline configuration
responses, including pipeline definitions, versions, steps, deployments, and
all associated metadata required for pipeline management and execution.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PipelineStepPosition(BaseModel):
    """Represents the graphical position of a pipeline step within a visual representation of a pipeline.

    Used for positioning pipeline steps in the visual pipeline editor interface.

    Attributes:
        x: The X-coordinate of the pipeline step in a 2D space
        y: The Y-coordinate of the pipeline step in a 2D space
    """

    x: float = Field(description="The X-coordinate of the pipeline step in a 2D space")
    y: float = Field(description="The Y-coordinate of the pipeline step in a 2D space")


class PipelineStepHandle(BaseModel):
    """Represents a handle for a pipeline step.

    Handles are connection points on pipeline steps that allow data flow between
    steps. They can be either source handles (output) or target handles (input).

    Attributes:
        pipeline_step_id: The PipelineStepId this handle belongs to
        uuid: The UUID of the handle
        type: The type of the handle (source or target)
        label: The label of the handle for display purposes
        tooltip: The tooltip text shown when hovering over the handle
        x: The X-coordinate of the handle within the pipeline step
        y: The Y-coordinate of the handle within the pipeline step
    """

    pipeline_step_id: str = Field(
        alias="pipelineStepId", description="The PipelineStepId this handle belongs to"
    )
    uuid: str = Field(description="The UUID of the handle")
    type: str = Field(description="The type of the handle (source or target)")
    label: Optional[str] = Field(default=None, description="The label of the handle")
    tooltip: Optional[str] = Field(
        default=None, description="The tooltip of the handle"
    )
    x: Optional[float] = Field(
        default=None, description="The X-coordinate of the pipeline step in a 2D space"
    )
    y: Optional[float] = Field(
        default=None, description="The Y-coordinate of the pipeline step in a 2D space"
    )


class PipelineStepDependency(BaseModel):
    """Represents a dependency between pipeline steps.

    Dependencies define the flow of data between pipeline steps by connecting
    output handles of parent steps to input handles of child steps.

    Attributes:
        pipeline_step_id: The PipelineStepId this dependency belongs to
        parent_id: The UUID of the parent pipeline step that provides input
        parent_handle_id: The UUID of the parent handle (source output)
        handle_id: The UUID of this handle (target input)
    """

    pipeline_step_id: str = Field(
        alias="pipelineStepId", description="The PipelineStepId this handle belongs to"
    )
    parent_id: str = Field(
        alias="parentId", description="The UUID of the parent pipeline step"
    )
    parent_handle_id: str = Field(
        alias="parentHandleId", description="The UUID of the parent handle (source)"
    )
    handle_id: str = Field(
        alias="handleId", description="The UUID of this handle (target)"
    )


class PipelineStep(BaseModel):
    """Represents a step within a pipeline.

    Pipeline steps are individual processing units that perform specific tasks
    within a pipeline workflow. Each step has a type, position, and connection
    points for data flow.

    Attributes:
        position: The graphical position of this step within the pipeline editor
        position_id: The identifier of the position for layout management
        handles: The connection points (handles) of this step for data flow
        dependencies_object: The input dependencies of this step from other steps
        step_type: The type of processing this step performs
        pipeline_version_id: The Pipeline Version Id this step belongs to
        step_title: The human-readable title/name of the step
    """

    position: Optional[PipelineStepPosition] = Field(
        default=None, description="The position of this step within the pipeline"
    )
    position_id: Optional[str] = Field(
        alias="positionId", default=None, description="The identifier of the position"
    )
    handles: Optional[List[PipelineStepHandle]] = Field(
        default=None, description="The handles of this step within the pipeline"
    )
    dependencies_object: Optional[List[PipelineStepDependency]] = Field(
        alias="dependenciesObject",
        default=None,
        description="The dependencies of this step within the pipeline",
    )
    step_type: str = Field(alias="stepType", description="The type of this step")
    pipeline_version_id: str = Field(
        alias="pipelineVersionId", description="The Pipeline Version Id"
    )
    step_title: str = Field(alias="stepTitle", description="The Step Title")


class PipelineVersion(BaseModel):
    """Represents a specific version of a pipeline.

    Pipeline versions allow for iteration and deployment management of pipelines.
    Each version contains a complete definition of the pipeline structure and steps.

    Attributes:
        pipeline_id: The identifier of the parent pipeline this version belongs to
        major_version: The major version number for significant changes
        minor_version: The minor version number for incremental changes
        version_number: The complete version number in string format (e.g., "1.2")
        is_draft_version: Whether this is a draft version or a released production version
        is_latest: Whether this version is the latest/current version of the pipeline
        steps: The list of processing steps that make up this pipeline version
        alignment: The UI alignment setting for pipeline visualization
    """

    pipeline_id: str = Field(
        alias="pipelineId", description="The identifier of the parent pipeline"
    )
    major_version: int = Field(
        alias="majorVersion", description="The major version number"
    )
    minor_version: int = Field(
        alias="minorVersion", description="The minor version number"
    )
    version_number: str = Field(
        alias="versionNumber", description="The version number in string format"
    )
    is_draft_version: bool = Field(
        alias="isDraftVersion",
        description="Whether the version is a draft or a major production version",
    )
    is_latest: bool = Field(
        alias="isLatest",
        description="Whether this version is the latest version of the pipeline",
    )
    steps: Optional[List[PipelineStep]] = Field(
        default=None, description="The list of steps that make up the pipeline"
    )
    alignment: str = Field(description="The alignment of the pipeline in UI")


class PipelineExecutionStats(BaseModel):
    """Represents the execution statistics for a pipeline.

    Tracks the historical performance and reliability metrics of pipeline executions
    to provide insights into pipeline health and success rates.

    Attributes:
        success_count: The total number of successful executions
        failure_count: The total number of failed executions
    """

    success_count: int = Field(
        alias="successCount", description="The total number of successful executions"
    )
    failure_count: int = Field(
        alias="failureCount", description="The total number of failed executions"
    )


class AgentDetailsEntry(BaseModel):
    """Represents a single agent details entry.

    Agent details entries define configurable parameters and metadata for
    agent behavior, including input types, default values, and available options.

    Attributes:
        type: The input type (e.g., text, select, multiselect, number)
        name: The parameter name for this configuration entry
        value: The current value of this parameter
        options: Available options for select or multiselect input types
    """

    type: str = Field(description="The input type")
    name: str = Field(description="The input name")
    value: Any = Field(description="The input value")
    options: Optional[List[str]] = Field(
        default=None, description="The options for select or multiselect"
    )


class AboutDeploymentMetadata(BaseModel):
    """Represents metadata about a deployment for the About tab.

    Contains versioned metadata that appears in the About section of a deployment,
    including educational and descriptive content.

    Attributes:
        version: The version of the About Deployment metadata schema
        video_url: The URL of the instructional or demonstration video
    """

    version: int = Field(description="The version of the About Deployment metadata")
    video_url: str = Field(alias="videoUrl", description="The video url")


class DeploymentAssignment(BaseModel):
    """Represents a deployment assignment.

    Deployment assignments link deployments to specific entities (users, groups, etc.)
    to control access and visibility of deployed pipelines.

    Attributes:
        deployment_id: The ID of the deployment being assigned
        id: The unique identifier of this assignment
        entity_id: The ID of the entity (user, group) receiving the assignment
        entity_type: The type of entity being assigned (user, group, etc.)
        created_at: Timestamp when the assignment was created
        updated_at: Timestamp when the assignment was last modified
        user_id: The ID of the user who created this assignment
    """

    deployment_id: str = Field(alias="deploymentId", description="The deployment ID")
    id: str = Field(description="The ID")
    entity_id: str = Field(alias="entityId", description="The entity ID")
    entity_type: str = Field(alias="entityType", description="The entity type")
    created_at: Optional[datetime] = Field(
        alias="createdAt", default=None, description="The created at timestamp"
    )
    updated_at: Optional[datetime] = Field(
        alias="updatedAt", default=None, description="The updated at timestamp"
    )
    user_id: Optional[str] = Field(
        alias="userId", default=None, description="The user ID"
    )


class DeploymentUserPrompt(BaseModel):
    """A join entity that represents a user prompt associated with a deployment.

    Links deployments with predefined user prompts to provide template
    interactions and guided user experiences.

    Attributes:
        deployment_id: The ID of the deployment this prompt is associated with
        user_prompt_id: The ID of the user prompt template
    """

    deployment_id: str = Field(alias="deploymentId", description="The deployment ID")
    user_prompt_id: str = Field(alias="userPromptId", description="The user prompt ID")


class Deployment(BaseModel):
    """Represents a deployment.

    Deployments make pipelines available to end users with specific configurations,
    branding, and access controls. They define how users interact with pipelines
    in production environments.

    Attributes:
        pipeline_id: The ID of the pipeline being deployed
        name: The human-readable name of the deployment
        description: A detailed description of the deployment's purpose and functionality
        deployment_user_prompts: List of predefined prompts available to users
        deployment_prompt: Optional system prompt that configures the deployment behavior
        project_id: The ID of the project containing this deployment
        is_recommended: Whether this deployment is featured/recommended to users
        tags: Categorization tags for discovery and organization
        conversation_type: The type of conversation interface (chat, form, etc.)
        about: Optional metadata for the About/help section
        assignments: Optional list of user/group assignments for access control
    """

    pipeline_id: str = Field(
        alias="pipelineId",
        description="The pipeline ID associated with this deployment",
    )
    name: str = Field(description="The Deployment Name")
    description: str = Field(description="A description of the deployment")
    deployment_user_prompts: Optional[List[DeploymentUserPrompt]] = Field(
        alias="deploymentUserPrompts",
        default=None,
        description="The DeploymentUserPrompts",
    )
    deployment_prompt: Optional[str] = Field(
        alias="deploymentPrompt", default=None, description="The DeploymentPrompt"
    )
    project_id: str = Field(alias="projectId", description="The Project Id")
    is_recommended: bool = Field(
        alias="isRecommended",
        description="Whether this is a recommended/featured deployment",
    )
    tags: List[str] = Field(description="The Tags")
    conversation_type: str = Field(
        alias="conversationType", description="The Conversation Start Type"
    )
    about: Optional[AboutDeploymentMetadata] = Field(
        default=None, description="Metadata about the deployment"
    )
    assignments: Optional[List[DeploymentAssignment]] = Field(
        default=None, description="The Assignments"
    )


class AgentTrigger(BaseModel):
    """Represents a trigger used to start a pipeline execution.

    Agent triggers enable automatic pipeline execution based on external events,
    particularly email-based triggers for document processing and workflow automation.

    Attributes:
        email_id: The email address that can trigger this agent
        allowed_type: The type of content allowed to trigger execution
        allowed_values: The specific values that are permitted for triggering
        pipeline_id: The ID of the pipeline to execute when triggered
        data_source_id: Optional ID of the data source for input data
        store_connector_id: Optional ID of the storage connector for file handling
        email_action: The action to perform when the email trigger activates
        forward_to: Optional email address to forward results to after execution
    """

    email_id: str = Field(
        alias="emailId", description="The email id corresponding to the Agent"
    )
    allowed_type: str = Field(
        alias="allowedType", description="The allowed type for the agent trigger"
    )
    allowed_values: str = Field(
        alias="allowedValues", description="The allowed values for the agent trigger"
    )
    pipeline_id: str = Field(
        alias="pipelineId", description="The Pipeline Version identifier"
    )
    data_source_id: Optional[str] = Field(
        alias="dataSourceId", default=None, description="The Data Source identifier"
    )
    store_connector_id: Optional[str] = Field(
        alias="storeConnectorId",
        default=None,
        description="The datastore connector identifier",
    )
    email_action: str = Field(
        alias="emailAction", description="The email action to be performed"
    )
    forward_to: Optional[str] = Field(
        alias="forwardTo",
        default=None,
        description="The recipient to forward to",
        max_length=4000,
    )


class Pipeline(BaseModel):
    """Represents a processing pipeline.

    Pipelines are the core workflow definition in the Airia platform, containing
    a series of connected steps that process data and execute AI tasks. Each pipeline
    can have multiple versions and can be deployed for end-user access.

    Attributes:
        id: The unique identifier of the pipeline
        tenant_id: The tenant ID this pipeline belongs to
        project_id: The project ID this pipeline belongs to
        created_at: Timestamp when the pipeline was created
        updated_at: Timestamp when the pipeline was last modified
        user_id: The ID of the user who created this pipeline
        active_version_id: The ID of the currently active version for execution
        name: The human-readable name of the pipeline
        execution_name: The name used when executing the pipeline programmatically
        description: A detailed description of the pipeline's purpose and functionality
        video_link: Optional URL to a video demonstration or tutorial
        agent_icon_id: The ID of the icon used to represent this pipeline
        versions: All available versions of this pipeline
        execution_stats: Historical execution performance statistics
        industry: The primary industry or domain this pipeline serves
        sub_industries: Additional industry classifications and tags
        agent_details: Configurable parameters and metadata for agent behavior
        agent_details_tags: Tags for categorizing agent capabilities
        active_version: The complete active version object (if loaded)
        backup_pipeline_id: ID of a fallback pipeline in case of failure
        deployment: The deployment configuration for end-user access
        library_agent_id: ID of the library agent this pipeline is based on
        library_imported_hash: Hash of the imported library agent for version tracking
        library_imported_version: Version of the imported library agent
        is_deleted: Whether this pipeline is marked for deletion
        agent_trigger: Optional trigger configuration for automatic execution
        api_key_id: ID of the API key used for external service authentication
        is_seeded: Whether this pipeline comes from the platform's seed data
        behaviours: List of capabilities and behaviors this agent can perform
    """

    id: str = Field(description="The unique identifier of the pipeline")
    tenant_id: Optional[str] = Field(
        alias="tenantId", default=None, description="The Tenant Id"
    )
    project_id: Optional[str] = Field(
        alias="projectId", default=None, description="The project Id"
    )
    created_at: Optional[datetime] = Field(
        alias="createdAt", default=None, description="The created at timestamp"
    )
    updated_at: Optional[datetime] = Field(
        alias="updatedAt", default=None, description="The updated at timestamp"
    )
    user_id: Optional[str] = Field(
        alias="userId", default=None, description="The user ID"
    )
    active_version_id: Optional[str] = Field(
        alias="activeVersionId",
        default=None,
        description="The unique identifier of pipeline's active version",
    )
    name: Optional[str] = Field(default=None, description="The name of the pipeline")
    execution_name: Optional[str] = Field(
        alias="executionName",
        default=None,
        description="The execution name of the pipeline",
    )
    description: Optional[str] = Field(
        default=None,
        description="The optional description of the pipeline",
        max_length=2000,
    )
    video_link: Optional[str] = Field(
        alias="videoLink", default=None, description="The video link of the pipeline"
    )
    agent_icon_id: Optional[str] = Field(
        alias="agentIconId", default=None, description="The Agent Icon Id"
    )
    versions: Optional[List[PipelineVersion]] = Field(
        default=None, description="The versions of this pipeline"
    )
    execution_stats: Optional[PipelineExecutionStats] = Field(
        alias="executionStats", default=None, description="The execution statistics"
    )
    industry: Optional[str] = Field(
        default=None, description="The main industry of the pipeline"
    )
    sub_industries: Optional[List[str]] = Field(
        alias="subIndustries", default=None, description="The agent sub-industries tags"
    )
    agent_details: Optional[Dict[str, List[AgentDetailsEntry]]] = Field(
        alias="agentDetails", default=None, description="The agent details properties"
    )
    agent_details_tags: Optional[List[str]] = Field(
        alias="agentDetailsTags", default=None, description="The agent details tags"
    )
    active_version: Optional[PipelineVersion] = Field(
        alias="activeVersion",
        default=None,
        description="The active version of this pipeline",
    )
    backup_pipeline_id: Optional[str] = Field(
        alias="backupPipelineId",
        default=None,
        description="The unique identifier of the backup pipeline",
    )
    deployment: Optional[Deployment] = Field(
        default=None, description="The associated Deployment for this pipeline"
    )
    library_agent_id: Optional[str] = Field(
        alias="libraryAgentId",
        default=None,
        description="The library agent id associated with the pipeline",
    )
    library_imported_hash: Optional[str] = Field(
        alias="libraryImportedHash", default=None, description="The library agent hash"
    )
    library_imported_version: Optional[str] = Field(
        alias="libraryImportedVersion",
        default=None,
        description="The library imported version",
    )
    is_deleted: Optional[bool] = Field(
        alias="isDeleted",
        default=None,
        description="Whether this entity is marked for deletion",
    )
    agent_trigger: Optional[AgentTrigger] = Field(
        alias="agentTrigger",
        default=None,
        description="The Agent trigger associated with the pipeline",
    )
    api_key_id: Optional[str] = Field(
        alias="apiKeyId", default=None, description="The Api Key navigation property"
    )
    is_seeded: Optional[bool] = Field(
        alias="isSeeded", default=None, description="Whether the pipeline is seeded"
    )
    behaviours: Optional[List[str]] = Field(
        default=None, description="The behaviours that the agent can perform"
    )


class PipelineConfigResponse(Pipeline):
    """Represents a complete pipeline configuration response.

    Extends the base Pipeline model with additional deployment and access control
    information. This is the primary response model for pipeline configuration
    endpoints that need full context including deployment details and user permissions.

    Attributes:
        deployment_id: The ID of the associated deployment (if deployed)
        deployment_name: The name of the associated deployment
        deployment_description: The description of the associated deployment
        user_keys: Dictionary mapping user roles to user IDs for access control
        group_keys: Dictionary mapping group roles to group IDs for access control
        agent_icon: Base64 encoded agent icon image data
        external: Whether this is an external agent imported via Agent-to-Agent (A2A)
    """

    deployment_id: Optional[str] = Field(
        alias="deploymentId", default=None, description="The Deployment Id"
    )
    deployment_name: Optional[str] = Field(
        alias="deploymentName", default=None, description="The Deployment Name"
    )
    deployment_description: Optional[str] = Field(
        alias="deploymentDescription",
        default=None,
        description="The Deployment Description",
    )
    user_keys: Optional[Dict[str, str]] = Field(
        alias="userKeys", default=None, description="The User Ids"
    )
    group_keys: Optional[Dict[str, str]] = Field(
        alias="groupKeys", default=None, description="The Group Ids"
    )
    agent_icon: Optional[str] = Field(
        alias="agentIcon", default=None, description="The Agent icon"
    )
    external: Optional[bool] = Field(
        default=None,
        description="Whether the agent is an external agent imported using A2A",
    )
