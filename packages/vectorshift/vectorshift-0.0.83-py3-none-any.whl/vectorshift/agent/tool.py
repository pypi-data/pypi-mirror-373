from abc import ABC
from typing import Any, ClassVar, Dict, List, Type, Protocol, runtime_checkable, TypeVar, Generic, Optional
from bson import ObjectId
from pydantic import BaseModel, Field

class ToolInput(BaseModel):
    type: str = Field(default="static", description="The type of the input: static (value must be provided for static inputs) or dynamic(description must be provided for dynamic inputs)")
    value: Optional[Any] = Field(default=None, description="The value of the input")
    description: Optional[str] = Field(default=None, description="The description of the input")

class Tool(ABC):
    # Class-level registry for tool types
    _tool_registry: ClassVar[Dict[str, Type['Tool']]] = {}

    # Common inputs
    _COMMON_INPUTS: List[Dict[str, Any]] = []
    
    # Configuration patterns and their associated inputs/outputs - to be overridden by subclasses
    _CONFIGS: ClassVar[Dict[str, Dict[str, Any]]] = {}
    
    # List of parameters that affect configuration - to be overridden by subclasses
    _PARAMS: ClassVar[List[str]] = []

    def __init__(self, tool_type: str, params: Dict[str, Any], id: str = None, tool_name: str = None, tool_description: str = None):
        """Initialize a tool with its type and configuration parameters.
        
        Args:
            tool_type: The type of tool (e.g., "llm", "text", etc.)
            params: Dictionary of parameter values that determine the tool's configuration.
                   These values are locked in for the lifetime of the tool.
            id: Optional ID for the tool. If not provided, one will be generated.
            tool_name: The name of the tool.
            tool_description: The description of the tool.
        """
        self.id = id if id else f"{tool_type}_{str(ObjectId())}"
        self.tool_type = tool_type
        self.name = tool_name
        self.description = tool_description
        self.inputs: Dict[str, Any] = {}
        
        # Validate and store params
        self._params = {}
        for param in self._PARAMS:
            if param not in params:
                raise ValueError(f"Missing required parameter: {param}")
            self._params[param] = params[param]

    @classmethod
    def register_tool_type(cls, tool_type: str):
        """Decorator to register tool types with their implementing classes."""
        def decorator(tool_class: Type['Tool']) -> Type['Tool']:
            cls._tool_registry[tool_type] = tool_class
            return tool_class
        return decorator

    @classmethod
    def from_json(cls, data: dict) -> 'Tool':
        """Create a tool instance from a JSON dictionary."""
        tool_value = data.get('value', {})
        tool_type = tool_value.get('node_type', {}).get('value')
        
        if not tool_type:
            raise ValueError("JSON data must include 'node_type' field")
        tool_class = cls._tool_registry.get(tool_type)
        if not tool_class:
            raise ValueError(f"Unknown tool type: {tool_type}")

        return tool_class.from_dict(data)

    @staticmethod
    def _parse_dynamic_pattern(config_key: str) -> tuple[Optional[str], Optional[str]]:
        """Parse a dynamic config pattern to extract object type and ID pattern.
        
        Args:
            config_key: The config key pattern (e.g., "[pipelines._id.<A>]")
            
        Returns:
            Tuple of (object_type, id_pattern) or (None, None) if not a dynamic pattern
        """
        if not (config_key.startswith("[") and config_key.endswith("]")):
            return None, None
        
        # Remove brackets
        pattern = config_key[1:-1]
        
        # Split into parts
        parts = pattern.split(".")
        
        if len(parts) < 2:
            return None, None
            
        object_type = parts[0]
        
        # Map object type to corresponding ID parameter name
        if object_type == "pipelines":
            id_pattern = "pipeline_id"
        elif object_type == "agents":
            id_pattern = "agent_id"
        elif object_type == "transformations":
            id_pattern = "transformation_id"
        else:
            # For other object types, use the object type with "_id" suffix
            id_pattern = f"{object_type}_id"
        
        return object_type, id_pattern

    @staticmethod
    def _fetch_object_definition(object_type: str, object_id: str) -> Dict[str, Any]:
        """Fetch object definition from the API.
        
        Args:
            object_type: Type of object to fetch (e.g., "pipelines", "agents")
            object_id: ID of the object to fetch
            
        Returns:
            Dictionary containing object definition
            
        Raises:
            RuntimeError: If object cannot be fetched
        """
        try:
            if object_type == "pipelines":
                from vectorshift import Pipeline
                return Pipeline.fetch(id=object_id)
            elif object_type == "agents":
                from vectorshift import Agent
                return Agent.fetch(id=object_id)
            elif object_type == "transformations":
                from vectorshift import Transformation
                return Transformation.fetch(id=object_id)
            else:
                raise ValueError(f"Unknown object type: {object_type}")
        except Exception as e:
            raise RuntimeError(f"Failed to fetch {object_type} definition: {str(e)}")

    @staticmethod
    def _match_config_key(config_key: str, param_values: Dict[str, Any]) -> bool:
        """Match a config key pattern against actual parameter values."""
        if not config_key or not param_values:
            return False
            
        # Check for dynamic pattern
        object_type, id_pattern = Tool._parse_dynamic_pattern(config_key)
        if object_type and id_pattern:
            # Get the actual ID from params
            object_id = param_values.get(id_pattern)
            if not object_id:
                return False
                
            try:
                # Fetch the object definition
                object_def = Tool._fetch_object_definition(object_type, object_id)
                # Store the definition for use in _get_valid_inputs/outputs
                Tool._cached_definitions[object_id] = object_def
                return True
            except Exception:
                return False
            
        # Handle regular pattern matching
        pattern_parts = config_key.split("**")
        if len(pattern_parts) != len(param_values):
            return False
            
        # Check each part against the corresponding value
        for pattern, (param, value) in zip(pattern_parts, param_values.items()):
            if pattern != "(*)" and str(value).lower() != pattern.lower():
                return False
                
        return True

    # Cache for object definitions
    _cached_definitions: ClassVar[Dict[str, Any]] = {}

    @classmethod
    def _get_valid_inputs_for_params(cls, param_values: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Get valid inputs based on the current parameter values."""
        valid_inputs = {input.get('field'): input for input in cls._COMMON_INPUTS}
        
        # Add inputs from configs
        for config_key, config in cls._CONFIGS.items():
            if cls._match_config_key(config_key, param_values):
                # Check if this is a dynamic config
                object_type, id_pattern = cls._parse_dynamic_pattern(config_key)
                if object_type and id_pattern:
                    # Get the object definition from cache
                    object_id = param_values[id_pattern]
                    object_def = cls._cached_definitions.get(object_id)
                    
                    if object_def:
                        # Add inputs from the object definition
                        for input_name, input_type in object_def.inputs.items():
                            valid_inputs[input_name] = {
                                'field': input_name,
                                'type': input_type,
                                'helper_text': f"Input from {object_type} {object_id}",
                                'value': None
                            }
                else:
                    # Handle regular config inputs
                    for input_def in config.get('inputs', []):
                        field = input_def['field']
                        valid_inputs[field] = input_def
        
        return valid_inputs

    @classmethod
    def get_available_inputs(cls, **params) -> Dict[str, Dict[str, Any]]:
        """Get available inputs based on the provided parameter values."""
        param_values = {param: params.get(param) for param in cls._PARAMS}
        return cls._get_valid_inputs_for_params(param_values)

    def update_inputs(self, **kwargs):
        """Update input values for the tool.
        
        Args:
            **kwargs: Input values to update
            
        Raises:
            ValueError: If an invalid input is provided for the current configuration
        """
        # Get valid inputs for current params
        valid_inputs = self._get_valid_inputs_for_params(self._params)
        
        # Check for invalid inputs
        invalid_inputs = []
        for key in kwargs:
            if key not in valid_inputs:
                invalid_inputs.append(key)
        
        if invalid_inputs:
            param_str = ", ".join(f"{k}={v!r}" for k, v in self._params.items())
            raise ValueError(
                f"Invalid input(s) for current parameters ({param_str}): {invalid_inputs}\n"
                f"Available inputs: {list(valid_inputs.keys())}"
            )
        
        # Update valid inputs
        for key, value in kwargs.items():
            if isinstance(value, ToolInput):
                self.inputs[key] = {
                    'type': value.type,
                    'value': value.value or value.description
                }
            else:
                self.inputs[key] = {
                    'type': 'static',
                    'value': value
                }

    def add_dynamic_inputs(self):
        """Add dynamic inputs to the tool."""
        # Get valid inputs for current params
        valid_inputs = self._get_valid_inputs_for_params(self._params)
        # Check for dynamic inputs
        for key in valid_inputs.keys():
            if key not in self.inputs:
                self.inputs[key] = {
                    'type': 'dynamic',
                    'value': "",
                }


    def set_tool_task_name(self):
        """Set the task name based on the current parameterization."""
        if not hasattr(self, '_CONFIGS') or not hasattr(self, '_PARAMS'):
            self.task_name = self.tool_type
            return
        
        # Get current parameter values
        current_params = []
        for param in self._PARAMS:
            if param in self.inputs:
                current_params.append(str(self.inputs[param]))
            else:
                current_params.append("(*)")
        
        # Find matching config
        for config_key, config_value in self._CONFIGS.items():
            config_parts = config_key.split("**")
            
            # Check if this config matches current parameters
            if len(config_parts) == len(current_params):
                matches = True
                for i, (config_part, current_param) in enumerate(zip(config_parts, current_params)):
                    # (*) matches any value, otherwise exact match required
                    if config_part != "(*)" and config_part != current_param:
                        matches = False
                        break
                
                if matches and "task_name" in config_value:
                    self.task_name = config_value["task_name"]
                    return
        
        # Fallback to tool type if no matching config found
        self.task_name = self.tool_type

    def __str__(self) -> str:
        """Return a string representation of the tool as a constructor call.
        
        Returns:
            A string in the format ClassName(input1="value1", input2="value2", ...)
        """
        # Get the actual class name
        class_name = self.__class__.__name__
        
        # Format each input as a key=value pair, properly handling different types
        input_pairs = []
        for field, value in self.inputs.items():
            if value is not None:  # Only include non-None values
                if isinstance(value, str):
                    formatted_value = f'"{value}"'
                elif isinstance(value, (list, dict)):
                    formatted_value = repr(value)
                else:
                    formatted_value = str(value)
                input_pairs.append(f"{field}={formatted_value}")
        
        # Join all input pairs with commas
        inputs_str = ", ".join(input_pairs)
        
        return f"{class_name}({inputs_str})"

    def __repr__(self) -> str:
        """Return a detailed string representation of the tool showing type, parameters, inputs, and outputs.
        
        Returns:
            A formatted string showing the tool's type, current inputs, and available outputs.
        """
        # Get the actual class name without the module prefix
        class_name = self.__class__.__name__
        
        # Format inputs section
        input_lines = []
        for field, value in self.inputs.items():
            # Format the value, handling special cases
            if isinstance(value, (list, dict)):
                formatted_value = repr(value)
            elif value is None:
                formatted_value = "None"
            else:
                formatted_value = f"'{value}'" if isinstance(value, str) else str(value)
            input_lines.append(f"    {field}: {formatted_value}")
        inputs_str = "\n".join(input_lines) if input_lines else "    None"

        # Format outputs section
        output_lines = []
        for output in self.outputs:
            output_lines.append(f"    {output}")
        outputs_str = "\n".join(output_lines) if output_lines else "    None"

        # Build the complete string
        return f"""{class_name} (id: {self.id})

Inputs:
{inputs_str}

Outputs:
{outputs_str}"""