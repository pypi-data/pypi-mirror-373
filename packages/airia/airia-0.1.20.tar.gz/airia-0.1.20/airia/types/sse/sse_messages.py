"""
Server-Sent Event (SSE) message types and models for the Airia API.

This module defines all possible SSE message types that can be received during
pipeline execution, including agent lifecycle events, processing steps, model
streaming, and tool execution messages.
"""

from datetime import datetime, time
from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict


class MessageType(str, Enum):
    """
    Enumeration of all possible SSE message types from the Airia API.

    These message types correspond to different events that occur during
    pipeline execution, agent processing, and streaming responses.

    Attributes:
        AGENT_PING: Ping message sent periodically to maintain connection health.
        AGENT_START: Message indicating that an agent has started processing.
        AGENT_INPUT: Message indicating that an agent has received input to process.
        AGENT_END: Message indicating that an agent has finished processing.
        AGENT_STEP_START: Message indicating that a processing step has started.
        AGENT_STEP_HALT: Message indicating that a step has been halted pending approval.
        AGENT_STEP_END: Message indicating that a processing step has completed.
        AGENT_OUTPUT: Message containing the output result from a completed step.
        AGENT_AGENT_CARD: Message indicating that an agent card step is being processed.
        AGENT_DATASEARCH: Message indicating that data source search is being performed.
        AGENT_INVOCATION: Message indicating that another agent is being invoked.
        AGENT_MODEL: Message indicating that a language model is being called.
        AGENT_PYTHON_CODE: Message indicating that Python code execution is taking place.
        AGENT_TOOL_ACTION: Message indicating that a tool or external service is being called.
        AGENT_MODEL_STREAM_START: Message indicating that model text streaming has begun.
        AGENT_MODEL_STREAM_END: Message indicating that model text streaming has completed.
        AGENT_MODEL_STREAM_ERROR: Message indicating that an error occurred during model streaming.
        AGENT_MODEL_STREAM_USAGE: Message containing token usage and cost information for model calls.
        AGENT_MODEL_STREAM_FRAGMENT: Fragment of streaming text content from a language model.
        MODEL_STREAM_FRAGMENT: Alternative fragment message type for model streaming.
        AGENT_AGENT_CARD_STREAM_START: Message indicating that agent card streaming has begun.
        AGENT_AGENT_CARD_STREAM_ERROR: Message indicating that an error occurred during agent card streaming.
        AGENT_AGENT_CARD_STREAM_FRAGMENT: Fragment of streaming agent card content.
        AGENT_AGENT_CARD_STREAM_END: Message indicating that agent card streaming has completed.
        AGENT_TOOL_REQUEST: Message indicating that a tool request has been initiated.
        AGENT_TOOL_RESPONSE: Message indicating that a tool request has completed.
    """

    AGENT_PING: str = "AgentPingMessage"
    AGENT_START: str = "AgentStartMessage"
    AGENT_INPUT: str = "AgentInputMessage"
    AGENT_END: str = "AgentEndMessage"
    AGENT_STEP_START: str = "AgentStepStartMessage"
    AGENT_STEP_HALT: str = "AgentStepHaltMessage"
    AGENT_STEP_END: str = "AgentStepEndMessage"
    AGENT_OUTPUT: str = "AgentOutputMessage"
    AGENT_AGENT_CARD: str = "AgentAgentCardMessage"
    AGENT_DATASEARCH: str = "AgentDatasearchMessage"
    AGENT_INVOCATION: str = "AgentInvocationMessage"
    AGENT_MODEL: str = "AgentModelMessage"
    AGENT_PYTHON_CODE: str = "AgentPythonCodeMessage"
    AGENT_TOOL_ACTION: str = "AgentToolActionMessage"
    AGENT_MODEL_STREAM_START: str = "AgentModelStreamStartMessage"
    AGENT_MODEL_STREAM_END: str = "AgentModelStreamEndMessage"
    AGENT_MODEL_STREAM_ERROR: str = "AgentModelStreamErrorMessage"
    AGENT_MODEL_STREAM_USAGE: str = "AgentModelStreamUsageMessage"
    AGENT_MODEL_STREAM_FRAGMENT: str = "AgentModelStreamFragmentMessage"
    MODEL_STREAM_FRAGMENT: str = "ModelStreamFragment"
    AGENT_AGENT_CARD_STREAM_START: str = "AgentAgentCardStreamStartMessage"
    AGENT_AGENT_CARD_STREAM_ERROR: str = "AgentAgentCardStreamErrorMessage"
    AGENT_AGENT_CARD_STREAM_FRAGMENT: str = "AgentAgentCardStreamFragmentMessage"
    AGENT_AGENT_CARD_STREAM_END: str = "AgentAgentCardStreamEndMessage"
    AGENT_TOOL_REQUEST: str = "AgentToolRequestMessage"
    AGENT_TOOL_RESPONSE: str = "AgentToolResponseMessage"


