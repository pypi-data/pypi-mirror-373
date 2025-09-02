from pydantic import BaseModel, computed_field, create_model, model_validator, Field
from typing import List, Callable, Union, Optional, Type, Any, Dict, Tuple, Literal
import logging
from gepeto.prompts import Prompt


logger = logging.getLogger(__name__)


AgentFunction = Callable[[], Union[str, "Agent", dict]]


class Agent(BaseModel):
    id: int
    name: str = "Agent"
    model: str = "gpt-4o"
    instructions: Union[str, Callable[[], str], Prompt] = "You are a helpful agent"
    functions: List[AgentFunction] = Field(default_factory=list)
    tool_choice: str = "auto"
    parallel_tool_calls: bool = True
    max_tokens: int = 4096
    temperature: float = 0.0
    response_schema: Optional[Dict[str, Any]] = None
    _response_model: Optional[Type[BaseModel]] = None

    @model_validator(mode="after")
    def build_response_model(self) -> "Agent":
        if self.response_schema:
            self._response_model = self.response_schema_as_pydantic()
        return self

    @computed_field
    @property
    def response_model(self) -> Optional[Type[BaseModel]]:
        return self._response_model

    @classmethod
    def from_dict(cls, data: dict) -> "Agent":
        return cls(**data)

    def equip(
        self, funcs: Union[AgentFunction, List[AgentFunction], object, List[object]]
    ) -> None:
        """Add one or more functions to this agent's available functions.

        Args:
            funcs: A single function, list of functions, object (to add all its methods),
                  or list of objects (to add all methods from each object)
        """
        # Convert single item to list for uniform handling
        funcs_list = funcs if isinstance(funcs, list) else [funcs]

        for func in funcs_list:
            if isinstance(func, object) and not callable(func):
                # Get all callable, non-private methods from object
                methods = [
                    getattr(func, name)
                    for name in dir(func)
                    if callable(getattr(func, name)) and not name.startswith("_")
                ]
                self.functions.extend(methods)
            else:
                self.functions.append(func)

    def response_schema_as_pydantic(self) -> Union[BaseModel, None]:
        if not self.response_schema:
            return None

        # Create the initial models dictionary from $defs
        models = self._create_definition_models()
        # Create the main model using the populated models dictionary
        main_model = self._create_main_model(models)
        return main_model

    def _create_definition_models(self) -> Dict[str, BaseModel]:
        """Create Pydantic models for all definitions in the schema."""
        defs = self.response_schema.get("$defs", {})
        models = {}
        for def_name, def_schema in defs.items():
            models[def_name] = self._create_pydantic_model(def_name, def_schema, models)
        return models

    def _create_main_model(self, models: Dict[str, BaseModel]) -> BaseModel:
        """Create the main Pydantic model from the schema."""
        main_model_name = self.response_schema.get("title", "DynamicModel")
        main_properties = self.response_schema.get("properties", {})
        main_required = set(self.response_schema.get("required", []))
        main_fields = {}

        for field_name, field_info in main_properties.items():
            required = field_name in main_required
            main_fields[field_name] = self._process_field(field_info, required, models)

        return create_model(main_model_name, **main_fields, __base__=BaseModel)

    def _create_pydantic_model(
        self, model_name: str, schema: Dict[str, Any], models: Dict[str, BaseModel]
    ) -> BaseModel:
        """Create a Pydantic model from a JSON schema definition."""
        properties = schema.get("properties", {})
        required_fields = set(schema.get("required", []))
        fields = {}

        for field_name, field_info in properties.items():
            required = field_name in required_fields
            fields[field_name] = self._process_field(field_info, required, models)

        return create_model(model_name, **fields, __base__=BaseModel)

    def _process_field(
        self, field_info: Dict[str, Any], required: bool, models: Dict[str, BaseModel]
    ) -> Tuple[Any, Any]:
        """Process individual field information and return a tuple for Pydantic model creation."""
        type_mapping = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "array": list,
            "object": dict,
        }

        if "anyOf" in field_info:
            return self._process_union_field(field_info, required, type_mapping)
        elif "enum" in field_info:
            return self._process_enum_field(field_info, required)
        elif "$ref" in field_info:
            return self._process_ref_field(field_info, required, models)
        else:
            return self._process_basic_field(field_info, required, type_mapping)

    def _process_union_field(
        self, field_info: Dict[str, Any], required: bool, type_mapping: Dict[str, type]
    ) -> Tuple[Any, Any]:
        union_types = [
            type_mapping.get(option["type"], str)
            for option in field_info["anyOf"]
            if option["type"] != "null"
        ]
        field_type = Union[tuple(union_types)]
        default = field_info.get("default")
        return (field_type, ...) if required else (Optional[field_type], default)

    def _process_enum_field(
        self, field_info: Dict[str, Any], required: bool
    ) -> Tuple[Any, Any]:
        enum_values = tuple(field_info["enum"])
        enum_type = Literal[enum_values]
        return (enum_type, ...) if required else (Optional[enum_type], None)

    def _process_ref_field(
        self, field_info: Dict[str, Any], required: bool, models: Dict[str, BaseModel]
    ) -> Tuple[Any, Any]:
        ref_path = field_info["$ref"]
        ref_name = ref_path.split("/")[-1]
        if ref_name not in models:
            logger.error(f"Reference '{ref_name}' not found in $defs.")
            raise ValueError(f"Reference '{ref_name}' not found in $defs.")
        ref_model = models[ref_name]
        return (ref_model, ...) if required else (Optional[ref_model], None)

    def _process_basic_field(
        self, field_info: Dict[str, Any], required: bool, type_mapping: Dict[str, type]
    ) -> Tuple[Any, Any]:
        python_type = type_mapping.get(field_info.get("type"), str)
        if required:
            return (python_type, ...)
        default = field_info.get("default")
        return (Optional[python_type], default)
