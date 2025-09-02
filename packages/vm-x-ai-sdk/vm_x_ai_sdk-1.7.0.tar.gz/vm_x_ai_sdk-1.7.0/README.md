# VM-X SDK for Python

## Description

VM-X AI SDK client for Python

## Installation

```bash
pip install vm-x-ai-sdk
```

```bash
poetry add vm-x-ai-sdk
```

## Create VMXClient

```python

from vmxai import (
    CompletionRequest,
    RequestMessage,
    RequestMessageToolCall,
    RequestMessageToolCallFunction,
    RequestToolFunction,
    RequestTools,
    VMXClient,
    VMXClientOAuth,
)

client = VMXClient(
    domain="env-abc123.clnt.dev.vm-x.ai", # (Or VMX_DOMAIN env variable)
    # API Key (Or VMX_API_KEY env variable)
    api_key="abc123",
)

# Streaming
streaming_response = client.completion(
    request=CompletionRequest(
        resource="default",
        messages=[
            RequestMessage(
                role="user",
                content="Hey there!",
            )
        ],
    ),
)

for message in streaming_response:
    print(message.message, end="", flush=True)

```

## Examples

### Non-Streaming

```python

from vmxai import (
    CompletionRequest,
    RequestMessage,
    VMXClient,
)

client = VMXClient()

response = client.completion(
    request=CompletionRequest(
        resource="default",
        messages=[
            RequestMessage(
                role="user",
                content="Hey there!",
            )
        ],
    ),
    stream=False,
)

print(response.message)

```

### Streaming

```python

from vmxai import (
    CompletionRequest,
    RequestMessage,
    VMXClient,
)

client = VMXClient()

streaming_response = client.completion(
    request=CompletionRequest(
        resource="default",
        messages=[
            RequestMessage(
                role="user",
                content="Hey there!",
            )
        ],
    ),
)

for message in streaming_response:
    print(message.message, end="", flush=True)

```

### Tool Call

```python

from vmxai import (
    CompletionRequest,
    RequestMessage,
    RequestMessageToolCall,
    RequestMessageToolCallFunction,
    RequestToolFunction,
    RequestTools,
    VMXClient,
)

client = VMXClient()

# Function Calling
function_response = client.completion(
    request=CompletionRequest(
        resource="default",
        messages=[
            RequestMessage(
                role="user",
                content="whats the temperature in Dallas, New York and San Diego?",
            )
        ],
        tools=[
            RequestTools(
                type="function",
                function=RequestToolFunction(
                    name="get_weather",
                    description="Lookup the temperature",
                    parameters={
                        "type": "object",
                        "properties": {"city": {"description": "City you want to get the temperature"}},
                        "required": ["city"],
                    },
                ),
            )
        ],
    ),
)

print("Function Response")
print("#" * 100)
for message in function_response:
    print(message, end="")

print("\n" * 2)

# Function Calling Callback
function_response_callback = client.completion(
    request=CompletionRequest(
        resource="default",
        messages=[
            RequestMessage(
                role="user",
                content="whats the temperature in Dallas, New York and San Diego?",
            ),
            RequestMessage(
                role="assistant",
                tool_calls=[
                    RequestMessageToolCall(
                        id="call_NLcWB6VCdG6x9UW6xrGVTTTR",
                        type="function",
                        function=RequestMessageToolCallFunction(name="get_weather", arguments='{"city": "Dallas"}'),
                    ),
                    RequestMessageToolCall(
                        id="call_6RDTuEDsaHvWr8XjwDXx4UjX",
                        type="function",
                        function=RequestMessageToolCallFunction(name="get_weather", arguments='{"city": "New York"}'),
                    ),
                    RequestMessageToolCall(
                        id="call_NsFzeGVbAWl5bor6RrUDCvTv",
                        type="function",
                        function=RequestMessageToolCallFunction(name="get_weather", arguments='{"city": "San Diego"}'),
                    ),
                ],
            ),
            RequestMessage(
                role="tool", content="The temperature in Dallas is 81F", tool_call_id="call_NLcWB6VCdG6x9UW6xrGVTTTR"
            ),
            RequestMessage(
                role="tool", content="The temperature in New York is 78F", tool_call_id="call_6RDTuEDsaHvWr8XjwDXx4UjX"
            ),
            RequestMessage(
                role="tool", content="The temperature in San Diego is 68F", tool_call_id="call_NsFzeGVbAWl5bor6RrUDCvTv"
            ),
        ],
        tools=[
            RequestTools(
                type="function",
                function=RequestToolFunction(
                    name="get_weather",
                    description="Lookup the temperature",
                    parameters={
                        "type": "object",
                        "properties": {"city": {"description": "City you want to get the temperature"}},
                        "required": ["city"],
                    },
                ),
            )
        ],
    ),
)

print("Function Callback Response")
print("#" * 100)
for message in function_response_callback:
    print(message.message, end="")
```

### Multi-Answer

```python
import asyncio
from typing import Iterator

from blessings import Terminal
from vmxai import (
    CompletionRequest,
    CompletionResponse,
    RequestMessage,
    VMXClient,
)

term = Terminal()
client = VMXClient()


async def print_streaming_response(response: asyncio.Task[Iterator[CompletionResponse]], term_location: int):
    """
    Print a streaming response to the terminal at a specific terminal location.
    So, we can demonstrate multiple streaming responses in parallel.

    Args:
        response (asyncio.Task[Iterator[CompletionResponse]]): Streaming response task
        term_location (int): Terminal location to print the response
    """
    first = True
    with term.location(y=term_location):
        result = await response
        x = 0
        y = term_location + 3
        for message in result:
            if first:
                print("\nModel: ", message.metadata.model)
                first = False
                # Some models start with 2 new lines, this is to remove them
                if message.message.startswith("\n\n"):
                    message.message = message.message[2:]

            await asyncio.sleep(0.01)
            print(term.move(y, x) + message.message)
            x += len(message.message)
            if x > term.width:
                x = 0
                y += 1


async def multi_answer():
    # Please make sure that the "default" resource have 3 providers configured in the VM-X Console.
    resp1, resp2, resp3 = client.completion(
        request=CompletionRequest(
            resource="default",
            messages=[
                RequestMessage(
                    role="user",
                    content="Hey there, how are you?",
                )
            ],
        ),
        multi_answer=True,
    )

    print("Multi-Answer Streaming Response")
    print("#" * 100)
    await asyncio.gather(
        *[print_streaming_response(resp1, 10), print_streaming_response(resp2, 16), print_streaming_response(resp3, 20)]
    )
    print("\n" * 7)

    resp1, resp2, resp3 = client.completion(
        request=CompletionRequest(
            resource="default",
            messages=[
                RequestMessage(
                    role="user",
                    content="Hey there, how are you?",
                )
            ],
        ),
        stream=False,
        multi_answer=True,
    )

    print("Multi-Answer Non-Streaming Response")
    print("#" * 100)

    async def _print(resp):
        result = await resp
        print(result.message, flush=True)

    await asyncio.gather(*[_print(resp1), _print(resp2), _print(resp3)])


asyncio.run(multi_answer())

```

## [Change Log](./CHANGELOG.md)
