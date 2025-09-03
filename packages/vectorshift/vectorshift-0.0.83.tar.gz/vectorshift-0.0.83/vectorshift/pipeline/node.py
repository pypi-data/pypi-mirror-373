from abc import ABC
from typing import Any, ClassVar, Dict, List, Type, Protocol, runtime_checkable, TypeVar, Generic, Optional
from bson import ObjectId
import re

@runtime_checkable
class NodeOutputs(Protocol):
    """Protocol for node outputs that can be statically type checked."""
    pass

T = TypeVar('T', bound=NodeOutputs)

class Node(ABC):
    # Class-level registry for node types
    _node_registry: ClassVar[Dict[str, Type['Node']]] = {}

    # Common inputs and outputs
    _COMMON_INPUTS: List[Dict[str, Any]] = []
    _COMMON_OUTPUTS: List[Dict[str, Any]] = []
    
    # Configuration patterns and their associated inputs/outputs - to be overridden by subclasses
    _CONFIGS: ClassVar[Dict[str, Dict[str, Any]]] = {}
    
    # List of parameters that affect configuration - to be overridden by subclasses
    _PARAMS: ClassVar[List[str]] = []

    def __init__(self, node_type: str, params: Dict[str, Any], id: str = None, node_name: str = None, execution_mode: str = None):
        """Initialize a node with its type and configuration parameters.
        
        Args:
            node_type: The type of node (e.g., "llm", "text", etc.)
            params: Dictionary of parameter values that determine the node's configuration.
                   These values are locked in for the lifetime of the node.
            id: Optional ID for the node. If not provided, one will be generated.
        """
        self.id = id if id else f"{node_type}_{str(ObjectId())}"
        self.node_type = node_type
        self.name = node_name
        self.task_name: str = None
        self.execution_mode = execution_mode
        
        # Validate and store params
        self._params = {}
        for param in self._PARAMS:
            if param not in params:
                raise ValueError(f"Missing required parameter: {param}")
            self._params[param] = params[param]
        
        # Initialize inputs and outputs based on configuration
        self.inputs: Dict[str, Any] = {}
        self.outputs: List[str] = []
        self.cyclic_inputs: Dict[str, Any] = {}
        
        # Get valid inputs and outputs for these params
        valid_inputs = self._get_valid_inputs_for_params()
        valid_outputs = self._get_valid_outputs_for_params()
        
        # Set up inputs with defaults from valid inputs
        for field, input_def in valid_inputs.items():
            self.inputs[field] = input_def.get('value')
        
        # Set up outputs
        self.outputs = valid_outputs

    @classmethod
    def register_node_type(cls, node_type: str):
        """Decorator to register node types with their implementing classes."""
        def decorator(node_class: Type['Node']) -> Type['Node']:
            cls._node_registry[node_type] = node_class
            return node_class
        return decorator

    @classmethod
    def from_json(cls, data: dict) -> 'Node':
        """Create a node instance from a JSON dictionary."""
        node_type = data.get('type')
        if not node_type:
            raise ValueError("JSON data must include 'type' field")
        node_class = cls._node_registry.get(node_type)
        if not node_class:
            raise ValueError(f"Unknown node type: {node_type}")

        return node_class.from_dict(data)

    def __getattr__(self, name: str) -> str:
        """Handle access to output names as attributes."""
        # Get valid outputs for current params
        valid_outputs = self._get_valid_outputs_for_params()
        
        # Check if output is valid for current configuration
        if name in self.outputs and name in valid_outputs:
            return f"{{{{ {self.id}.{name} }}}}"
        raise AttributeError(
            f"'{self.__class__.__name__}' has no output '{name}' for current parameter values: "
            f"{', '.join(f'{k}={v!r}' for k, v in self._params.items())}\n"
            f"Available outputs: {valid_outputs}"
        )

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
            id_pattern = "pipeline"
        elif object_type == "agents":
            id_pattern = "agent_id"
        elif object_type == "transformations":
            id_pattern = "transformation"
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
    def _match_config_key(config_key: str, param_values: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
        """Match a config key pattern against actual parameter values."""
        if not config_key or not param_values:
            return (False, {})
            
        # Check for dynamic pattern
        object_type, id_pattern = Node._parse_dynamic_pattern(config_key)
        if object_type and id_pattern:
            # Get the actual ID from params
            object_id = param_values.get(id_pattern)
            if not isinstance(object_id, str):
                object_id = object_id.get('object_id')
            if not object_id:
                return (False, {})
                
            try:
                # Fetch the object definition
                object_def = Node._fetch_object_definition(object_type, object_id)
                # Store the definition for use in _get_valid_inputs/outputs
                Node._cached_definitions[object_id] = object_def
                return (True, {})
            except Exception:
                return (False, {})
            
        # Handle regular pattern matching
        pattern_parts = config_key.split("**")
        if len(pattern_parts) != len(param_values):
            return (False, {})
            
        # Check each part against the corresponding value
        generic_params = {}
        for pattern, (param, value) in zip(pattern_parts, param_values.items()):
            if pattern.startswith("<") and pattern.endswith(">"):
                generic_params[pattern] = value
            elif pattern != "(*)" and str(value).lower() != pattern.lower():
                return (False, {})
                
        return (True, generic_params)

    # Cache for object definitions
    _cached_definitions: ClassVar[Dict[str, Any]] = {}

    def _get_valid_inputs_for_params(self) -> Dict[str, Dict[str, Any]]:
        """Get valid inputs based on the current parameter values."""
        valid_inputs = {input.get('field'): input for input in self._COMMON_INPUTS}
        valid_inputs['dependencies'] = {'field': 'dependencies', 'type': 'vec<string>', 'value': []}
        
        # Add inputs from configs
        for config_key, config in self._CONFIGS.items():
            matches, generic_params = self._match_config_key(config_key, self._params)
            if matches:
                # Check if this is a dynamic config
                object_type, id_pattern = self._parse_dynamic_pattern(config_key)
                if object_type and id_pattern:
                    # Get the object definition from cache
                    object_id = self._params[id_pattern]
                    if not isinstance(object_id, str):
                        object_id = object_id.get('object_id')
                    object_def = self._cached_definitions.get(object_id)
                    
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
                        type = str(input_def['type'])

                        if type.startswith("<") and type.endswith(">"):
                            input_def['type'] = generic_params[type]

                        valid_inputs[field] = input_def
        
        return valid_inputs

    def _get_valid_outputs_for_params(self) -> List[str]:
        """Get valid outputs based on the current parameter values."""
        valid_outputs = set(output.get('field') for output in self._COMMON_OUTPUTS)
        
        for config_key, config in self._CONFIGS.items():
            matches, _ = self._match_config_key(config_key, self._params)
            if matches:
                # Check if this is a dynamic config
                object_type, id_pattern = self._parse_dynamic_pattern(config_key)
                if object_type and id_pattern:
                    # Get the object definition from cache
                    object_id = self._params[id_pattern]
                    if not isinstance(object_id, str):
                        object_id = object_id.get('object_id')
                    object_def = self._cached_definitions.get(object_id)
                    
                    if object_def:
                        # Add outputs from the object definition
                        valid_outputs.update(object_def.outputs.keys())
                else:
                    # Handle regular config outputs
                    if 'outputs' in config:
                        for output_def in config['outputs']:
                            valid_outputs.add(output_def['field'])
        
        # handle dynamic outputs dependent on inputs
        fields_to_add = set()
        fields_to_remove = set()
        for field in valid_outputs:
            if field.startswith("[") and field.endswith("]"):
                stripped_parts = field[1:-1].split(".")
                inputs_map = self.inputs
                for part in stripped_parts:
                    inputs_map = inputs_map.get(part, {})
                fields_to_add.update(inputs_map.keys())
                fields_to_remove.add(field)
        
        # Add the collected fields after iteration
        valid_outputs.update(fields_to_add)
        valid_outputs -= fields_to_remove
        valid_outputs.add("complete")
        return list(valid_outputs)
    
    def set_output_name_attributes(self):
        """Set the output name attributes for the node."""
        self.outputs = self._get_valid_outputs_for_params()
        for output in self.outputs:
            def make_property(output_name):
                return property(lambda self, name=output_name: self.__getattr__(name))
            
            setattr(self.__class__, output, make_property(output))

    def update_inputs(self, **kwargs):
        """Update input values for the node.
        
        Args:
            **kwargs: Input values to update
            
        Raises:
            ValueError: If an invalid input is provided for the current configuration
        """
        # Get valid inputs for current params
        valid_inputs = self._get_valid_inputs_for_params()
        
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
            self.inputs[key] = value
    
    def get_dependencies(self) -> tuple[set[str], set[str]]:
        """Get the dependency node ids of the node."""
        non_cyclic_dependencies = set()
        dependencies = set()
        for input_value in self.inputs.values():
            node_input_deps = extract_dependecies_from_node_input(input_value)
            non_cyclic_dependencies.update(node_input_deps - dependencies)
            dependencies.update(node_input_deps)

        for cyclic_input_value in self.cyclic_inputs.values():
            node_input_deps = extract_dependecies_from_node_input(cyclic_input_value)
            dependencies.update(node_input_deps)

        return non_cyclic_dependencies, dependencies
    
    def add_cyclic_input(self, key: str, value: str):
        """Add a cyclic input to the node. This input value will be used during subsequent iterations of the node after the first iteration."""
         # Get valid inputs for current params
        valid_inputs = self._get_valid_inputs_for_params()
        if key not in valid_inputs:
            param_str = ", ".join(f"{k}={v!r}" for k, v in self._params.items())
            raise ValueError(
                f"Invalid input(s) for current parameters ({param_str}): {key}\n"
                f"Available inputs: {list(valid_inputs.keys())}"
            )
        self.cyclic_inputs[key] = value


    def set_node_task_name(self):
        """Set the task name based on the current parameterization."""
        if not hasattr(self, '_CONFIGS') or not hasattr(self, '_PARAMS'):
            self.task_name = self.node_type
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
        
        # Fallback to node type if no matching config found
        self.task_name = self.node_type


    def __str__(self) -> str:
        """Return a string representation of the node as a constructor call.
        
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
        """Return a detailed string representation of the node showing type, parameters, inputs, and outputs.
        
        Returns:
            A formatted string showing the node's type, current inputs, and available outputs.
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
    
def extract_dependecies_from_node_input(node_input: Any) -> list[str]:
    """Extract dependency node ids from a node input."""
    dependencies = set()
    if isinstance(node_input, str):
        variable_regex = re.compile(r"\{\{\s*([\w.]+)\s*\}\}")
        matches = variable_regex.findall(node_input)
        
        for match in matches:
            # Split by dot and take the first part (node_id)
            if "." in match:
                node_id = match.split(".")[0]
                dependencies.add(node_id)
    
    elif isinstance(node_input, list):
        for item in node_input:
            dependencies.update(extract_dependecies_from_node_input(item))
    
    elif isinstance(node_input, dict):
        for value in node_input.values():
            dependencies.update(extract_dependecies_from_node_input(value))
    
    return dependencies

