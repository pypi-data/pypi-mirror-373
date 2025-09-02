"""VM-X chat wrapper."""

from __future__ import annotations

import json
import logging
from operator import itemgetter
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Literal,
    Mapping,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
)

from google.protobuf.json_format import (
    MessageToDict,
)
from langchain_core.callbacks import (
    CallbackManagerForLLMRun,
)
from langchain_core.language_models import LanguageModelInput
from langchain_core.language_models.chat_models import (
    BaseChatModel,
    LangSmithParams,
    generate_from_stream,
)
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    BaseMessageChunk,
    ChatMessage,
    ChatMessageChunk,
    FunctionMessage,
    FunctionMessageChunk,
    HumanMessage,
    HumanMessageChunk,
    InvalidToolCall,
    SystemMessage,
    SystemMessageChunk,
    ToolCall,
    ToolMessage,
    ToolMessageChunk,
)
from langchain_core.messages.ai import UsageMetadata
from langchain_core.messages.tool import tool_call_chunk
from langchain_core.output_parsers.base import OutputParserLike
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_core.pydantic_v1 import BaseModel, Field, SecretStr, root_validator
from langchain_core.runnables import Runnable, RunnableMap, RunnablePassthrough
from langchain_core.tools import BaseTool
from langchain_core.utils import (
    convert_to_secret_str,
    get_from_dict_or_env,
    get_pydantic_field_names,
)
from langchain_core.utils.pydantic import (
    is_basemodel_subclass,
)
from langchain_core.utils.utils import build_extra_kwargs
from vmxai import (
    CompletionRequest,
    CompletionResponse,
    RequestMessage,
    RequestMessageToolCall,
    RequestMessageToolCallFunction,
    RequestToolChoiceFunction,
    RequestToolChoiceItem,
    VMXClient,
)

from langchain_vmxai.output_parsers.tools import (
    JsonOutputKeyToolsParser,
    PydanticToolsParser,
    make_invalid_tool_call,
    parse_tool_call,
)
from langchain_vmxai.utils.function_calling import convert_to_vmx_tool

logger = logging.getLogger(__name__)


def _convert_vmx_response_to_message(response: CompletionResponse) -> BaseMessage:
    """Convert a dictionary to a LangChain message.

    Args:
        response: The VMX response.

    Returns:
        The LangChain message.
    """
    result: BaseMessage
    if response.role == "user":
        return HumanMessage(
            content=response.message or "",
            id=response.id,
        )
    elif response.role == "assistant":
        additional_kwargs: Dict = {}
        tool_calls = []
        invalid_tool_calls = []
        if raw_tool_calls := response.tool_calls:
            additional_kwargs["tool_calls"] = raw_tool_calls
            for raw_tool_call in raw_tool_calls:
                try:
                    tool_calls.append(parse_tool_call(raw_tool_call, return_id=True))
                except Exception as e:
                    invalid_tool_calls.append(make_invalid_tool_call(raw_tool_call, str(e)))
        result = AIMessage(
            content=response.message or "",
            additional_kwargs=additional_kwargs,
            id=response.id,
            tool_calls=tool_calls,
            invalid_tool_calls=invalid_tool_calls,
        )
    elif response.role == "system":
        result = SystemMessage(content=response.message or "", id=response.id)
    elif response.role == "tool":
        additional_kwargs = {}
        result = ToolMessage(
            content=response.message or "",
            tool_call_id=response.tool_call_id or "",
            additional_kwargs=additional_kwargs,
            id=response.id,
        )
    else:
        result = ChatMessage(content=response.message or "", role=response.role, id=response.id)

    result.usage_metadata = UsageMetadata(
        input_tokens=response.usage.prompt,
        output_tokens=response.usage.completion,
        total_tokens=response.usage.total,
    )

    return result


def _format_message_content(content: Any) -> Any:
    """Format message content."""
    if content and isinstance(content, list):
        # Remove unexpected block types
        formatted_content = []
        for block in content:
            if isinstance(block, dict) and "type" in block and block["type"] == "tool_use":
                continue
            else:
                formatted_content.append(block)
    else:
        formatted_content = content

    return formatted_content