class BaseSSEMessage(BaseModel):
    """
    Base class for all Server-Sent Event (SSE) messages from the Airia API.

    All SSE messages include a message_type field that identifies the specific
    type of event being reported.

    Attributes:
        message_type: The type of SSE message, identifying the specific event being reported.
    """

    model_config = ConfigDict(use_enum_values=True)
    message_type: MessageType


class AgentPingMessage(BaseSSEMessage):
    """
    Ping message sent periodically to maintain connection health.

    These messages help verify that the connection is still active during
    long-running pipeline executions.

    Attributes:
        message_type: Always set to AGENT_PING for ping messages.
        timestamp: The time when the ping message was sent.
    """

    message_type: MessageType = MessageType.AGENT_PING
    timestamp: datetime


### Agent Messages ###


class BaseAgentMessage(BaseSSEMessage):
    """
    Base class for messages related to agent execution.

    All agent messages include identifiers for the specific agent
    and execution session.

    Attributes:
        agent_id: Unique identifier for the agent generating this message.
        execution_id: Unique identifier for the current execution session.
    """

    agent_id: str
    execution_id: str


class AgentStartMessage(BaseAgentMessage):
    """
    Message indicating that an agent has started processing.

    Attributes:
        message_type: Always set to AGENT_START for agent start messages.
        agent_id: Unique identifier for the agent that started.
        execution_id: Unique identifier for the execution session.
    """

    message_type: MessageType = MessageType.AGENT_START


class AgentInputMessage(BaseAgentMessage):
    """
    Message indicating that an agent has received input to process.

    Attributes:
        message_type: Always set to AGENT_INPUT for agent input messages.
        agent_id: Unique identifier for the agent receiving input.
        execution_id: Unique identifier for the execution session.
    """

    message_type: MessageType = MessageType.AGENT_INPUT


class AgentEndMessage(BaseAgentMessage):
    """
    Message indicating that an agent has finished processing.

    Attributes:
        message_type: Always set to AGENT_END for agent end messages.
        agent_id: Unique identifier for the agent that finished.
        execution_id: Unique identifier for the execution session.
    """

    message_type: MessageType = MessageType.AGENT_END


### Step Messages ###


class BaseStepMessage(BaseAgentMessage):
    """
    Base class for messages related to individual processing steps within an agent.

    Steps represent discrete operations or tasks that an agent performs
    as part of its overall processing workflow.

    Attributes:
        agent_id: Unique identifier for the agent performing the step.
        execution_id: Unique identifier for the execution session.
        step_id: Unique identifier for the processing step.
        step_type: The type/category of the processing step.
        step_title: Optional human-readable title for the step.
    """

    step_id: str
    step_type: str
    step_title: Optional[str] = None


