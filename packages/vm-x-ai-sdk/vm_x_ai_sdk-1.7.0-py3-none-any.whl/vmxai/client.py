import asyncio
import json
import os
import textwrap
import uuid
from typing import Any, AsyncGenerator, Dict, Iterable, List, Literal, Optional, Tuple, Union, overload

import grpc
import grpc._grpcio_metadata
import requests
from google.protobuf.struct_pb2 import Struct
from grpc import aio
from vmxai_completion_client import (
    CompletionRequest as GrpcCompletionRequest,
)
from vmxai_completion_client import (
    CompletionResponse,
    CompletionServiceStub,
    GetResourceProviderCountRequest,
    GetResourceProviderCountResponse,
    RequestToolChoiceItem,
)
from vmxai_completion_client import (
    RequestMessage as GrpcRequestMessage,
)
from vmxai_completion_client import (
    RequestToolChoice as GrpcRequestToolChoice,
)
from vmxai_completion_client import (
    RequestToolFunction as GrpcRequestToolFunction,
)
from vmxai_completion_client import (
    RequestTools as GrpcRequestTools,
)

from vmxai.auth.api_key import VMXClientAPIKey
from vmxai.types import (
    BatchRequestCallbackOptions,
    BatchRequestType,
    CompletionBatchItem,
    CompletionBatchRequest,
    CompletionBatchRequestStatus,
    CompletionBatchResponse,
    CompletionBatchStream,
    CompletionBatchStreamBatchCreated,
    CompletionBatchStreamCompleted,
    CompletionBatchStreamItem,
    CompletionRequest,
    RequestTools,
)