def _convert_tool_call_dict_to_vmx_tool_call(_dict: Mapping[str, Any]) -> RequestMessageToolCall:
    """Convert a LangChain tool call dictionary to a VMX tool call dictionary.

    Args:
        _dict: The LangChain tool call dictionary.

    Returns:
        The VMX tool call dictionary.
    """
    function = _dict["function"]
    return RequestMessageToolCall(
        id=_dict.get("id"),
        type=_dict.get("type"),
        function=RequestMessageToolCallFunction(name=function["name"], arguments=json.dumps(function["arguments"])),
    )


def _convert_message_to_vmx(message: BaseMessage) -> RequestMessage:
    """Convert a LangChain message to a dictionary.

    Args:
        message: The LangChain message.

    Returns:
        The dictionary.
    """

    vmx_message = RequestMessage(role="assistant", content=_format_message_content(message.content))
    if (name := message.name or message.additional_kwargs.get("name")) is not None:
        vmx_message.name = name

    # populate role and additional message data
    if isinstance(message, ChatMessage):
        vmx_message.role = message.role
    elif isinstance(message, HumanMessage):
        vmx_message.role = "user"
    elif isinstance(message, AIMessage):
        vmx_message.role = "assistant"
        if message.tool_calls or message.invalid_tool_calls:
            vmx_message.tool_calls = [_lc_tool_call_to_vmx_tool_call(tc) for tc in message.tool_calls] + [
                _lc_invalid_tool_call_to_vmx_tool_call(tc) for tc in message.invalid_tool_calls
            ]
        elif "tool_calls" in message.additional_kwargs:
            vmx_message.tool_calls = [
                _convert_tool_call_dict_to_vmx_tool_call(tool) for tool in message.additional_kwargs["tool_calls"]
            ]
        else:
            pass
        # If tool calls present, content null value should be None not empty string.
        if vmx_message.tool_calls:
            vmx_message.content = vmx_message.content or None
    elif isinstance(message, SystemMessage):
        vmx_message.role = "system"
    elif isinstance(message, FunctionMessage):
        vmx_message.role = "function"
    elif isinstance(message, ToolMessage):
        vmx_message.role = "tool"
        vmx_message.tool_call_id = message.tool_call_id
    else:
        raise TypeError(f"Got unknown type {message}")
    return vmx_message


def _convert_delta_to_message_chunk(
    response: CompletionResponse, default_class: Type[BaseMessageChunk]
) -> BaseMessageChunk:
    additional_kwargs: Dict = {}
    tool_call_chunks = []
    if raw_tool_calls := response.tool_calls:
        additional_kwargs["tool_calls"] = raw_tool_calls
        try:
            tool_call_chunks = [
                tool_call_chunk(
                    name=rtc.function.name,
                    args=rtc.function.arguments,
                    id=rtc.id,
                    index=idx,
                )
                for idx, rtc in enumerate(raw_tool_calls)
            ]
        except KeyError:
            pass

    if response.role == "user" or default_class == HumanMessageChunk:
        return HumanMessageChunk(content=response.message or "", id=response.id)
    elif response.role == "assistant" or default_class == AIMessageChunk:
        return AIMessageChunk(
            content=response.message or "",
            additional_kwargs=additional_kwargs,
            id=response.id,
            tool_call_chunks=tool_call_chunks,
        )
    elif response.role == "system" or default_class == SystemMessageChunk:
        return SystemMessageChunk(content=response.message or "", id=response.id)
    elif response.role == "function" or default_class == FunctionMessageChunk:
        return FunctionMessageChunk(content=response.message or "", id=response.id)
    elif response.role == "tool" or default_class == ToolMessageChunk:
        return ToolMessageChunk(content=response.message or "", id=response.id)
    elif response.role or default_class == ChatMessageChunk:
        return ChatMessageChunk(content=response.message or "", role=response.role, id=response.id)
    else:
        return default_class(content=response.message or "", id=response.id)