class AgentStepStartMessage(BaseStepMessage):
    """
    Message indicating that a processing step has started.

    Attributes:
        message_type: Always set to AGENT_STEP_START for step start messages.
        agent_id: Unique identifier for the agent performing the step.
        execution_id: Unique identifier for the execution session.
        step_id: Unique identifier for the processing step that started.
        step_type: The type/category of the processing step.
        step_title: Optional human-readable title for the step.
        start_time: The timestamp when the step began execution.
    """

    message_type: MessageType = MessageType.AGENT_STEP_START
    start_time: datetime


class AgentStepHaltMessage(BaseStepMessage):
    """
    Message indicating that a step has been halted pending approval.

    This occurs when human approval is required before proceeding
    with potentially sensitive or high-impact operations.

    Attributes:
        message_type: Always set to AGENT_STEP_HALT for step halt messages.
        agent_id: Unique identifier for the agent performing the step.
        execution_id: Unique identifier for the execution session.
        step_id: Unique identifier for the processing step that was halted.
        step_type: The type/category of the processing step.
        step_title: Optional human-readable title for the step.
        approval_id: Unique identifier for the approval request.
    """

    message_type: MessageType = MessageType.AGENT_STEP_HALT
    approval_id: str


class AgentStepEndMessage(BaseStepMessage):
    """
    Message indicating that a processing step has completed.

    Includes timing information and the final status of the step.

    Attributes:
        message_type: Always set to AGENT_STEP_END for step end messages.
        agent_id: Unique identifier for the agent performing the step.
        execution_id: Unique identifier for the execution session.
        step_id: Unique identifier for the processing step that ended.
        step_type: The type/category of the processing step.
        step_title: Optional human-readable title for the step.
        end_time: The timestamp when the step completed execution.
        duration: The total time the step took to execute.
        status: The final status of the step (e.g., 'success', 'failed').
    """

    message_type: MessageType = MessageType.AGENT_STEP_END
    end_time: datetime
    duration: time
    status: str


class AgentOutputMessage(BaseStepMessage):
    """
    Message containing the output result from a completed step.

    Attributes:
        message_type: Always set to AGENT_OUTPUT for output messages.
        agent_id: Unique identifier for the agent that produced the output.
        execution_id: Unique identifier for the execution session.
        step_id: Unique identifier for the processing step that generated output.
        step_type: The type/category of the processing step.
        step_title: Optional human-readable title for the step.
        step_result: The output result or content from the completed step.
    """

    message_type: MessageType = MessageType.AGENT_OUTPUT
    step_result: str


### Status Messages ###


class BaseStatusMessage(BaseStepMessage):
    """
    Base class for status update messages within processing steps.

    Status messages provide real-time updates about what operations
    are being performed during step execution.

    Attributes:
        agent_id: Unique identifier for the agent performing the step.
        execution_id: Unique identifier for the execution session.
        step_id: Unique identifier for the processing step.
        step_type: The type/category of the processing step.
        step_title: Optional human-readable title for the step.
    """

    pass


class AgentAgentCardMessage(BaseStatusMessage):
    """
    Message indicating that an agent card step is being processed.

    Agent cards represent interactive UI components or displays
    that provide rich information to users during pipeline execution.

    Attributes:
        message_type: Always set to AGENT_AGENT_CARD for agent card messages.
        agent_id: Unique identifier for the agent processing the card.
        execution_id: Unique identifier for the execution session.
        step_id: Unique identifier for the processing step.
        step_type: The type/category of the processing step.
        step_title: Optional human-readable title for the step.
        step_name: The name of the agent card step being processed.
    """

    message_type: MessageType = MessageType.AGENT_AGENT_CARD
    step_name: str


class AgentDatasearchMessage(BaseStatusMessage):
    """
    Message indicating that data source search is being performed.

    This message is sent when an agent is querying or searching
    through configured data sources to retrieve relevant information.

    Attributes:
        message_type: Always set to AGENT_DATASEARCH for data search messages.
        agent_id: Unique identifier for the agent performing the search.
        execution_id: Unique identifier for the execution session.
        step_id: Unique identifier for the processing step.
        step_type: The type/category of the processing step.
        step_title: Optional human-readable title for the step.
        datastore_id: Unique identifier for the data source being searched.
        datastore_type: The type of data source (e.g., 'database', 'file', 'api').
        datastore_name: Human-readable name of the data source.
    """

    message_type: MessageType = MessageType.AGENT_DATASEARCH
    datastore_id: str
    datastore_type: str
    datastore_name: str


