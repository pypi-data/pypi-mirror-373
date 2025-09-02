from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

import humps
from google.protobuf.struct_pb2 import Struct
from pydantic import BaseModel, Field, RootModel, field_serializer, field_validator
from vmxai_completion_client import CompletionResponse, RequestMessageToolCall, RequestToolChoiceItem


class RequestToolFunction(BaseModel):
    """
    Represents a function that can be called by a tool.

    Attributes:
        name: The name of the function to be called.
        description: A description of what the function does.
        parameters: The parameters that the function accepts, in JSON Schema format.
    """
    name: str
    description: str
    parameters: dict


class RequestTools(BaseModel):
    """
    Defines a tool that can be made available during a completion request.

    Attributes:
        type: The type of tool, currently only "function" is supported.
        function: Configuration for the function tool.
    """
    type: Literal["function"]
    function: RequestToolFunction


class RequestMessage(BaseModel):
    """
    Represents a message in a chat completion conversation.

    Attributes:
        role: The role of the entity sending the message (system, user, assistant, or tool).
        name: Optional name of the entity sending the message.
        content: The text content of the message.
        tool_call_id: ID of the tool call this message is responding to.
        tool_calls: List of tool calls made in this message.
    """
    role: Literal["system", "user", "assistant", "tool"]
    name: Optional[str] = None
    content: Optional[str] = None
    tool_call_id: Optional[str] = Field(default=None, alias="toolCallId")
    tool_calls: Optional[list[RequestMessageToolCall]] = Field(
        default_factory=list, alias="toolCalls")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class CompletionRequest(BaseModel):
    """
    Represents a request for a completion.

    Attributes:
        resource: The resource identifier to use for generating the completion.
        workspace_id: Optional workspace ID where the request should run.
        environment_id: Optional environment ID where the request should run.
        tools: List of tools that should be available for this completion.
        tool_choice: Controls whether tools can be called ("auto", "none", or a specific tool).
        config: Optional custom configuration for the request.
        messages: The conversation messages to use for the completion.
        resource_config_overrides: Optional overrides for the resource configuration.
        metadata: Optional metadata to include with the request.
    """
    resource: str
    workspace_id: Optional[str] = Field(default=None, alias="workspaceId")
    environment_id: Optional[str] = Field(default=None, alias="environmentId")
    tools: Optional[list[RequestTools]] = Field(default_factory=list)
    tool_choice: Optional[Union[Literal["auto", "none"], RequestToolChoiceItem]] = Field(
        default=None, alias="toolChoice"
    )
    config: Optional[dict] = Field(default_factory=dict)
    messages: list[RequestMessage] = Field(default_factory=list)
    resource_config_overrides: Optional[dict] = Field(
        default_factory=dict, alias="resourceConfigOverrides")
    metadata: Optional[dict] = Field(default_factory=dict)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

    @field_serializer('tool_choice')
    def serialize_tool_choice(self, value: Optional[Union[Literal["auto", "none"], RequestToolChoiceItem]], _info):
        if value is None:
            return None
        
        if isinstance(value, str):
            return value

        from google.protobuf.json_format import MessageToDict
        result = MessageToDict(
            value
        )

        return result

    @field_validator("tool_choice", mode="before")
    def validate_tool_choice(cls, value: Any):
        if value is None:
            return None

        if isinstance(value, dict):
            if value.get("auto"):
                return "auto"
            elif value.get("none"):
                return "none"
            elif 'tool' in value:
                return RequestToolChoiceItem(**value.get("tool"))
            else:
                return RequestToolChoiceItem(**value)

        return value


class CompletionBatchRequestStatus(str, Enum):
    """
    Enum representing the possible states of a batch completion request.

    Values:
        PENDING: The batch is waiting to be processed.
        RUNNING: The batch is currently processing.
        COMPLETED: The batch has completed successfully.
        FAILED: The batch has failed.
        CANCELLED: The batch was cancelled.
    """
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class BatchRequestType(str, Enum):
    """
    Enum representing the types of batch requests.

    Values:
        ASYNC: Execute the batch asynchronously and return immediately.
        SYNC: Execute the batch synchronously and stream events as they occur.
        CALLBACK: Execute the batch asynchronously and notify a callback URL when complete.
    """
    ASYNC = "ASYNC"
    SYNC = "SYNC"
    CALLBACK = "CALLBACK"


class BaseEntity(BaseModel):
    """
    Base class for entities with creation and update metadata.

    Attributes:
        created_at: ISO timestamp when the entity was created.
        updated_at: ISO timestamp when the entity was last updated.
        created_by: ID of the user or system that created the entity.
        updated_by: ID of the user or system that last updated the entity.
    """
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")
    created_by: str = Field(alias="createdBy")
    updated_by: str = Field(alias="updatedBy")

    class Config:
        populate_by_name = True


class BatchRequestCallbackOptions(BaseModel):
    """
    Configuration for the callback mechanism used in CALLBACK batch requests.

    Attributes:
        url: The URL to send the callback to when the batch completes or fails.
        headers: Optional headers to include in the callback request.
        events: List of events to include in the callback request.
    """
    url: str
    headers: Optional[Dict[str, str]] = None
    events: List[Literal["BATCH_UPDATE", "ITEM_UPDATE", "ALL"]
                 ] = Field(default_factory=list)


