"""Methods for creating function specs in the style of VMX Tools."""

from __future__ import annotations

import collections
import inspect
import logging
import typing
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
    cast,
)

from langchain_core.pydantic_v1 import BaseModel, Field, create_model
from langchain_core.utils.json_schema import dereference_refs
from langchain_core.utils.pydantic import is_basemodel_subclass
from typing_extensions import Annotated, TypedDict, get_args, get_origin, is_typeddict
from vmxai import RequestToolFunction, RequestTools

if TYPE_CHECKING:
    from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)

PYTHON_TO_JSON_TYPES = {
    "str": "string",
    "int": "integer",
    "float": "number",
    "bool": "boolean",
}


class FunctionDescription(TypedDict):
    """Representation of a callable function to send to an LLM."""

    name: str
    """The name of the function."""
    description: str
    """A description of the function."""
    parameters: dict
    """The parameters of the function."""


class ToolDescription(TypedDict):
    """Representation of a callable function to the VMX API."""

    type: Literal["function"]
    """The type of the tool."""
    function: FunctionDescription
    """The function description."""


def _rm_titles(kv: dict, prev_key: str = "") -> dict:
    new_kv = {}
    for k, v in kv.items():
        if k == "title":
            if isinstance(v, dict) and prev_key == "properties" and "title" in v:
                new_kv[k] = _rm_titles(v, k)
            else:
                continue
        elif isinstance(v, dict):
            new_kv[k] = _rm_titles(v, k)
        else:
            new_kv[k] = v
    return new_kv


def _convert_pydantic_to_vmx_function(
    model: Type[BaseModel],
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    rm_titles: bool = True,
) -> RequestToolFunction:
    """Converts a Pydantic model to a function description for the VMX API.

    Args:
        model: The Pydantic model to convert.
        name: The name of the function. If not provided, the title of the schema will be
            used.
        description: The description of the function. If not provided, the description
            of the schema will be used.
        rm_titles: Whether to remove titles from the schema. Defaults to True.

    Returns:
        The function description.
    """
    schema = schema = model.model_json_schema() if hasattr(model, "model_json_schema") else model.schema()
    schema = dereference_refs(schema)
    schema.pop("definitions", None)
    title = schema.pop("title", "")
    default_description = schema.pop("description", "")
    return RequestToolFunction(
        name=name or title,
        description=description or default_description,
        parameters=_rm_titles(schema) if rm_titles else schema,
    )


def _get_python_function_name(function: Callable) -> str:
    """Get the name of a Python function."""
    return function.__name__


def _convert_python_function_to_vmx_function(
    function: Callable,
) -> RequestToolFunction:
    """Convert a Python function to an VM-X function-calling API compatible dict.

    Assumes the Python function has type hints and a docstring with a description. If
        the docstring has Google Python style argument descriptions, these will be
        included as well.

    Args:
        function: The Python function to convert.

    Returns:
        The VM-X function description.
    """
    from langchain_core import tools

    func_name = _get_python_function_name(function)
    model = tools.create_schema_from_function(
        func_name,
        function,
        filter_args=(),
        parse_docstring=True,
        error_on_invalid_docstring=False,
        include_injected=False,
    )
    return _convert_pydantic_to_vmx_function(
        model,
        name=func_name,
        description=model.__doc__,
    )


def _convert_typed_dict_to_vmx_function(typed_dict: Type) -> RequestToolFunction:
    visited: Dict = {}
    model = cast(
        Type[BaseModel],
        _convert_any_typed_dicts_to_pydantic(typed_dict, visited=visited),
    )
    return _convert_pydantic_to_vmx_function(model)


_MAX_TYPED_DICT_RECURSION = 25