class AgentInvocationMessage(BaseStatusMessage):
    """
    Message indicating that another agent is being invoked.

    This occurs when the current agent calls or delegates work
    to another specialized agent in the pipeline.

    Attributes:
        message_type: Always set to AGENT_INVOCATION for agent invocation messages.
        agent_id: Unique identifier for the agent making the invocation.
        execution_id: Unique identifier for the execution session.
        step_id: Unique identifier for the processing step.
        step_type: The type/category of the processing step.
        step_title: Optional human-readable title for the step.
        agent_name: The name of the agent being invoked.
    """

    message_type: MessageType = MessageType.AGENT_INVOCATION
    agent_name: str


class AgentModelMessage(BaseStatusMessage):
    """
    Message indicating that a language model is being called.

    This message is sent when an agent begins interacting with
    a language model for text generation or processing.

    Attributes:
        message_type: Always set to AGENT_MODEL for model messages.
        agent_id: Unique identifier for the agent calling the model.
        execution_id: Unique identifier for the execution session.
        step_id: Unique identifier for the processing step.
        step_type: The type/category of the processing step.
        step_title: Optional human-readable title for the step.
        model_name: The name of the language model being called.
    """

    message_type: MessageType = MessageType.AGENT_MODEL
    model_name: str


class AgentPythonCodeMessage(BaseStatusMessage):
    """
    Message indicating that Python code execution is taking place.

    This message is sent when an agent executes custom Python code
    blocks as part of its processing workflow.

    Attributes:
        message_type: Always set to AGENT_PYTHON_CODE for Python code messages.
        agent_id: Unique identifier for the agent executing the code.
        execution_id: Unique identifier for the execution session.
        step_id: Unique identifier for the processing step.
        step_type: The type/category of the processing step.
        step_title: Optional human-readable title for the step.
        step_name: The name of the Python code step being executed.
    """

    message_type: MessageType = MessageType.AGENT_PYTHON_CODE
    step_name: str


class AgentToolActionMessage(BaseStatusMessage):
    """
    Message indicating that a tool or external service is being called.

    This message is sent when an agent invokes an external tool,
    API, or service to perform a specific action or retrieve data.

    Attributes:
        message_type: Always set to AGENT_TOOL_ACTION for tool action messages.
        agent_id: Unique identifier for the agent calling the tool.
        execution_id: Unique identifier for the execution session.
        step_id: Unique identifier for the processing step.
        step_type: The type/category of the processing step.
        step_title: Optional human-readable title for the step.
        step_name: The name of the tool action step being performed.
        tool_name: The name of the external tool being called.
    """

    message_type: MessageType = MessageType.AGENT_TOOL_ACTION
    step_name: str
    tool_name: str


### Model Stream Messages ###


class BaseModelStreamMessage(BaseAgentMessage):
    """
    Base class for language model streaming messages.

    Model streaming allows real-time display of text generation
    as it occurs, providing better user experience for long responses.

    Attributes:
        agent_id: Unique identifier for the agent performing the streaming.
        execution_id: Unique identifier for the execution session.
        step_id: Unique identifier for the processing step.
        stream_id: Unique identifier for the streaming session.
    """

    step_id: str
    stream_id: str


class AgentModelStreamStartMessage(BaseModelStreamMessage):
    """
    Message indicating that model text streaming has begun.

    Attributes:
        message_type: Always set to AGENT_MODEL_STREAM_START for stream start messages.
        agent_id: Unique identifier for the agent performing the streaming.
        execution_id: Unique identifier for the execution session.
        step_id: Unique identifier for the processing step.
        stream_id: Unique identifier for the streaming session.
        model_name: The name of the language model being streamed.
    """

    message_type: MessageType = MessageType.AGENT_MODEL_STREAM_START
    model_name: str


