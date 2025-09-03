from typing import Any, Dict, List, Optional, Type, Union, Protocol, runtime_checkable
import tomli
from pathlib import Path
import black
import ast
from textwrap import dedent
import shutil
from .node import Node, NodeOutputs
import re
import textwrap
import keyword


def load_toml_config(config_path: str) -> Dict[str, Any]:
    """Load and parse the TOML configuration file."""
    with open(config_path, 'rb') as f:
        return tomli.load(f)

def _format_type_annotation(type_str: str) -> str:
    """Convert TOML type strings to Python type annotations."""
    # Handle generic types (those with angle brackets that aren't vec, enum, interface, or map)
    if "<" in type_str and ">" in type_str and not (
        type_str.startswith('vec<') or 
        type_str.startswith('enum<') or 
        type_str.startswith('interface<') or 
        type_str.startswith('map<')
    ):
        # For generic types, just return Any
        return 'Any'
        
    if type_str.startswith('vec<'):
        inner_type = type_str[4:-1]  # Remove vec< and >
        return f"List[{_format_type_annotation(inner_type)}]"
    elif type_str.startswith('enum<'):
        inner_type = type_str[5:-1]  # Remove enum< and >
        if inner_type == 'string':
            return 'str'
        return inner_type
    elif type_str == 'string':
        return 'str'
    elif type_str == 'int32' or type_str == 'int64':
        return 'int'
    elif type_str == 'float32' or type_str == 'float64':
        return 'float'
    elif type_str == 'bool':
        return 'bool'
    elif type_str == 'file':
        return 'str'  # File paths are represented as strings
    elif type_str.startswith('interface<'):
        # For now, treat interfaces as Dict[str, Any]
        return 'Dict[str, Any]'
    elif type_str.startswith('map<'):
        # Handle map types, e.g., map<string, any> -> Dict[str, Any]
        key_type, value_type = type_str[4:-1].split(',')
        return f"Dict[{_format_type_annotation(key_type.strip())}, {_format_type_annotation(value_type.strip())}]"
    return 'Any'  # Default to Any for unknown types

def _format_default_value(value: Any, python_type: str) -> str:
    """Format a default value based on its Python type."""
    if value is None:
        # For List types, default to empty list instead of None
        if python_type.startswith('List['):
            return "[]"
        return "None"
    if python_type == 'str':
        return f'"{value}"'
    elif python_type == 'List[str]' and isinstance(value, list):
        formatted_items = [f'"{v}"' for v in value]
        return f'[{", ".join(formatted_items)}]'
    elif python_type == 'bool':
        # Convert JavaScript-style boolean to Python-style
        return 'True' if value else 'False'
    return str(value)

def _escape_reserved_keyword(param: str) -> str:
    """Escape Python reserved keywords by appending underscore."""
    if keyword.iskeyword(param):
        return f"{param}_"
    return param

def generate_node_class(node_type: str, node_config: Dict[str, Any]) -> Type[Node]:
    """Generate a Node class from TOML configuration."""
    
    # Get the docstring from helper_text if available
    docstring = node_config.get('helper_text', '')
    if not docstring and 'short_description' in node_config:
        docstring = node_config['short_description']
    # If still no docstring, use the title as fallback
    if not docstring and 'title' in node_config:
        docstring = node_config['title']
    
    # Get default inputs and outputs
    defaults = node_config.get('defaults', {})
    default_inputs = {
        input_def['field']: input_def.get('value', None)
        for input_def in defaults.get('inputs', [])
    }
    default_outputs = [output_def['field'] for output_def in defaults.get('outputs', [])]

    # Create the class
    @Node.register_node_type(node_type)
    class GeneratedNode(Node):
        def __init__(self, **kwargs):
            # Initialize with node type from TOML key
            super().__init__(node_type=node_type)
            
            # Set default values for inputs
            self.inputs = default_inputs.copy()
            
            # Update with provided values
            for key, value in kwargs.items():
                if key in self.inputs:
                    self.inputs[key] = value
                else:
                    raise ValueError(f"Unknown input parameter: {key}")
            
            # Set outputs
            self.outputs = default_outputs.copy()
            
            # Set task name if specified
            if 'task_name' in kwargs:
                self.task_name = kwargs['task_name']

        @classmethod
        def from_dict(cls, data: dict) -> 'GeneratedNode':
            """Create a node instance from a dictionary."""
            inputs = data.get('inputs', {})
            return cls(**inputs)

    # Set class name, docstring and other metadata
    GeneratedNode.__name__ = f"{node_type.title().replace('_', '')}Node"
    GeneratedNode.__doc__ = docstring
    
    return GeneratedNode

def _escape_field_name(field: str) -> str:
    """Escape a field name for use in string literals."""
    return field.replace('"', '\\"')