def _convert_any_typed_dicts_to_pydantic(
    type_: Type,
    *,
    visited: Dict,
    depth: int = 0,
) -> Type:
    if type_ in visited:
        return visited[type_]
    elif depth >= _MAX_TYPED_DICT_RECURSION:
        return type_
    elif is_typeddict(type_):
        typed_dict = type_
        docstring = inspect.getdoc(typed_dict)
        annotations_ = typed_dict.__annotations__
        description, arg_descriptions = _parse_google_docstring(docstring, list(annotations_))
        fields: dict = {}
        for arg, arg_type in annotations_.items():
            if get_origin(arg_type) is Annotated:
                annotated_args = get_args(arg_type)
                new_arg_type = _convert_any_typed_dicts_to_pydantic(annotated_args[0], depth=depth + 1, visited=visited)
                field_kwargs = {k: v for k, v in zip(("default", "description"), annotated_args[1:])}
                if (field_desc := field_kwargs.get("description")) and not isinstance(field_desc, str):
                    raise ValueError(
                        f"Invalid annotation for field {arg}. Third argument to "
                        f"Annotated must be a string description, received value of "
                        f"type {type(field_desc)}."
                    )
                elif arg_desc := arg_descriptions.get(arg):
                    field_kwargs["description"] = arg_desc
                else:
                    pass
                fields[arg] = (new_arg_type, Field(**field_kwargs))
            else:
                new_arg_type = _convert_any_typed_dicts_to_pydantic(arg_type, depth=depth + 1, visited=visited)
                field_kwargs = {"default": ...}
                if arg_desc := arg_descriptions.get(arg):
                    field_kwargs["description"] = arg_desc
                fields[arg] = (new_arg_type, Field(**field_kwargs))
        model = create_model(typed_dict.__name__, **fields)
        model.__doc__ = description
        visited[typed_dict] = model
        return model
    elif (origin := get_origin(type_)) and (type_args := get_args(type_)):
        subscriptable_origin = _py_38_safe_origin(origin)
        type_args = tuple(
            _convert_any_typed_dicts_to_pydantic(arg, depth=depth + 1, visited=visited) for arg in type_args
        )
        return subscriptable_origin[type_args]
    else:
        return type_


def _format_tool_to_vmx_function(tool: BaseTool) -> RequestToolFunction:
    """Format tool into the VMX function API.

    Args:
        tool: The tool to format.

    Returns:
        The function description.
    """
    if tool.tool_call_schema:
        return _convert_pydantic_to_vmx_function(tool.tool_call_schema, name=tool.name, description=tool.description)
    else:
        return RequestToolFunction(
            name=tool.name,
            description=tool.description,
            parameters={
                "properties": {
                    "__arg1": {"title": "__arg1", "type": "string"},
                },
                "required": ["__arg1"],
                "type": "object",
            },
        )


def convert_to_vmx_function(
    function: Union[Dict[str, Any], Type, Callable, BaseTool],
    *,
    strict: Optional[bool] = None,
) -> RequestToolFunction:
    """Convert a raw function/class to an VMX function.

    Args:
        function:
            A dictionary, Pydantic BaseModel class, TypedDict class, a LangChain
            Tool object, or a Python function. If a dictionary is passed in, it is
            assumed to already be a valid VMX function or a JSON schema with
            top-level 'title' and 'description' keys specified.
        strict:
            If True, model output is guaranteed to exactly match the JSON Schema
            provided in the function definition. If None, ``strict`` argument will not
            be included in function definition.

    Returns:
        A dict version of the passed in function which is compatible with the VMX
        function-calling API.

    Raises:
        ValueError: If function is not in a supported format.
    """
    from langchain_core.tools import BaseTool

    if isinstance(function, dict) and all(k in function for k in ("name", "description", "parameters")):
        vmx_function = RequestToolFunction(
            name=function["name"], description=function["description"], parameters=function["parameters"]
        )
    # a JSON schema with title and description
    elif isinstance(function, dict) and all(k in function for k in ("title", "description", "properties")):
        function = function.copy()
        vmx_function = RequestToolFunction(
            name=function.pop("title"),
            description=function.pop("description"),
            parameters=function,
        )
    elif isinstance(function, type) and is_basemodel_subclass(function):
        vmx_function = _convert_pydantic_to_vmx_function(function)
    elif is_typeddict(function):
        vmx_function = _convert_typed_dict_to_vmx_function(cast(Type, function))
    elif isinstance(function, BaseTool):
        vmx_function = _format_tool_to_vmx_function(function)
    elif callable(function):
        vmx_function = _convert_python_function_to_vmx_function(function)
    else:
        raise ValueError(
            f"Unsupported function\n\n{function}\n\nFunctions must be passed in"
            " as Dict, pydantic.BaseModel, or Callable. If they're a dict they must"
            " either be in VMX function format or valid JSON schema with top-level"
            " 'title' and 'description' keys."
        )

    if strict is not None:
        # vmx_function["strict"] = strict # TODO: Add this back in after updating the VMX API
        vmx_function.parameters["additionalProperties"] = False
    return vmx_function


