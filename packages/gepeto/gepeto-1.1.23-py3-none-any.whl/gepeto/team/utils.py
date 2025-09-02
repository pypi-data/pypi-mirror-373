import inspect
import typing
from typing import get_origin, get_args, Literal
from pydantic import BaseModel
from datetime import datetime


def debug_print(debug: bool, *args: str) -> None:
    if not debug:
        return
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = " ".join(map(str, args))
    print(f"\033[97m[\033[90m{timestamp}\033[97m]\033[90m {message}\033[0m")


TYPE_MAP = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    type(None): "null",
}


def is_pydantic_model(t) -> bool:
    """Return True if t is a subclass of pydantic.BaseModel."""
    return isinstance(t, type) and issubclass(t, BaseModel)


def parse_type(t) -> dict:
    """
    Recursively convert a Python/Pydantic type to a JSON-compatible schema.
    Includes handling for built-in types, Pydantic models, arrays, dicts, and Literal.
    """
    if t in TYPE_MAP:
        # Direct map for built-in types
        return {"type": TYPE_MAP[t]}

    # If it's a Pydantic model, parse its fields
    if is_pydantic_model(t):
        return model_to_schema(t)

    origin = get_origin(t)
    args = get_args(t)

    # Handle Literal[...]
    if origin is Literal:
        # e.g. Literal["s", "m", "l"]
        literal_values = list(args)
        # Attempt a single JSON "type" if all literal values share a Python type
        first_type = type(literal_values[0])
        if all(isinstance(v, first_type) for v in literal_values):
            mapped_type = TYPE_MAP.get(first_type, "string")
        else:
            mapped_type = "string"
        return {
            "type": mapped_type,
            "enum": literal_values,
        }

    # Handle list/tuple
    if origin in (list, tuple):
        # If the type is e.g. list[str], parse str
        if args:
            item_schema = parse_type(args[0])
        else:
            item_schema = {"type": "any"}
        return {"type": "array", "items": item_schema}

    # Handle dict
    if origin == dict:
        # Usually Dict[str, <something>]
        if len(args) == 2:
            _, val_type = args
        else:
            val_type = None
        val_schema = parse_type(val_type) if val_type else {"type": "any"}
        return {
            "type": "object",
            "additionalProperties": val_schema,
        }

    # Fallback to "string" if we can't map it more specifically
    return {"type": "string"}


def model_to_schema(model: typing.Type[BaseModel]) -> dict:
    """
    Given a Pydantic v2 model class, build a JSON schema definition for it.
    """
    props = {}
    required_fields = []

    for field_name, field_info in model.model_fields.items():
        # field_info.annotation is the type hint
        field_schema = parse_type(field_info.annotation)
        props[field_name] = field_schema
        if field_info.is_required():
            required_fields.append(field_name)

    return {
        "type": "object",
        "properties": props,
        "required": required_fields if required_fields else [],
        # Typically good practice to disallow extra fields unless you intentionally allow them
        "additionalProperties": False,
    }


def func_to_json(func) -> dict:
    """
    Introspect a function's signature to produce a JSON schema describing
    the function name, docstring, parameter structure, etc.
    """
    try:
        signature = inspect.signature(func)
    except ValueError as e:
        raise ValueError(f"Failed to get signature for {func.__name__}: {e}")

    properties = {}
    required = []

    for param in signature.parameters.values():
        param_type = param.annotation
        schema_for_param = parse_type(param_type)
        properties[param.name] = schema_for_param

        # If the parameter has no default, it's required
        if param.default == inspect._empty:
            required.append(param.name)

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": func.__doc__ or "",
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": False,
            },
        },
    }