_BM = TypeVar("_BM", bound=BaseModel)
_DictOrPydanticClass = Union[Dict[str, Any], Type[_BM], Type]
_DictOrPydantic = Union[Dict, _BM]


class BaseChatVMX(BaseChatModel):
    client: VMXClient = Field(default=None, exclude=True)  #: :meta private:
    resource_name: str = Field(default="default", alias="resource")
    """Model name to use."""
    config_kwargs: Dict[str, Any] = Field(default_factory=dict)
    """Holds any model parameters valid for `create` call not explicitly specified."""
    vmx_api_key: Optional[SecretStr] = Field(default=None, alias="api_key")
    """Automatically inferred from env var `VMX_API_KEY` if not provided."""
    vmx_domain: Optional[str] = Field(default=None, alias="domain")
    """Automatically inferred from env var `VMX_WORKSPACE_ID` if not provided."""
    vmx_workspace_id: Optional[str] = Field(default=None, alias="workspace_id")
    """Automatically inferred from env var `VMX_ENVIRONMENT_ID` if not provided."""
    vmx_environment_id: Optional[str] = Field(default=None, alias="environment_id")
    """Automatically inferred from env var `VMX_DOMAIN` if not provided."""
    streaming: bool = False
    """Whether to stream the results or not."""
    max_tokens: Optional[int] = None
    """Maximum number of tokens to generate."""

    class Config:
        """Configuration for this pydantic object."""

        allow_population_by_field_name = True

    @root_validator(pre=True)
    def build_extra(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Build extra kwargs from additional params that were passed in."""
        all_required_field_names = get_pydantic_field_names(cls)
        extra = values.get("config_kwargs", {})
        values["config_kwargs"] = build_extra_kwargs(extra, values, all_required_field_names)
        return values

    @root_validator(pre=False, skip_on_failure=True)
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key and python package exists in environment."""
        values["vmx_api_key"] = convert_to_secret_str(get_from_dict_or_env(values, "api_key", "VMX_API_KEY"))
        values["vmx_domain"] = get_from_dict_or_env(values, "domain", "VMX_DOMAIN")
        values["vmx_workspace_id"] = get_from_dict_or_env(values, "workspace_id", "VMX_WORKSPACE_ID", "")
        values["vmx_environment_id"] = get_from_dict_or_env(values, "environment_id", "VMX_ENVIRONMENT_ID", "")

        client_params = {
            "api_key": (values["vmx_api_key"].get_secret_value() if values["vmx_api_key"] else None),
            "domain": values["vmx_domain"],
            "workspace_id": values["vmx_workspace_id"] if values["vmx_environment_id"] else None,
            "environment_id": values["vmx_environment_id"] if values["vmx_environment_id"] else None,
        }

        if not values.get("client"):
            values["client"] = VMXClient(
                api_key=client_params["api_key"],
                domain=client_params["domain"],
                workspace_id=client_params["workspace_id"],
                environment_id=client_params["environment_id"],
            )
        return values

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling VM-X."""
        exclude_if_none = {"max_tokens": self.max_tokens}

        params = {
            "resource": self.resource_name,
            "config": {**self.config_kwargs, **{k: v for k, v in exclude_if_none.items() if v is not None}},
        }

        return params

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        payload = self._get_request_payload(messages, stop=stop, **kwargs)
        default_chunk_class: Type[BaseMessageChunk] = AIMessageChunk
        response = self.client.completion(request=CompletionRequest(**payload), stream=True)

        for chunk in response:
            message_chunk = _convert_delta_to_message_chunk(chunk, default_chunk_class)
            if chunk.usage:
                message_chunk.usage_metadata = UsageMetadata(
                    input_tokens=chunk.usage.prompt,
                    output_tokens=chunk.usage.completion,
                    total_tokens=chunk.usage.total,
                )

            generation_chunk = ChatGenerationChunk(
                message=message_chunk, generation_info={"metadata": MessageToDict(chunk.metadata)}
            )
            if run_manager:
                run_manager.on_llm_new_token(generation_chunk.text, chunk=generation_chunk)

            yield generation_chunk

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        if self.streaming:
            stream_iter = self._stream(messages, stop=stop, run_manager=run_manager, **kwargs)
            return generate_from_stream(stream_iter)
        payload = self._get_request_payload(messages, stop=stop, **kwargs)
        if "parallel_tool_calls" in payload:
            # TODO: Add back in after VM-X supports parallel tool calls
            del payload["parallel_tool_calls"]

        request = CompletionRequest(**payload)
        response = self.client.completion(request=request, stream=False)
        return self._create_chat_result(response)

    def _get_request_payload(
        self,
        input_: LanguageModelInput,
        *,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> dict:
        messages = self._convert_input(input_).to_messages()
        return {
            "messages": [_convert_message_to_vmx(m) for m in messages],
            **self._default_params,
            **kwargs,
        }

    def _create_chat_result(
        self,
        response: CompletionResponse,
    ) -> ChatResult:
        message = _convert_vmx_response_to_message(response)
        generations: List[ChatGeneration] = [ChatGeneration(message=message, generation_info={})]

        llm_output = {
            "token_usage": response.usage,
            "metadata": response.metadata,
        }

        return ChatResult(generations=generations, llm_output=llm_output)

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get the identifying parameters."""
        return {"resource_name": self.resource_name, **self._default_params}

    def _get_invocation_params(self, stop: Optional[List[str]] = None, **kwargs: Any) -> Dict[str, Any]:
        """Get the parameters used to invoke the model."""
        return {
            "resource": self.resource_name,
            **super()._get_invocation_params(stop=stop),
            **self._default_params,
            **kwargs,
        }

    def _get_ls_params(self, stop: Optional[List[str]] = None, **kwargs: Any) -> LangSmithParams:
        """Get standard params for tracing."""
        params = self._get_invocation_params(stop=stop, **kwargs)

        # TODO: Investigate how LangSmith works here.
        ls_params = LangSmithParams(
            ls_provider="vmx",
            ls_resource_name=self.resource_name,
            ls_model_type="chat",
        )
        if ls_max_tokens := params.get("max_tokens", self.max_tokens):
            ls_params["ls_max_tokens"] = ls_max_tokens

        return ls_params

    @property
    def _llm_type(self) -> str:
        """Return type of chat model."""
        return "vmx-chat"

    def bind_tools(
        self,
        tools: Sequence[Union[Dict[str, Any], Type, Callable, BaseTool]],
        *,
        tool_choice: Optional[Union[dict, str, Literal["auto", "none", "required", "any"], bool]] = None,
        strict: Optional[bool] = None,
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, BaseMessage]:
        """Bind tool-like objects to this chat model.

        Assumes model is compatible with VM-X tool-calling API.

        Args:
            tools: A list of tool definitions to bind to this chat model.
                Supports any tool definition handled by
                :meth:`langchain_core.utils.function_calling.convert_to_vmx_tool`.
            tool_choice: Which tool to require the model to call.
                Options are:
                    - str of the form ``"<<tool_name>>"``: calls <<tool_name>> tool.
                    - ``"auto"``: automatically selects a tool (including no tool).
                    - ``"none"``: does not call a tool.
                    - ``"any"`` or ``"required"`` or ``True``: force at least one tool to be called.
                    - dict of the form ``{"type": "function", "function": {"name": <<tool_name>>}}``: calls <<tool_name>> tool.
                    - ``False`` or ``None``: no effect, default VM-X behavior.
            strict: If True, model output is guaranteed to exactly match the JSON Schema
                provided in the tool definition.

            kwargs: Any additional parameters are passed directly to
                ``self.bind(**kwargs)``.
        """  # noqa: E501

        formatted_tools = [convert_to_vmx_tool(tool, strict=strict) for tool in tools]
        if tool_choice:
            if isinstance(tool_choice, str):
                if tool_choice not in ("auto", "none", "any", "required"):
                    tool_choice = RequestToolChoiceItem(
                        type="function", function=RequestToolChoiceFunction(name=tool_choice)
                    )

                if tool_choice == "any":
                    tool_choice = "required"

            elif isinstance(tool_choice, bool):
                tool_choice = "required"
            elif isinstance(tool_choice, RequestToolChoiceItem):
                tool_names = [formatted_tool.function.name for formatted_tool in formatted_tools]
                if not any(tool_name == tool_choice.function.name for tool_name in tool_names):
                    raise ValueError(
                        f"Tool choice {tool_choice} was specified, but the only " f"provided tools were {tool_names}."
                    )

            kwargs["tool_choice"] = tool_choice
        return super().bind(tools=formatted_tools, **kwargs)

    def with_structured_output(
        self,
        schema: Optional[_DictOrPydanticClass] = None,
        *,
        method: Literal["function_calling"] = "function_calling",
        include_raw: bool = False,
        strict: Optional[bool] = None,
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, _DictOrPydantic]:
        """Model wrapper that returns outputs formatted to match the given schema.

        Args:
            schema:
                The output schema. Can be passed in as:

                    - an VMX function/tool schema,
                    - a JSON Schema,
                    - a TypedDict class,
                    - or a Pydantic class.
                If ``schema`` is a Pydantic class then the model output will be a
                Pydantic instance of that class, and the model-generated fields will be
                validated by the Pydantic class. Otherwise the model output will be a
                dict and will not be validated. See :meth:`langchain_vmxai.utils.function_calling.convert_to_vmx_tool`
                for more on how to properly specify types and descriptions of
                schema fields when specifying a Pydantic or TypedDict class.


            method:
                The method for steering model generation, one of:

                    - "function_calling":
                        Uses VMX's tool-calling (formerly called function calling)

            include_raw:
                If False then only the parsed structured output is returned. If
                an error occurs during model output parsing it will be raised. If True
                then both the raw model response (a BaseMessage) and the parsed model
                response will be returned. If an error occurs during output parsing it
                will be caught and returned as well. The final output is always a dict
                with keys "raw", "parsed", and "parsing_error".
            strict:
                - True:
                    Model output is guaranteed to exactly match the schema.
                - False:
                    Input schema will not be validated and model output will not be
                    validated.
                - None:
                    ``strict`` argument will not be passed to the model.

            kwargs: Additional keyword args aren't supported.

        Returns:
            A Runnable that takes same inputs as a :class:`langchain_core.language_models.chat.BaseChatModel`.

            If ``include_raw`` is False and ``schema`` is a Pydantic class, Runnable outputs
            an instance of ``schema`` (i.e., a Pydantic object).

            Otherwise, if ``include_raw`` is False then Runnable outputs a dict.

            If ``include_raw`` is True, then Runnable outputs a dict with keys:

                - "raw": BaseMessage
                - "parsed": None if there was a parsing error, otherwise the type depends on the ``schema`` as described above.
                - "parsing_error": Optional[BaseException]

        Example: schema=Pydantic class, method="function_calling", include_raw=False, strict=True:
            .. note:: Valid schemas when using ``strict`` = True

            .. code-block:: python

                from typing import Optional

                from langchain_vmxai import ChatVMX
                from langchain_core.pydantic_v1 import BaseModel, Field


                class AnswerWithJustification(BaseModel):
                    '''An answer to the user question along with justification for the answer.'''

                    answer: str
                    justification: Optional[str] = Field(
                        default=..., description="A justification for the answer."
                    )


                llm = ChatVMX(resource="default")
                structured_llm = llm.with_structured_output(
                    AnswerWithJustification, strict=True
                )

                structured_llm.invoke(
                    "What weighs more a pound of bricks or a pound of feathers"
                )

                # -> AnswerWithJustification(
                #     answer='They weigh the same',
                #     justification='Both a pound of bricks and a pound of feathers weigh one pound. The weight is the same, but the volume or density of the objects may differ.'
                # )

        Example: schema=Pydantic class, method="function_calling", include_raw=True:
            .. code-block:: python

                from langchain_vmxai import ChatVMX
                from langchain_core.pydantic_v1 import BaseModel


                class AnswerWithJustification(BaseModel):
                    '''An answer to the user question along with justification for the answer.'''

                    answer: str
                    justification: str


                llm = ChatVMX(resource="default")
                structured_llm = llm.with_structured_output(
                    AnswerWithJustification, include_raw=True
                )

                structured_llm.invoke(
                    "What weighs more a pound of bricks or a pound of feathers"
                )
                # -> {
                #     'raw': AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_Ao02pnFYXD6GN1yzc0uXPsvF', 'function': {'arguments': '{"answer":"They weigh the same.","justification":"Both a pound of bricks and a pound of feathers weigh one pound. The weight is the same, but the volume or density of the objects may differ."}', 'name': 'AnswerWithJustification'}, 'type': 'function'}]}),
                #     'parsed': AnswerWithJustification(answer='They weigh the same.', justification='Both a pound of bricks and a pound of feathers weigh one pound. The weight is the same, but the volume or density of the objects may differ.'),
                #     'parsing_error': None
                # }

        Example: schema=TypedDict class, method="function_calling", include_raw=False:
            .. code-block:: python

                # IMPORTANT: If you are using Python <=3.8, you need to import Annotated
                # from typing_extensions, not from typing.
                from typing_extensions import Annotated, TypedDict

                from langchain_vmxai import ChatVMX


                class AnswerWithJustification(TypedDict):
                    '''An answer to the user question along with justification for the answer.'''

                    answer: str
                    justification: Annotated[
                        Optional[str], None, "A justification for the answer."
                    ]


                llm = ChatVMX(resource="default")
                structured_llm = llm.with_structured_output(AnswerWithJustification)

                structured_llm.invoke(
                    "What weighs more a pound of bricks or a pound of feathers"
                )
                # -> {
                #     'answer': 'They weigh the same',
                #     'justification': 'Both a pound of bricks and a pound of feathers weigh one pound. The weight is the same, but the volume and density of the two substances differ.'
                # }

        Example: schema=VMX function schema, method="function_calling", include_raw=False:
            .. code-block:: python

                from langchain_vmxai import ChatVMX

                oai_schema = {
                    'name': 'AnswerWithJustification',
                    'description': 'An answer to the user question along with justification for the answer.',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'answer': {'type': 'string'},
                            'justification': {'description': 'A justification for the answer.', 'type': 'string'}
                        },
                       'required': ['answer']
                   }
               }

                llm = ChatVMX(resource="default")
                structured_llm = llm.with_structured_output(oai_schema)

                structured_llm.invoke(
                    "What weighs more a pound of bricks or a pound of feathers"
                )
                # -> {
                #     'answer': 'They weigh the same',
                #     'justification': 'Both a pound of bricks and a pound of feathers weigh one pound. The weight is the same, but the volume and density of the two substances differ.'
                # }
        """  # noqa: E501
        if kwargs:
            raise ValueError(f"Received unsupported arguments {kwargs}")
        if strict is not None and method == "json_mode":
            raise ValueError("Argument `strict` is not supported with `method`='json_mode'")
        is_pydantic_schema = _is_pydantic_class(schema)
        if method == "function_calling":
            if schema is None:
                raise ValueError("schema must be specified when method is not 'json_mode'. " "Received None.")
            tool_name = convert_to_vmx_tool(schema).function.name
            llm = self.bind_tools(
                [schema],
                tool_choice=tool_name,
                parallel_tool_calls=False,
                strict=strict,
            )
            if is_pydantic_schema:
                output_parser: OutputParserLike = PydanticToolsParser(
                    tools=[schema],  # type: ignore[list-item]
                    first_tool_only=True,  # type: ignore[list-item]
                )
            else:
                output_parser = JsonOutputKeyToolsParser(key_name=tool_name, first_tool_only=True)
        else:
            raise ValueError(f"Unrecognized method argument. Expected one of 'function_calling'. Received: '{method}'")

        if include_raw:
            parser_assign = RunnablePassthrough.assign(
                parsed=itemgetter("raw") | output_parser, parsing_error=lambda _: None
            )
            parser_none = RunnablePassthrough.assign(parsed=lambda _: None)
            parser_with_fallback = parser_assign.with_fallbacks([parser_none], exception_key="parsing_error")
            return RunnableMap(raw=llm) | parser_with_fallback
        else:
            return llm | output_parser


class ChatVMX(BaseChatVMX):
    """VMX chat model integration.

    Setup:
        Install ``langchain-vm-x-ai`` and set environment variable ``VMX_API_KEY``.

        .. code-block:: bash

            pip install -U langchain-vm-x-ai
            export VMX_API_KEY="your-api-key"

    Key init args — completion params:
        resource: str
            Name of VMX resource to use.
        max_tokens: Optional[int]
            Max number of tokens to generate.

    Key init args — client params:
        api_key: Optional[str]
            VMX API key. If not passed in will be read from env var VMX_API_KEY.

    See full list of supported init args and their descriptions in the params section.

    Instantiate:
        .. code-block:: python

            from langchain_vmxai import ChatVMX

            llm = ChatVMX(
                resource="default",
                max_tokens=None,
                # api_key="...",
                # domain="...",
                # other params...
            )

    Invoke:
        .. code-block:: python

            messages = [
                (
                    "system",
                    "You are a helpful translator. Translate the user sentence to French.",
                ),
                ("human", "I love programming."),
            ]
            llm.invoke(messages)

        .. code-block:: python

            AIMessage(
                content="J'adore la programmation.",
                response_metadata={
                    "token_usage": {
                        "completion": 5,
                        "prompt": 31,
                        "total": 36,
                    },
                    "metadata: {
                        "primary": true,
                        "provider": "openai",
                        "model": "gpt-40",
                        "done": true,
                        "success": true,
                    }
                },
                id="run-012cffe2-5d3d-424d-83b5-51c6d4a593d1-0",
                usage_metadata={"input_tokens": 31, "output_tokens": 5, "total_tokens": 36},
            )

    Stream:
        .. code-block:: python

            for chunk in llm.stream(messages):
                print(chunk)

        .. code-block:: python

            AIMessageChunk(content="", id="run-9e1517e3-12bf-48f2-bb1b-2e824f7cd7b0")
            AIMessageChunk(content="J", id="run-9e1517e3-12bf-48f2-bb1b-2e824f7cd7b0")
            AIMessageChunk(content="'adore", id="run-9e1517e3-12bf-48f2-bb1b-2e824f7cd7b0")
            AIMessageChunk(content=" la", id="run-9e1517e3-12bf-48f2-bb1b-2e824f7cd7b0")
            AIMessageChunk(
                content=" programmation", id="run-9e1517e3-12bf-48f2-bb1b-2e824f7cd7b0"
            )
            AIMessageChunk(content=".", id="run-9e1517e3-12bf-48f2-bb1b-2e824f7cd7b0")
            AIMessageChunk(
                content="",
                response_metadata={'metadata': {'primary': True, 'provider': 'openai', 'model': 'gpt-4o', 'success': True}},
                id="run-9e1517e3-12bf-48f2-bb1b-2e824f7cd7b0",
            )

        .. code-block:: python

            stream = llm.stream(messages)
            full = next(stream)
            for chunk in stream:
                full += chunk
            full

        .. code-block:: python

            AIMessageChunk(
                content="J'adore la programmation.",
                response_metadata={'metadata': {'primary': True, 'provider': 'openai', 'model': 'gpt-4o', 'success': True}},
                id="run-bf917526-7f58-4683-84f7-36a6b671d140",
            )

    Tool calling:
        .. code-block:: python

            from langchain_core.pydantic_v1 import BaseModel, Field


            class GetWeather(BaseModel):
                '''Get the current weather in a given location'''

                location: str = Field(
                    ..., description="The city and state, e.g. San Francisco, CA"
                )


            class GetPopulation(BaseModel):
                '''Get the current population in a given location'''

                location: str = Field(
                    ..., description="The city and state, e.g. San Francisco, CA"
                )


            llm_with_tools = llm.bind_tools(
                [GetWeather, GetPopulation]
                # strict = True  # enforce tool args schema is respected
            )
            ai_msg = llm_with_tools.invoke(
                "Which city is hotter today and which is bigger: LA or NY?"
            )
            ai_msg.tool_calls

        .. code-block:: python

            [
                {
                    "name": "GetWeather",
                    "args": {"location": "Los Angeles, CA"},
                    "id": "call_6XswGD5Pqk8Tt5atYr7tfenU",
                },
                {
                    "name": "GetWeather",
                    "args": {"location": "New York, NY"},
                    "id": "call_ZVL15vA8Y7kXqOy3dtmQgeCi",
                },
                {
                    "name": "GetPopulation",
                    "args": {"location": "Los Angeles, CA"},
                    "id": "call_49CFW8zqC9W7mh7hbMLSIrXw",
                },
                {
                    "name": "GetPopulation",
                    "args": {"location": "New York, NY"},
                    "id": "call_6ghfKxV264jEfe1mRIkS3PE7",
                },
            ]

    Structured output:
        .. code-block:: python

            from typing import Optional

            from langchain_core.pydantic_v1 import BaseModel, Field


            class Joke(BaseModel):
                '''Joke to tell user.'''

                setup: str = Field(description="The setup of the joke")
                punchline: str = Field(description="The punchline to the joke")
                rating: Optional[int] = Field(description="How funny the joke is, from 1 to 10")


            structured_llm = llm.with_structured_output(Joke)
            structured_llm.invoke("Tell me a joke about cats")

        .. code-block:: python

            Joke(
                setup="Why was the cat sitting on the computer?",
                punchline="To keep an eye on the mouse!",
                rating=None,
            )

        See ``ChatVMX.with_structured_output()`` for more.

    Token usage:
        .. code-block:: python

            ai_msg = llm.invoke(messages)
            ai_msg.usage_metadata

        .. code-block:: python

            {"input_tokens": 28, "output_tokens": 5, "total_tokens": 33}

    Response metadata:
        .. code-block:: python

            ai_msg = llm.invoke(messages)
            ai_msg.response_metadata

        .. code-block:: python

            {
                "token_usage": {
                    "completion": 5,
                    "prompt": 28,
                    "total": 33,
                },
                "metadata": {
                    "primary": true,
                    "provider": "openai",
                    "model": "gpt-40",
                    "done": true,
                    "success": true,
                }
            }

    """  # noqa: E501

    @property
    def lc_secrets(self) -> Dict[str, str]:
        return {"vmx_api_key": "VMX_API_KEY"}

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        """Get the namespace of the langchain object."""
        return ["langchain", "chat_models", "vmx"]

    @property
    def lc_attributes(self) -> Dict[str, Any]:
        attributes: Dict[str, Any] = {}

        if self.vmx_domain:
            attributes["vmx_domain"] = self.vmx_domain

        if self.vmx_workspace_id:
            attributes["vmx_workspace_id"] = self.vmx_workspace_id

        if self.vmx_environment_id:
            attributes["vmx_environment_id"] = self.vmx_environment_id

        return attributes

    @classmethod
    def is_lc_serializable(cls) -> bool:
        """Return whether this model can be serialized by Langchain."""
        return True


def _is_pydantic_class(obj: Any) -> bool:
    return isinstance(obj, type) and is_basemodel_subclass(obj)


def _lc_tool_call_to_vmx_tool_call(tool_call: ToolCall) -> RequestMessageToolCall:
    return RequestMessageToolCall(
        id=tool_call["id"],
        type="function",
        function=RequestMessageToolCallFunction(name=tool_call["name"], arguments=json.dumps(tool_call["args"])),
    )


def _lc_invalid_tool_call_to_vmx_tool_call(
    invalid_tool_call: InvalidToolCall,
) -> RequestMessageToolCall:
    return RequestMessageToolCall(
        id=invalid_tool_call["id"],
        type="function",
        function=RequestMessageToolCallFunction(name=invalid_tool_call["name"], arguments=invalid_tool_call["args"]),
    )