def convert_to_vmx_tool(
    tool: Union[Dict[str, Any], Type[BaseModel], Callable, BaseTool],
    *,
    strict: Optional[bool] = None,
) -> RequestTools:
    """Convert a raw function/class to an VMX tool.

    Args:
        tool:
            Either a dictionary, a pydantic.BaseModel class, Python function, or
            BaseTool. If a dictionary is passed in, it is assumed to already be a valid
            VMX tool, or a JSON schema with top-level 'title' and
            'description' keys specified.
        strict:
            If True, model output is guaranteed to exactly match the JSON Schema
            provided in the function definition. If None, ``strict`` argument will not
            be included in tool definition.

    Returns:
        A dict version of the passed in tool which is compatible with the
        VMX tool-calling API.
    """
    if isinstance(tool, dict) and tool.get("type") == "function" and "function" in tool:
        return RequestTools(type="function", function=convert_to_vmx_function(tool["function"]))

    vmx_tool = RequestTools(type='function', function=convert_to_vmx_function(tool, strict=strict))
    return vmx_tool


def _parse_google_docstring(
    docstring: Optional[str],
    args: List[str],
    *,
    error_on_invalid_docstring: bool = False,
) -> Tuple[str, dict]:
    """Parse the function and argument descriptions from the docstring of a function.

    Assumes the function docstring follows Google Python style guide.
    """
    if docstring:
        docstring_blocks = docstring.split("\n\n")
        if error_on_invalid_docstring:
            filtered_annotations = {arg for arg in args if arg not in ("run_manager", "callbacks", "return")}
            if filtered_annotations and (len(docstring_blocks) < 2 or not docstring_blocks[1].startswith("Args:")):
                raise ValueError("Found invalid Google-Style docstring.")
        descriptors = []
        args_block = None
        past_descriptors = False
        for block in docstring_blocks:
            if block.startswith("Args:"):
                args_block = block
                break
            elif block.startswith("Returns:") or block.startswith("Example:"):
                # Don't break in case Args come after
                past_descriptors = True
            elif not past_descriptors:
                descriptors.append(block)
            else:
                continue
        description = " ".join(descriptors)
    else:
        if error_on_invalid_docstring:
            raise ValueError("Found invalid Google-Style docstring.")
        description = ""
        args_block = None
    arg_descriptions = {}
    if args_block:
        arg = None
        for line in args_block.split("\n")[1:]:
            if ":" in line:
                arg, desc = line.split(":", maxsplit=1)
                arg_descriptions[arg.strip()] = desc.strip()
            elif arg:
                arg_descriptions[arg.strip()] += " " + line.strip()
    return description, arg_descriptions


def _py_38_safe_origin(origin: Type) -> Type:
    origin_map: Dict[Type, Any] = {
        dict: Dict,
        list: List,
        tuple: Tuple,
        set: Set,
        collections.abc.Iterable: typing.Iterable,
        collections.abc.Mapping: typing.Mapping,
        collections.abc.Sequence: typing.Sequence,
        collections.abc.MutableMapping: typing.MutableMapping,
    }
    return cast(Type, origin_map.get(origin, origin))