class VMXClient:
    """
    Client for interacting with VM-X AI services.
    
    This client provides access to VM-X AI's capabilities, including text completions,
    batch processing, and related functionality. It handles authentication, connection
    setup, and provides a Pythonic interface to the underlying gRPC and REST APIs.
    
    Attributes:
        domain: The domain name for the VM-X AI service.
        workspace_id: The default workspace ID to use for requests.
        environment_id: The default environment ID to use for requests.
        secure_channel: Whether to use a secure channel for gRPC communication.
        api_key: The API key used for authentication.
        auth: The authentication provider used for requests.
        completion_client: The gRPC client for completion requests.
    """
    
    def __init__(
        self,
        domain: str = os.getenv("VMX_DOMAIN", None),
        api_key: str = os.getenv("VMX_API_KEY", None),
        secure_channel: bool = os.getenv("VMX_SECURE_CHANNEL", "true").lower() == "true",
        workspace_id: Optional[str] = os.getenv("VMX_WORKSPACE_ID", None),
        environment_id: Optional[str] = os.getenv("VMX_ENVIRONMENT_ID", None),
    ):
        """
        Initialize a new VM-X AI client.
        
        Args:
            domain: The domain name for the VM-X AI service. If not provided, 
                   read from VMX_DOMAIN environment variable.
            api_key: The API key to use for authentication. If not provided, 
                    read from VMX_API_KEY environment variable.
            secure_channel: Whether to use a secure channel for gRPC communication.
                           Defaults to True unless VMX_SECURE_CHANNEL is set to "false".
            workspace_id: The default workspace ID to use for requests. If not provided,
                         read from VMX_WORKSPACE_ID environment variable.
            environment_id: The default environment ID to use for requests. If not provided,
                           read from VMX_ENVIRONMENT_ID environment variable.
                           
        Raises:
            AttributeError: If domain or api_key is not provided and not available
                           from environment variables.
        """
        if not domain:
            raise AttributeError(
                textwrap.wrap("""
                'domain' must be provided.

                Or

                set the 'VMX_DOMAIN' environment variable.
                """)
            )

        self.domain = domain
        self.workspace_id = workspace_id
        self.environment_id = environment_id
        self.secure_channel = secure_channel

        if api_key:
            self.auth = VMXClientAPIKey(api_key)
        else:
            raise AttributeError(
                textwrap.wrap("""
                'api_key' must be provided.

                Or

                set the 'VMX_API_KEY' environment variable.

                Or

                set the 'VMX_OAUTH_CLIENT_ID' and 'VMX_OAUTH_CLIENT_SECRET' environment variables.
                """)
            )

        self.api_key = api_key

        self.completion_client = CompletionServiceStub(
            grpc.secure_channel(self.grpc_domain, grpc.ssl_channel_credentials())
            if self.secure_channel and not self.domain.startswith("localhost")
            else grpc.insecure_channel(self.grpc_domain)
        )

    @property
    def api_domain(self) -> str:
        """
        Returns the API domain for REST API calls.
        
        For localhost domains, uses http://, otherwise uses https://api.{domain}.
        
        Returns:
            str: The full API domain URL.
        """
        if self.domain.startswith("localhost"):
            return f"http://{self.domain}"
        return f"https://api.{self.domain}"
    
    @property
    def grpc_domain(self) -> str:
        """
        Returns the gRPC domain for gRPC calls.
        
        When secure_channel is True, prefixes with "grpc.", otherwise returns domain as is.
        
        Returns:
            str: The gRPC domain.
        """
        if self.secure_channel:
            return f"grpc.{self.domain}"
        return self.domain

    @overload
    def completion(
        self, *, request: CompletionRequest, multi_answer: Literal[True]
    ) -> Tuple[asyncio.Task[Iterable[CompletionResponse]], ...]: ...

    @overload
    def completion(
        self, *, request: CompletionRequest, multi_answer: Literal[True], answer_count: int
    ) -> Tuple[asyncio.Task[Iterable[CompletionResponse]], ...]: ...

    @overload
    def completion(self, *, request: CompletionRequest) -> Iterable[CompletionResponse]: ...

    @overload
    def completion(self, *, request: CompletionRequest, stream: Literal[True]) -> Iterable[CompletionResponse]: ...

    @overload
    def completion(
        self, *, request: CompletionRequest, stream: Literal[True], multi_answer: Literal[True]
    ) -> Tuple[asyncio.Task[Iterable[CompletionResponse]], ...]: ...

    @overload
    def completion(
        self, *, request: CompletionRequest, stream: Literal[True], multi_answer: Literal[True], answer_count: int
    ) -> Tuple[asyncio.Task[Iterable[CompletionResponse]], ...]: ...

    @overload
    def completion(self, *, request: CompletionRequest, stream: Literal[False]) -> CompletionResponse: ...

    @overload
    def completion(
        self, *, request: CompletionRequest, stream: Literal[False], multi_answer: Literal[True]
    ) -> Tuple[asyncio.Task[CompletionResponse], ...]: ...

    @overload
    def completion(
        self, *, request: CompletionRequest, stream: Literal[False], multi_answer: Literal[True], answer_count: int
    ) -> Tuple[asyncio.Task[CompletionResponse], ...]: ...

    def completion(
        self,
        *,
        request: CompletionRequest,
        stream: bool = True,
        multi_answer: bool = False,
        answer_count: Optional[int] = None,
    ) -> Union[
        Iterable[CompletionResponse],
        Tuple[asyncio.Task[Iterable[CompletionResponse]]],
        CompletionResponse,
        Tuple[asyncio.Task[CompletionResponse]],
    ]:
        """
        Execute a completion request to generate text or perform other AI tasks.
        
        This method supports different modes of operation:
        - Standard streaming completions (default)
        - Non-streaming completions
        - Multi-answer completions that query multiple providers in parallel
        
        Args:
            request: The completion request configuration.
            stream: Whether to stream the response (True) or wait for the full response (False).
            multi_answer: Whether to get multiple answers from different providers.
            answer_count: Optional number of answers to request when multi_answer is True.
                         If not specified, all available providers for the resource will be used.
                         
        Returns:
            Depending on the combination of stream and multi_answer:
            - stream=True, multi_answer=False: An iterable of CompletionResponse objects
            - stream=True, multi_answer=True: A tuple of tasks yielding iterables of CompletionResponse objects
            - stream=False, multi_answer=False: A single CompletionResponse object
            - stream=False, multi_answer=True: A tuple of tasks yielding CompletionResponse objects
        """
        metadata: list[tuple[str, str]] = []
        if "_X_AMZN_TRACE_ID" in os.environ:
            metadata.append(("x-amzn-trace-id", os.environ["_X_AMZN_TRACE_ID"]))

        metadata.append(("correlation-id", str(uuid.uuid4())))

        self.auth.inject_credentials(self, metadata)
        config = Struct()
        if request.config:
            config.update(request.config)

        grpc_request = dict(
            workspace_id=request.workspace_id or self.workspace_id,
            environment_id=request.environment_id or self.environment_id,
            resource=request.resource,
            config=config,
            stream=stream,
            tools=self._parse_tools(request.tools),
            tool_choice=self._parse_tool_choice(request.tool_choice),
            metadata=request.metadata or None,
            resource_config_overrides=request.resource_config_overrides or None,
            messages=[
                GrpcRequestMessage(
                    name=message.name,
                    role=message.role,
                    tool_call_id=message.tool_call_id,
                    tool_calls=message.tool_calls or [],
                    content=message.content,
                )
                for message in request.messages
            ],
        )

        if multi_answer and answer_count is None:
            provider_count_response: GetResourceProviderCountResponse = self.completion_client.getResourceProviderCount(
                GetResourceProviderCountRequest(
                    workspace_id=request.workspace_id or self.workspace_id,
                    environment_id=request.environment_id or self.environment_id,
                    resource=request.resource
                ), metadata=tuple(metadata)
            )

            answer_count = provider_count_response.count

        if stream:
            if not multi_answer:
                return self.completion_client.create(GrpcCompletionRequest(**grpc_request), metadata=tuple(metadata))

            return tuple(
                [
                    asyncio.create_task(self._call_multi_answer(index, grpc_request, metadata, stream))
                    for index in range(answer_count)
                ]
            )
        else:
            if not multi_answer:
                result = self.completion_client.create(GrpcCompletionRequest(**grpc_request), metadata=tuple(metadata))
                for response in result:
                    return response

            return tuple(
                [
                    asyncio.create_task(self._call_multi_answer(index, grpc_request, metadata, stream))
                    for index in range(answer_count)
                ]
            )

    async def _call_multi_answer(
        self,
        index: int,
        grpc_request: dict,
        metadata: List[Tuple[str, str]],
        stream: bool,
    ):
        """
        Internal method to handle requests for multiple answers.
        
        This method is used by completion() to execute requests against multiple
        providers in parallel when multi_answer=True.
        
        Args:
            index: The index of the provider to use (0 is primary, others are secondary).
            grpc_request: The gRPC request dictionary.
            metadata: The metadata to include with the request.
            stream: Whether to stream the response or not.
            
        Returns:
            For streaming requests: An async iterable of CompletionResponse.
            For non-streaming requests: A single CompletionResponse.
        """
        primary = index == 0
        secondary_model_index = index - 1 if index > 0 else None

        if stream:
            return self.completion_client.create(
                GrpcCompletionRequest(primary=primary, secondary_model_index=secondary_model_index, **grpc_request),
                metadata=metadata,
            )
        else:
            async with (
                aio.secure_channel(f"grpc.{self.domain}", grpc.ssl_channel_credentials())
                if self.secure_channel
                else aio.insecure_channel(self.domain)
            ) as channel:
                result = CompletionServiceStub(channel).create(
                    GrpcCompletionRequest(primary=primary, secondary_model_index=secondary_model_index, **grpc_request),
                    metadata=metadata,
                )
                async for item in result:
                    return item

    def _parse_tools(self, tools: list[RequestTools]) -> list[GrpcRequestTools]:
        """
        Convert tool definitions from Python dataclasses to gRPC format.
        
        Args:
            tools: List of tool definitions to convert.
            
        Returns:
            list[GrpcRequestTools]: The tools in gRPC format.
        """
        result: list[GrpcRequestTools] = []
        for tool in tools or []:
            grpc_function_params = Struct()
            grpc_function_params.update(tool.function.parameters)

            grpc_tool = GrpcRequestTools(
                type=tool.type,
                function=GrpcRequestToolFunction(
                    name=tool.function.name, description=tool.function.description, parameters=grpc_function_params
                ),
            )
            result.append(grpc_tool)

        return result

    def _parse_tool_choice(
        self, tool_choice: Union[Literal["auto", "none"], RequestToolChoiceItem]
    ) -> GrpcRequestToolChoice:
        """
        Convert tool_choice from Python format to gRPC format.
        
        Args:
            tool_choice: The tool choice setting ("auto", "none", or a specific tool).
            
        Returns:
            GrpcRequestToolChoice: The tool choice in gRPC format.
        """
        if tool_choice == "auto":
            return GrpcRequestToolChoice(auto=True, none=False)
        elif tool_choice == "none":
            return GrpcRequestToolChoice(auto=False, none=True)
        else:
            return GrpcRequestToolChoice(auto=False, none=False, tool=tool_choice)

    async def get_completion_batch_result(
        self, batch_id: str,
        include_results: bool = False
    ) -> CompletionBatchResponse:
        """
        Get the result of a batch completion request.

        Args:
            batch_id: The ID of the batch to retrieve.
            include_results: Whether to include the results in the response.
        Returns:
            CompletionBatchResponse: The batch response object.
        """
        result = await self._execute_api_request(
            f"/completion-batch/{self.workspace_id}/{self.environment_id}/{batch_id}",
            "GET",
            query_params={"includeResults": str(include_results).lower()},
        )
        return CompletionBatchResponse.model_validate(result)

    async def wait_for_completion_batch(
        self,
        batch_id: str,
        timeout: Optional[float] = None,
        retry_interval: float = 1.0,
    ) -> CompletionBatchResponse:
        """
        Wait for a batch completion request to finish.

        Args:
            batch_id: The ID of the batch to wait for.
            timeout: Optional timeout in seconds. If None, wait indefinitely.
            retry_interval: Time in seconds between status checks.

        Returns:
            CompletionBatchResponse: The final batch response object.

        Raises:
            TimeoutError: If the batch doesn't complete within the timeout period.
        """
        response = await self.get_completion_batch_result(batch_id)
        start_time = asyncio.get_event_loop().time()

        while response.status in [
            CompletionBatchRequestStatus.PENDING,
            CompletionBatchRequestStatus.RUNNING,
        ]:
            if timeout is not None and (asyncio.get_event_loop().time() - start_time) > timeout:
                raise TimeoutError("Timeout waiting for completion batch to finish")

            await asyncio.sleep(retry_interval)
            response = await self.get_completion_batch_result(batch_id)

        return await self.get_completion_batch_result(batch_id, include_results=True)
    
    async def get_completion_batch_item_result(self, batch_id: str, item_id: str) -> CompletionBatchItem:
        """
        Get the result of a batch completion item.
        """
        result = await self._execute_api_request(
            f"/completion-batch/{self.workspace_id}/{self.environment_id}/{batch_id}/item/{item_id}",
            "GET",
        )
        return CompletionBatchItem.model_validate(result)
    
    async def wait_for_completion_batch_item(
        self,
        batch_id: str,
        item_id: str,
        timeout: Optional[float] = None,
        retry_interval: float = 1.0,
    ) -> CompletionBatchItem:
        """
        Wait for a batch completion item to finish.
        """
        response = await self.get_completion_batch_item_result(batch_id, item_id)
        start_time = asyncio.get_event_loop().time()

        while response.status in [
            CompletionBatchRequestStatus.PENDING,
            CompletionBatchRequestStatus.RUNNING,
        ]:
            if timeout is not None and (asyncio.get_event_loop().time() - start_time) > timeout:
                raise TimeoutError("Timeout waiting for completion batch item to finish")

            await asyncio.sleep(retry_interval)
            response = await self.get_completion_batch_item_result(batch_id, item_id)

        return response

    async def completion_batch_sync(
        self, completion_requests: List[CompletionRequest]
    ) -> AsyncGenerator[CompletionBatchStream, None]:
        """
        Execute a synchronous batch completion request and stream the results.

        Args:
            requests: List of completion requests to process in batch.

        Yields:
            CompletionBatchStream: Stream of batch events as they occur.

        Raises:
            Exception: If an error occurs during batch processing.
        """
        payload = CompletionBatchRequest(
            type=BatchRequestType.SYNC,
            requests=completion_requests,
        )

        headers = {}
        self.auth.inject_credentials(self, headers)

        # Prepare requests without streaming
        # Use model_dump with by_alias=True to convert to camelCase
        payload_dict = payload.model_dump(by_alias=True)
        payload_dict["requests"] = [self._prepare_completion_request(req) for req in payload_dict["requests"]]

        url = f"{self.api_domain}/completion-batch/{self.workspace_id}/{self.environment_id}"
        response = requests.post(
            url,
            json=payload_dict,
            headers={
                **headers,
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
            },
            stream=True,
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if not line:
                continue
            
            line_str = line.decode("utf-8")
            if not line_str.startswith("data: "):
                continue
                
            data_str = line_str[6:].strip()  # Remove "data: " prefix
            
            if data_str == "[DONE]":
                break
                
            try:
                data = json.loads(data_str)
                if "error" in data:
                    raise Exception(data["error"])
                
                # Parse the stream event based on the action type
                action = data.get("action")
                
                if action == "batch-created":
                    yield CompletionBatchStreamBatchCreated(
                        action=action,
                        payload=CompletionBatchResponse.model_validate(data["payload"])
                    )
                elif action in ["item-running", "item-completed", "item-failed"]:
                    yield CompletionBatchStreamItem(
                        action=action,
                        payload=CompletionBatchItem.model_validate(data["payload"])
                    )
                elif action in ["batch-completed", "batch-failed"]:
                    yield CompletionBatchStreamCompleted(
                        action=action,
                        payload=CompletionBatchResponse.model_validate(data["payload"])
                    )
            except json.JSONDecodeError as e:
                raise Exception(f"Failed to parse SSE event: {e}") from e

    async def completion_batch(self, requests: List[CompletionRequest]) -> CompletionBatchResponse:
        """
        Execute an asynchronous batch completion request.

        Args:
            requests: List of completion requests to process in batch.

        Returns:
            CompletionBatchResponse: The batch response object with initial status.
        """
        payload = CompletionBatchRequest(
            type=BatchRequestType.ASYNC,
            requests=requests,
        )
        return await self._execute_completion_batch(payload)

    async def completion_batch_callback(
        self, 
        requests: List[CompletionRequest],
        callback_options: BatchRequestCallbackOptions
    ) -> CompletionBatchResponse:
        """
        Execute a batch completion request with results sent to a callback URL.

        Args:
            requests: List of completion requests to process in batch.
            callback_options: Callback configuration including URL and optional headers.

        Returns:
            CompletionBatchResponse: The batch response object with initial status.
        """
        payload = CompletionBatchRequest(
            type=BatchRequestType.CALLBACK,
            requests=requests,
            callback_options=callback_options,
        )
        return await self._execute_completion_batch(payload)

    async def _execute_completion_batch(self, payload: CompletionBatchRequest) -> CompletionBatchResponse:
        """
        Internal method to execute a batch completion request.

        Args:
            payload: The batch request configuration.

        Returns:
            CompletionBatchResponse: The batch response object.
        """
        # Use model_dump with by_alias=True to convert to camelCase
        payload_dict = payload.model_dump(by_alias=True)
        payload_dict["requests"] = [self._prepare_completion_request(req) for req in payload_dict["requests"]]
            
        result = await self._execute_api_request(
            f"/completion-batch/{self.workspace_id}/{self.environment_id}",
            "POST",
            payload_dict,
        )
        return CompletionBatchResponse.model_validate(result)

    async def _execute_api_request(
        self, 
        url: str, 
        method: str, 
        payload: Optional[Dict[str, Any]] = None,
        query_params: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        Execute a REST API request to the VMX API.

        Args:
            url: The URL path (without domain).
            method: HTTP method (GET, POST, etc.).
            payload: Optional request payload for POST requests.
            query_params: Optional query parameters for GET requests.

        Returns:
            dict: The response data parsed into a dictionary.

        Raises:
            Exception: If the API request fails.
        """
        headers = {}
        self.auth.inject_credentials(self, headers)
        
        if payload:
            headers["Content-Type"] = "application/json"
        
        full_url = f"{self.api_domain}{url}"
        
        if method.upper() == "GET":
            response = requests.get(full_url, headers=headers, params=query_params)
        elif method.upper() == "POST":
            response = requests.post(full_url, json=payload, headers=headers, params=query_params)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
            
        response.raise_for_status()
        return response.json()

    def _prepare_completion_request(self, request: dict) -> dict:
        """
        Convert a CompletionRequest dataclass to a dictionary for API requests.
        
        This method handles the conversion from Python dataclasses to the JSON structure
        expected by the REST API, including proper property name formatting.
        
        Args:
            request: The completion request to convert.
            
        Returns:
            Dict[str, Any]: Dictionary representation of the request.
        """
        # Use model_dump with by_alias=True to convert to camelCase
        result = {**request}
        if request.get("toolChoice"):
            if request.get("toolChoice") == "auto":
                result["toolChoice"] = {"auto": True}
            elif request.get("toolChoice") == "none":
                result["toolChoice"] = {"none": True}
            else:
                result["toolChoice"] = {"tool": request.get("toolChoice")}

        # Ensure stream is False for batch requests
        result["stream"] = False
        
        return result