class AgentModelStreamErrorMessage(BaseModelStreamMessage):
    """
    Message indicating that an error occurred during model streaming.

    Attributes:
        message_type: Always set to AGENT_MODEL_STREAM_ERROR for stream error messages.
        agent_id: Unique identifier for the agent performing the streaming.
        execution_id: Unique identifier for the execution session.
        step_id: Unique identifier for the processing step.
        stream_id: Unique identifier for the streaming session.
        error_message: Description of the error that occurred during streaming.
    """

    message_type: MessageType = MessageType.AGENT_MODEL_STREAM_ERROR
    error_message: str


class AgentModelStreamFragmentMessage(BaseModelStreamMessage):
    """
    Fragment of streaming text content from a language model.

    These messages contain individual chunks of text as they are generated
    by the model, allowing for real-time display of results.

    Attributes:
        message_type: Always set to AGENT_MODEL_STREAM_FRAGMENT for fragment messages.
        agent_id: Unique identifier for the agent performing the streaming.
        execution_id: Unique identifier for the execution session.
        step_id: Unique identifier for the processing step.
        stream_id: Unique identifier for the streaming session.
        index: The sequential index of this fragment within the stream.
        content: The text content of this fragment, or None if no content.
    """

    message_type: MessageType = MessageType.AGENT_MODEL_STREAM_FRAGMENT
    index: int
    content: Optional[str] = None


class AgentModelStreamEndMessage(BaseModelStreamMessage):
    """
    Message indicating that model text streaming has completed.

    Attributes:
        message_type: Always set to AGENT_MODEL_STREAM_END for stream end messages.
        agent_id: Unique identifier for the agent performing the streaming.
        execution_id: Unique identifier for the execution session.
        step_id: Unique identifier for the processing step.
        stream_id: Unique identifier for the streaming session.
        content_id: Unique identifier for the generated content.
        duration: Optional duration of the streaming session in seconds.
    """

    message_type: MessageType = MessageType.AGENT_MODEL_STREAM_END
    content_id: str
    duration: Optional[float] = None


class AgentModelStreamUsageMessage(BaseModelStreamMessage):
    """
    Message containing token usage and cost information for model calls.

    Attributes:
        message_type: Always set to AGENT_MODEL_STREAM_USAGE for usage messages.
        agent_id: Unique identifier for the agent performing the streaming.
        execution_id: Unique identifier for the execution session.
        step_id: Unique identifier for the processing step.
        stream_id: Unique identifier for the streaming session.
        token: Optional number of tokens used during the model call.
        tokens_cost: Optional cost in dollars for the tokens used.
    """

    message_type: MessageType = MessageType.AGENT_MODEL_STREAM_USAGE
    token: Optional[int] = None
    tokens_cost: Optional[float] = None


### Agent Card Messages ###


class BaseAgentAgentCardStreamMessage(BaseAgentMessage):
    """
    Base class for agent card streaming messages.

    Agent card streaming allows real-time updates to interactive
    UI components during their generation or processing.

    Attributes:
        agent_id: Unique identifier for the agent performing the streaming.
        execution_id: Unique identifier for the execution session.
        step_id: Unique identifier for the processing step.
        stream_id: Unique identifier for the streaming session.
    """

    step_id: str
    stream_id: str


class AgentAgentCardStreamStartMessage(BaseAgentAgentCardStreamMessage):
    """
    Message indicating that agent card streaming has begun.

    Attributes:
        message_type: Always set to AGENT_AGENT_CARD_STREAM_START for card stream start messages.
        agent_id: Unique identifier for the agent performing the streaming.
        execution_id: Unique identifier for the execution session.
        step_id: Unique identifier for the processing step.
        stream_id: Unique identifier for the streaming session.
        content: Optional initial content for the agent card.
    """

    message_type: MessageType = MessageType.AGENT_AGENT_CARD_STREAM_START
    content: Optional[str] = None