def generate_node_code(node_type: str, node_config: Dict[str, Any], include_imports: bool = True) -> str:
    """Generate Python code for a node class."""
    
    # Get docstring and metadata
    docstring = node_config.get('helper_text', '')
    if not docstring and 'short_description' in node_config:
        docstring = node_config['short_description']
    # If still no docstring, use the title as fallback
    if not docstring and 'title' in node_config:
        docstring = node_config['title']
    
    # Get params array and their types/defaults
    params = node_config.get('params', [])
    
    # Get configs
    configs = node_config.get('configs', {})
    
    # Collect ALL inputs and outputs from defaults and ALL configs
    all_inputs = {}  # field -> {type, helper_text, default, configs}
    all_outputs = {}  # field -> {type, helper_text, configs}
    
    # Helper function to process config values
    def process_config(config_value, config_name=None):
        # Process inputs at this level
        if 'inputs' in config_value and isinstance(config_value['inputs'], list):
            for input_def in config_value['inputs']:
                if isinstance(input_def, dict) and 'field' in input_def:
                    field = input_def['field']
                    if field not in all_inputs:
                        all_inputs[field] = {
                            'type': input_def.get('type', 'Any'),
                            'helper_text': input_def.get('helper_text', ''),
                            'default': input_def.get('value'),
                            'configs': []
                        }
                    if config_name and config_name not in all_inputs[field]['configs']:
                        all_inputs[field]['configs'].append(config_name)
        
        # Process outputs at this level
        if 'outputs' in config_value and isinstance(config_value['outputs'], list):
            for output_def in config_value['outputs']:
                if isinstance(output_def, dict) and 'field' in output_def:
                    field = output_def['field']
                    helper_text = output_def.get('helper_text', '')
                    output_type = output_def.get('type', 'Any')
                    
                    if field not in all_outputs:
                        all_outputs[field] = {
                            'type': output_type,
                            'helper_text': helper_text,
                            'configs': []
                        }
                    else:
                        # If we have an existing output with a generic helper_text or no helper_text,
                        # and this one has a more specific one, update it
                        existing_helper = all_outputs[field]['helper_text']
                        existing_is_generic = existing_helper == '' or existing_helper == f"The {field} output"
                        
                        if existing_is_generic and helper_text:
                            all_outputs[field]['helper_text'] = helper_text
                            all_outputs[field]['type'] = output_type
                    
                    if config_name and config_name not in all_outputs[field]['configs']:
                        all_outputs[field]['configs'].append(config_name)
    
    # Helper function to recursively find all inputs and outputs in a dictionary
    def extract_io_from_dict(d, config_name=None):
        if not isinstance(d, dict):
            return
        
        # First process the current dictionary
        process_config(d, config_name)
        
        # Recursively check all nested dictionaries
        for key, value in d.items():
            if isinstance(value, dict):
                extract_io_from_dict(value, f"{config_name}.{key}" if config_name else key)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        extract_io_from_dict(item, f"{config_name}[{i}]" if config_name else f"[{i}]")
    
    # Process defaults
    extract_io_from_dict(node_config.get('defaults', {}), 'default')
    
    # Check for output_priority in the node definition
    if 'output_priority' in node_config and isinstance(node_config['output_priority'], list):
        for field in node_config['output_priority']:
            if field not in all_outputs:
                # Add a placeholder that will be updated with real info when found
                all_outputs[field] = {
                    'type': 'Any',
                    'helper_text': f'The {field} output',
                    'configs': ['output_priority']
                }
    
    # Process configs section directly
    if 'configs' in node_config and isinstance(node_config['configs'], dict):
        # Process each config entry
        for config_key, config_value in node_config['configs'].items():
            process_config(config_value, config_key)
    
    # Process other configs
    for config_key, config in configs.items():
        extract_io_from_dict(config, config_key)
    
    # Generate param hints and docs
    required_params = []
    optional_params = []
    param_docs = []
    
    # Handle parameters first
    for param in params:
        if param.startswith("endpoint_"):
            print(f"Skipping parameter: {param} for node: {node_type}")
            continue

        param_info = all_inputs.get(param, {
            'type': 'Any',
            'helper_text': '',
            'default': None,
            'configs': []
        })
        
        param_type = _format_type_annotation(param_info['type'])
        default_value = param_info['default']
        helper_text = param_info['helper_text']
        
        # Check if this is a generic type parameter that should be skipped
        original_type = param_info['type']
        has_generic = ("<" in original_type and ">" in original_type and not (
            original_type.startswith('vec<') or 
            original_type.startswith('enum<') or 
            original_type.startswith('interface<') or 
            original_type.startswith('map<')
        ))
        
        # Skip parameters with generic types or special characters that would cause syntax errors
        if has_generic or "<" in param or ">" in param or "[" in param or "]" in param:
            continue
        
        # Escape reserved keywords
        escaped_param = _escape_reserved_keyword(param)
        
        # Format the parameter
        if default_value is not None:
            default_str = _format_default_value(default_value, param_type)
            optional_params.append(f"{escaped_param}: {param_type} = {default_str}")
        else:
            required_params.append(f"{escaped_param}: {param_type}")
        
        if helper_text:
            param_docs.append(f"    {param}: {helper_text}")
    
    # Generate input hints and docs
    input_hints = []
    input_docs = []
    
    # Handle non-parameter inputs
    for field, info in sorted(all_inputs.items()):
        if field not in params:  # Skip params as they're handled separately
            python_type = _format_type_annotation(info['type'])
            default_value = info['default']
            
            # Check if this is a generic type field that should be skipped
            original_type = info['type']
            has_generic = ("<" in original_type and ">" in original_type and not (
                original_type.startswith('vec<') or 
                original_type.startswith('enum<') or 
                original_type.startswith('interface<') or 
                original_type.startswith('map<')
            ))
            
            # Skip inputs with generic types or special characters that would cause syntax errors
            if has_generic or "<" in field or ">" in field or "[" in field or "]" in field:
                continue
            
            # Escape reserved keywords
            escaped_field = _escape_reserved_keyword(field)
            
            # Format the input parameter
            if default_value is not None:
                default_str = _format_default_value(default_value, python_type)
                input_hints.append(f"{escaped_field}: {python_type} = {default_str}")
            else:
                # For List types, use empty list as default instead of None
                if python_type.startswith('List['):
                    input_hints.append(f"{escaped_field}: {python_type} = []")
                else:
                    input_hints.append(f"{escaped_field}: Optional[{python_type}] = None")
            
            # Format the input documentation with configs
            doc = info['helper_text'] if info['helper_text'] else f"The {field} input"
            
            # Group inputs by type if they appear in multiple configs
            if info['configs']:
                # Group configs with the same type/helper text
                config_types = {}
                for config_name in info['configs']:
                    # Find the config data
                    config_data = _find_config(config_name, node_config)
                                    
                    # Look for the input in this config
                    input_def = None
                    if config_data and 'inputs' in config_data:
                        for inp in config_data['inputs']:
                            if isinstance(inp, dict) and inp.get('field') == field:
                                input_def = inp
                                break
                    
                    # Get type and helper text information
                    if input_def:
                        input_type = input_def.get('type', 'Any')
                        helper_text = input_def.get('helper_text', '')
                        key = f"{input_type}:{helper_text}"
                        
                        if key not in config_types:
                            config_types[key] = {
                                'type': input_type,
                                'helper_text': helper_text,
                                'configs': []
                            }
                        config_types[key]['configs'].append(config_name)
                
                # Add condition information
                if len(config_types) > 1:
                    doc += "\n\nAvailable with different behavior based on configuration:"
                    for type_info in config_types.values():
                        # Create human-readable config conditions
                        config_conditions = []
                        # Track unique conditions to avoid duplicates
                        unique_conditions = set()
                        for config_name in type_info['configs']:
                            condition = _parse_config_key(config_name, params)
                            # Only include human-readable conditions (filter out raw patterns)
                            if condition and "**" not in condition and "(*)" not in condition and condition not in unique_conditions:
                                unique_conditions.add(condition)
                                config_conditions.append(condition)
                        
                        if config_conditions:
                            formatted_type = _format_type_annotation(type_info['type'])
                            helper = type_info['helper_text'] if type_info['helper_text'] else f"The {field} input"
                            doc += f"\n  - {helper} ({', '.join(config_conditions)})"
                elif info['configs']:
                    # Just add the conditions for when this input is available
                    config_conditions = []
                    # Track unique conditions to avoid duplicates
                    unique_conditions = set()
                    for config_name in info['configs']:
                        condition = _parse_config_key(config_name, params)
                        # Only include human-readable conditions (filter out raw patterns)
                        if condition and "**" not in condition and "(*)" not in condition and condition not in unique_conditions:
                            unique_conditions.add(condition)
                            config_conditions.append(condition)
                    
                    if config_conditions:
                        doc += "\n\nAvailable: " + ", ".join(config_conditions)
            
            input_docs.append(f"    {field}: {doc}")
    
    # Combine params and inputs in the correct order: required params, optional params, inputs
    all_params = required_params + optional_params + input_hints
    # Generate output properties and docs
    output_docs = []
    
    # Generate properties for ALL outputs
    for field, info in sorted(all_outputs.items()):
        python_type = _format_type_annotation(info['type'])
        doc = info['helper_text'] if info['helper_text'] else f"The {field} output"
        
        # Add config info if not available in all configs
        if info['configs']:
            # Group configs with the same type
            config_types = {}
            for config_name in info['configs']:
                # Find the config data
                config_data = _find_config(config_name, node_config)
                                
                # Look for the output in this config
                output_def = None
                if config_data and 'outputs' in config_data:
                    for out in config_data['outputs']:
                        if isinstance(out, dict) and out.get('field') == field:
                            output_def = out
                            break
                
                # Get type information
                if output_def:
                    output_type = output_def.get('type', 'Any')
                    helper_text = output_def.get('helper_text', '')
                    key = f"{output_type}:{helper_text}"
                    
                    if key not in config_types:
                        config_types[key] = {
                            'type': output_type,
                            'helper_text': helper_text,
                            'configs': []
                        }
                    config_types[key]['configs'].append(config_name)
            
            # Add condition information for each type
            if len(config_types) > 1:
                doc += "\n\nDifferent behavior based on configuration:"
                for type_info in config_types.values():
                    # Create human-readable config conditions
                    config_conditions = []
                    # Track unique conditions to avoid duplicates
                    unique_conditions = set()
                    for config_name in type_info['configs']:
                        condition = _parse_config_key(config_name, params)
                        # Only include human-readable conditions (filter out raw patterns)
                        if condition and "**" not in condition and "(*)" not in condition and condition not in unique_conditions:
                            unique_conditions.add(condition)
                            config_conditions.append(condition)
                    
                    if config_conditions:
                        # Getting the actual helper text for the output
                        helper = type_info['helper_text'] if type_info['helper_text'] else f"The {field} output"
                        doc += f"\n  - {helper} ({', '.join(config_conditions)})"
            elif len(config_types) == 1 and info['configs']:
                # Just add the conditions for when this output is available
                config_conditions = []
                # Track unique conditions to avoid duplicates
                unique_conditions = set()
                for config_name in info['configs']:
                    condition = _parse_config_key(config_name, params)
                    # Only include human-readable conditions (filter out raw patterns)
                    if condition and "**" not in condition and "(*)" not in condition and condition not in unique_conditions:
                        unique_conditions.add(condition)
                        config_conditions.append(condition)
                
                if config_conditions:
                    doc += "\n\nAvailable: " + ", ".join(config_conditions)
        
        output_docs.append(f"    {field}: {doc}")
        
        # Skip property generation for generic types or fields with special characters
        original_type = info['type']
        has_generic = ("<" in original_type and ">" in original_type and not (
            original_type.startswith('vec<') or 
            original_type.startswith('enum<') or 
            original_type.startswith('interface<') or 
            original_type.startswith('map<') or
            original_type.startswith('stream<')
        ))
        
        # Skip property generation for fields with special characters that would cause syntax errors
        if has_generic or "<" in field or ">" in field or "[" in field or "]" in field:
            continue
        
    
    # Create the class code
    class_name = f"{node_type.title().replace('_', '')}Node"
    
    code = ""
    if include_imports:
        code += '''
from typing import Any, Dict, List, Optional, Union
from .node import Node

'''
    
    code += f'''
class {class_name}(Node):
    """
{docstring}

'''

    # Build deduplicated docstring sections for inputs and outputs
    # First, organize inputs by availability/conditions
    inputs_by_config = {"Common Inputs": []}
    
    # Check for inputs available in different configurations
    for field, info in sorted(all_inputs.items()):
        doc = info['helper_text'] if info['helper_text'] else f"The {field} input"
        default_val = info.get('default', None)
        type_val = info.get('type', None)
        input_def = {"field": field, "helper_text": doc, "value": default_val, "type": type_val}
        
        # Check if this is available in default config or appears in all configs
        is_common = 'default' in info.get('configs', []) or not info.get('configs')
        
        if is_common:
            inputs_by_config["Common Inputs"].append(input_def)
        else:
            # Group by conditions
            for config_name in info.get('configs', []):
                condition = _parse_config_key(config_name, params)
                if condition and "**" not in condition and "(*)" not in condition:
                    if condition not in inputs_by_config:
                        inputs_by_config[condition] = []
                    inputs_by_config[condition].append(input_def)
    
    # Generate input sections with deduplication
    code += "## Inputs\n"
    input_sections = _get_docstring_sections(inputs_by_config)
    if input_sections:
        code += '\n'.join(input_sections)
    else:
        code += "    None"
    
    # Now organize outputs similarly
    outputs_by_config = {"Common Outputs": []}
    
    # Check for outputs available in different configurations
    for field, info in sorted(all_outputs.items()):
        # Don't use a default helper text here, we'll get it from the specific config
        output_def = {"field": field}
        
        # Check if this is available in default config or appears in all configs
        is_common = 'default' in info.get('configs', []) or not info.get('configs')
        
        if is_common:
            # For common outputs, use the helper text from the info
            output_def['helper_text'] = info['helper_text'] if info['helper_text'] else f"The {field} output"
            outputs_by_config["Common Outputs"].append(output_def)
        else:
            # For conditional outputs, find the specific helper text for each config
            for config_name in info.get('configs', []):
                condition = _parse_config_key(config_name, params)
                if condition and "**" not in condition and "(*)" not in condition:
                    if condition not in outputs_by_config:
                        outputs_by_config[condition] = []
                    
                    # Find the specific helper text for this configuration
                    config_data = _find_config(config_name, node_config)
                    if config_data and 'outputs' in config_data:
                        for out in config_data['outputs']:
                            if isinstance(out, dict) and out.get('field') == field:
                                # Use the helper text specific to this configuration
                                output_def = {
                                    "field": field,
                                    "helper_text": out.get('helper_text', f"The {field} output")
                                }
                                break
                    
                    outputs_by_config[condition].append(output_def)
    
    # Generate output sections with deduplication
    code += "\n\n## Outputs\n"
    output_sections = _get_docstring_sections(outputs_by_config)
    if output_sections:
        code += '\n'.join(output_sections)
    else:
        code += "    None"
    
    code += '''
    """

    # Common inputs and outputs
    _COMMON_INPUTS = '''
    
    # Add the actual common inputs value, not a placeholder
    code += repr(inputs_by_config["Common Inputs"])

    code += '''

    # Common outputs and inputs
    _COMMON_OUTPUTS = '''
    
    # Add the actual common outputs value, not a placeholder
    code += repr(outputs_by_config["Common Outputs"])

    code += '''

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = '''
    
    # Add the actual configs value, not a placeholder
    code += repr(configs)
    
    code += '''
    
    # List of parameters that affect configuration
    _PARAMS = '''
    
    # Add the actual params value, not a placeholder
    code += repr(params)
    seen_param_names = set()
    deduplicated_params = []
    for param in all_params:
        param_name = param.split(':')[0].strip()
        if param_name not in seen_param_names:
            seen_param_names.add(param_name)
            deduplicated_params.append(param)
    all_params = deduplicated_params
    
    code += '''
    
    def __init__(self, id: Optional[str] = None, node_name: Optional[str] = None, execution_mode: Optional[str] = None'''
    
    if all_params:
        code += ", " + ", ".join(all_params)
    
    code += ''', **kwargs):
'''

    # Fix any List parameters without defaults before they're written to the file
    # This replaces incomplete default values like `list: List[Any] = ` with proper ones
    if code.find(': List[Any] = ,') > 0:
        code = code.replace(': List[Any] = ,', ': List[Any] = [],')
    
    # Handle other List types too
    list_pattern = r': List\[[^\]]+\] = ,'
    code = re.sub(list_pattern, lambda m: m.group()[:-1] + '[]', code)
    
    # Fix more general missing default values for lists
    missing_list_default_pattern = r': List\[[^\]]+\] = ([,\)])'
    code = re.sub(missing_list_default_pattern, r': List[Any] = []\1', code)
    
    # Fix parameters with missing default values
    missing_default_pattern = r': Any = ,'
    code = re.sub(missing_default_pattern, ': Any = None,', code)
    
    # Fix parameters with no value after =
    missing_value_pattern = r': (\w+) = ([,\)])'
    code = re.sub(missing_value_pattern, r': \1 = None\2', code)
    
    # Fix parameters with missing commas
    missing_comma_pattern = r'] = \[\]([a-zA-Z])'
    code = re.sub(missing_comma_pattern, r'] = [], \1', code)
    
    # Fix interface types
    interface_pattern = r'interface{([^}]+)}'
    code = re.sub(interface_pattern, r'Dict[str, Any]', code)
    
    # Fix type annotations for int32 and int64
    int32_pattern = r': int32\b'
    code = re.sub(int32_pattern, r': int', code)
    int64_pattern = r': int64\b'
    code = re.sub(int64_pattern, r': int', code)

    # Fix List of Lists with missing default
    list_of_lists_pattern = r': List\[List\[.+?\]\] = ([,\)])'
    code = re.sub(list_of_lists_pattern, r': List[List[Any]] = []\1', code)
    
    # Fix for any parameter with a value-less equals - more general case
    equals_no_value_pattern = r'(\w+:.*?)= *(,|\))'
    code = re.sub(equals_no_value_pattern, r'\1= None\2', code)
    
    # Fix for missing commas between parameters
    missing_comma_between_params_pattern = r'(= \S+) (\w+:)'
    code = re.sub(missing_comma_between_params_pattern, r'\1, \2', code)
    
    # Fix for double commas between parameters
    double_comma_pattern = r',\s*,'
    code = re.sub(double_comma_pattern, ',', code)
    
    # Fix for incorrect kwargs syntax - more comprehensive regex to catch various cases
    # This will find patterns like "= [] ** kwargs" or any similar incorrect syntax
    incorrect_kwargs_pattern = r'= (\[[^\]]*\]) \*\* (kwargs)'
    code = re.sub(incorrect_kwargs_pattern, r'= \1, **\2', code)
    
    # Fix for any parameter improperly followed by **kwargs without comma
    incorrect_kwargs_general_pattern = r'(\w+: .+?) = ([^,]+) \*\*kwargs'
    code = re.sub(incorrect_kwargs_general_pattern, r'\1 = \2, **kwargs', code)
    
    # Final catch-all for any remaining parameters with missing values
    # This looks for any parameter with a type annotation that's just followed by =
    # without any value after it and before a comma or closing parenthesis
    missing_value_general_pattern = r'(\w+: [^=]+)= ([,\)])'
    code = re.sub(missing_value_general_pattern, r'\1= None\2', code)
    
    code += '''        # Initialize with params
        params = {}
'''
    
    # Add param assignments with escaped keywords
    for param in params:
        if param.startswith("endpoint_"):
            print(f"Skipping parameter: {param} for node: {node_type}")
            continue
        escaped_param = _escape_reserved_keyword(param)
        code += f'        params["{param}"] = {escaped_param}\n'
    
    code += f'''
        super().__init__(node_type="{node_type}", params=params, id=id, node_name=node_name, execution_mode=execution_mode)
        
        # Set input values
'''
    
    # Add input assignments - fixed to prevent the "nameif" syntax error
    for field in all_inputs:
        # Skip inputs with generic types or special characters that would cause syntax errors
        if "<" in field or ">" in field or "[" in field or "]" in field:
            continue
        
        # Escape reserved keywords for the variable name
        escaped_field = _escape_reserved_keyword(field)
        
        # Ensure proper spacing for the if statement
        code += f'        if {escaped_field} is not None:\n'
        code += f'            self.inputs["{field}"] = {escaped_field}\n'
    
    code += '''
        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)
        self.set_node_task_name()
        self.set_output_name_attributes()
'''
    
    # Add from_dict method
    code += f'''
    @classmethod
    def from_dict(cls, data: dict) -> '{class_name}':
        """Create a node instance from a dictionary."""
        inputs = data.get('inputs', {{}})
        id = data.get('id', None)
        name = data.get('name', None)
        execution_mode = data.get('execution_mode', None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)
'''
    
    # Post-processing: Find and fix references to undefined inputs
    # First gather all input fields from docstring to ensure we have a complete list
    all_input_fields = set()
    for field in all_inputs.keys():
        all_input_fields.add(field)
    
    # Add all input fields from the function parameters
    for param in all_params:
        if ':' in param:
            param_name = param.split(':', 1)[0].strip()
            all_input_fields.add(param_name)
    
    # Instead of adding "Removed reference" comments, ensure all documented input fields 
    # are properly added to __init__ parameters and have assignment code
    init_params = []
    existing_params = set()
    
    # Extract existing parameter names from all_params
    for param in all_params:
        if ':' in param:
            param_name = param.split(':', 1)[0].strip()
            existing_params.add(param_name)
    
    # Find input fields that are missing from parameters
    missing_params = all_input_fields - existing_params
    
    # Generate code to handle these fields properly
    for field in sorted(missing_params):
        if field.isidentifier():  # Ensure it's a valid Python identifier
            escaped_field = _escape_reserved_keyword(field)
            # Add field assignment code that was missing
            assignment_code = f"\n        if {escaped_field} is not None:\n            self.inputs[\"{field}\"] = {escaped_field}"
            # Insert before the kwargs handling
            kwargs_pattern = r'(\s+# Update any additional inputs\s+if kwargs:)'
            code = re.sub(kwargs_pattern, f"{assignment_code}\\1", code)
            
            # Also add to init parameters
            init_params.append(f"{escaped_field}: Optional[Any] = None")
    
    # Add missing parameters to the __init__ method if needed
    if init_params:
        # Filter out duplicate parameters that have already been added
        init_params = [param for param in init_params if param.split(':')[0].strip() not in existing_params]
        
        # Find the __init__ method definition
        init_pattern = r'def __init__\(\s*self,\s*(.*?)\):'
        
        def add_params_to_init(match):
            current_params = match.group(1)
            # If kwargs is present, insert before it
            if '**kwargs' in current_params:
                new_params = current_params.replace('**kwargs', f"{', '.join(init_params)}, **kwargs")
            else:
                # Otherwise add at the end
                new_params = f"{current_params}, {', '.join(init_params)}"
            return f"def __init__(self, {new_params}):"
        
        code = re.sub(init_pattern, add_params_to_init, code, flags=re.DOTALL)
    
    # Format the code with black
    code = f"@Node.register_node_type(\"{node_type}\")\n" + code
    try:
        formatted_code = black.format_str(dedent(code), mode=black.FileMode())
    except Exception as e:
        formatted_code = dedent(code)
    
    return formatted_code

