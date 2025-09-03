from typing import Any, Dict, List, Optional, Type, Union, Protocol, runtime_checkable
import tomli
from pathlib import Path
import black
import ast
from textwrap import dedent
import shutil
from .tool import Tool
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

def _escape_field_name(field: str) -> str:
    """Escape a field name for use in string literals."""
    return field.replace('"', '\\"')

def generate_tool_code(tool_type: str, tool_config: Dict[str, Any], include_imports: bool = True) -> str:
    """Generate Python code for a tool class."""
    
    # Get docstring and metadata
    docstring = tool_config.get('helper_text', '')
    if not docstring and 'short_description' in tool_config:
        docstring = tool_config['short_description']
    # If still no docstring, use the title as fallback
    if not docstring and 'title' in tool_config:
        docstring = tool_config['title']
    
    # Get params array and their types/defaults
    params = tool_config.get('params', [])
    
    # Get configs
    configs = tool_config.get('configs', {})
    
    # Collect ALL inputs and outputs from defaults and ALL configs
    all_inputs = {}  # field -> {type, helper_text, default, configs}
    
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
                            'configs': [],
                            'agent_field_type': input_def.get('agent_field_type', None)
                        }
                    if config_name and config_name not in all_inputs[field]['configs']:
                        all_inputs[field]['configs'].append(config_name)
    
    # Helper function to recursively find all inputs in a dictionary
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
    extract_io_from_dict(tool_config.get('defaults', {}), 'default')
    
    # Process configs section directly
    if 'configs' in tool_config and isinstance(tool_config['configs'], dict):
        # Process each config entry
        for config_key, config_value in tool_config['configs'].items():
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
            optional_params.append(f"{escaped_param}: {param_type} | ToolInput = {default_str}")
        else:
            required_params.append(f"{escaped_param}: {param_type} | ToolInput = None")
        
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
            agent_field_type = info.get('agent_field_type', None)
            
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
            if agent_field_type == "static":
                if default_value is not None:
                    default_str = _format_default_value(default_value, python_type)
                    input_hints.append(f"{escaped_field}: {python_type} | ToolInput = {default_str}")
                else:
                    # For List types, use empty list as default instead of None
                    if python_type.startswith('List['):
                        input_hints.append(f"{escaped_field}: {python_type} | ToolInput = []")
                    else:
                        input_hints.append(f"{escaped_field}: Optional[{python_type}] | ToolInput = None")
            
            # Format the input documentation with configs
            doc = info['helper_text'] if info['helper_text'] else f"The {field} input"
            
            # Group inputs by type if they appear in multiple configs
            if info['configs']:
                # Group configs with the same type/helper text
                config_types = {}
                for config_name in info['configs']:
                    # Find the config data
                    config_data = _find_config(config_name, tool_config)
                                    
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
    
    # Combine params and inputs in the correct order: optional params, input hints, required params
    all_params = input_hints + optional_params + required_params
    
    # Create the class code
    class_name = f"{tool_type.title().replace('_', '')}Tool"
    
    code = ""
    if include_imports:
        code += '''
from typing import Any, Dict, List, Optional, Union
from .tool import Tool

'''
    
    code += f'''
class {class_name}(Tool):
    """
{docstring}

'''

    # Build deduplicated docstring sections for inputs
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
    
    code += '''
    """

    # Common inputs
    _COMMON_INPUTS = '''
    
    # Add the actual common inputs value, not a placeholder
    code += repr(inputs_by_config["Common Inputs"])

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
    
    code += f'''
    
    def __init__(self, id: Optional[str] = None, tool_name: Optional[str] = None, tool_description: str = "{docstring}"'''
    
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
        escaped_param = _escape_reserved_keyword(param)
        code += f'        if isinstance({param}, ToolInput):\n'
        code += f'            if {param}.type == "static":\n'
        code += f'                params["{param}"] = {param}.value\n'
        code += f'            else:\n'
        code += f'                raise ValueError(f"{param} cannot be a dynamic input")\n'
        code += f'        else:\n'
        code += f'            params["{param}"] = {escaped_param}\n'
    
    code += f'''
        super().__init__(tool_type="{tool_type}", params=params, id=id, tool_name=tool_name, tool_description=tool_description)
        
        # Set static input values
'''
    
    # Add input assignments - fixed to prevent the "nameif" syntax error
    for field in all_params:
        field = field.split(':')[0].strip()
        # Skip inputs with generic types or special characters that would cause syntax errors
        if "<" in field or ">" in field or "[" in field or "]" in field:
            continue
        
        # Escape reserved keywords for the variable name
        escaped_field = _escape_reserved_keyword(field)
        
        # Ensure proper spacing for the if statement
        code += f'        if {escaped_field} is not None:\n'
        code += f'            if isinstance({escaped_field}, ToolInput):\n'
        code += f'                self.inputs["{field}"] = {{"type": {escaped_field}.type, "value": {escaped_field}.value or {escaped_field}.description}}\n'
        code += f'            else:\n'
        code += f'                self.inputs["{field}"] = {{"type": "static", "value": {escaped_field}}}\n'
    
    code += '''
        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)
'''

    code += '''
        # Add dynamic inputs
        self.add_dynamic_inputs()
    '''

    code += '''
        # add task name
        self.set_tool_task_name()
    '''
    
    # Add from_dict method
    code += f'''
    @classmethod
    def from_dict(cls, data: dict) -> '{class_name}':
        """Create a tool instance from a dictionary."""
        inputs = data.get('value', {{}}).get('inputs', {{}})
        inputs = {{k: v.get('value') for k, v in inputs.items()}}
        id = data.get('id', None)
        name = data.get('name', None)
        description = data.get('description', None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)
'''
    
    # Format the code with black
    code = f"@Tool.register_tool_type(\"{tool_type}\")\n" + code
    try:
        formatted_code = black.format_str(dedent(code), mode=black.FileMode())
    except Exception as e:
        formatted_code = dedent(code)
    
    return formatted_code