class AgentAgentCardStreamErrorMessage(BaseAgentAgentCardStreamMessage):
    """
    Message indicating that an error occurred during agent card streaming.

    Attributes:
        message_type: Always set to AGENT_AGENT_CARD_STREAM_ERROR for card stream error messages.
        agent_id: Unique identifier for the agent performing the streaming.
        execution_id: Unique identifier for the execution session.
        step_id: Unique identifier for the processing step.
        stream_id: Unique identifier for the streaming session.
        error_message: Description of the error that occurred during card streaming.
    """

    message_type: MessageType = MessageType.AGENT_AGENT_CARD_STREAM_ERROR
    error_message: str


class AgentAgentCardStreamFragmentMessage(BaseAgentAgentCardStreamMessage):
    """
    Fragment of streaming agent card content.

    These messages contain individual chunks of agent card data
    as they are generated, allowing for real-time UI updates.

    Attributes:
        message_type: Always set to AGENT_AGENT_CARD_STREAM_FRAGMENT for card fragment messages.
        agent_id: Unique identifier for the agent performing the streaming.
        execution_id: Unique identifier for the execution session.
        step_id: Unique identifier for the processing step.
        stream_id: Unique identifier for the streaming session.
        index: The sequential index of this fragment within the stream.
        content: The card content of this fragment, or None if no content.
    """

    message_type: MessageType = MessageType.AGENT_AGENT_CARD_STREAM_FRAGMENT
    index: int
    content: Optional[str]


class AgentAgentCardStreamEndMessage(BaseAgentAgentCardStreamMessage):
    """
    Message indicating that agent card streaming has completed.

    Attributes:
        message_type: Always set to AGENT_AGENT_CARD_STREAM_END for card stream end messages.
        agent_id: Unique identifier for the agent performing the streaming.
        execution_id: Unique identifier for the execution session.
        step_id: Unique identifier for the processing step.
        stream_id: Unique identifier for the streaming session.
        content: Optional final content for the agent card.
    """

    message_type: MessageType = MessageType.AGENT_AGENT_CARD_STREAM_END
    content: Optional[str] = None


### Tool Messages ###


class BaseAgentToolMessage(BaseStepMessage):
    """
    Base class for tool execution messages.

    Tool messages track the lifecycle of external tool or service
    calls made by agents during pipeline execution.

    Attributes:
        agent_id: Unique identifier for the agent performing the step.
        execution_id: Unique identifier for the execution session.
        step_id: Unique identifier for the processing step.
        step_type: The type/category of the processing step.
        step_title: Optional human-readable title for the step.
        id: Unique identifier for the tool execution.
        name: The name of the tool being executed.
    """

    id: str
    name: str


class AgentToolRequestMessage(BaseAgentToolMessage):
    """
    Message indicating that a tool request has been initiated.

    This message is sent when an agent begins calling an external
    tool or service to perform a specific operation.

    Attributes:
        message_type: Always set to AGENT_TOOL_REQUEST for tool request messages.
        agent_id: Unique identifier for the agent making the tool request.
        execution_id: Unique identifier for the execution session.
        step_id: Unique identifier for the processing step.
        step_type: The type/category of the processing step.
        step_title: Optional human-readable title for the step.
        id: Unique identifier for the tool execution.
        name: The name of the tool being requested.
    """

    message_type: MessageType = MessageType.AGENT_TOOL_REQUEST


class AgentToolResponseMessage(BaseAgentToolMessage):
    """
    Message indicating that a tool request has completed.

    This message contains the results and timing information
    from a completed tool or service call.

    Attributes:
        message_type: Always set to AGENT_TOOL_RESPONSE for tool response messages.
        agent_id: Unique identifier for the agent that made the tool request.
        execution_id: Unique identifier for the execution session.
        step_id: Unique identifier for the processing step.
        step_type: The type/category of the processing step.
        step_title: Optional human-readable title for the step.
        id: Unique identifier for the tool execution.
        name: The name of the tool that was executed.
        duration: The time it took for the tool to complete execution.
        success: Whether the tool execution was successful.
    """

    message_type: MessageType = MessageType.AGENT_TOOL_RESPONSE
    duration: time
    success: bool