def post_process_nodes_file(file_path):
    """
    Applies post-processing to the entire nodes.py file to:
    1. Remove duplicate entries in docstring "When..." sections
    2. Fix comments about "Removed reference to undefined input"
    """
    
    with open(file_path, "r") as f:
        content = f.read()
    
    # Fix missing newline after "# Set input values" comment
    missing_newline_pattern = re.compile(r'(# Set input values)if\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+is not None:')
    content = missing_newline_pattern.sub(r'\1\n        if \2 is not None:', content)
    
    # Fix duplicate entries in docstring "When..." sections
    when_sections = re.findall(r'###\s+When\s+[^#]+?(?=###|\n\s*##\s+Outputs|\n\s*""")', content)
    
    def deduplicate_section(section):
        # Extract the field entries from the section
        entries = re.findall(r'^\s*([^:]+?):\s*(.*?)$', section, re.MULTILINE)
        seen = {}
        deduplicated_entries = []
        
        for name, desc in entries:
            name = name.strip()
            if name not in seen:
                seen[name] = True
                deduplicated_entries.append(f"    {name}: {desc}")
        
        # Reconstruct the section with deduplicated entries
        section_title = re.match(r'(###\s+When\s+[^\n]+)', section).group(1)
        return f"{section_title}\n" + "\n".join(deduplicated_entries)
    
    # Replace each When section with its deduplicated version
    for section in when_sections:
        deduplicated = deduplicate_section(section)
        content = content.replace(section, deduplicated)
    
    # Fix "Removed reference to undefined input" comments by replacing with proper code
    removed_refs = re.findall(r'# Removed reference to undefined input: ([a-zA-Z_][a-zA-Z0-9_]*)', content)
    
    for field in removed_refs:
        escaped_field = _escape_reserved_keyword(field)
        pattern = rf'# Removed reference to undefined input: {field}'
        replacement = f'if {escaped_field} is not None:\n            self.inputs["{field}"] = {escaped_field}'
        content = content.replace(pattern, replacement)
    
    with open(file_path, "w") as f:
        f.write(content)
    