def post_process_tools_file(file_path):
    """
    Applies post-processing to the entire tools.py file to:
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
    

def post_process_code(code: str, tool_type: str) -> str:
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

def generate_tools_file(config_path: str, output_file: str, tool_types: Optional[List[str]] = None) -> None:
    """Generate a single Python file containing the specified tool classes."""
    config = load_toml_config(config_path)
    
    # If no tool types specified, use all
    if tool_types is None:
        tool_types = list(config.keys())
    
    # Validate tool types
    invalid_tools = [tool_type for tool_type in tool_types if tool_type not in config]
    if invalid_tools:
        raise ValueError(f"Invalid tool types: {invalid_tools}")
    
    # Create the output directory if it doesn't exist
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Start with the imports
    code = '''"""
Generated tool classes from TOML configuration.
This file is auto-generated. Do not edit manually.
"""

from typing import Any, List, Optional
from .tool import Tool, ToolInput
'''
    
    # Add each tool class
    for tool_type in tool_types:
        tool_config = config[tool_type]
        tool_code = generate_tool_code(tool_type, tool_config, include_imports=False)
        code += f"\n{tool_code}\n"
    
    # Add __all__ declaration
    class_names = [f"{tool_type.title().replace('_', '')}Tool" for tool_type in tool_types]
    code += "\n__all__ = [\n    " + ",\n    ".join(f'"{name}"' for name in class_names) + "\n]\n"
    
    # Format the entire file
    try:
        formatted_code = black.format_str(code, mode=black.FileMode())
    except Exception:
        formatted_code = code
    
    # Apply post-processing to fix duplicate entries in docstrings and undefined inputs
    post_process_tools_file(output_file)
    
    # Write the file
    with open(output_path, 'w') as f:
        f.write(formatted_code)

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

def _find_config(config_name, tool_config):
    """Find a config in the tool_config structure."""
    # For configs in the main configs section
    if 'configs' in tool_config and config_name in tool_config['configs']:
        return tool_config['configs'][config_name]
    
    # For configs in other sections
    for key, value in tool_config.items():
        if key.startswith('config.') and key[7:] == config_name:
            return value
            
    # Not found
    return None

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
# tools = generate_all_tools("path/to/pipeline_tool.toml")
# Llmtool = tools['llm']
# tool = Llmtool(system="You are a helpful assistant", prompt="Hello!") 