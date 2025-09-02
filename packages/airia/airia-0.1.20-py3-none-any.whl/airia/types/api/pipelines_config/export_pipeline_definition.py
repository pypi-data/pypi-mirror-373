"""Types for the export_pipeline_definition API response.

This module defines comprehensive data structures for pipeline export functionality,
including complete pipeline definitions, data sources, tools, models, and all
associated metadata required for pipeline import/export operations.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ExportCredentialDataList(BaseModel):
    """Represents a key-value pair within credential data.

    Used to store credential information as structured key-value pairs
    for authentication and authorization purposes.

    Attributes:
        key: The key name for the credential data
        value: The value associated with the key
    """
    key: str = Field(..., description="Gets or sets the key.")
    value: str = Field(..., description="Gets or sets the value.")


class ExportCredentials(BaseModel):
    """Represents credential information for external service authentication.

    Defines the complete credential configuration including type, source,
    and associated data required for authenticating with external services.

    Attributes:
        name: The name of the credential set
        credential_type: The type of credential (API key, OAuth, etc.)
        source_type: The source where the credential originates
        credential_data_list: List of key-value pairs containing credential data
        id: The unique identifier for the credential set
    """
    name: str = Field(..., description="Gets or sets the name.")
    credential_type: str = Field(
        ..., description="Gets or sets the type.", alias="credentialType"
    )
    source_type: str = Field(
        ..., description="Gets or sets the source type.", alias="sourceType"
    )
    credential_data_list: List[ExportCredentialDataList] = Field(
        ...,
        description="Gets or sets the credential data list.",
        alias="credentialDataList",
    )
    id: str = Field(..., description="Gets or sets the ID.")


class ExportPosition(BaseModel):
    """Represents the position coordinates for UI elements.

    Defines X and Y coordinates for positioning elements within
    the visual pipeline editor interface.

    Attributes:
        x: The X-coordinate position
        y: The Y-coordinate position
    """
    x: str = Field(..., description="Gets or sets the X.")
    y: str = Field(..., description="Gets or sets the Y.")


class ExportHandle(BaseModel):
    """Represents a connection handle for pipeline steps.

    Handles are connection points that allow data flow between pipeline steps.
    They define input and output points with positioning and labeling information.

    Attributes:
        uuid: The unique identifier of the handle
        type: The type of handle (source or target)
        label: Optional display label for the handle
        tooltip: Optional tooltip text for the handle
        x: The X-coordinate position of the handle
        y: The Y-coordinate position of the handle
    """
    uuid: str = Field(..., description="Gets or sets the UUID of the handle.")
    type: str = Field(
        ...,
        description="Gets or sets the type of the handle (source or target).",
        max_length=6,
    )
    label: Optional[str] = Field(
        None, description="Gets or sets the label of the handle.", max_length=100
    )
    tooltip: Optional[str] = Field(
        None, description="Gets or sets the tooltip of the handle."
    )
    x: float = Field(
        ...,
        description="Gets or sets the X-coordinate of the pipeline step in a 2D space.",
    )
    y: float = Field(
        ...,
        description="Gets or sets the Y-coordinate of the pipeline step in a 2D space.",
    )


class ExportDependency(BaseModel):
    """Represents a dependency relationship between pipeline steps.

    Defines the connection between a parent step's output handle and
    a child step's input handle, establishing data flow dependencies.

    Attributes:
        parent_id: The UUID of the parent pipeline step
        parent_handle_id: The UUID of the parent's output handle
        handle_id: The UUID of the child's input handle
    """
    parent_id: str = Field(
        ...,
        description="Gets or sets the UUID of the parent pipeline step.",
        alias="parentId",
    )
    parent_handle_id: str = Field(
        ...,
        description="Gets or sets the UUID of the parent handle (source).",
        alias="parentHandleId",
    )
    handle_id: str = Field(
        ...,
        description="Gets or sets the UUID of this handle (target).",
        alias="handleId",
    )


class ExportPipelineStep(BaseModel):
    """Represents a complete pipeline step definition for export.

    Contains all configuration and metadata for a single step in a pipeline,
    including positioning, connections, and step-specific parameters.

    Attributes:
        id: The unique identifier of the step
        step_type: The type of step (LLM, retrieval, etc.)
        position: The visual position of the step
        handles: List of connection handles for the step
        dependencies_object: List of input dependencies from other steps
        temperature: Optional temperature setting for LLM steps
        include_date_time_context: Whether to include datetime context
        prompt_id: Optional ID of the associated prompt
        model_id: Optional ID of the associated model
        tool_ids: Optional list of tool IDs used by this step
        tool_params: Optional default parameters for tools
        data_source_id: Optional ID of the associated data source
        top_k: Optional number of top results to retrieve
        relevance_threshold: Optional relevance threshold for retrieval
        neighboring_chunks_count: Optional number of neighboring chunks
        hybrid_search_alpha: Optional alpha parameter for hybrid search
        database_type: Optional database type for data operations
        memory_id: Optional ID of the associated memory
        python_code_block_id: Optional ID of the associated Python code
        background_color: Optional background color for the step
        content: Optional content or configuration data
        step_title: The human-readable title of the step
    """
    id: str = Field(..., description="Gets or sets the ID.")
    step_type: str = Field(
        ..., description="Gets or sets the step type.", alias="stepType"
    )
    position: ExportPosition = Field(..., description="Gets or sets the position.")
    handles: List[ExportHandle] = Field(..., description="Gets or sets the handles.")
    dependencies_object: List[ExportDependency] = Field(
        ..., description="Gets or sets the dependencies.", alias="dependenciesObject"
    )
    temperature: Optional[float] = Field(
        None, description="Gets or sets the temperature."
    )
    include_date_time_context: Optional[bool] = Field(
        None,
        description="Gets or sets a value indicating whether to include date time context.",
        alias="includeDateTimeContext",
    )
    prompt_id: Optional[str] = Field(
        None, description="Gets or sets the prompt ID.", alias="promptId"
    )
    model_id: Optional[str] = Field(
        None, description="Gets or sets the model ID.", alias="modelId"
    )
    tool_ids: Optional[List[str]] = Field(
        None, description="Gets or sets the tool IDs.", alias="toolIds"
    )
    tool_params: Optional[Dict[str, str]] = Field(
        None, description="Gets or sets the tool default params.", alias="toolParams"
    )
    data_source_id: Optional[str] = Field(
        None, description="Gets or sets the data source.", alias="dataSourceId"
    )
    top_k: Optional[int] = Field(
        None, description="Gets or sets the top K.", alias="topK"
    )
    relevance_threshold: Optional[int] = Field(
        None,
        description="Gets or sets the relevance threshold.",
        alias="relevanceThreshold",
    )
    neighboring_chunks_count: Optional[int] = Field(
        None,
        description="Gets or sets the neighboring chunks count.",
        alias="neighboringChunksCount",
    )
    hybrid_search_alpha: Optional[float] = Field(
        None,
        description="Gets or sets the hybrid search Alpha parameter.",
        alias="hybridSearchAlpha",
    )
    database_type: Optional[str] = Field(
        None, description="Gets or sets the database type.", alias="databaseType"
    )
    memory_id: Optional[str] = Field(
        None, description="Gets or sets the memory.", alias="memoryId"
    )
    python_code_block_id: Optional[str] = Field(
        None, description="Gets or sets the code.", alias="pythonCodeBlockId"
    )
    background_color: Optional[str] = Field(
        None, description="Gets or sets the backgroundColor.", alias="backgroundColor"
    )
    content: Optional[str] = Field(None, description="Gets or sets the content.")
    step_title: str = Field(
        ..., description="Gets or sets the Step Title.", alias="stepTitle"
    )


class AgentDetailItemDefinition(BaseModel):
    """Represents a single configuration item for agent details.

    Defines configurable parameters for agent behavior, including input types,
    values, and available options for form-based configuration.

    Attributes:
        item_type: The type of input control (text, select, multiselect, etc.)
        name: The parameter name for this configuration item
        value: The current value of the parameter
        options: Optional list of available options for select/multiselect types
    """
    item_type: str = Field(
        ...,
        description="Gets or sets the entries for the agent details item input type.",
        alias="itemType",
    )
    name: str = Field(
        ...,
        description="Gets or sets the entries for the agent details item input value.",
    )
    value: str = Field(
        ...,
        description="Gets or sets the entries for the agent details item input value.",
    )
    options: Optional[List[str]] = Field(
        None,
        description="Gets or sets the entries for the agent details item options if it is a select or multiselect.",
    )


class ExportPipeline(BaseModel):
    """Represents a complete pipeline definition for export.

    Contains all metadata and configuration for a pipeline, including
    identification, description, industry classification, and step definitions.

    Attributes:
        name: The name of the pipeline
        execution_name: The name used for programmatic execution
        agent_description: Detailed description of the pipeline's purpose
        video_link: Optional URL to instructional video
        industry: The primary industry served by this pipeline
        sub_industries: Additional industry classifications
        agent_details: Dictionary of configurable agent parameters
        id: The unique identifier of the pipeline
        agent_icon: Optional base64-encoded icon image
        steps: List of pipeline steps that make up the workflow
    """
    name: str = Field(..., description="Gets or sets the name.")
    execution_name: Optional[str] = Field(
        None, description="Gets or sets the execution name.", alias="executionName"
    )
    agent_description: str = Field(
        ..., description="Gets or sets the description.", alias="agentDescription"
    )
    video_link: Optional[str] = Field(
        None, description="Gets or sets the video link.", alias="videoLink"
    )
    industry: Optional[str] = Field(None, description="Gets or sets the industry.")
    sub_industries: Optional[List[str]] = Field(
        None, description="Gets or sets the sub industries.", alias="subIndustries"
    )
    agent_details: Optional[Dict[str, List[AgentDetailItemDefinition]]] = Field(
        None, description="Gets or sets the industry.", alias="agentDetails"
    )
    id: str = Field(..., description="Gets or sets the ID.")
    agent_icon: Optional[str] = Field(
        None, description="Gets or sets the Agent Icon.", alias="agentIcon"
    )
    steps: List[ExportPipelineStep] = Field(..., description="Gets or sets the steps.")


class ExportDataSourceFile(BaseModel):
    """Represents a file within a data source for export.

    Defines file information including location, path, and access tokens
    for files associated with data sources.

    Attributes:
        data_source_id: The ID of the associated data source
        file_path: Optional path or location of the file
        input_token: Optional access token for the file
    """
    data_source_id: str = Field(
        ...,
        description="Gets or sets the ID of the associated DataSource.",
        alias="dataSourceId",
    )
    file_path: Optional[str] = Field(
        None,
        description="Gets or sets the file path or location within the data source.",
        alias="filePath",
    )
    input_token: Optional[str] = Field(
        None,
        description="Gets or sets the InputToken for the file.",
        alias="inputToken",
    )


class ExportChunkingConfig(BaseModel):
    """Represents chunking configuration for data processing.

    Defines how documents are split into chunks for vector storage
    and retrieval operations.

    Attributes:
        id: The unique identifier of the chunking configuration
        chunk_size: The size of each chunk in characters or tokens
        chunk_overlap: The number of characters/tokens that overlap between chunks
        strategy_type: The chunking strategy used (sentence, paragraph, etc.)
    """
    id: str = Field(
        ..., description="Gets or sets the chunking configuration identifier."
    )
    chunk_size: int = Field(
        ..., description="Gets or sets the chunk size.", alias="chunkSize"
    )
    chunk_overlap: int = Field(
        ..., description="Gets or sets the chunk overlap.", alias="chunkOverlap"
    )
    strategy_type: str = Field(
        ..., description="Gets or sets the strategy type.", alias="strategyType"
    )


class ExportDataSource(BaseModel):
    """Represents a complete data source definition for export.

    Contains all configuration and metadata for a data source, including
    chunking settings, database configuration, and associated files.

    Attributes:
        id: The unique identifier of the data source
        name: Optional name of the data source
        execution_name: Optional execution name for programmatic access
        chunking_config: The chunking configuration for document processing
        data_source_type: The type of data source (file, database, etc.)
        database_type: The database type for storage
        embedding_provider: The provider for text embeddings
        is_user_specific: Whether the data source is user-specific
        files: Optional list of files associated with the data source
        file_count: Optional count of files in the data source
        configuration_json: Optional JSON configuration string
        credentials: Optional credential information for access
        is_image_processing_enabled: Whether image processing is enabled
    """
    id: str = Field(..., description="Gets the id.")
    name: Optional[str] = Field(None, description="Gets the Name.")
    execution_name: Optional[str] = Field(
        None,
        description="Gets or sets the execution name of the datasource.",
        alias="executionName",
    )
    chunking_config: ExportChunkingConfig = Field(
        ..., description="Gets the chunking config.", alias="chunkingConfig"
    )
    data_source_type: str = Field(
        ..., description="Gets the data source type.", alias="dataSourceType"
    )
    database_type: str = Field(
        ..., description="Gets the database type.", alias="databaseType"
    )
    embedding_provider: str = Field(
        ..., description="Gets the Embedding provider type.", alias="embeddingProvider"
    )
    is_user_specific: bool = Field(
        ...,
        description="Gets or sets a value indicating whether defines if a Data Source is user specific.",
        alias="isUserSpecific",
    )
    files: Optional[List[ExportDataSourceFile]] = Field(
        None,
        description="Gets or sets the collection of files associated with this data source.",
    )
    file_count: Optional[int] = Field(
        None, description="Gets the file count.", alias="fileCount"
    )
    configuration_json: Optional[str] = Field(
        None,
        description="Gets or sets the configuration json.",
        alias="configurationJson",
    )
    credentials: Optional[ExportCredentials] = Field(
        None, description="Gets or sets the Credentials."
    )
    is_image_processing_enabled: bool = Field(
        ...,
        description="Gets or sets a value indicating whether the image processing is enabled.",
        alias="isImageProcessingEnabled",
    )


class ExportPromptMessageList(BaseModel):
    """Represents a single message within a prompt sequence.

    Defines individual messages that make up a prompt, including
    content and ordering information.

    Attributes:
        text: The content of the message
        order: The order of this message in the prompt sequence
    """
    text: str = Field(..., description="Gets or sets the text.")
    order: int = Field(..., description="Gets or sets the order.")


class ExportPrompt(BaseModel):
    """Represents a complete prompt definition for export.

    Contains all information for a prompt including name, version information,
    and the sequence of messages that make up the prompt.

    Attributes:
        name: The name of the prompt
        version_change_description: Description of changes in this version
        prompt_message_list: List of messages that make up the prompt
        id: The unique identifier of the prompt
    """
    name: str = Field(..., description="Gets or sets the name.")
    version_change_description: str = Field(
        ...,
        description="Gets or sets the version change description.",
        alias="versionChangeDescription",
    )
    prompt_message_list: List[ExportPromptMessageList] = Field(
        ...,
        description="Gets or sets the prompt message list.",
        alias="promptMessageList",
    )
    id: str = Field(..., description="Gets or sets the ID.")


class ExportToolHeaders(BaseModel):
    """Represents HTTP headers for tool API calls.

    Defines key-value pairs for HTTP headers used when making
    API calls to external tools.

    Attributes:
        key: The header name
        value: The header value
    """
    key: str = Field(..., description="Gets or sets the key of the header.")
    value: str = Field(..., description="Gets or sets the value of the header.")


class ExportToolParameters(BaseModel):
    """Represents a parameter definition for external tools.

    Defines input parameters for external tools including type,
    description, default values, and validation options.

    Attributes:
        name: The parameter name
        parameter_type: The data type of the parameter
        parameter_description: Description of the parameter's purpose
        default: The default value for the parameter
        valid_options: Optional list of valid values for the parameter
        id: The unique identifier of the parameter
    """
    name: str = Field(..., description="Gets or sets the name.")
    parameter_type: str = Field(
        ..., description="Gets or sets the type.", alias="parameterType"
    )
    parameter_description: str = Field(
        ..., description="Gets or sets the description.", alias="parameterDescription"
    )
    default: str = Field(..., description="Gets or sets the default value.")
    valid_options: Optional[List[str]] = Field(
        None,
        description="Gets or sets the list of valid options.",
        alias="validOptions",
    )
    id: str = Field(..., description="Gets or sets the ID.")


class ExportTool(BaseModel):
    """Represents a complete external tool definition for export.

    Contains all configuration and metadata for an external tool,
    including API endpoints, authentication, and parameter definitions.

    Attributes:
        tool_type: The type of tool (native, external, etc.)
        name: The name of the tool
        standardized_name: The standardized name for the tool
        tool_description: Description of the tool's functionality
        purpose: The purpose or use case for the tool
        api_endpoint: The API endpoint URL for the tool
        credentials_definition: Optional credential requirements
        headers_definition: Optional HTTP headers for API calls
        body: Optional request body template
        parameters_definition: Optional parameter definitions
        method_type: The HTTP method type (GET, POST, etc.)
        route_through_acc: Whether to route through the Access Control Center
        use_user_credentials: Whether to use user-specific credentials
        use_user_credentials_type: The type of user credentials to use
        id: The unique identifier of the tool
    """
    tool_type: str = Field(
        ...,
        description="Gets or sets a value indicating whether flag that indicates if the tool is native.",
        alias="toolType",
    )
    name: str = Field(..., description="Gets or sets the name.")
    standardized_name: str = Field(
        ..., description="Gets or sets the standardized name.", alias="standardizedName"
    )
    tool_description: str = Field(
        ..., description="Gets or sets the description.", alias="toolDescription"
    )
    purpose: str = Field(..., description="Gets or sets the purpose.")
    api_endpoint: str = Field(
        ..., description="Gets or sets the API endpoint.", alias="apiEndpoint"
    )
    credentials_definition: Optional[ExportCredentials] = Field(
        None,
        description="Gets or sets the authentication.",
        alias="credentialsDefinition",
    )
    headers_definition: Optional[List[ExportToolHeaders]] = Field(
        None, description="Gets or sets the headers.", alias="headersDefinition"
    )
    body: Optional[str] = Field(None, description="Gets or sets the body.")
    parameters_definition: Optional[List[ExportToolParameters]] = Field(
        None, description="Gets or sets the parameters.", alias="parametersDefinition"
    )
    method_type: str = Field(
        ..., description="Gets or sets the method type.", alias="methodType"
    )
    route_through_acc: bool = Field(
        ...,
        description="Gets or sets a value indicating whether the tool should route through the ACC.",
        alias="routeThroughACC",
    )
    use_user_credentials: bool = Field(
        ...,
        description="Gets or sets a value indicating whether the tool should use user based credentials.",
        alias="useUserCredentials",
    )
    use_user_credentials_type: str = Field(
        ...,
        description="Gets or sets a value indicating what the credential type is when the tool use user based credentials.",
        alias="useUserCredentialsType",
    )
    id: str = Field(..., description="Gets or sets the ID.")


class ExportModel(BaseModel):
    """Represents a complete AI model definition for export.

    Contains all configuration and metadata for an AI model,
    including deployment settings, pricing, and capability information.

    Attributes:
        id: The unique identifier of the model
        display_name: The human-readable name for display
        model_name: Optional internal model name
        prompt_id: Optional ID of the associated system prompt
        system_prompt_definition: Optional system prompt definition
        url: Optional API endpoint URL for the model
        input_type: The type of input the model accepts
        provider: The AI provider (OpenAI, Anthropic, etc.)
        credentials_definition: Optional credential requirements
        deployment_type: The deployment type (cloud, on-premises, etc.)
        source_type: The source type of the model
        connection_string: Optional connection string for deployment
        container_name: Optional container name for deployment
        deployed_key: Optional deployment key
        deployed_url: Optional deployed URL
        state: Optional current state of the model
        uploaded_container_id: Optional ID of uploaded container
        library_model_id: Optional ID of the library model
        input_token_price: Optional pricing for input tokens
        output_token_price: Optional pricing for output tokens
        token_units: Optional token unit multiplier
        has_tool_support: Whether the model supports tool calling
        allow_airia_credentials: Whether to allow Airia-provided credentials
        allow_byok_credentials: Whether to allow bring-your-own-key credentials
        author: Optional author information
        price_type: The pricing model type
    """
    id: str = Field(..., description="Gets or sets the ID.")
    display_name: str = Field(
        ..., description="Gets or sets the display name.", alias="displayName"
    )
    model_name: Optional[str] = Field(
        None, description="Gets or sets the model name.", alias="modelName"
    )
    prompt_id: Optional[str] = Field(
        None, description="Gets or sets the prompt ID.", alias="promptId"
    )
    system_prompt_definition: Optional[ExportPrompt] = Field(
        None,
        description="Gets or sets the system prompt.",
        alias="systemPromptDefinition",
    )
    url: Optional[str] = Field(None, description="Gets or sets the URL.")
    input_type: str = Field(
        ..., description="Gets or sets the type.", alias="inputType"
    )
    provider: str = Field(..., description="Gets or sets the provider.")
    credentials_definition: Optional[ExportCredentials] = Field(
        None, description="Gets or sets the credentials.", alias="credentialsDefinition"
    )
    deployment_type: str = Field(
        ..., description="Gets or sets the deployment type.", alias="deploymentType"
    )
    source_type: str = Field(
        ..., description="Gets or sets the source type.", alias="sourceType"
    )
    connection_string: Optional[str] = Field(
        None,
        description="Gets or sets the connection string.",
        alias="connectionString",
    )
    container_name: Optional[str] = Field(
        None, description="Gets or sets the container name.", alias="containerName"
    )
    deployed_key: Optional[str] = Field(
        None, description="Gets or sets the deployed key.", alias="deployedKey"
    )
    deployed_url: Optional[str] = Field(
        None, description="Gets or sets the deployed URL.", alias="deployedUrl"
    )
    state: Optional[str] = Field(None, description="Gets or sets the state.")
    uploaded_container_id: Optional[str] = Field(
        None,
        description="Gets or sets the uploaded container ID.",
        alias="uploadedContainerId",
    )
    library_model_id: Optional[str] = Field(
        None, description="Gets or sets the library model ID.", alias="libraryModelId"
    )
    input_token_price: Optional[str] = Field(
        None, description="Gets or sets the input token price.", alias="inputTokenPrice"
    )
    output_token_price: Optional[str] = Field(
        None,
        description="Gets or sets the output token price.",
        alias="outputTokenPrice",
    )
    token_units: Optional[int] = Field(
        None, description="Gets or sets the token units.", alias="tokenUnits"
    )
    has_tool_support: bool = Field(
        ...,
        description="Gets or sets a value indicating whether the model has tool support.",
        alias="hasToolSupport",
    )
    allow_airia_credentials: bool = Field(
        ...,
        description="Gets or sets a value indicating whether to allow Airia credentials.",
        alias="allowAiriaCredentials",
    )
    allow_byok_credentials: bool = Field(
        ...,
        description="Gets or sets a value indicating whether to allow BYOK credentials.",
        alias="allowBYOKCredentials",
    )
    author: Optional[str] = Field(None, description="Gets or sets the author.")
    price_type: str = Field(
        ..., description="Gets or sets the price type.", alias="priceType"
    )


class ExportMemory(BaseModel):
    """Represents a memory definition for export.

    Defines persistent memory storage for maintaining context
    and state across pipeline executions.

    Attributes:
        id: The unique identifier of the memory
        name: The name of the memory
        is_user_specific: Whether the memory is specific to individual users
    """
    id: str = Field(..., description="Gets or sets the memory id.")
    name: str = Field(..., description="Gets or sets the memory name.")
    is_user_specific: bool = Field(
        ...,
        description="Gets or sets a value indicating whether the memory is user specific.",
        alias="isUserSpecific",
    )


class ExportPythonCodeBlock(BaseModel):
    """Represents a Python code block for export.

    Defines executable Python code that can be used within
    pipeline steps for custom processing logic.

    Attributes:
        id: The unique identifier of the code block
        code: The Python code content
    """
    id: str = Field(..., description="Gets or sets the memory id.")
    code: str = Field(..., description="Gets or sets the code.")


class ExportRouterConfig(BaseModel):
    """Represents router configuration for conditional execution.

    Defines routing rules and conditions for directing pipeline
    execution flow based on content analysis.

    Attributes:
        id: The unique identifier of the router configuration
        prompt: The prompt used for routing decisions
        is_default: Whether this is the default routing option
    """
    id: str = Field(..., description="Gets or sets the Id.")
    prompt: str = Field(..., description="Gets or sets the Prompt.")
    is_default: Optional[bool] = Field(
        None,
        description="Gets or sets a value indicating whether this is a default route.",
        alias="isDefault",
    )


class ExportRouter(BaseModel):
    """Represents a complete router definition for export.

    Contains all configuration for intelligent routing of pipeline
    execution based on content analysis and decision logic.

    Attributes:
        id: The unique identifier of the router
        model_id: Optional ID of the model used for routing decisions
        model: Optional AI model definition for routing
        router_config: Dictionary of routing configurations
    """
    id: str = Field(..., description="Gets or sets the Router identifier.")
    model_id: Optional[str] = Field(
        None, description="Gets or sets the Model identifier.", alias="modelId"
    )
    model: Optional[ExportModel] = Field(None, description="Gets or sets the AI Model.")
    router_config: Dict[str, ExportRouterConfig] = Field(
        ..., description="Gets or sets the Router Configuration.", alias="routerConfig"
    )


class ExportUserPrompt(BaseModel):
    """Represents a user prompt template for export.

    Defines predefined prompts that users can select from
    when interacting with deployed pipelines.

    Attributes:
        name: The name of the user prompt
        message: The prompt message content
        prompt_description: Description of the prompt's purpose
    """
    name: str = Field(..., description="Gets or sets the name of the UserPrompt.")
    message: str = Field(..., description="Gets or sets the UserPrompt Message.")
    prompt_description: str = Field(
        ...,
        description="Gets or sets the UserPrompt Description.",
        alias="promptDescription",
    )


class ExportDeployment(BaseModel):
    """Represents a deployment configuration for export.

    Contains all settings for deploying a pipeline to end users,
    including branding, user prompts, and access controls.

    Attributes:
        name: The name of the deployment
        deployment_icon: Optional base64-encoded icon for the deployment
        deployment_description: Description of the deployment's purpose
        user_prompts: Optional list of predefined user prompts
        deployment_prompt: Optional hardcoded system prompt
        is_recommended: Whether this is a featured/recommended deployment
        tags: Optional list of tags for categorization
        deployment_type: The type of deployment
        conversation_type: The type of conversation interface
        about_json: Optional JSON metadata about the deployment
    """
    name: str = Field(..., description="Gets the Deployment Name.")
    deployment_icon: Optional[str] = Field(
        None, description="Gets the Deployment Icon.", alias="deploymentIcon"
    )
    deployment_description: str = Field(
        ...,
        description="Gets the description of the deployment.",
        alias="deploymentDescription",
    )
    user_prompts: Optional[List[ExportUserPrompt]] = Field(
        None, description="Gets the DeploymentUserPrompts.", alias="userPrompts"
    )
    deployment_prompt: Optional[str] = Field(
        None,
        description="Gets the DeploymentPrompt. Optional hardcoded prompt.",
        alias="deploymentPrompt",
    )
    is_recommended: bool = Field(
        ...,
        description="Gets a value indicating whether this is a recommended/featured deployment.",
        alias="isRecommended",
    )
    tags: Optional[List[str]] = Field(None, description="Gets the Tags.")
    deployment_type: str = Field(
        ..., description="Gets the deployment type.", alias="deploymentType"
    )
    conversation_type: str = Field(
        ..., description="Gets the conversation type.", alias="conversationType"
    )
    about_json: Optional[str] = Field(
        None,
        description="Gets information about the deployment. This is a json value.",
        alias="aboutJson",
    )


class ExportMetadata(BaseModel):
    """Represents metadata for pipeline export operations.

    Contains versioning, description, and export configuration
    information for pipeline import/export operations.

    Attributes:
        id: The unique identifier of the export metadata
        export_version: Optional version timestamp for the export
        tagline: A brief tagline describing the pipeline
        agent_description: Detailed description of the agent
        industry: The primary industry served
        tasks: Description of tasks the pipeline performs
        credential_export_option: How credentials are handled in export
        data_source_export_option: How data sources are handled in export
        version_information: Information about the pipeline version
        state: The current state of the agent
    """
    id: str = Field(..., description="Gets or sets the id.")
    export_version: Optional[str] = Field(
        None,
        description="Gets or sets the export version (EF Migration timestamp).",
        alias="exportVersion",
    )
    tagline: str = Field(..., description="Gets or sets the tag line.")
    agent_description: str = Field(
        ..., description="Gets or sets the name.", alias="agentDescription"
    )
    industry: str = Field(..., description="Gets or sets the industry.")
    tasks: str = Field(..., description="Gets or sets the tasks.")
    credential_export_option: str = Field(
        ...,
        description="Gets or sets the credential export option.",
        alias="credentialExportOption",
    )
    data_source_export_option: str = Field(
        ...,
        description="Gets or sets the data source export option.",
        alias="dataSourceExportOption",
    )
    version_information: str = Field(
        ...,
        description="Gets or sets the version information.",
        alias="versionInformation",
    )
    state: str = Field(..., description="Gets or sets the state of the agent.")


class ExportPipelineDefinitionResponse(BaseModel):
    """Represents the complete response for pipeline export operations.

    The main response object containing all components of a pipeline export,
    including the pipeline definition, associated resources, and metadata.

    Attributes:
        metadata: Export metadata and configuration information
        agent: The main pipeline definition and configuration
        data_sources: Optional list of data sources used by the pipeline
        prompts: Optional list of prompts used by the pipeline
        tools: Optional list of external tools used by the pipeline
        models: Optional list of AI models used by the pipeline
        memories: Optional list of memory definitions used by the pipeline
        python_code_blocks: Optional list of Python code blocks used by the pipeline
        routers: Optional list of router configurations used by the pipeline
        deployment: Optional deployment configuration for the pipeline
    """
    metadata: ExportMetadata = Field(..., description="Gets or sets the Metadata.")
    agent: ExportPipeline = Field(..., description="Gets or sets the pipeline.")
    data_sources: Optional[List[ExportDataSource]] = Field(
        None, description="Gets or sets the Steps.", alias="dataSources"
    )
    prompts: Optional[List[ExportPrompt]] = Field(
        None, description="Gets or sets the Prompt."
    )
    tools: Optional[List[ExportTool]] = Field(
        None, description="Gets or sets the Tools."
    )
    models: Optional[List[ExportModel]] = Field(
        None, description="Gets or sets the Models."
    )
    memories: Optional[List[ExportMemory]] = Field(
        None, description="Gets or sets the Memories."
    )
    python_code_blocks: Optional[List[ExportPythonCodeBlock]] = Field(
        None, description="Gets or sets the code blocks.", alias="pythonCodeBlocks"
    )
    routers: Optional[List[ExportRouter]] = Field(
        None, description="Gets or sets the Routers."
    )
    deployment: Optional[ExportDeployment] = Field(
        None, description="Gets or sets the deployment."
    )