def post_process_code(code: str, node_type: str) -> str:
    """Post-process generated code to fix common issues.
    
    This function performs several operations:
    1. Deduplicates entries in docstrings for both inputs and outputs
    2. Replaces "Removed reference to undefined input" comments with proper code
    3. Adds missing parameters to the __init__ method if needed
    """
    # 1. Fix duplicate entries in docstrings for both inputs and outputs
    when_section_pattern = r'(### When [^\n]+\n)((    \w+:.*?\n)+)'
    
    def deduplicate_section(match):
        # Fix the unpacking issue - groups() returns a tuple with all capturing groups
        groups = match.groups()
        header = groups[0]
        entries = groups[1]
        
        seen_fields = {}
        result_lines = []
        
        for line in entries.split('\n'):
            if not line.strip():
                continue
                
            # Extract field name (before the colon)
            parts = line.split(':', 1)
            if len(parts) == 2:
                field = parts[0].strip()
                # Only keep the first occurrence of each field
                if field not in seen_fields:
                    seen_fields[field] = True
                    result_lines.append(line)
        
        # Return the header plus deduplicated entries
        return header + '\n'.join(result_lines) + '\n'
    
    # Apply deduplication to all "When..." sections
    deduped_code = re.sub(when_section_pattern, deduplicate_section, code, flags=re.DOTALL)
    
    # 2. Replace "Removed reference to undefined input" comments with proper code
    # First, gather all input field names from the docstring
    docstring_pattern = r'""".*?## Inputs(.*?)##'
    input_section_match = re.search(docstring_pattern, deduped_code, re.DOTALL)
    
    all_input_fields = set()
    if input_section_match:
        input_section = input_section_match.group(1)
        # Find all field names (they appear before a colon)
        field_pattern = r'^\s+(\w+):'
        fields = re.findall(field_pattern, input_section, re.MULTILINE)
        all_input_fields.update(fields)
    
    # Find the __init__ method to see what parameters already exist
    init_pattern = r'def __init__\(\s*self,\s*(.*?)\):'
    init_match = re.search(init_pattern, deduped_code, re.DOTALL)
    
    existing_params = set()
    kwargs_present = False
    
    if init_match:
        init_params = init_match.group(1)
        
        # Check for **kwargs
        if '**kwargs' in init_params:
            kwargs_present = True
            
        # Extract parameter names
        for param in init_params.split(','):
            param = param.strip()
            if param and not param.startswith('**'):
                param_name = param.split(':', 1)[0].strip()
                existing_params.add(param_name)
    
    # Find parameters that need to be added
    missing_params = all_input_fields - existing_params
    
    # 3. Fix the "Removed reference" comments with proper field assignments
    removed_ref_pattern = r'# Removed reference to undefined input: (\w+)'
    
    def fix_removed_ref(match):
        field = match.group(1)
        escaped_field = _escape_reserved_keyword(field)
        # If this is an actual input field but wasn't in params, add proper assignment
        if field in all_input_fields:
            return f"if {escaped_field} is not None:\n            self.inputs[\"{field}\"] = {escaped_field}"
        # Otherwise, leave a better comment
        return f"# Note: Field '{field}' is documented but not in function signature"
    
    # Apply the fix for removed reference comments
    fixed_code = re.sub(removed_ref_pattern, fix_removed_ref, deduped_code)
    
    # 4. If there are missing parameters, add them to the __init__ method
    if missing_params:
        # Create parameter declarations for missing fields
        new_params = []
        for param in sorted(missing_params):
            if param.isidentifier():  # Make sure it's a valid identifier
                escaped_param = _escape_reserved_keyword(param)
                new_params.append(f"{escaped_param}: Optional[Any] = None")
        
        if new_params and init_match:
            # Add parameters to __init__ method signature
            if kwargs_present:
                # Add before **kwargs
                new_init = init_match.group(1).replace('**kwargs', f"{', '.join(new_params)}, **kwargs")
            else:
                # Otherwise add at the end
                new_init = f"{init_match.group(1)}, {', '.join(new_params)}"
                
            # Replace in the code
            fixed_code = fixed_code.replace(f"def __init__(self, {init_match.group(1)}):", 
                                          f"def __init__(self, {new_init}):")
    
    return fixed_code