# Union type for all possible messages
SSEMessage = Union[
    AgentPingMessage,
    AgentStartMessage,
    AgentInputMessage,
    AgentEndMessage,
    AgentStepStartMessage,
    AgentStepHaltMessage,
    AgentStepEndMessage,
    AgentOutputMessage,
    AgentAgentCardMessage,
    AgentDatasearchMessage,
    AgentInvocationMessage,
    AgentModelMessage,
    AgentPythonCodeMessage,
    AgentToolActionMessage,
    AgentModelStreamStartMessage,
    AgentModelStreamEndMessage,
    AgentModelStreamErrorMessage,
    AgentModelStreamUsageMessage,
    AgentModelStreamFragmentMessage,
    AgentAgentCardStreamStartMessage,
    AgentAgentCardStreamErrorMessage,
    AgentAgentCardStreamFragmentMessage,
    AgentAgentCardStreamEndMessage,
    AgentToolRequestMessage,
    AgentToolResponseMessage,
]
"""Union type representing all possible SSE message types from the Airia API."""

SSEDict = {
    MessageType.AGENT_PING.value: AgentPingMessage,
    MessageType.AGENT_START.value: AgentStartMessage,
    MessageType.AGENT_INPUT.value: AgentInputMessage,
    MessageType.AGENT_END.value: AgentEndMessage,
    MessageType.AGENT_STEP_START.value: AgentStepStartMessage,
    MessageType.AGENT_STEP_HALT.value: AgentStepHaltMessage,
    MessageType.AGENT_STEP_END.value: AgentStepEndMessage,
    MessageType.AGENT_OUTPUT.value: AgentOutputMessage,
    MessageType.AGENT_AGENT_CARD.value: AgentAgentCardMessage,
    MessageType.AGENT_DATASEARCH.value: AgentDatasearchMessage,
    MessageType.AGENT_INVOCATION.value: AgentInvocationMessage,
    MessageType.AGENT_MODEL.value: AgentModelMessage,
    MessageType.AGENT_PYTHON_CODE.value: AgentPythonCodeMessage,
    MessageType.AGENT_TOOL_ACTION.value: AgentToolActionMessage,
    MessageType.AGENT_MODEL_STREAM_START.value: AgentModelStreamStartMessage,
    MessageType.AGENT_MODEL_STREAM_END.value: AgentModelStreamEndMessage,
    MessageType.AGENT_MODEL_STREAM_ERROR.value: AgentModelStreamErrorMessage,
    MessageType.AGENT_MODEL_STREAM_USAGE.value: AgentModelStreamUsageMessage,
    MessageType.AGENT_MODEL_STREAM_FRAGMENT.value: AgentModelStreamFragmentMessage,
    MessageType.AGENT_AGENT_CARD_STREAM_START.value: AgentAgentCardStreamStartMessage,
    MessageType.AGENT_AGENT_CARD_STREAM_ERROR.value: AgentAgentCardStreamErrorMessage,
    MessageType.AGENT_AGENT_CARD_STREAM_FRAGMENT.value: AgentAgentCardStreamFragmentMessage,
    MessageType.AGENT_AGENT_CARD_STREAM_END.value: AgentAgentCardStreamEndMessage,
    MessageType.AGENT_TOOL_REQUEST.value: AgentToolRequestMessage,
    MessageType.AGENT_TOOL_RESPONSE.value: AgentToolResponseMessage,
}
"""
Mapping from message type strings to their corresponding Pydantic model classes.

This dictionary is used by the SSE parser to instantiate the correct message
type based on the 'event' field in incoming SSE data.
"""
