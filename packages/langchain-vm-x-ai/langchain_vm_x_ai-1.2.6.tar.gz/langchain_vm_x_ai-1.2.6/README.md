# VM-X SDK for Python Langchain

## Description

VM-X AI SDK client for Python Langchain

## Installation

```bash
pip install langchain-vm-x-ai
```

```bash
poetry add langchain-vm-x-ai
```

## Usage

### Non-Streaming

```python
from langchain_vmxai import ChatVMX

llm = ChatVMX(
    resource="default",
)

messages = [
    (
        "system",
        "You are a helpful translator. Translate the user sentence to French.",
    ),
    ("human", "I love programming."),
]
result = llm.invoke(messages)
```

### Streaming

```python
from langchain_vmxai import ChatVMX

llm = ChatVMX(
    resource="default",
)

messages = [
    (
        "system",
        "You are a helpful translator. Translate the user sentence to French.",
    ),
    ("human", "I love programming."),
]

for chunk in llm.stream(messages):
    print(chunk.content, end="", flush=True)
```

### Function Calling

#### Decorator

```python
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_vmxai import ChatVMX


@tool
def add(a: int, b: int) -> int:
    """Adds a and b.

    Args:
        a: first int
        b: second int
    """
    return a + b


@tool
def multiply(a: int, b: int) -> int:
    """Multiplies a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b


tools = [add, multiply]
llm = ChatVMX(
    resource="default",
)

llm_with_tools = llm.bind_tools(tools)
query = "What is 3 * 12? Also, what is 11 + 49?"

messages = [HumanMessage(query)]
ai_msg = llm_with_tools.invoke(messages)
messages.append(ai_msg)

for tool_call in ai_msg.tool_calls:
    selected_tool = {"add": add, "multiply": multiply}[tool_call["name"].lower()]
    tool_output = selected_tool.invoke(tool_call["args"])
    messages.append(ToolMessage(tool_output, tool_call_id=tool_call["id"]))

print(llm_with_tools.invoke(messages))
```

#### Pydantic

```python
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_vmxai import ChatVMX
from langchain_vmxai.output_parsers.tools import PydanticToolsParser


# Note that the docstrings here are crucial, as they will be passed along
# to the model along with the class name.
class add(BaseModel):
    """Add two integers together."""

    a: int = Field(..., description="First integer")
    b: int = Field(..., description="Second integer")


class multiply(BaseModel):
    """Multiply two integers together."""

    a: int = Field(..., description="First integer")
    b: int = Field(..., description="Second integer")


tools = [add, multiply]

llm = ChatVMX(
    resource="default",
)

llm_with_tools = llm.bind_tools(tools) | PydanticToolsParser(tools=[multiply, add])

query = "What is 3 * 12? Also, what is 11 + 49?"

print(llm_with_tools.invoke(query))

```

#### Function Calling Streaming

```python
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_vmxai import ChatVMX
from langchain_vmxai.output_parsers.tools import PydanticToolsParser


# Note that the docstrings here are crucial, as they will be passed along
# to the model along with the class name.
class add(BaseModel):
    """Add two integers together."""

    a: int = Field(..., description="First integer")
    b: int = Field(..., description="Second integer")


class multiply(BaseModel):
    """Multiply two integers together."""

    a: int = Field(..., description="First integer")
    b: int = Field(..., description="Second integer")


tools = [add, multiply]

llm = ChatVMX(
    resource="default",
)

llm_with_tools = llm.bind_tools(tools) | PydanticToolsParser(tools=[multiply, add])

query = "What is 3 * 12? Also, what is 11 + 49?"

for chunk in llm_with_tools.stream(query):
    print(chunk)
```

### Structured Output

```python
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_vmxai import ChatVMX


class Joke(BaseModel):
    setup: str = Field(description="The setup of the joke")
    punchline: str = Field(description="The punchline to the joke")


llm = ChatVMX(resource="default")
structured_llm = llm.with_structured_output(Joke, strict=True)

print(structured_llm.invoke("Tell me a joke about cats"))

```

## Limitations

1. Async client is not supported.
2. `json_mode` and `json_schema` Structured output are not supported.

## [Change Log](./CHANGELOG.md)