def generate_nodes_file(config_path: str, output_file: str, node_types: Optional[List[str]] = None) -> None:
    """Generate a single Python file containing the specified node classes."""
    config = load_toml_config(config_path)
    
    # If no node types specified, use all
    if node_types is None:
        node_types = list(config.keys())
    
    # Validate node types
    invalid_nodes = [n for n in node_types if n not in config]
    if invalid_nodes:
        raise ValueError(f"Invalid node types: {invalid_nodes}")
    
    # Create the output directory if it doesn't exist
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Start with the imports
    code = '''"""
Generated node classes from TOML configuration.
This file is auto-generated. Do not edit manually.
"""

from typing import Any, Dict, List, Optional, Union, Protocol, runtime_checkable
from .node import Node, NodeOutputs

'''
    
    # Add each node class
    for node_type in node_types:
        node_config = config[node_type]
        node_code = generate_node_code(node_type, node_config, include_imports=False)
        code += f"\n{node_code}\n"
    
    # Add __all__ declaration
    class_names = [f"{node_type.title().replace('_', '')}Node" for node_type in node_types]
    code += "\n__all__ = [\n    " + ",\n    ".join(f'"{name}"' for name in class_names) + "\n]\n"
    
    # Format the entire file
    try:
        formatted_code = black.format_str(code, mode=black.FileMode())
    except Exception:
        formatted_code = code
    
    # Apply post-processing to fix duplicate entries in docstrings and undefined inputs
    post_process_nodes_file(output_file)
    
    # Write the file
    with open(output_path, 'w') as f:
        f.write(formatted_code)
    