class CompletionBatchItem(BaseEntity):
    """
    Represents a single item in a batch completion request.

    Attributes:
        workspace_environment_item_id: The workspace environment batch item ID.
        timestamp: The timestamp when the item was created.
        item_id: The item ID.
        batch_id: The batch ID.
        request: The original completion request for this item.
        response: The completion response for this item.
        status: The current status of this item.
        error: Optional error message if the item failed.
        retry_count: Optional count of retries for this item.
    """
    workspace_environment_item_id: str = Field(
        alias="workspaceEnvironmentItemId")
    timestamp: str
    item_id: str = Field(alias="itemId")
    batch_id: str = Field(alias="batchId")
    request: CompletionRequest
    response: Optional[CompletionResponse] = None
    status: CompletionBatchRequestStatus
    error: Optional[str] = None
    retry_count: Optional[int] = Field(default=None, alias="retryCount")

    @field_serializer('response')
    def serialize_response(self, value: Optional[CompletionResponse], _info):
        if value is None:
            return None

        from google.protobuf.json_format import MessageToDict
        result = MessageToDict(
            value
        )

        # Convert responseTimestamp to int
        if 'responseTimestamp' in result:
            result['response_timestamp'] = int(result['responseTimestamp'])

        return result

    @field_validator("response", mode="before")
    def validate_response(cls, value: Any):
        if value is None:
            return None

        if isinstance(value, dict):
            normalized_value = humps.decamelize(value)
            if 'raw_response' in normalized_value:
                raw_response = Struct()
                raw_response.update(normalized_value['raw_response'])
                normalized_value['raw_response'] = raw_response

            return CompletionResponse(**normalized_value)
        return value

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class CompletionBatchResponse(BaseEntity):
    """
    Response containing information about a batch completion request.

    Attributes:
        workspace_environment_batch_id: The workspace environment batch ID.
        timestamp: The timestamp when the batch was created.
        workspace_id: The workspace ID where the batch was executed.
        environment_id: The environment ID where the batch was executed.
        type: The type of batch request.
        batch_id: The unique identifier for this batch.
        status: The current status of the batch.
        items: List of items in this batch.
        error: Optional error message if the batch failed.
        completed: Optional count of completed items.
        failed: Optional count of failed items.
        pending: Optional count of pending items.
        completed_percentage: Optional percentage of completed items.
    """
    workspace_environment_batch_id: str = Field(
        alias="workspaceEnvironmentBatchId")
    timestamp: str
    type: BatchRequestType
    batch_id: str = Field(alias="batchId")
    status: CompletionBatchRequestStatus
    items: List[CompletionBatchItem] = []
    error: Optional[str] = None
    completed: Optional[int] = None
    running: Optional[int] = None
    failed: Optional[int] = None
    pending: Optional[int] = None
    completed_percentage: Optional[str] = Field(
        default=None, alias="completedPercentage")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

class CompletionBatchCapacity(BaseModel):
    """
    Capacity for a batch completion request.
    """
    requests: int
    tokens: int
    period: Literal["minute", "hour", "day", "week", "month", "lifetime"]


class CompletionBatchRequest(BaseModel):
    """
    Request to execute a batch of completion requests.

    Attributes:
        type: The type of batch to execute (ASYNC, SYNC, or CALLBACK).
        requests: List of completion requests to execute.
        callback_options: Optional callback configuration for CALLBACK batch types.
    """
    type: BatchRequestType
    requests: List[CompletionRequest]
    callback_options: Optional[BatchRequestCallbackOptions] = Field(
        default=None, alias="callbackOptions")
    capacity: Optional[List[CompletionBatchCapacity]] = Field(
        default=None, alias="capacity")

    class Config:
        populate_by_name = True


class CompletionBatchStreamBatchCreated(BaseModel):
    """
    Stream event indicating a batch has been created.

    Attributes:
        action: The action type, always "batch-created".
        payload: Information about the created batch.
    """
    action: Literal["batch-created"]
    payload: CompletionBatchResponse

    class Config:
        arbitrary_types_allowed = True


class CompletionBatchStreamItem(BaseModel):
    """
    Stream event for a batch item status change.

    Attributes:
        action: The action type, one of "item-running", "item-completed", or "item-failed".
        payload: Information about the item that changed status.
    """
    action: Literal["item-running", "item-completed", "item-failed"]
    payload: CompletionBatchItem

    class Config:
        arbitrary_types_allowed = True


class CompletionBatchStreamCompleted(BaseModel):
    """
    Stream event indicating a batch has completed or failed.

    Attributes:
        action: The action type, either "batch-completed" or "batch-failed".
        payload: Information about the completed/failed batch.
    """
    action: Literal["batch-completed", "batch-failed"]
    payload: CompletionBatchResponse

    class Config:
        arbitrary_types_allowed = True


# Type alias for the union of all stream events
CompletionBatchStream = Union[
    CompletionBatchStreamBatchCreated,
    CompletionBatchStreamItem,
    CompletionBatchStreamCompleted
]
"""
Union type representing all possible batch stream events.
This can be one of:
- CompletionBatchStreamBatchCreated: When a batch is created
- CompletionBatchStreamItem: When an item's status changes
- CompletionBatchStreamCompleted: When a batch is completed or fails
"""


class CompletionBatchUpdateCallbackPayload(BaseModel):
    """
    Payload for a completion batch update callback.

    Attributes:
        events: The events to include in the callback.
        payload: Information about the batch.
    """
    event: Literal["BATCH_UPDATE"]
    payload: CompletionBatchResponse

    class Config:
        arbitrary_types_allowed = True


class CompletionBatchItemUpdateCallbackPayload(BaseModel):
    """
    Payload for a completion batch item update callback.

    Attributes:
        event: The event type, always "item-update".
        payload: Information about the item that changed status.
    """
    event: Literal["ITEM_UPDATE"]
    payload: CompletionBatchItem

    class Config:
        arbitrary_types_allowed = True


class CompletionBatchCallbackPayload(
    RootModel[
        Union[CompletionBatchUpdateCallbackPayload, CompletionBatchItemUpdateCallbackPayload]
    ]
):
    class Config:
        arbitrary_types_allowed = True