def generate_node_files(config_path: str, output_dir: str) -> None:
    """Generate Python files for all nodes in the TOML configuration."""
    config = load_toml_config(config_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py
    init_imports = []
    
    for node_type, node_config in config.items():
        try:
            # Generate the code
            code = generate_node_code(node_type, node_config)
            
            # Create the file
            class_name = f"{node_type.title().replace('_', '')}Node"
            file_name = f"{node_type.lower()}_node.py"
            file_path = output_path / file_name
            
            with open(file_path, 'w') as f:
                f.write(code)
            
            # Add to __init__.py imports
            init_imports.append(f"from .{node_type.lower()}_node import {class_name}")
            
            print(f"Generated {file_path}")
        except Exception as e:
            print(f"Error generating node file for {node_type}: {e}")
    
    # Create __init__.py
    init_code = "\n".join(init_imports) + "\n\n__all__ = [\n    " + ",\n    ".join(
        [f"'{name.split()[-1]}'" for name in init_imports]
    ) + "\n]\n"
    
    with open(output_path / "__init__.py", 'w') as f:
        f.write(init_code)

def generate_all_nodes(config_path: str) -> Dict[str, Type[Node]]:
    """Generate all node classes from the TOML configuration."""
    config = load_toml_config(config_path)
    nodes = {}
    
    for node_type, node_config in config.items():
        try:
            node_class = generate_node_class(node_type, node_config)
            nodes[node_type] = node_class
        except Exception as e:
            print(f"Error generating node class for {node_type}: {e}")
    
    return nodes

def _parse_config_key(config_key: str, params: List[str]) -> str:
    """Convert a config key pattern to a human-readable condition.
    
    Args:
        config_key: The configuration key pattern (e.g., "true", "false", "(*)**true**(*)**(*)**(*)")
        params: List of parameter names in order
    
    Returns:
        A human-readable condition string or the original key if not parseable
    """
    if not config_key or not params:
        return ""
        
    # Handle default case
    if config_key == 'default':
        return "Default configuration"
    
    # Skip output_priority
    if config_key == 'output_priority':
        return ""
    
    # Handle simple boolean config keys (like "true" or "false")
    if config_key.lower() in ["true", "false"]:
        # For simple boolean keys, use the first parameter as it's typically the main toggle
        if params:
            param = params[0]
            value = config_key.lower() == "true"
            return f"When {param} = {str(value)}"
        return config_key
        
    # Parse patterns like "(*)**true**(*)**(*)**(*)"
    if '**' in config_key:
        try:
            parts = config_key.split('**')
            conditions = []
            
            # Process each part of the pattern
            for i, part in enumerate(parts):
                if i < len(params) and part != "(*)":
                    param = params[i]
                    # Handle string values (like "documents" or "chunks")
                    if part.lower() not in ["true", "false"]:
                        conditions.append(f"{param} = '{part}'")
                    else:
                        # Handle boolean values
                        value = part.lower() == "true"
                        conditions.append(f"{param} = {str(value)}")
            
            if conditions:
                # Remove duplicate conditions (same param name, different values)
                unique_conditions = []
                seen_params = set()
                for condition in conditions:
                    param_name = condition.split(' =')[0].strip()
                    if param_name not in seen_params:
                        seen_params.add(param_name)
                        unique_conditions.append(condition)
                
                if len(unique_conditions) == 1:
                    return "When " + unique_conditions[0]
                else:
                    return "When " + " and ".join(unique_conditions)
        except Exception as e:
            # If parsing fails, return the config key as is
            return config_key
    
    # Handle other config keys
    return config_key

def _find_config(config_name, node_config):
    """Find a config in the node_config structure."""
    # For configs in the main configs section
    if 'configs' in node_config and config_name in node_config['configs']:
        return node_config['configs'][config_name]
    
    # For configs in other sections
    for key, value in node_config.items():
        if key.startswith('config.') and key[7:] == config_name:
            return value
            
    # Not found
    return None

def _get_output_config_types(field, info, node_config):
    """Get the different configuration types for an output field."""
    config_types = {}
    for config_name in info['configs']:
        # Find the config data
        config_data = _find_config(config_name, node_config)
                        
        # Look for the output in this config
        output_def = None
        if config_data and 'outputs' in config_data:
            for out in config_data['outputs']:
                if isinstance(out, dict) and out.get('field') == field:
                    output_def = out
                    break
        
        # Get type information
        if output_def:
            output_type = output_def.get('type', 'Any')
            helper_text = output_def.get('helper_text', '')
            key = f"{output_type}:{helper_text}"
            
            if key not in config_types:
                config_types[key] = {
                    'type': output_type,
                    'helper_text': helper_text,
                    'configs': []
                }
            config_types[key]['configs'].append(config_name)
    
    return config_types

def _get_docstring_sections(inputs_by_config: Dict[str, List[Dict[str, str]]]) -> List[str]:
    """Generate deduplicated docstring sections for inputs grouped by config."""
    sections = []
    
    for config_name, input_list in inputs_by_config.items():
        # Start section with config name
        section_lines = [f"### {config_name}"]
        
        # Track fields we've seen to eliminate duplicates
        seen_fields = set()
        
        for input_def in input_list:
            field = input_def.get('field', '')
            if field and field not in seen_fields:
                seen_fields.add(field)
                # Use the specific helper text for this configuration
                helper_text = input_def.get('helper_text', f"The {field} input")
                section_lines.append(f"    {field}: {helper_text}")
        
        # Only add the section if it has at least one field
        if len(section_lines) > 1:
            sections.append('\n'.join(section_lines))
    
    return sections

# Example usage:
# nodes = generate_all_nodes("path/to/pipeline_node.toml")
# LlmNode = nodes['llm']
# node = LlmNode(system="You are a helpful assistant", prompt="Hello!") 