"""
Generated tool classes from TOML configuration.
This file is auto-generated. Do not edit manually.
"""

from typing import Any, List, Optional
from .tool import Tool, ToolInput


@Tool.register_tool_type("append_files")
class AppendFilesTool(Tool):
    """
    Append files together in successive fashion

    ## Inputs
    ### Common Inputs
        file_type: The type of file to append.
        selected_files: The number of files to be appended. Files will be appended in successive fashion (e.g., file-1 first, then file-2, etc.).
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "file_type",
            "helper_text": "The type of file to append.",
            "value": "PDF",
            "type": "enum<string>",
        },
        {
            "field": "selected_files",
            "helper_text": "The number of files to be appended. Files will be appended in successive fashion (e.g., file-1 first, then file-2, etc.).",
            "value": [""],
            "type": "vec<file>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Append files together in successive fashion",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="append_files",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "AppendFilesTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("sticky_note")
class StickyNoteTool(Tool):
    """


    ## Inputs
    ### Common Inputs
        text: The text input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "text",
            "helper_text": "The text input",
            "value": "",
            "type": "string",
        }
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="sticky_note",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "StickyNoteTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("custom_group")
class CustomGroupTool(Tool):
    """


    ## Inputs
        None
    """

    # Common inputs
    _COMMON_INPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="custom_group",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "CustomGroupTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("transformation")
class TransformationTool(Tool):
    """


    ## Inputs
    ### Common Inputs
        transformation_id: The transformation_id input
    ### [transformations._id.<A>]
        [<A>.inputs]: The [<A>.inputs] input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "transformation_id",
            "helper_text": "The transformation_id input",
            "value": "",
            "type": "enum<string>",
        }
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "[transformations._id.<A>]": {
            "inputs": [{"field": "[<A>.inputs]", "type": ""}],
            "outputs": [{"field": "[<A>.outputs]", "type": ""}],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["transformation_id"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "",
        transformation_id: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(transformation_id, ToolInput):
            if transformation_id.type == "static":
                params["transformation_id"] = transformation_id.value
            else:
                raise ValueError(f"transformation_id cannot be a dynamic input")
        else:
            params["transformation_id"] = transformation_id

        super().__init__(
            tool_type="transformation",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if transformation_id is not None:
            if isinstance(transformation_id, ToolInput):
                self.inputs["transformation_id"] = {
                    "type": transformation_id.type,
                    "value": transformation_id.value or transformation_id.description,
                }
            else:
                self.inputs["transformation_id"] = {
                    "type": "static",
                    "value": transformation_id,
                }

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "TransformationTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("chat_file_reader")
class ChatFileReaderTool(Tool):
    """
    Allows for document upload within chatbots (often connected to the LLM node).

    ## Inputs
    ### Common Inputs
        chunk_overlap: The number of tokens of overlap between chunks (1 token = 4 characters)
        chunk_size: The number of tokens per chunk (1 token = 4 characters)
        file_parser: The processing model with which the document will be processed. Default processing model includes standard document parsing / OCR. Llamaparse will allow for ability to read documents with complex features (e.g., tables, charts, etc.). Llamaparse will be charged at 0.3 cents per page. Textract for most advanced data extraction and will be charged at 1.5 cents per page.
        max_docs_per_query: Sets the maximum number of chunks to retrieve for each query
        retrieval_unit: Return the most relevant Chunks (text content) or Documents (will return the document metadata)
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "chunk_overlap",
            "helper_text": "The number of tokens of overlap between chunks (1 token = 4 characters)",
            "value": 200,
            "type": "int32",
        },
        {
            "field": "chunk_size",
            "helper_text": "The number of tokens per chunk (1 token = 4 characters)",
            "value": 1000,
            "type": "int32",
        },
        {
            "field": "file_parser",
            "helper_text": "The processing model with which the document will be processed. Default processing model includes standard document parsing / OCR. Llamaparse will allow for ability to read documents with complex features (e.g., tables, charts, etc.). Llamaparse will be charged at 0.3 cents per page. Textract for most advanced data extraction and will be charged at 1.5 cents per page.",
            "value": "default",
            "type": "enum<string>",
        },
        {
            "field": "max_docs_per_query",
            "helper_text": "Sets the maximum number of chunks to retrieve for each query",
            "value": 10,
            "type": "int32",
        },
        {
            "field": "retrieval_unit",
            "helper_text": "Return the most relevant Chunks (text content) or Documents (will return the document metadata)",
            "value": "chunks",
            "type": "enum<string>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Allows for document upload within chatbots (often connected to the LLM node).",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="chat_file_reader",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "ChatFileReaderTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("pipeline")
class PipelineTool(Tool):
    """
    Pipeline

    ## Inputs
    ### Common Inputs
        pipeline_id: The pipeline_id input
    ### [pipelines._id.<A>]
        [<A>.inputs]: The [<A>.inputs] input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "pipeline_id",
            "helper_text": "The pipeline_id input",
            "value": "",
            "type": "enum<string>",
        }
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "[pipelines._id.<A>]": {
            "inputs": [{"field": "[<A>.inputs]", "type": ""}],
            "outputs": [{"field": "[<A>.outputs]", "type": ""}],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["pipeline_id"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Pipeline",
        pipeline_id: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(pipeline_id, ToolInput):
            if pipeline_id.type == "static":
                params["pipeline_id"] = pipeline_id.value
            else:
                raise ValueError(f"pipeline_id cannot be a dynamic input")
        else:
            params["pipeline_id"] = pipeline_id

        super().__init__(
            tool_type="pipeline",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if pipeline_id is not None:
            if isinstance(pipeline_id, ToolInput):
                self.inputs["pipeline_id"] = {
                    "type": pipeline_id.type,
                    "value": pipeline_id.value or pipeline_id.description,
                }
            else:
                self.inputs["pipeline_id"] = {"type": "static", "value": pipeline_id}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "PipelineTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("agent")
class AgentTool(Tool):
    """
    Agent

    ## Inputs
    ### Common Inputs
        agent_id: The agent_id input
    ### [agents._id.<A>]
        [<A>.inputs]: The [<A>.inputs] input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "agent_id",
            "helper_text": "The agent_id input",
            "value": "",
            "type": "enum<string>",
        }
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "[agents._id.<A>]": {
            "inputs": [{"field": "[<A>.inputs]", "type": ""}],
            "outputs": [{"field": "[<A>.outputs]", "type": ""}],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["agent_id"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Agent",
        agent_id: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(agent_id, ToolInput):
            if agent_id.type == "static":
                params["agent_id"] = agent_id.value
            else:
                raise ValueError(f"agent_id cannot be a dynamic input")
        else:
            params["agent_id"] = agent_id

        super().__init__(
            tool_type="agent",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if agent_id is not None:
            if isinstance(agent_id, ToolInput):
                self.inputs["agent_id"] = {
                    "type": agent_id.type,
                    "value": agent_id.value or agent_id.description,
                }
            else:
                self.inputs["agent_id"] = {"type": "static", "value": agent_id}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "AgentTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("chat_memory")
class ChatMemoryTool(Tool):
    """
    Give connected nodes access to conversation history.

    ## Inputs
    ### Common Inputs
        memory_type: The type of memory to use
        memory_window: The number of tokens to store in memory
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "memory_type",
            "helper_text": "The type of memory to use",
            "value": "Token Buffer",
            "type": "string",
        },
        {
            "field": "memory_window",
            "helper_text": "The number of tokens to store in memory",
            "value": 2048,
            "type": "int32",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "Vector Database": {
            "inputs": [
                {"field": "memory_window", "type": "int32", "value": 20},
                {
                    "field": "memory_type",
                    "type": "string",
                    "value": "Vector Database",
                    "helper_text": "Stores all previous messages in a Vector Database. Will return most similar messages based on the user message",
                },
            ],
            "outputs": [],
        },
        "Message Buffer": {
            "inputs": [
                {
                    "field": "memory_type",
                    "type": "string",
                    "value": "Message Buffer",
                    "helper_text": "Returns a set number of previous consecutive messages",
                },
                {"field": "memory_window", "type": "int32", "value": 10},
            ],
            "outputs": [],
        },
        "Token Buffer": {
            "inputs": [
                {
                    "field": "memory_type",
                    "type": "string",
                    "value": "Token Buffer",
                    "helper_text": "Returns a set number of previous consecutive messages until adding an additional message would cause the total history size to be larger than the Max Tokens",
                },
                {"field": "memory_window", "type": "int32", "value": 2048},
            ],
            "outputs": [],
        },
        "Full - Formatted": {
            "inputs": [
                {
                    "field": "memory_type",
                    "type": "string",
                    "value": "Full - Formatted",
                    "helper_text": "Returns all previous chat history",
                }
            ],
            "outputs": [],
        },
        "Full - Raw": {
            "inputs": [
                {
                    "field": "memory_type",
                    "type": "string",
                    "value": "Full - Raw",
                    "helper_text": 'Returns a Python list with elements in the following format: {"type": type, "message": message}',
                }
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["memory_type"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Give connected nodes access to conversation history.",
        memory_type: str | ToolInput = "Token Buffer",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(memory_type, ToolInput):
            if memory_type.type == "static":
                params["memory_type"] = memory_type.value
            else:
                raise ValueError(f"memory_type cannot be a dynamic input")
        else:
            params["memory_type"] = memory_type

        super().__init__(
            tool_type="chat_memory",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if memory_type is not None:
            if isinstance(memory_type, ToolInput):
                self.inputs["memory_type"] = {
                    "type": memory_type.type,
                    "value": memory_type.value or memory_type.description,
                }
            else:
                self.inputs["memory_type"] = {"type": "static", "value": memory_type}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "ChatMemoryTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("llm")
class LlmTool(Tool):
    """
    LLM

    ## Inputs
    ### Common Inputs
        enable_moderation: Whether to enable moderation
        enable_pii_address: Whether to enable PII address
        enable_pii_cc: Whether to enable PII cc
        enable_pii_email: Whether to enable PII email
        enable_pii_name: Whether to enable PII name
        enable_pii_phone: Whether to enable PII phone
        enable_pii_ssn: Whether to enable PII ssn
        max_tokens: The maximum amount of input + output tokens the model will take in and generate per run (1 token = 4 characters). Note: different models have different token limits and the workflow will error if the max token is reached.
        model: Select the LLM model to be used
        prompt: The data that is sent to the LLM. Add data from other nodes with double curly braces e.g., {{input_0.text}}
        provider: Select the LLM provider to be used
        retry_on_failure: Enable retrying when the node execution fails
        safe_context_token_window: If enabled, the context window will be reduced to fit the model's maximum context window.
        show_confidence: Whether to show the confidence score of the response
        show_sources: Whether to show the sources used to generate the response
        stream: Whether to stream the response
        system: The system prompt to be used
        temperature: The “creativity” of the response - increase the temperature for more creative responses.
        thinking_token_limit: The maximum number of tokens the model can use for thinking
        top_p: The “randomness” of the output - higher Top P values increase the randomness
    ### When use_personal_api_key = True
        api_key: Your personal API key
    ### When provider = 'custom'
        api_key: Your personal API key
        base_url: The base URL of the custom LLM provider
        finetuned_model: Use your finetuned model for response generation. Make sure to select the matching base model from the dropdown.
        use_personal_api_key: Whether to use a personal API key
    ### When show_sources = True
        citation_metadata: The metadata of the sources used to generate the response
        json_response: Whether to return the response as a JSON object
        use_personal_api_key: Whether to use a personal API key
    ### When provider = 'azure' and use_personal_api_key = True
        deployment_id: The deployment ID for the Azure OpenAI model. This is required when using Azure OpenAI services.
        endpoint: The Azure OpenAI endpoint URL (e.g., https://your-resource-name.openai.azure.com)
    ### When provider = 'openai' and use_personal_api_key = True
        finetuned_model: Use your finetuned model for response generation. Make sure to select the matching base model from the dropdown.
    ### When provider = 'openai'
        json_response: Whether to return the response as a JSON object
        use_personal_api_key: Whether to use a personal API key
    ### When provider = 'anthropic'
        json_response: Whether to return the response as a JSON object
        use_personal_api_key: Whether to use a personal API key
    ### When provider = 'google'
        json_response: Whether to return the response as a JSON object
        use_personal_api_key: Whether to use a personal API key
    ### When provider = 'cohere'
        json_response: Whether to return the response as a JSON object
        use_personal_api_key: Whether to use a personal API key
    ### When provider = 'together'
        json_response: Whether to return the response as a JSON object
        use_personal_api_key: Whether to use a personal API key
    ### When provider = 'bedrock'
        json_response: Whether to return the response as a JSON object
    ### When provider = 'azure'
        json_response: Whether to return the response as a JSON object
        use_personal_api_key: Whether to use a personal API key
    ### When json_response = True
        json_schema: The schema of the JSON response
    ### When retry_on_failure = True
        max_retries: The maximum number of retries
        retry_interval_ms: The interval between retries in milliseconds
    ### When provider = 'perplexity'
        use_personal_api_key: Whether to use a personal API key
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "enable_moderation",
            "helper_text": "Whether to enable moderation",
            "value": False,
            "type": "bool",
        },
        {
            "field": "enable_pii_address",
            "helper_text": "Whether to enable PII address",
            "value": False,
            "type": "bool",
        },
        {
            "field": "enable_pii_cc",
            "helper_text": "Whether to enable PII cc",
            "value": False,
            "type": "bool",
        },
        {
            "field": "enable_pii_email",
            "helper_text": "Whether to enable PII email",
            "value": False,
            "type": "bool",
        },
        {
            "field": "enable_pii_name",
            "helper_text": "Whether to enable PII name",
            "value": False,
            "type": "bool",
        },
        {
            "field": "enable_pii_phone",
            "helper_text": "Whether to enable PII phone",
            "value": False,
            "type": "bool",
        },
        {
            "field": "enable_pii_ssn",
            "helper_text": "Whether to enable PII ssn",
            "value": False,
            "type": "bool",
        },
        {
            "field": "max_tokens",
            "helper_text": "The maximum amount of input + output tokens the model will take in and generate per run (1 token = 4 characters). Note: different models have different token limits and the workflow will error if the max token is reached.",
            "value": 128000,
            "type": "int64",
        },
        {
            "field": "model",
            "helper_text": "Select the LLM model to be used",
            "value": "gpt-4o",
            "type": "enum<string>",
        },
        {
            "field": "prompt",
            "helper_text": "The data that is sent to the LLM. Add data from other nodes with double curly braces e.g., {{input_0.text}}",
            "value": "",
            "type": "string",
        },
        {
            "field": "provider",
            "helper_text": "Select the LLM provider to be used",
            "value": "openai",
            "type": "enum<string>",
        },
        {
            "field": "retry_on_failure",
            "helper_text": "Enable retrying when the node execution fails",
            "value": False,
            "type": "bool",
        },
        {
            "field": "safe_context_token_window",
            "helper_text": "If enabled, the context window will be reduced to fit the model's maximum context window.",
            "value": False,
            "type": "bool",
        },
        {
            "field": "show_confidence",
            "helper_text": "Whether to show the confidence score of the response",
            "value": False,
            "type": "bool",
        },
        {
            "field": "show_sources",
            "helper_text": "Whether to show the sources used to generate the response",
            "value": False,
            "type": "bool",
        },
        {
            "field": "stream",
            "helper_text": "Whether to stream the response",
            "value": False,
            "type": "bool",
        },
        {
            "field": "system",
            "helper_text": "The system prompt to be used",
            "value": "",
            "type": "string",
        },
        {
            "field": "temperature",
            "helper_text": "The “creativity” of the response - increase the temperature for more creative responses.",
            "value": 0.5,
            "type": "float",
        },
        {
            "field": "thinking_token_limit",
            "helper_text": "The maximum number of tokens the model can use for thinking",
            "value": 0,
            "type": "int64",
        },
        {
            "field": "top_p",
            "helper_text": "The “randomness” of the output - higher Top P values increase the randomness",
            "value": 0.5,
            "type": "float",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "(*)**true**(*)**(*)**(*)**(*)": {
            "inputs": [],
            "outputs": [
                {
                    "field": "response",
                    "type": "stream<string>",
                    "helper_text": "The response as a stream of text",
                }
            ],
        },
        "(*)**false**(*)**(*)**(*)**(*)": {
            "inputs": [],
            "outputs": [
                {
                    "field": "response",
                    "type": "string",
                    "helper_text": "The response as a single string",
                }
            ],
        },
        "(*)**(*)**true**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "api_key",
                    "type": "string",
                    "value": "",
                    "helper_text": "Your personal API key",
                }
            ],
            "outputs": [],
        },
        "(*)**(*)**(*)**true**(*)**(*)": {
            "inputs": [
                {
                    "field": "json_schema",
                    "type": "string",
                    "value": "",
                    "helper_text": "The schema of the JSON response",
                }
            ],
            "outputs": [],
        },
        "(*)**(*)**(*)**(*)**true**(*)": {
            "inputs": [
                {
                    "field": "citation_metadata",
                    "type": "vec<string>",
                    "value": "",
                    "helper_text": "The metadata of the sources used to generate the response",
                },
                {
                    "field": "json_response",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to return the response as a JSON object",
                },
                {
                    "field": "use_personal_api_key",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to use a personal API key",
                },
            ],
            "outputs": [],
        },
        "(*)**(*)**(*)**(*)**(*)**true": {
            "inputs": [
                {
                    "field": "max_retries",
                    "type": "int32",
                    "value": 1,
                    "helper_text": "The maximum number of retries",
                },
                {
                    "field": "retry_interval_ms",
                    "type": "int32",
                    "value": 1000,
                    "helper_text": "The interval between retries in milliseconds",
                },
            ],
            "outputs": [],
        },
        "custom**(*)**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "base_url",
                    "type": "string",
                    "value": "",
                    "helper_text": "The base URL of the custom LLM provider",
                },
                {
                    "field": "model",
                    "type": "string",
                    "value": "",
                    "helper_text": "The model to be used",
                },
                {
                    "field": "api_key",
                    "type": "string",
                    "value": "",
                    "helper_text": "Your API key",
                },
                {
                    "field": "use_personal_api_key",
                    "type": "bool",
                    "value": True,
                    "helper_text": "Whether to use a personal API key",
                },
                {
                    "field": "finetuned_model",
                    "type": "string",
                    "value": "",
                    "helper_text": "Use your finetuned model for response generation. Make sure to select the matching base model from the dropdown.",
                },
            ],
            "outputs": [],
            "title": "Custom",
        },
        "openai**(*)**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "json_response",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to return the response as a JSON object",
                },
                {
                    "field": "use_personal_api_key",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to use a personal API key",
                },
            ],
            "outputs": [],
            "title": "OpenAI",
        },
        "openai**(*)**true**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "finetuned_model",
                    "type": "string",
                    "value": "",
                    "helper_text": "Use your finetuned model for response generation. Make sure to select the matching base model from the dropdown.",
                }
            ],
            "outputs": [],
        },
        "anthropic**(*)**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "use_personal_api_key",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to use a personal API key",
                },
                {
                    "field": "json_response",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to return the response as a JSON object",
                },
            ],
            "outputs": [],
            "title": "Anthropic",
        },
        "perplexity**(*)**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "use_personal_api_key",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to use a personal API key",
                }
            ],
            "outputs": [],
            "title": "Perplexity",
        },
        "google**(*)**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "use_personal_api_key",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to use a personal API key",
                },
                {
                    "field": "json_response",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to return the response as a JSON object",
                },
            ],
            "outputs": [],
            "title": "Google",
        },
        "cohere**(*)**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "json_response",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to return the response as a JSON object",
                },
                {
                    "field": "use_personal_api_key",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to use a personal API key",
                },
            ],
            "outputs": [],
            "title": "Cohere",
        },
        "together**(*)**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "json_response",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to return the response as a JSON object",
                },
                {
                    "field": "use_personal_api_key",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to use a personal API key",
                },
            ],
            "outputs": [],
            "title": "Open Source",
        },
        "bedrock**(*)**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "json_response",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to return the response as a JSON object",
                }
            ],
            "outputs": [],
            "title": "Bedrock",
        },
        "azure**(*)**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "json_response",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to return the response as a JSON object",
                },
                {
                    "field": "use_personal_api_key",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to use a personal API key",
                },
            ],
            "outputs": [],
            "title": "Azure",
        },
        "azure**(*)**true**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "endpoint",
                    "type": "string",
                    "value": "",
                    "helper_text": "The Azure OpenAI endpoint URL (e.g., https://your-resource-name.openai.azure.com)",
                },
                {
                    "field": "deployment_id",
                    "type": "string",
                    "value": "",
                    "helper_text": "The deployment ID for the Azure OpenAI model. This is required when using Azure OpenAI services.",
                },
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = [
        "provider",
        "stream",
        "use_personal_api_key",
        "json_response",
        "show_sources",
        "retry_on_failure",
    ]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "LLM",
        provider: str | ToolInput = "openai",
        stream: bool | ToolInput = False,
        use_personal_api_key: bool | ToolInput = False,
        json_response: bool | ToolInput = False,
        show_sources: bool | ToolInput = False,
        retry_on_failure: bool | ToolInput = False,
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(provider, ToolInput):
            if provider.type == "static":
                params["provider"] = provider.value
            else:
                raise ValueError(f"provider cannot be a dynamic input")
        else:
            params["provider"] = provider
        if isinstance(stream, ToolInput):
            if stream.type == "static":
                params["stream"] = stream.value
            else:
                raise ValueError(f"stream cannot be a dynamic input")
        else:
            params["stream"] = stream
        if isinstance(use_personal_api_key, ToolInput):
            if use_personal_api_key.type == "static":
                params["use_personal_api_key"] = use_personal_api_key.value
            else:
                raise ValueError(f"use_personal_api_key cannot be a dynamic input")
        else:
            params["use_personal_api_key"] = use_personal_api_key
        if isinstance(json_response, ToolInput):
            if json_response.type == "static":
                params["json_response"] = json_response.value
            else:
                raise ValueError(f"json_response cannot be a dynamic input")
        else:
            params["json_response"] = json_response
        if isinstance(show_sources, ToolInput):
            if show_sources.type == "static":
                params["show_sources"] = show_sources.value
            else:
                raise ValueError(f"show_sources cannot be a dynamic input")
        else:
            params["show_sources"] = show_sources
        if isinstance(retry_on_failure, ToolInput):
            if retry_on_failure.type == "static":
                params["retry_on_failure"] = retry_on_failure.value
            else:
                raise ValueError(f"retry_on_failure cannot be a dynamic input")
        else:
            params["retry_on_failure"] = retry_on_failure

        super().__init__(
            tool_type="llm",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if provider is not None:
            if isinstance(provider, ToolInput):
                self.inputs["provider"] = {
                    "type": provider.type,
                    "value": provider.value or provider.description,
                }
            else:
                self.inputs["provider"] = {"type": "static", "value": provider}
        if stream is not None:
            if isinstance(stream, ToolInput):
                self.inputs["stream"] = {
                    "type": stream.type,
                    "value": stream.value or stream.description,
                }
            else:
                self.inputs["stream"] = {"type": "static", "value": stream}
        if use_personal_api_key is not None:
            if isinstance(use_personal_api_key, ToolInput):
                self.inputs["use_personal_api_key"] = {
                    "type": use_personal_api_key.type,
                    "value": use_personal_api_key.value
                    or use_personal_api_key.description,
                }
            else:
                self.inputs["use_personal_api_key"] = {
                    "type": "static",
                    "value": use_personal_api_key,
                }
        if json_response is not None:
            if isinstance(json_response, ToolInput):
                self.inputs["json_response"] = {
                    "type": json_response.type,
                    "value": json_response.value or json_response.description,
                }
            else:
                self.inputs["json_response"] = {
                    "type": "static",
                    "value": json_response,
                }
        if show_sources is not None:
            if isinstance(show_sources, ToolInput):
                self.inputs["show_sources"] = {
                    "type": show_sources.type,
                    "value": show_sources.value or show_sources.description,
                }
            else:
                self.inputs["show_sources"] = {"type": "static", "value": show_sources}
        if retry_on_failure is not None:
            if isinstance(retry_on_failure, ToolInput):
                self.inputs["retry_on_failure"] = {
                    "type": retry_on_failure.type,
                    "value": retry_on_failure.value or retry_on_failure.description,
                }
            else:
                self.inputs["retry_on_failure"] = {
                    "type": "static",
                    "value": retry_on_failure,
                }

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "LlmTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("input")
class InputTool(Tool):
    """
    Pass data of different types into your workflow.

    ## Inputs
    ### Common Inputs
        description: The description of the input
        input_type: Raw Text
        use_default_value: Set default value to be used if no value is provided
    ### When input_type = 'string' and use_default_value = True
        default_value: The default value to be used if no value is provided
    ### When input_type = 'file' and use_default_value = True
        default_value: The default value to be used if no value is provided
        file_parser: The processing model with which the document will be processed. Default processing model includes standard document parsing / OCR. Llamaparse will allow for ability to read documents with complex features (e.g., tables, charts, etc.). Llamaparse will be charged at 0.3 cents per page. Textract for most advanced data extraction and will be charged at 1.5 cents per page.
    ### When input_type = 'audio' and use_default_value = True
        default_value: The default value to be used if no value is provided
    ### When input_type = 'image' and use_default_value = True
        default_value: The default value to be used if no value is provided
    ### When input_type = 'knowledge_base' and use_default_value = True
        default_value: The default value to be used if no value is provided
    ### When input_type = 'pipeline' and use_default_value = True
        default_value: The default value to be used if no value is provided
    ### When input_type = 'vec<file>' and use_default_value = True
        default_value: The default value to be used if no value is provided
        file_parser: The processing model with which the document will be processed. Default processing model includes standard document parsing / OCR. Llamaparse will allow for ability to read documents with complex features (e.g., tables, charts, etc.). Llamaparse will be charged at 0.3 cents per page. Textract for most advanced data extraction and will be charged at 1.5 cents per page.
    ### When input_type = 'int32' and use_default_value = True
        default_value: The default value to be used if no value is provided
    ### When input_type = 'bool' and use_default_value = True
        default_value: The default value to be used if no value is provided
    ### When input_type = 'timestamp' and use_default_value = True
        default_value: The default value to be used if no value is provided
    ### When input_type = 'vec<string>' and use_default_value = True
        default_value: The default value to be used if no value is provided
    ### When input_type = 'file' and use_default_value = False
        file_parser: The processing model with which the document will be processed. Default processing model includes standard document parsing / OCR. Llamaparse will allow for ability to read documents with complex features (e.g., tables, charts, etc.). Llamaparse will be charged at 0.3 cents per page. Textract for most advanced data extraction and will be charged at 1.5 cents per page.
    ### When input_type = 'vec<file>' and use_default_value = False
        file_parser: The processing model with which the document will be processed. Default processing model includes standard document parsing / OCR. Llamaparse will allow for ability to read documents with complex features (e.g., tables, charts, etc.). Llamaparse will be charged at 0.3 cents per page. Textract for most advanced data extraction and will be charged at 1.5 cents per page.
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "description",
            "helper_text": "The description of the input",
            "value": "",
            "type": "string",
        },
        {
            "field": "input_type",
            "helper_text": "Raw Text",
            "value": "string",
            "type": "enum<string>",
        },
        {
            "field": "use_default_value",
            "helper_text": "Set default value to be used if no value is provided",
            "value": False,
            "type": "bool",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "string**false": {
            "inputs": [
                {
                    "field": "input_type",
                    "type": "enum<string>",
                    "value": "string",
                    "helper_text": "Raw Text",
                }
            ],
            "outputs": [
                {
                    "field": "text",
                    "type": "string",
                    "helper_text": "The text that was passed in",
                }
            ],
        },
        "string**true": {
            "inputs": [
                {
                    "field": "input_type",
                    "type": "enum<string>",
                    "value": "string",
                    "helper_text": "Raw Text",
                },
                {
                    "field": "default_value",
                    "type": "string",
                    "helper_text": "The default value to be used if no value is provided",
                },
            ],
            "outputs": [
                {
                    "field": "text",
                    "type": "string",
                    "helper_text": "The text that was passed in",
                }
            ],
        },
        "file**false": {
            "inputs": [
                {
                    "field": "file_parser",
                    "type": "enum<string>",
                    "value": "default",
                    "helper_text": "The processing model with which the document will be processed. Default processing model includes standard document parsing / OCR. Llamaparse will allow for ability to read documents with complex features (e.g., tables, charts, etc.). Llamaparse will be charged at 0.3 cents per page. Textract for most advanced data extraction and will be charged at 1.5 cents per page.",
                },
                {
                    "field": "input_type",
                    "type": "enum<string>",
                    "value": "file",
                    "helper_text": "File of any type: PDF, Word, MP3, JPEG, etc.",
                },
            ],
            "outputs": [
                {
                    "field": "processed_text",
                    "type": "string",
                    "helper_text": "The processed text of the file.",
                },
                {
                    "field": "file",
                    "type": "file",
                    "helper_text": "The file that was passed in",
                },
            ],
        },
        "file**true": {
            "inputs": [
                {
                    "field": "file_parser",
                    "type": "enum<string>",
                    "value": "default",
                    "helper_text": "The processing model with which the document will be processed. Default processing model includes standard document parsing / OCR. Llamaparse will allow for ability to read documents with complex features (e.g., tables, charts, etc.). Llamaparse will be charged at 0.3 cents per page. Textract for most advanced data extraction and will be charged at 1.5 cents per page.",
                },
                {
                    "field": "input_type",
                    "type": "enum<string>",
                    "value": "file",
                    "helper_text": "File of any type: PDF, Word, MP3, JPEG, etc.",
                },
                {
                    "field": "default_value",
                    "type": "file",
                    "helper_text": "The default value to be used if no value is provided",
                },
            ],
            "outputs": [
                {
                    "field": "processed_text",
                    "type": "string",
                    "helper_text": "The processed text of the file.",
                },
                {
                    "field": "file",
                    "type": "file",
                    "helper_text": "The file that was passed in",
                },
            ],
        },
        "audio**false": {
            "inputs": [
                {
                    "field": "input_type",
                    "type": "enum<string>",
                    "value": "audio",
                    "helper_text": "Allows you to record audio through the VectorShift platform. To convert the audio to text, connect the input node to a Speech to Text node",
                }
            ],
            "outputs": [
                {
                    "field": "audio",
                    "type": "audio",
                    "helper_text": "The audio that was passed in",
                }
            ],
        },
        "audio**true": {
            "inputs": [
                {
                    "field": "input_type",
                    "type": "enum<string>",
                    "value": "audio",
                    "helper_text": "Allows you to record audio through the VectorShift platform. To convert the audio to text, connect the input node to a Speech to Text node",
                },
                {
                    "field": "default_value",
                    "type": "audio",
                    "helper_text": "The default value to be used if no value is provided",
                },
            ],
            "outputs": [
                {
                    "field": "audio",
                    "type": "audio",
                    "helper_text": "The audio that was passed in",
                }
            ],
        },
        "image**false": {
            "inputs": [
                {
                    "field": "input_type",
                    "type": "enum<string>",
                    "value": "image",
                    "helper_text": "Image of any type: JPEG, PNG, etc.",
                }
            ],
            "outputs": [
                {
                    "field": "image",
                    "type": "image",
                    "helper_text": "The image that was passed in",
                }
            ],
        },
        "image**true": {
            "inputs": [
                {
                    "field": "input_type",
                    "type": "enum<string>",
                    "value": "image",
                    "helper_text": "Image of any type: JPEG, PNG, etc.",
                },
                {
                    "field": "default_value",
                    "type": "image",
                    "helper_text": "The default value to be used if no value is provided",
                },
            ],
            "outputs": [
                {
                    "field": "image",
                    "type": "image",
                    "helper_text": "The image that was passed in",
                }
            ],
        },
        "knowledge_base**false": {
            "inputs": [
                {
                    "field": "input_type",
                    "type": "enum<string>",
                    "value": "knowledge_base",
                    "helper_text": "Allows you to pass a Knowledge Base as an input",
                }
            ],
            "outputs": [
                {
                    "field": "knowledge_base",
                    "type": "knowledge_base",
                    "helper_text": "The Knowledge Base that was passed in",
                }
            ],
        },
        "knowledge_base**true": {
            "inputs": [
                {
                    "field": "input_type",
                    "type": "enum<string>",
                    "value": "knowledge_base",
                    "helper_text": "Allows you to pass a Knowledge Base as an input",
                },
                {
                    "field": "default_value",
                    "type": "knowledge_base",
                    "helper_text": "The default value to be used if no value is provided",
                },
            ],
            "outputs": [
                {
                    "field": "knowledge_base",
                    "type": "knowledge_base",
                    "helper_text": "The Knowledge Base that was passed in",
                }
            ],
        },
        "pipeline**false": {
            "inputs": [
                {
                    "field": "input_type",
                    "type": "enum<string>",
                    "value": "pipeline",
                    "helper_text": "Allows you to pass a Pipeline as an input",
                }
            ],
            "outputs": [{"field": "pipeline", "type": "pipeline"}],
        },
        "pipeline**true": {
            "inputs": [
                {
                    "field": "input_type",
                    "type": "enum<string>",
                    "value": "pipeline",
                    "helper_text": "Allows you to pass a Pipeline as an input",
                },
                {
                    "field": "default_value",
                    "type": "pipeline",
                    "helper_text": "The default value to be used if no value is provided",
                },
            ],
            "outputs": [{"field": "pipeline", "type": "pipeline"}],
        },
        "vec<file>**false": {
            "inputs": [
                {
                    "field": "file_parser",
                    "type": "enum<string>",
                    "value": "default",
                    "helper_text": "The processing model with which the document will be processed. Default processing model includes standard document parsing / OCR. Llamaparse will allow for ability to read documents with complex features (e.g., tables, charts, etc.). Llamaparse will be charged at 0.3 cents per page. Textract for most advanced data extraction and will be charged at 1.5 cents per page.",
                },
                {
                    "field": "input_type",
                    "type": "enum<string>",
                    "value": "vec<file>",
                    "helper_text": "Allows you to pass a list of files as an input",
                },
            ],
            "outputs": [
                {
                    "field": "processed_texts",
                    "type": "vec<string>",
                    "helper_text": "The processed text of the files",
                },
                {
                    "field": "files",
                    "type": "vec<file>",
                    "helper_text": "The files that were passed in",
                },
            ],
        },
        "vec<file>**true": {
            "inputs": [
                {
                    "field": "file_parser",
                    "type": "enum<string>",
                    "value": "default",
                    "helper_text": "The processing model with which the document will be processed. Default processing model includes standard document parsing / OCR. Llamaparse will allow for ability to read documents with complex features (e.g., tables, charts, etc.). Llamaparse will be charged at 0.3 cents per page. Textract for most advanced data extraction and will be charged at 1.5 cents per page.",
                },
                {
                    "field": "input_type",
                    "type": "enum<string>",
                    "value": "vec<file>",
                    "helper_text": "Allows you to pass a list of files as an input",
                },
                {
                    "field": "default_value",
                    "type": "vec<file>",
                    "helper_text": "The default value to be used if no value is provided",
                },
            ],
            "outputs": [
                {
                    "field": "processed_texts",
                    "type": "vec<string>",
                    "helper_text": "The processed text of the files",
                },
                {
                    "field": "files",
                    "type": "vec<file>",
                    "helper_text": "The files that were passed in",
                },
            ],
        },
        "int32**false": {
            "inputs": [
                {
                    "field": "input_type",
                    "type": "enum<string>",
                    "value": "int32",
                    "helper_text": "Allows you to pass an integer as an input",
                }
            ],
            "outputs": [
                {
                    "field": "value",
                    "type": "int32",
                    "helper_text": "The integer that was passed in",
                }
            ],
        },
        "int32**true": {
            "inputs": [
                {
                    "field": "input_type",
                    "type": "enum<string>",
                    "value": "int32",
                    "helper_text": "Allows you to pass an integer as an input",
                },
                {
                    "field": "default_value",
                    "type": "int32",
                    "helper_text": "The default value to be used if no value is provided",
                },
            ],
            "outputs": [
                {
                    "field": "value",
                    "type": "int32",
                    "helper_text": "The integer that was passed in",
                }
            ],
        },
        "bool**false": {
            "inputs": [
                {
                    "field": "input_type",
                    "type": "enum<string>",
                    "value": "bool",
                    "helper_text": "Allows you to pass a boolean as an input",
                }
            ],
            "outputs": [
                {
                    "field": "value",
                    "type": "bool",
                    "helper_text": "The boolean that was passed in",
                }
            ],
        },
        "bool**true": {
            "inputs": [
                {
                    "field": "input_type",
                    "type": "enum<string>",
                    "value": "bool",
                    "helper_text": "Allows you to pass a boolean as an input",
                },
                {
                    "field": "default_value",
                    "type": "bool",
                    "helper_text": "The default value to be used if no value is provided",
                },
            ],
            "outputs": [
                {
                    "field": "value",
                    "type": "bool",
                    "helper_text": "The boolean that was passed in",
                }
            ],
        },
        "timestamp**false": {
            "inputs": [
                {
                    "field": "input_type",
                    "type": "enum<string>",
                    "value": "timestamp",
                    "helper_text": "Allows you to pass a timestamp as an input",
                }
            ],
            "outputs": [
                {
                    "field": "value",
                    "type": "timestamp",
                    "helper_text": "The timestamp that was passed in",
                }
            ],
        },
        "timestamp**true": {
            "inputs": [
                {
                    "field": "input_type",
                    "type": "enum<string>",
                    "value": "timestamp",
                    "helper_text": "Allows you to pass a timestamp as an input",
                },
                {
                    "field": "default_value",
                    "type": "timestamp",
                    "helper_text": "The default value to be used if no value is provided",
                },
            ],
            "outputs": [
                {
                    "field": "value",
                    "type": "timestamp",
                    "helper_text": "The timestamp that was passed in",
                }
            ],
        },
        "vec<string>**false": {
            "inputs": [
                {
                    "field": "input_type",
                    "type": "enum<string>",
                    "value": "vec<string>",
                    "helper_text": "Allows you to pass a list of strings as an input",
                }
            ],
            "outputs": [
                {
                    "field": "value",
                    "type": "vec<string>",
                    "helper_text": "The list of strings that was passed in",
                }
            ],
        },
        "vec<string>**true": {
            "inputs": [
                {
                    "field": "input_type",
                    "type": "enum<string>",
                    "value": "vec<string>",
                    "helper_text": "Allows you to pass a list of strings as an input",
                },
                {
                    "field": "default_value",
                    "type": "vec<string>",
                    "helper_text": "The default value to be used if no value is provided",
                },
            ],
            "outputs": [
                {
                    "field": "value",
                    "type": "vec<string>",
                    "helper_text": "The list of strings that was passed in",
                }
            ],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["input_type", "use_default_value"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Pass data of different types into your workflow.",
        input_type: str | ToolInput = "string",
        use_default_value: bool | ToolInput = False,
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(input_type, ToolInput):
            if input_type.type == "static":
                params["input_type"] = input_type.value
            else:
                raise ValueError(f"input_type cannot be a dynamic input")
        else:
            params["input_type"] = input_type
        if isinstance(use_default_value, ToolInput):
            if use_default_value.type == "static":
                params["use_default_value"] = use_default_value.value
            else:
                raise ValueError(f"use_default_value cannot be a dynamic input")
        else:
            params["use_default_value"] = use_default_value

        super().__init__(
            tool_type="input",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if input_type is not None:
            if isinstance(input_type, ToolInput):
                self.inputs["input_type"] = {
                    "type": input_type.type,
                    "value": input_type.value or input_type.description,
                }
            else:
                self.inputs["input_type"] = {"type": "static", "value": input_type}
        if use_default_value is not None:
            if isinstance(use_default_value, ToolInput):
                self.inputs["use_default_value"] = {
                    "type": use_default_value.type,
                    "value": use_default_value.value or use_default_value.description,
                }
            else:
                self.inputs["use_default_value"] = {
                    "type": "static",
                    "value": use_default_value,
                }

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "InputTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("output")
class OutputTool(Tool):
    """
    Output data of different types from your workflow.

    ## Inputs
    ### Common Inputs
        description: The description of the output
        output_type: The output_type input
    ### string
        value: The value input
    ### file
        value: The value input
    ### audio
        value: The value input
    ### json
        value: The value input
    ### image
        value: The value input
    ### stream<string>
        value: The value input
    ### vec<file>
        value: The value input
    ### int32
        value: The value input
    ### float
        value: The value input
    ### bool
        value: The value input
    ### timestamp
        value: The value input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "description",
            "helper_text": "The description of the output",
            "value": "",
            "type": "string",
        },
        {
            "field": "output_type",
            "helper_text": "The output_type input",
            "value": "string",
            "type": "enum<string>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "string": {
            "inputs": [
                {"field": "value", "type": "string", "value": ""},
                {
                    "field": "output_type",
                    "type": "enum<string>",
                    "value": "string",
                    "helper_text": "Output raw text",
                },
            ],
            "outputs": [],
        },
        "file": {
            "inputs": [
                {"field": "value", "type": "file", "value": ""},
                {
                    "field": "output_type",
                    "type": "enum<string>",
                    "value": "file",
                    "helper_text": "Output file of any type: PDF, Word, Excel, CSV, MP3, JPEG, etc.",
                },
            ],
            "outputs": [],
        },
        "audio": {
            "inputs": [
                {"field": "value", "type": "audio", "value": ""},
                {
                    "field": "output_type",
                    "type": "enum<string>",
                    "value": "audio",
                    "helper_text": "Output raw audio. Output can be generated with the text to speech node",
                },
            ],
            "outputs": [],
        },
        "json": {
            "inputs": [
                {"field": "value", "type": "string", "value": ""},
                {
                    "field": "output_type",
                    "type": "enum<string>",
                    "value": "json",
                    "helper_text": "Output JSON (e.g., LLMs can output JSON - input the schema by selecting “JSON Output” in the gear of the LLM)",
                },
            ],
            "outputs": [],
        },
        "image": {
            "inputs": [
                {"field": "value", "type": "image", "value": ""},
                {
                    "field": "output_type",
                    "type": "enum<string>",
                    "value": "image",
                    "helper_text": "Output Image(s) (images are of file type PNG)",
                },
            ],
            "outputs": [],
        },
        "stream<string>": {
            "inputs": [
                {"field": "value", "type": "stream<string>", "value": ""},
                {
                    "field": "output_type",
                    "type": "enum<string>",
                    "value": "stream<string>",
                    "helper_text": "Output as a stream of raw text",
                },
            ],
            "outputs": [],
            "banner_text": 'Ensure to check "Stream Response" in gear of the LLM',
        },
        "vec<file>": {
            "inputs": [
                {"field": "value", "type": "vec<file>", "value": []},
                {
                    "field": "output_type",
                    "type": "enum<string>",
                    "value": "vec<file>",
                    "helper_text": "Output a list of files",
                },
            ],
            "outputs": [],
        },
        "int32": {
            "inputs": [
                {"field": "value", "type": "int32", "value": ""},
                {
                    "field": "output_type",
                    "type": "enum<string>",
                    "value": "int32",
                    "helper_text": "Output an integer",
                },
            ],
            "outputs": [],
        },
        "float": {
            "inputs": [
                {"field": "value", "type": "float", "value": ""},
                {
                    "field": "output_type",
                    "type": "enum<string>",
                    "value": "float",
                    "helper_text": "Output a float",
                },
            ],
            "outputs": [],
        },
        "bool": {
            "inputs": [
                {"field": "value", "type": "bool", "value": ""},
                {
                    "field": "output_type",
                    "type": "enum<string>",
                    "value": "bool",
                    "helper_text": "Output a boolean",
                },
            ],
            "outputs": [],
        },
        "timestamp": {
            "inputs": [
                {"field": "value", "type": "timestamp", "value": ""},
                {
                    "field": "output_type",
                    "type": "enum<string>",
                    "value": "timestamp",
                    "helper_text": "Output a timestamp",
                },
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["output_type"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Output data of different types from your workflow.",
        output_type: str | ToolInput = "string",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(output_type, ToolInput):
            if output_type.type == "static":
                params["output_type"] = output_type.value
            else:
                raise ValueError(f"output_type cannot be a dynamic input")
        else:
            params["output_type"] = output_type

        super().__init__(
            tool_type="output",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if output_type is not None:
            if isinstance(output_type, ToolInput):
                self.inputs["output_type"] = {
                    "type": output_type.type,
                    "value": output_type.value or output_type.description,
                }
            else:
                self.inputs["output_type"] = {"type": "static", "value": output_type}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "OutputTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("categorizer")
class CategorizerTool(Tool):
    """
    Categorize text using AI into custom-defined buckets

    ## Inputs
    ### Common Inputs
        additional_context: Provide any additional context or instructions
        fields: The fields to be categorized
        justification: Include the AI’s justification for its score
        max_tokens: The maximum number of tokens to generate
        model: The specific model for categorization
        provider: The model provider
        temperature: The temperature of the model
        text: The text that will be categorized
        top_p: The top-p value
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "additional_context",
            "helper_text": "Provide any additional context or instructions",
            "value": "",
            "type": "string",
        },
        {
            "field": "fields",
            "helper_text": "The fields to be categorized",
            "value": [],
            "type": "vec<Dict[str, Any]>",
        },
        {
            "field": "justification",
            "helper_text": "Include the AI’s justification for its score",
            "value": False,
            "type": "bool",
        },
        {
            "field": "max_tokens",
            "helper_text": "The maximum number of tokens to generate",
            "value": 2048,
            "type": "int64",
        },
        {
            "field": "model",
            "helper_text": "The specific model for categorization",
            "value": "gpt-4o",
            "type": "enum<string>",
        },
        {
            "field": "provider",
            "helper_text": "The model provider",
            "value": "openai",
            "type": "enum<string>",
        },
        {
            "field": "temperature",
            "helper_text": "The temperature of the model",
            "value": 0.7,
            "type": "float",
        },
        {
            "field": "text",
            "helper_text": "The text that will be categorized",
            "value": "",
            "type": "string",
        },
        {
            "field": "top_p",
            "helper_text": "The top-p value",
            "value": 1.0,
            "type": "float",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "true": {
            "inputs": [],
            "outputs": [
                {
                    "field": "justification",
                    "type": "string",
                    "helper_text": "The AI justification",
                }
            ],
        },
        "false": {"inputs": [], "outputs": []},
    }

    # List of parameters that affect configuration
    _PARAMS = ["justification"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Categorize text using AI into custom-defined buckets",
        justification: bool | ToolInput = False,
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(justification, ToolInput):
            if justification.type == "static":
                params["justification"] = justification.value
            else:
                raise ValueError(f"justification cannot be a dynamic input")
        else:
            params["justification"] = justification

        super().__init__(
            tool_type="categorizer",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if justification is not None:
            if isinstance(justification, ToolInput):
                self.inputs["justification"] = {
                    "type": justification.type,
                    "value": justification.value or justification.description,
                }
            else:
                self.inputs["justification"] = {
                    "type": "static",
                    "value": justification,
                }

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "CategorizerTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("extract_data")
class ExtractDataTool(Tool):
    """
    Extract key pieces of information or a list of information from a input text.

    ## Inputs
    ### Common Inputs
        additional_context: Provide any additional context or instructions
        fields: The fields input
        model: The specific model for data extraction
        processed_outputs: The processed_outputs input
        provider: The model provider
        text: The text that data will be extracted from
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "additional_context",
            "helper_text": "Provide any additional context or instructions",
            "value": "",
            "type": "string",
        },
        {
            "field": "fields",
            "helper_text": "The fields input",
            "value": [],
            "type": "vec<Dict[str, Any]>",
        },
        {
            "field": "model",
            "helper_text": "The specific model for data extraction",
            "value": "gpt-4o",
            "type": "enum<string>",
        },
        {
            "field": "processed_outputs",
            "helper_text": "The processed_outputs input",
            "value": {},
            "type": "map<string, string>",
        },
        {
            "field": "provider",
            "helper_text": "The model provider",
            "value": "openai",
            "type": "enum<string>",
        },
        {
            "field": "text",
            "helper_text": "The text that data will be extracted from",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Extract key pieces of information or a list of information from a input text.",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="extract_data",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "ExtractDataTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("data_collector")
class DataCollectorTool(Tool):
    """
    Allows a chatbot to collect information by asking the user to provide specific pieces of information (e.g., name, email, etc.).

    ## Inputs
    ### Common Inputs
        auto_generate: If checked, the node will output questions in successive order until all fields are successfully collected. If unchecked, the node will output the data that is collected (often passed to an LLM with a prompt to ask successive questions to the user, along with specific instructions after all fields are collected) - e.g., {'Field1': 'Collected_Data', 'Field2': 'Collected_Data'}
        data_collector_node_id: The ID of the data collector node
        fields: The fields to be collected
        prompt: Specific instructions of how the LLM should collect the information
        query: The query to be analysed for data collection (passed to the LLM)
    ### When auto_generate = True
        llm: The model provider
        model: The specific model for question generation
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "auto_generate",
            "helper_text": "If checked, the node will output questions in successive order until all fields are successfully collected. If unchecked, the node will output the data that is collected (often passed to an LLM with a prompt to ask successive questions to the user, along with specific instructions after all fields are collected) - e.g., {'Field1': 'Collected_Data', 'Field2': 'Collected_Data'}",
            "value": True,
            "type": "bool",
        },
        {
            "field": "data_collector_node_id",
            "helper_text": "The ID of the data collector node",
            "value": "",
            "type": "string",
        },
        {
            "field": "fields",
            "helper_text": "The fields to be collected",
            "value": [],
            "type": "vec<Dict[str, Any]>",
        },
        {
            "field": "prompt",
            "helper_text": "Specific instructions of how the LLM should collect the information",
            "value": "",
            "type": "string",
        },
        {
            "field": "query",
            "helper_text": "The query to be analysed for data collection (passed to the LLM)",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "true": {
            "inputs": [
                {
                    "field": "llm",
                    "type": "enum<string>",
                    "value": "openai",
                    "helper_text": "The model provider",
                },
                {
                    "field": "model",
                    "type": "enum<string>",
                    "value": "gpt-4-1106-preview",
                    "helper_text": "The specific model for question generation",
                },
            ],
            "outputs": [
                {
                    "field": "question",
                    "type": "string",
                    "helper_text": "The question to be asked to the user",
                }
            ],
        },
        "false": {
            "inputs": [],
            "outputs": [
                {
                    "field": "collected_data",
                    "type": "string",
                    "helper_text": "The data that is collected",
                }
            ],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["auto_generate"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Allows a chatbot to collect information by asking the user to provide specific pieces of information (e.g., name, email, etc.).",
        auto_generate: bool | ToolInput = True,
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(auto_generate, ToolInput):
            if auto_generate.type == "static":
                params["auto_generate"] = auto_generate.value
            else:
                raise ValueError(f"auto_generate cannot be a dynamic input")
        else:
            params["auto_generate"] = auto_generate

        super().__init__(
            tool_type="data_collector",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if auto_generate is not None:
            if isinstance(auto_generate, ToolInput):
                self.inputs["auto_generate"] = {
                    "type": auto_generate.type,
                    "value": auto_generate.value or auto_generate.description,
                }
            else:
                self.inputs["auto_generate"] = {
                    "type": "static",
                    "value": auto_generate,
                }

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "DataCollectorTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("scorer")
class ScorerTool(Tool):
    """
    Score text using AI based on a set of criteria.

    ## Inputs
    ### Common Inputs
        additional_context: Provide any additional context or instructions
        criteria: The criteria that the text will be scored
        justification: Include the AI’s justification for its score
        model: The specific model for scoring
        provider: The model provider
        text: The text that will be scored
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "additional_context",
            "helper_text": "Provide any additional context or instructions",
            "value": "",
            "type": "string",
        },
        {
            "field": "criteria",
            "helper_text": "The criteria that the text will be scored",
            "value": "",
            "type": "string",
        },
        {
            "field": "justification",
            "helper_text": "Include the AI’s justification for its score",
            "value": False,
            "type": "bool",
        },
        {
            "field": "model",
            "helper_text": "The specific model for scoring",
            "value": "gpt-4o",
            "type": "enum<string>",
        },
        {
            "field": "provider",
            "helper_text": "The model provider",
            "value": "openai",
            "type": "enum<string>",
        },
        {
            "field": "text",
            "helper_text": "The text that will be scored",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "true": {
            "inputs": [],
            "outputs": [
                {
                    "field": "justification",
                    "type": "string",
                    "helper_text": "The AI justification",
                }
            ],
        },
        "false": {"inputs": [], "outputs": []},
    }

    # List of parameters that affect configuration
    _PARAMS = ["justification"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Score text using AI based on a set of criteria.",
        justification: bool | ToolInput = False,
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(justification, ToolInput):
            if justification.type == "static":
                params["justification"] = justification.value
            else:
                raise ValueError(f"justification cannot be a dynamic input")
        else:
            params["justification"] = justification

        super().__init__(
            tool_type="scorer",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if justification is not None:
            if isinstance(justification, ToolInput):
                self.inputs["justification"] = {
                    "type": justification.type,
                    "value": justification.value or justification.description,
                }
            else:
                self.inputs["justification"] = {
                    "type": "static",
                    "value": justification,
                }

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "ScorerTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("speech_to_text")
class SpeechToTextTool(Tool):
    """


    ## Inputs
    ### Common Inputs
        audio: The audio input
        model: The model input
    ### Deepgram
        submodel: The submodel input
        tier: The tier input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "audio",
            "helper_text": "The audio input",
            "value": "",
            "type": "audio",
        },
        {
            "field": "model",
            "helper_text": "The model input",
            "value": "OpenAI Whisper",
            "type": "enum<string>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "OpenAI Whisper": {"inputs": [], "outputs": []},
        "Deepgram": {
            "inputs": [
                {"field": "submodel", "type": "enum<string>", "value": "nova-2"},
                {"field": "tier", "type": "enum<string>", "value": "general"},
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["model"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "",
        model: str | ToolInput = "OpenAI Whisper",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(model, ToolInput):
            if model.type == "static":
                params["model"] = model.value
            else:
                raise ValueError(f"model cannot be a dynamic input")
        else:
            params["model"] = model

        super().__init__(
            tool_type="speech_to_text",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if model is not None:
            if isinstance(model, ToolInput):
                self.inputs["model"] = {
                    "type": model.type,
                    "value": model.value or model.description,
                }
            else:
                self.inputs["model"] = {"type": "static", "value": model}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "SpeechToTextTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("file_save")
class FileSaveTool(Tool):
    """
    Save a file on the VectorShift platform (under the 'Files' tab).

    ## Inputs
    ### Common Inputs
        files: The files to be saved
        name: The name of the file
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "files",
            "helper_text": "The files to be saved",
            "value": [""],
            "type": "vec<file>",
        },
        {
            "field": "name",
            "helper_text": "The name of the file",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Save a file on the VectorShift platform (under the 'Files' tab).",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="file_save",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "FileSaveTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("image_gen")
class ImageGenTool(Tool):
    """


    ## Inputs
    ### Common Inputs
        aspect_ratio: The aspect_ratio input
        image_count: The image_count input
        model: The model input
        prompt: The prompt input
        provider: The provider input
        size: The size input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "aspect_ratio",
            "helper_text": "The aspect_ratio input",
            "value": "1:1",
            "type": "enum<string>",
        },
        {
            "field": "image_count",
            "helper_text": "The image_count input",
            "value": "1",
            "type": "string",
        },
        {
            "field": "model",
            "helper_text": "The model input",
            "value": "gpt-4-1106-preview",
            "type": "enum<string>",
        },
        {
            "field": "prompt",
            "helper_text": "The prompt input",
            "value": "",
            "type": "string",
        },
        {
            "field": "provider",
            "helper_text": "The provider input",
            "value": "llmOpenAI",
            "type": "enum<string>",
        },
        {
            "field": "size",
            "helper_text": "The size input",
            "value": "512x512",
            "type": "enum<string>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="image_gen",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "ImageGenTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("file")
class FileTool(Tool):
    """
    Load a static file into the workflow as a raw File or process it into Text.

    ## Inputs
    ### Common Inputs
        file_parser: The processing model with which the document will be processed. Default processing model includes standard document parsing / OCR. Llamaparse will allow for ability to read documents with complex features (e.g., tables, charts, etc.). Llamaparse will be charged at 0.3 cents per page. Textract for most advanced data extraction and will be charged at 1.5 cents per page.
        selected_option: Select an existing file from the VectorShift platform
    ### upload
        file: The file that was passed in
    ### name
        file_name: The name of the file from the VectorShift platform (for files on the File tab)
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "file_parser",
            "helper_text": "The processing model with which the document will be processed. Default processing model includes standard document parsing / OCR. Llamaparse will allow for ability to read documents with complex features (e.g., tables, charts, etc.). Llamaparse will be charged at 0.3 cents per page. Textract for most advanced data extraction and will be charged at 1.5 cents per page.",
            "value": "default",
            "type": "enum<string>",
        },
        {
            "field": "selected_option",
            "helper_text": "Select an existing file from the VectorShift platform",
            "value": "upload",
            "type": "enum<string>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "upload": {
            "inputs": [
                {
                    "field": "file",
                    "type": "file",
                    "helper_text": "The file that was passed in",
                }
            ],
            "outputs": [],
        },
        "name": {
            "inputs": [
                {
                    "field": "file_name",
                    "type": "string",
                    "value": "",
                    "helper_text": "The name of the file from the VectorShift platform (for files on the File tab)",
                }
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["selected_option"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Load a static file into the workflow as a raw File or process it into Text.",
        selected_option: str | ToolInput = "upload",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(selected_option, ToolInput):
            if selected_option.type == "static":
                params["selected_option"] = selected_option.value
            else:
                raise ValueError(f"selected_option cannot be a dynamic input")
        else:
            params["selected_option"] = selected_option

        super().__init__(
            tool_type="file",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if selected_option is not None:
            if isinstance(selected_option, ToolInput):
                self.inputs["selected_option"] = {
                    "type": selected_option.type,
                    "value": selected_option.value or selected_option.description,
                }
            else:
                self.inputs["selected_option"] = {
                    "type": "static",
                    "value": selected_option,
                }

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "FileTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("get_list_item")
class GetListItemTool(Tool):
    """
    Get a value from a list given an index. The first item in the list is index 0.

    ## Inputs
    ### Common Inputs
        index: The index of the item to retrieve
        type: The type of the list
    ### <T>
        list: The list to retrieve the item from
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "index",
            "helper_text": "The index of the item to retrieve",
            "value": 0,
            "type": "int32",
        },
        {
            "field": "type",
            "helper_text": "The type of the list",
            "value": "string",
            "type": "enum<string>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "<T>": {
            "inputs": [
                {
                    "field": "list",
                    "type": "vec<<T>>",
                    "value": "",
                    "helper_text": "The list to retrieve the item from",
                }
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "<T>",
                    "helper_text": "The item retrieved from the list",
                }
            ],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["type"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Get a value from a list given an index. The first item in the list is index 0.",
        type: str | ToolInput = "string",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(type, ToolInput):
            if type.type == "static":
                params["type"] = type.value
            else:
                raise ValueError(f"type cannot be a dynamic input")
        else:
            params["type"] = type

        super().__init__(
            tool_type="get_list_item",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if type is not None:
            if isinstance(type, ToolInput):
                self.inputs["type"] = {
                    "type": type.type,
                    "value": type.value or type.description,
                }
            else:
                self.inputs["type"] = {"type": "static", "value": type}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "GetListItemTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("llm_open_ai_vision")
class LlmOpenAiVisionTool(Tool):
    """


    ## Inputs
    ### Common Inputs
        image: The image input
        json_response: The json_response input
        max_tokens: The max_tokens input
        model: The model input
        prompt: The prompt input
        provider: The provider input
        stream: The stream input
        system: The system input
        temperature: The temperature input
        top_p: The top_p input
        use_personal_api_key: The use_personal_api_key input
    ### When use_personal_api_key = True
        api_key: The api_key input
    ### When json_response = True
        json_schema: The json_schema input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "image",
            "helper_text": "The image input",
            "value": None,
            "type": "image",
        },
        {
            "field": "json_response",
            "helper_text": "The json_response input",
            "value": False,
            "type": "bool",
        },
        {
            "field": "max_tokens",
            "helper_text": "The max_tokens input",
            "value": 128000,
            "type": "int32",
        },
        {
            "field": "model",
            "helper_text": "The model input",
            "value": "gpt-4-vision-preview",
            "type": "enum<string>",
        },
        {
            "field": "prompt",
            "helper_text": "The prompt input",
            "value": "",
            "type": "string",
        },
        {
            "field": "provider",
            "helper_text": "The provider input",
            "value": "openAiImageToText",
            "type": "enum<string>",
        },
        {
            "field": "stream",
            "helper_text": "The stream input",
            "value": False,
            "type": "bool",
        },
        {
            "field": "system",
            "helper_text": "The system input",
            "value": "",
            "type": "string",
        },
        {
            "field": "temperature",
            "helper_text": "The temperature input",
            "value": 0.7,
            "type": "float",
        },
        {
            "field": "top_p",
            "helper_text": "The top_p input",
            "value": 0.9,
            "type": "float",
        },
        {
            "field": "use_personal_api_key",
            "helper_text": "The use_personal_api_key input",
            "value": False,
            "type": "bool",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "(*)**true**(*)**(*)": {
            "inputs": [],
            "outputs": [{"field": "response_deltas", "type": "Stream<string>"}],
        },
        "(*)**false**(*)**(*)": {"inputs": [], "outputs": []},
        "(*)**(*)**true**(*)": {
            "inputs": [{"field": "api_key", "type": "string", "value": ""}],
            "outputs": [],
        },
        "(*)**(*)**false**(*)": {"inputs": [], "outputs": []},
        "(*)**(*)**(*)**true": {
            "inputs": [{"field": "json_schema", "type": "string", "value": ""}],
            "outputs": [],
        },
        "(*)**(*)**(*)**false": {"inputs": [], "outputs": []},
    }

    # List of parameters that affect configuration
    _PARAMS = ["provider", "stream", "use_personal_api_key", "json_response"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "",
        provider: str | ToolInput = "openAiImageToText",
        stream: bool | ToolInput = False,
        use_personal_api_key: bool | ToolInput = False,
        json_response: bool | ToolInput = False,
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(provider, ToolInput):
            if provider.type == "static":
                params["provider"] = provider.value
            else:
                raise ValueError(f"provider cannot be a dynamic input")
        else:
            params["provider"] = provider
        if isinstance(stream, ToolInput):
            if stream.type == "static":
                params["stream"] = stream.value
            else:
                raise ValueError(f"stream cannot be a dynamic input")
        else:
            params["stream"] = stream
        if isinstance(use_personal_api_key, ToolInput):
            if use_personal_api_key.type == "static":
                params["use_personal_api_key"] = use_personal_api_key.value
            else:
                raise ValueError(f"use_personal_api_key cannot be a dynamic input")
        else:
            params["use_personal_api_key"] = use_personal_api_key
        if isinstance(json_response, ToolInput):
            if json_response.type == "static":
                params["json_response"] = json_response.value
            else:
                raise ValueError(f"json_response cannot be a dynamic input")
        else:
            params["json_response"] = json_response

        super().__init__(
            tool_type="llm_open_ai_vision",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if provider is not None:
            if isinstance(provider, ToolInput):
                self.inputs["provider"] = {
                    "type": provider.type,
                    "value": provider.value or provider.description,
                }
            else:
                self.inputs["provider"] = {"type": "static", "value": provider}
        if stream is not None:
            if isinstance(stream, ToolInput):
                self.inputs["stream"] = {
                    "type": stream.type,
                    "value": stream.value or stream.description,
                }
            else:
                self.inputs["stream"] = {"type": "static", "value": stream}
        if use_personal_api_key is not None:
            if isinstance(use_personal_api_key, ToolInput):
                self.inputs["use_personal_api_key"] = {
                    "type": use_personal_api_key.type,
                    "value": use_personal_api_key.value
                    or use_personal_api_key.description,
                }
            else:
                self.inputs["use_personal_api_key"] = {
                    "type": "static",
                    "value": use_personal_api_key,
                }
        if json_response is not None:
            if isinstance(json_response, ToolInput):
                self.inputs["json_response"] = {
                    "type": json_response.type,
                    "value": json_response.value or json_response.description,
                }
            else:
                self.inputs["json_response"] = {
                    "type": "static",
                    "value": json_response,
                }

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "LlmOpenAiVisionTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("llm_google_vision")
class LlmGoogleVisionTool(Tool):
    """


    ## Inputs
    ### Common Inputs
        api_key: The api_key input
        image: The image input
        json_response: The json_response input
        max_tokens: The max_tokens input
        model: The model input
        prompt: The prompt input
        provider: The provider input
        stream: The stream input
        temperature: The temperature input
        top_p: The top_p input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "api_key",
            "helper_text": "The api_key input",
            "value": "",
            "type": "string",
        },
        {
            "field": "image",
            "helper_text": "The image input",
            "value": None,
            "type": "image",
        },
        {
            "field": "json_response",
            "helper_text": "The json_response input",
            "value": False,
            "type": "bool",
        },
        {
            "field": "max_tokens",
            "helper_text": "The max_tokens input",
            "value": 32760,
            "type": "int32",
        },
        {
            "field": "model",
            "helper_text": "The model input",
            "value": "gemini-pro-vision",
            "type": "enum<string>",
        },
        {
            "field": "prompt",
            "helper_text": "The prompt input",
            "value": "",
            "type": "string",
        },
        {
            "field": "provider",
            "helper_text": "The provider input",
            "value": "googleImageToText",
            "type": "enum<string>",
        },
        {
            "field": "stream",
            "helper_text": "The stream input",
            "value": False,
            "type": "bool",
        },
        {
            "field": "temperature",
            "helper_text": "The temperature input",
            "value": 0.7,
            "type": "float",
        },
        {
            "field": "top_p",
            "helper_text": "The top_p input",
            "value": 0.9,
            "type": "float",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="llm_google_vision",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "LlmGoogleVisionTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("split_text")
class SplitTextTool(Tool):
    """
    Takes input text and separate it into a List of texts based on the delimiter.

    ## Inputs
    ### Common Inputs
        delimiter: The delimiter to split the text on
        text: The text to split
    ### character(s)
        character: The character(s) to split the text on
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "delimiter",
            "helper_text": "The delimiter to split the text on",
            "value": "space",
            "type": "enum<string>",
        },
        {
            "field": "text",
            "helper_text": "The text to split",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "character(s)": {
            "inputs": [
                {
                    "field": "character",
                    "type": "string",
                    "value": "",
                    "helper_text": "The character(s) to split the text on",
                }
            ],
            "outputs": [],
        },
        "space": {"inputs": [], "outputs": []},
        "newline": {"inputs": [], "outputs": []},
    }

    # List of parameters that affect configuration
    _PARAMS = ["delimiter"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Takes input text and separate it into a List of texts based on the delimiter.",
        delimiter: str | ToolInput = "space",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(delimiter, ToolInput):
            if delimiter.type == "static":
                params["delimiter"] = delimiter.value
            else:
                raise ValueError(f"delimiter cannot be a dynamic input")
        else:
            params["delimiter"] = delimiter

        super().__init__(
            tool_type="split_text",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if delimiter is not None:
            if isinstance(delimiter, ToolInput):
                self.inputs["delimiter"] = {
                    "type": delimiter.type,
                    "value": delimiter.value or delimiter.description,
                }
            else:
                self.inputs["delimiter"] = {"type": "static", "value": delimiter}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "SplitTextTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("summarizer")
class SummarizerTool(Tool):
    """
    Summarize text with AI

    ## Inputs
    ### Common Inputs
        model: The specific model for summarization
        provider: The model provider
        text: The text to be summarized
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "model",
            "helper_text": "The specific model for summarization",
            "value": "gpt-4o",
            "type": "enum<string>",
        },
        {
            "field": "provider",
            "helper_text": "The model provider",
            "value": "openai",
            "type": "enum<string>",
        },
        {
            "field": "text",
            "helper_text": "The text to be summarized",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Summarize text with AI",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="summarizer",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "SummarizerTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("text")
class TextTool(Tool):
    """
    Accepts Text from upstream nodes and allows you to write additional text / concatenate different texts to pass to downstream nodes.

    ## Inputs
    ### Common Inputs
        text: The text to be processed
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "text",
            "helper_text": "The text to be processed",
            "value": "",
            "type": "string",
        }
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Accepts Text from upstream nodes and allows you to write additional text / concatenate different texts to pass to downstream nodes.",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="text",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "TextTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("text_to_file")
class TextToFileTool(Tool):
    """
    Convert data from type Text to type File

    ## Inputs
    ### Common Inputs
        file_type: The type of file to convert the text to.
        text: The text for conversion.
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "file_type",
            "helper_text": "The type of file to convert the text to.",
            "value": "PDF",
            "type": "enum<string>",
        },
        {
            "field": "text",
            "helper_text": "The text for conversion.",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Convert data from type Text to type File",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="text_to_file",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "TextToFileTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("time")
class TimeTool(Tool):
    """
    Outputs the current time (often connected to LLM node)

    ## Inputs
    ### Common Inputs
        delta_time_unit: The unit of the delta
        delta_value: The value of the delta
        is_positive: If the time should be positive
        is_positive_delta: If the time should be positive
        output_format: The format of the output time
        time_node_zone: The timezone of the time node
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "delta_time_unit",
            "helper_text": "The unit of the delta",
            "value": "Seconds",
            "type": "enum<string>",
        },
        {
            "field": "delta_value",
            "helper_text": "The value of the delta",
            "value": 0,
            "type": "int32",
        },
        {
            "field": "is_positive",
            "helper_text": "If the time should be positive",
            "value": "+",
            "type": "enum<string>",
        },
        {
            "field": "is_positive_delta",
            "helper_text": "If the time should be positive",
            "value": True,
            "type": "bool",
        },
        {
            "field": "output_format",
            "helper_text": "The format of the output time",
            "value": "DD/MM/YYYY",
            "type": "enum<string>",
        },
        {
            "field": "time_node_zone",
            "helper_text": "The timezone of the time node",
            "value": "America/New_York",
            "type": "enum<string>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Outputs the current time (often connected to LLM node)",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="time",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "TimeTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("translator")
class TranslatorTool(Tool):
    """
    Translate text from one language to another

    ## Inputs
    ### Common Inputs
        model: The specific model for translation
        provider: The model provider
        source_language: The language of the input text
        target_language: The language to translate to
        text: The text to be translated
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "model",
            "helper_text": "The specific model for translation",
            "value": "gpt-4o",
            "type": "enum<string>",
        },
        {
            "field": "provider",
            "helper_text": "The model provider",
            "value": "openai",
            "type": "enum<string>",
        },
        {
            "field": "source_language",
            "helper_text": "The language of the input text",
            "value": "Detect Language",
            "type": "enum<string>",
        },
        {
            "field": "target_language",
            "helper_text": "The language to translate to",
            "value": "English",
            "type": "enum<string>",
        },
        {
            "field": "text",
            "helper_text": "The text to be translated",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Translate text from one language to another",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="translator",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "TranslatorTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("tts_eleven_labs")
class TtsElevenLabsTool(Tool):
    """


    ## Inputs
    ### Common Inputs
        api_key: The api_key input
        model: The model input
        text: The text input
        voice: The voice input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "api_key",
            "helper_text": "The api_key input",
            "value": "",
            "type": "string",
        },
        {
            "field": "model",
            "helper_text": "The model input",
            "value": "eleven_multilingual_v2",
            "type": "enum<string>",
        },
        {
            "field": "text",
            "helper_text": "The text input",
            "value": "",
            "type": "string",
        },
        {
            "field": "voice",
            "helper_text": "The voice input",
            "value": "shimmer",
            "type": "enum<string>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="tts_eleven_labs",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "TtsElevenLabsTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("tts_open_ai")
class TtsOpenAiTool(Tool):
    """


    ## Inputs
    ### Common Inputs
        model: The model input
        text: The text input
        use_personal_api_key: The use_personal_api_key input
        voice: The voice input
    ### When use_personal_api_key = True
        api_key: The api_key input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "model",
            "helper_text": "The model input",
            "value": "tts-1",
            "type": "enum<string>",
        },
        {
            "field": "text",
            "helper_text": "The text input",
            "value": "",
            "type": "string",
        },
        {
            "field": "use_personal_api_key",
            "helper_text": "The use_personal_api_key input",
            "value": False,
            "type": "bool",
        },
        {
            "field": "voice",
            "helper_text": "The voice input",
            "value": "alloy",
            "type": "enum<string>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "false": {"inputs": [], "outputs": []},
        "true": {
            "inputs": [{"field": "api_key", "type": "string", "value": ""}],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["use_personal_api_key"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "",
        use_personal_api_key: bool | ToolInput = False,
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(use_personal_api_key, ToolInput):
            if use_personal_api_key.type == "static":
                params["use_personal_api_key"] = use_personal_api_key.value
            else:
                raise ValueError(f"use_personal_api_key cannot be a dynamic input")
        else:
            params["use_personal_api_key"] = use_personal_api_key

        super().__init__(
            tool_type="tts_open_ai",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if use_personal_api_key is not None:
            if isinstance(use_personal_api_key, ToolInput):
                self.inputs["use_personal_api_key"] = {
                    "type": use_personal_api_key.type,
                    "value": use_personal_api_key.value
                    or use_personal_api_key.description,
                }
            else:
                self.inputs["use_personal_api_key"] = {
                    "type": "static",
                    "value": use_personal_api_key,
                }

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "TtsOpenAiTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("ai_audio_operations")
class AiAudioOperationsTool(Tool):
    """


    ## Inputs
    ### Common Inputs
        sub_type: The sub_type input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "sub_type",
            "helper_text": "The sub_type input",
            "value": "",
            "type": "string",
        }
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="ai_audio_operations",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "AiAudioOperationsTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("ai_text_to_speech")
class AiTextToSpeechTool(Tool):
    """
    Generate Audio from text using AI

    ## Inputs
    ### Common Inputs
        model: Select the text-to-speech model
        provider: Select the model provider.
        text: The text for conversion.
        use_personal_api_key: Use your personal API key
        voice: Select the voice
    ### When use_personal_api_key = True
        api_key: Input your personal API key from the model provider. Note: if you do not have access to the selected model, the workflow will not run
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "model",
            "helper_text": "Select the text-to-speech model",
            "value": "tts-1",
            "type": "enum<string>",
        },
        {
            "field": "provider",
            "helper_text": "Select the model provider.",
            "value": "openai",
            "type": "enum<string>",
        },
        {
            "field": "text",
            "helper_text": "The text for conversion.",
            "value": "",
            "type": "string",
        },
        {
            "field": "use_personal_api_key",
            "helper_text": "Use your personal API key",
            "value": False,
            "type": "bool",
        },
        {
            "field": "voice",
            "helper_text": "Select the voice",
            "value": "alloy",
            "type": "enum<string>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "false**(*)": {"inputs": [], "outputs": []},
        "true**(*)": {
            "inputs": [
                {
                    "field": "api_key",
                    "type": "string",
                    "value": "",
                    "helper_text": "Input your personal API key from the model provider. Note: if you do not have access to the selected model, the workflow will not run",
                }
            ],
            "outputs": [],
        },
        "(*)**openai": {"inputs": [], "outputs": [], "title": "OpenAI Text to Speech"},
        "(*)**eleven_labs": {
            "inputs": [],
            "outputs": [],
            "title": "Eleven Labs Text to Speech",
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["use_personal_api_key", "provider"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Generate Audio from text using AI",
        use_personal_api_key: bool | ToolInput = False,
        provider: str | ToolInput = "openai",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(use_personal_api_key, ToolInput):
            if use_personal_api_key.type == "static":
                params["use_personal_api_key"] = use_personal_api_key.value
            else:
                raise ValueError(f"use_personal_api_key cannot be a dynamic input")
        else:
            params["use_personal_api_key"] = use_personal_api_key
        if isinstance(provider, ToolInput):
            if provider.type == "static":
                params["provider"] = provider.value
            else:
                raise ValueError(f"provider cannot be a dynamic input")
        else:
            params["provider"] = provider

        super().__init__(
            tool_type="ai_text_to_speech",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if use_personal_api_key is not None:
            if isinstance(use_personal_api_key, ToolInput):
                self.inputs["use_personal_api_key"] = {
                    "type": use_personal_api_key.type,
                    "value": use_personal_api_key.value
                    or use_personal_api_key.description,
                }
            else:
                self.inputs["use_personal_api_key"] = {
                    "type": "static",
                    "value": use_personal_api_key,
                }
        if provider is not None:
            if isinstance(provider, ToolInput):
                self.inputs["provider"] = {
                    "type": provider.type,
                    "value": provider.value or provider.description,
                }
            else:
                self.inputs["provider"] = {"type": "static", "value": provider}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "AiTextToSpeechTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("ai_speech_to_text")
class AiSpeechToTextTool(Tool):
    """
    Generate Text from Audio using AI

    ## Inputs
    ### Common Inputs
        audio: The audio for conversion
        model: Select the speech-to-text model
        provider: Select the model provider.
        use_personal_api_key: Use your personal API key
    ### When use_personal_api_key = True
        api_key: The api_key input
    ### When provider = 'deepgram'
        tier: Select the tier
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "audio",
            "helper_text": "The audio for conversion",
            "value": "",
            "type": "audio",
        },
        {
            "field": "model",
            "helper_text": "Select the speech-to-text model",
            "value": "whisper-1",
            "type": "enum<string>",
        },
        {
            "field": "provider",
            "helper_text": "Select the model provider.",
            "value": "openai",
            "type": "enum<string>",
        },
        {
            "field": "use_personal_api_key",
            "helper_text": "Use your personal API key",
            "value": False,
            "type": "bool",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "(*)**openai": {"inputs": [], "outputs": [], "title": "OpenAI Speech to Text"},
        "(*)**deepgram": {
            "inputs": [
                {
                    "field": "tier",
                    "type": "enum<string>",
                    "value": "general",
                    "helper_text": "Select the tier",
                }
            ],
            "outputs": [],
            "title": "Deepgram Speech to Text",
        },
        "false**(*)": {"inputs": [], "outputs": []},
        "true**(*)": {
            "inputs": [{"field": "api_key", "type": "string", "value": ""}],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["use_personal_api_key", "provider"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Generate Text from Audio using AI",
        use_personal_api_key: bool | ToolInput = False,
        provider: str | ToolInput = "openai",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(use_personal_api_key, ToolInput):
            if use_personal_api_key.type == "static":
                params["use_personal_api_key"] = use_personal_api_key.value
            else:
                raise ValueError(f"use_personal_api_key cannot be a dynamic input")
        else:
            params["use_personal_api_key"] = use_personal_api_key
        if isinstance(provider, ToolInput):
            if provider.type == "static":
                params["provider"] = provider.value
            else:
                raise ValueError(f"provider cannot be a dynamic input")
        else:
            params["provider"] = provider

        super().__init__(
            tool_type="ai_speech_to_text",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if use_personal_api_key is not None:
            if isinstance(use_personal_api_key, ToolInput):
                self.inputs["use_personal_api_key"] = {
                    "type": use_personal_api_key.type,
                    "value": use_personal_api_key.value
                    or use_personal_api_key.description,
                }
            else:
                self.inputs["use_personal_api_key"] = {
                    "type": "static",
                    "value": use_personal_api_key,
                }
        if provider is not None:
            if isinstance(provider, ToolInput):
                self.inputs["provider"] = {
                    "type": provider.type,
                    "value": provider.value or provider.description,
                }
            else:
                self.inputs["provider"] = {"type": "static", "value": provider}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "AiSpeechToTextTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("ai_image_operations")
class AiImageOperationsTool(Tool):
    """


    ## Inputs
    ### Common Inputs
        sub_type: The sub_type input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "sub_type",
            "helper_text": "The sub_type input",
            "value": "",
            "type": "string",
        }
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="ai_image_operations",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "AiImageOperationsTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("ai_image_to_text")
class AiImageToTextTool(Tool):
    """
    Generate Text from Image using AI

    ## Inputs
    ### Common Inputs
        image: The image for conversion
        json_response: Return the response as a JSON object
        max_tokens: The maximum number of tokens to generate
        model: Select the image-to-text model
        prompt: The data that is sent to the LLM. Add data from other nodes with double curly braces, e.g., {{input1}}
        provider: Select the model provider.
        stream: Stream the response
        system: Tell the AI model how you would like it to respond. Be as specific as possible. For example, you can instruct the model on what tone to respond in or how to respond given the information you provide
        temperature: The temperature of the model
        top_p: The top-p value
        use_personal_api_key: Use your personal API key
    ### When use_personal_api_key = True
        api_key: Input your personal API key from the model provider. Note: if you do not have access to the selected model, the workflow will not run
    ### When json_response = True
        json_schema: The JSON schema to use for the response
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "image",
            "helper_text": "The image for conversion",
            "value": None,
            "type": "image",
        },
        {
            "field": "json_response",
            "helper_text": "Return the response as a JSON object",
            "value": False,
            "type": "bool",
        },
        {
            "field": "max_tokens",
            "helper_text": "The maximum number of tokens to generate",
            "value": 128000,
            "type": "int64",
        },
        {
            "field": "model",
            "helper_text": "Select the image-to-text model",
            "value": "chatgpt-4o-latest",
            "type": "enum<string>",
        },
        {
            "field": "prompt",
            "helper_text": "The data that is sent to the LLM. Add data from other nodes with double curly braces, e.g., {{input1}}",
            "value": "",
            "type": "string",
        },
        {
            "field": "provider",
            "helper_text": "Select the model provider.",
            "value": "openai",
            "type": "enum<string>",
        },
        {
            "field": "stream",
            "helper_text": "Stream the response",
            "value": False,
            "type": "bool",
        },
        {
            "field": "system",
            "helper_text": "Tell the AI model how you would like it to respond. Be as specific as possible. For example, you can instruct the model on what tone to respond in or how to respond given the information you provide",
            "value": "",
            "type": "string",
        },
        {
            "field": "temperature",
            "helper_text": "The temperature of the model",
            "value": 0.7,
            "type": "float",
        },
        {
            "field": "top_p",
            "helper_text": "The top-p value",
            "value": 0.9,
            "type": "float",
        },
        {
            "field": "use_personal_api_key",
            "helper_text": "Use your personal API key",
            "value": False,
            "type": "bool",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "false**(*)**(*)**(*)": {"inputs": [], "outputs": []},
        "true**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "api_key",
                    "type": "string",
                    "value": "",
                    "helper_text": "Input your personal API key from the model provider. Note: if you do not have access to the selected model, the workflow will not run",
                }
            ],
            "outputs": [],
        },
        "(*)**false**(*)**(*)": {"inputs": [], "outputs": []},
        "(*)**true**(*)**(*)": {
            "inputs": [
                {
                    "field": "json_schema",
                    "type": "string",
                    "value": "",
                    "helper_text": "The JSON schema to use for the response",
                }
            ],
            "outputs": [],
        },
        "(*)**(*)**false**(*)": {
            "inputs": [],
            "outputs": [
                {
                    "field": "text",
                    "type": "string",
                    "helper_text": "The Text from the Image.",
                }
            ],
        },
        "(*)**(*)**true**(*)": {
            "inputs": [],
            "outputs": [
                {
                    "field": "text",
                    "type": "stream<string>",
                    "helper_text": "Stream of text generated from the Image.",
                }
            ],
        },
        "(*)**(*)**(*)**openai": {
            "inputs": [],
            "outputs": [],
            "title": "OpenAI Image to Text",
        },
        "(*)**(*)**(*)**anthropic": {
            "inputs": [],
            "outputs": [],
            "title": "Anthropic Image to Text",
        },
        "(*)**(*)**(*)**google": {
            "inputs": [],
            "outputs": [],
            "title": "Google Image to Text",
        },
        "(*)**(*)**(*)**xai": {
            "inputs": [],
            "outputs": [],
            "title": "XAI Image to Text",
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["use_personal_api_key", "json_response", "stream", "provider"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Generate Text from Image using AI",
        use_personal_api_key: bool | ToolInput = False,
        json_response: bool | ToolInput = False,
        stream: bool | ToolInput = False,
        provider: str | ToolInput = "openai",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(use_personal_api_key, ToolInput):
            if use_personal_api_key.type == "static":
                params["use_personal_api_key"] = use_personal_api_key.value
            else:
                raise ValueError(f"use_personal_api_key cannot be a dynamic input")
        else:
            params["use_personal_api_key"] = use_personal_api_key
        if isinstance(json_response, ToolInput):
            if json_response.type == "static":
                params["json_response"] = json_response.value
            else:
                raise ValueError(f"json_response cannot be a dynamic input")
        else:
            params["json_response"] = json_response
        if isinstance(stream, ToolInput):
            if stream.type == "static":
                params["stream"] = stream.value
            else:
                raise ValueError(f"stream cannot be a dynamic input")
        else:
            params["stream"] = stream
        if isinstance(provider, ToolInput):
            if provider.type == "static":
                params["provider"] = provider.value
            else:
                raise ValueError(f"provider cannot be a dynamic input")
        else:
            params["provider"] = provider

        super().__init__(
            tool_type="ai_image_to_text",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if use_personal_api_key is not None:
            if isinstance(use_personal_api_key, ToolInput):
                self.inputs["use_personal_api_key"] = {
                    "type": use_personal_api_key.type,
                    "value": use_personal_api_key.value
                    or use_personal_api_key.description,
                }
            else:
                self.inputs["use_personal_api_key"] = {
                    "type": "static",
                    "value": use_personal_api_key,
                }
        if json_response is not None:
            if isinstance(json_response, ToolInput):
                self.inputs["json_response"] = {
                    "type": json_response.type,
                    "value": json_response.value or json_response.description,
                }
            else:
                self.inputs["json_response"] = {
                    "type": "static",
                    "value": json_response,
                }
        if stream is not None:
            if isinstance(stream, ToolInput):
                self.inputs["stream"] = {
                    "type": stream.type,
                    "value": stream.value or stream.description,
                }
            else:
                self.inputs["stream"] = {"type": "static", "value": stream}
        if provider is not None:
            if isinstance(provider, ToolInput):
                self.inputs["provider"] = {
                    "type": provider.type,
                    "value": provider.value or provider.description,
                }
            else:
                self.inputs["provider"] = {"type": "static", "value": provider}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "AiImageToTextTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("ai_text_to_image")
class AiTextToImageTool(Tool):
    """
    Generate Image from Text using AI

    ## Inputs
    ### Common Inputs
        aspect_ratio: Select the aspect ratio.
        model: Select the text-to-image model
        prompt: Tell the AI model how you would like it to respond. Be as specific as possible. For example, you can instruct the model to use bright colors.
        provider: Select the model provider.
        size: Select the size.
        use_personal_api_key: Use your personal API key
    ### When use_personal_api_key = True
        api_key: Input your personal API key from the model provider. Note: if you do not have access to the selected model, the workflow will not run
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "aspect_ratio",
            "helper_text": "Select the aspect ratio.",
            "value": "1:1",
            "type": "enum<string>",
        },
        {
            "field": "model",
            "helper_text": "Select the text-to-image model",
            "value": "dall-e-2",
            "type": "enum<string>",
        },
        {
            "field": "prompt",
            "helper_text": "Tell the AI model how you would like it to respond. Be as specific as possible. For example, you can instruct the model to use bright colors.",
            "value": "",
            "type": "string",
        },
        {
            "field": "provider",
            "helper_text": "Select the model provider.",
            "value": "openai",
            "type": "enum<string>",
        },
        {
            "field": "size",
            "helper_text": "Select the size.",
            "value": "512x512",
            "type": "enum<string>",
        },
        {
            "field": "use_personal_api_key",
            "helper_text": "Use your personal API key",
            "value": False,
            "type": "bool",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "false**(*)": {"inputs": [], "outputs": []},
        "true**(*)": {
            "inputs": [
                {
                    "field": "api_key",
                    "type": "string",
                    "value": "",
                    "helper_text": "Input your personal API key from the model provider. Note: if you do not have access to the selected model, the workflow will not run",
                }
            ],
            "outputs": [],
        },
        "(*)**openai": {"inputs": [], "outputs": [], "title": "OpenAI Text to Image"},
        "(*)**stabilityai": {
            "inputs": [],
            "outputs": [],
            "title": "Stability AI Text to Image",
        },
        "(*)**flux": {"inputs": [], "outputs": [], "title": "Flux Text to Image"},
    }

    # List of parameters that affect configuration
    _PARAMS = ["use_personal_api_key", "provider"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Generate Image from Text using AI",
        use_personal_api_key: bool | ToolInput = False,
        provider: str | ToolInput = "openai",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(use_personal_api_key, ToolInput):
            if use_personal_api_key.type == "static":
                params["use_personal_api_key"] = use_personal_api_key.value
            else:
                raise ValueError(f"use_personal_api_key cannot be a dynamic input")
        else:
            params["use_personal_api_key"] = use_personal_api_key
        if isinstance(provider, ToolInput):
            if provider.type == "static":
                params["provider"] = provider.value
            else:
                raise ValueError(f"provider cannot be a dynamic input")
        else:
            params["provider"] = provider

        super().__init__(
            tool_type="ai_text_to_image",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if use_personal_api_key is not None:
            if isinstance(use_personal_api_key, ToolInput):
                self.inputs["use_personal_api_key"] = {
                    "type": use_personal_api_key.type,
                    "value": use_personal_api_key.value
                    or use_personal_api_key.description,
                }
            else:
                self.inputs["use_personal_api_key"] = {
                    "type": "static",
                    "value": use_personal_api_key,
                }
        if provider is not None:
            if isinstance(provider, ToolInput):
                self.inputs["provider"] = {
                    "type": provider.type,
                    "value": provider.value or provider.description,
                }
            else:
                self.inputs["provider"] = {"type": "static", "value": provider}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "AiTextToImageTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("llm_anthropic_vision")
class LlmAnthropicVisionTool(Tool):
    """


    ## Inputs
    ### Common Inputs
        image: The image input
        json_response: The json_response input
        max_tokens: The max_tokens input
        model: The model input
        prompt: The prompt input
        system: The system input
        temperature: The temperature input
        top_p: The top_p input
        use_personal_api_key: The use_personal_api_key input
    ### When use_personal_api_key = True
        api_key: The api_key input
    ### When json_response = True
        json_schema: The json_schema input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "image",
            "helper_text": "The image input",
            "value": None,
            "type": "image",
        },
        {
            "field": "json_response",
            "helper_text": "The json_response input",
            "value": False,
            "type": "bool",
        },
        {
            "field": "max_tokens",
            "helper_text": "The max_tokens input",
            "value": 200000,
            "type": "int32",
        },
        {
            "field": "model",
            "helper_text": "The model input",
            "value": "claude-3-haiku-20240307",
            "type": "enum<string>",
        },
        {
            "field": "prompt",
            "helper_text": "The prompt input",
            "value": "",
            "type": "string",
        },
        {
            "field": "system",
            "helper_text": "The system input",
            "value": "",
            "type": "string",
        },
        {
            "field": "temperature",
            "helper_text": "The temperature input",
            "value": 0.7,
            "type": "float",
        },
        {
            "field": "top_p",
            "helper_text": "The top_p input",
            "value": 0.9,
            "type": "float",
        },
        {
            "field": "use_personal_api_key",
            "helper_text": "The use_personal_api_key input",
            "value": False,
            "type": "bool",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "false**(*)": {"inputs": [], "outputs": []},
        "true**(*)": {
            "inputs": [{"field": "api_key", "type": "string", "value": ""}],
            "outputs": [],
        },
        "(*)**false": {"inputs": [], "outputs": []},
        "(*)**true": {
            "inputs": [{"field": "json_schema", "type": "string", "value": ""}],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["use_personal_api_key", "json_response"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "",
        use_personal_api_key: bool | ToolInput = False,
        json_response: bool | ToolInput = False,
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(use_personal_api_key, ToolInput):
            if use_personal_api_key.type == "static":
                params["use_personal_api_key"] = use_personal_api_key.value
            else:
                raise ValueError(f"use_personal_api_key cannot be a dynamic input")
        else:
            params["use_personal_api_key"] = use_personal_api_key
        if isinstance(json_response, ToolInput):
            if json_response.type == "static":
                params["json_response"] = json_response.value
            else:
                raise ValueError(f"json_response cannot be a dynamic input")
        else:
            params["json_response"] = json_response

        super().__init__(
            tool_type="llm_anthropic_vision",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if use_personal_api_key is not None:
            if isinstance(use_personal_api_key, ToolInput):
                self.inputs["use_personal_api_key"] = {
                    "type": use_personal_api_key.type,
                    "value": use_personal_api_key.value
                    or use_personal_api_key.description,
                }
            else:
                self.inputs["use_personal_api_key"] = {
                    "type": "static",
                    "value": use_personal_api_key,
                }
        if json_response is not None:
            if isinstance(json_response, ToolInput):
                self.inputs["json_response"] = {
                    "type": json_response.type,
                    "value": json_response.value or json_response.description,
                }
            else:
                self.inputs["json_response"] = {
                    "type": "static",
                    "value": json_response,
                }

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "LlmAnthropicVisionTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("semantic_search")
class SemanticSearchTool(Tool):
    """
    Generate a temporary vector database at run-time and retrieve the most relevant pieces from the documents based on the query.

    ## Inputs
    ### Common Inputs
        alpha: The alpha value for the retrieval
        analyze_documents: To analyze document contents and enrich them when parsing
        answer_multiple_questions: Extract separate questions from the query and retrieve content separately for each question to improve search performance
        do_advanced_qa: Use additional LLM calls to analyze each document to improve answer correctness
        do_nl_metadata_query: Do a natural language metadata query
        documents: The text for semantic search. Note: you may add multiple upstream nodes to this field.
        enable_context: Additional context passed to advanced search and query analysis
        enable_document_db_filter: Filter the documents returned from the knowledge base
        enable_filter: Filter the content returned from the knowledge base
        expand_query: Expand query to improve semantic search
        expand_query_terms: Expand query terms to improve semantic search
        format_context_for_llm: Format the context for the LLM
        is_hybrid: Whether to create a hybrid knowledge base
        max_docs_per_query: The maximum number of relevant chunks to be returned
        model: The model to use for the embedding
        query: The query will be used to search documents for relevant pieces semantically.
        rerank_documents: Refine the initial ranking of returned chunks based on relevancy
        retrieval_unit: The unit of retrieval
        score_cutoff: The score cutoff
        segmentation_method: The method to break text into units before chunking. 'words': splits by word; 'sentences': splits by sentence boundary; 'paragraphs': splits by blank line/paragraph.
        show_intermediate_steps: Show intermediate steps
        splitter_method: Strategy for grouping segmented text into final chunks. 'sentence': groups sentences; 'markdown': respects Markdown structure (headers, code); 'dynamic': optimizes breaks for size using chosen segmentation method.
        transform_query: Transform the query for better semantic search
    ### When do_advanced_qa = True
        advanced_search_mode: The mode to use for the advanced search
        qa_model_name: The model to use for the QA
    ### When enable_context = True
        context: Additional context to pass to the query analysis and qa steps
    ### When enable_document_db_filter = True
        document_db_filter: Filter the documents returned from the knowledge base
    ### When enable_filter = True
        filter: Filter the content returned from the knowledge base
    ### When rerank_documents = True
        rerank_model: Refine the initial ranking of returned chunks based on relevancy
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "alpha",
            "helper_text": "The alpha value for the retrieval",
            "value": 0.5,
            "type": "float",
        },
        {
            "field": "analyze_documents",
            "helper_text": "To analyze document contents and enrich them when parsing",
            "value": False,
            "type": "bool",
        },
        {
            "field": "answer_multiple_questions",
            "helper_text": "Extract separate questions from the query and retrieve content separately for each question to improve search performance",
            "value": False,
            "type": "bool",
        },
        {
            "field": "do_advanced_qa",
            "helper_text": "Use additional LLM calls to analyze each document to improve answer correctness",
            "value": False,
            "type": "bool",
        },
        {
            "field": "do_nl_metadata_query",
            "helper_text": "Do a natural language metadata query",
            "value": False,
            "type": "bool",
        },
        {
            "field": "documents",
            "helper_text": "The text for semantic search. Note: you may add multiple upstream nodes to this field.",
            "value": [],
            "type": "string",
        },
        {
            "field": "enable_context",
            "helper_text": "Additional context passed to advanced search and query analysis",
            "value": False,
            "type": "bool",
        },
        {
            "field": "enable_document_db_filter",
            "helper_text": "Filter the documents returned from the knowledge base",
            "value": False,
            "type": "bool",
        },
        {
            "field": "enable_filter",
            "helper_text": "Filter the content returned from the knowledge base",
            "value": False,
            "type": "bool",
        },
        {
            "field": "expand_query",
            "helper_text": "Expand query to improve semantic search",
            "value": False,
            "type": "bool",
        },
        {
            "field": "expand_query_terms",
            "helper_text": "Expand query terms to improve semantic search",
            "value": False,
            "type": "bool",
        },
        {
            "field": "format_context_for_llm",
            "helper_text": "Format the context for the LLM",
            "value": False,
            "type": "bool",
        },
        {
            "field": "is_hybrid",
            "helper_text": "Whether to create a hybrid knowledge base",
            "value": False,
            "type": "bool",
        },
        {
            "field": "max_docs_per_query",
            "helper_text": "The maximum number of relevant chunks to be returned",
            "value": 5,
            "type": "int32",
        },
        {
            "field": "model",
            "helper_text": "The model to use for the embedding",
            "value": "openai/text-embedding-3-small",
            "type": "enum<string>",
        },
        {
            "field": "query",
            "helper_text": "The query will be used to search documents for relevant pieces semantically.",
            "value": "",
            "type": "string",
        },
        {
            "field": "rerank_documents",
            "helper_text": "Refine the initial ranking of returned chunks based on relevancy",
            "value": False,
            "type": "bool",
        },
        {
            "field": "retrieval_unit",
            "helper_text": "The unit of retrieval",
            "value": "chunks",
            "type": "enum<string>",
        },
        {
            "field": "score_cutoff",
            "helper_text": "The score cutoff",
            "value": 0,
            "type": "float",
        },
        {
            "field": "segmentation_method",
            "helper_text": "The method to break text into units before chunking. 'words': splits by word; 'sentences': splits by sentence boundary; 'paragraphs': splits by blank line/paragraph.",
            "value": "words",
            "type": "enum<string>",
        },
        {
            "field": "show_intermediate_steps",
            "helper_text": "Show intermediate steps",
            "value": False,
            "type": "bool",
        },
        {
            "field": "splitter_method",
            "helper_text": "Strategy for grouping segmented text into final chunks. 'sentence': groups sentences; 'markdown': respects Markdown structure (headers, code); 'dynamic': optimizes breaks for size using chosen segmentation method.",
            "value": "markdown",
            "type": "enum<string>",
        },
        {
            "field": "transform_query",
            "helper_text": "Transform the query for better semantic search",
            "value": False,
            "type": "bool",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "true**(*)**(*)**(*)**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "qa_model_name",
                    "type": "enum<string>",
                    "value": "gpt-4o-mini",
                    "helper_text": "The model to use for the QA",
                },
                {
                    "field": "advanced_search_mode",
                    "type": "enum<string>",
                    "value": "accurate",
                    "helper_text": "The mode to use for the advanced search",
                },
            ],
            "outputs": [
                {
                    "field": "response",
                    "type": "string",
                    "helper_text": "The response from the semantic search",
                },
                {
                    "field": "citation_metadata",
                    "type": "vec<string>",
                    "helper_text": "Citation metadata for semantic search outputs, used for showing sources in LLM responses",
                },
            ],
        },
        "(*)**true**(*)**(*)**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "filter",
                    "type": "string",
                    "value": "",
                    "helper_text": "Filter the content returned from the knowledge base",
                }
            ],
            "outputs": [],
        },
        "(*)**(*)**true**(*)**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "rerank_model",
                    "type": "enum<string>",
                    "value": "cohere/rerank-english-v3.0",
                    "helper_text": "Refine the initial ranking of returned chunks based on relevancy",
                }
            ],
            "outputs": [],
        },
        "false**(*)**(*)**documents**(*)**false**(*)**(*)": {
            "inputs": [],
            "outputs": [
                {
                    "field": "documents",
                    "type": "vec<string>",
                    "helper_text": "Semantically similar documents retrieved from the knowledge base",
                }
            ],
        },
        "false**(*)**(*)**chunks**(*)**false**(*)**(*)": {
            "inputs": [],
            "outputs": [
                {
                    "field": "chunks",
                    "type": "vec<string>",
                    "helper_text": "Semantically similar chunks retrieved from the knowledge base",
                }
            ],
        },
        "false**(*)**(*)**documents**(*)**true**(*)**(*)": {
            "inputs": [],
            "outputs": [
                {
                    "field": "documents",
                    "type": "vec<string>",
                    "helper_text": "Semantically similar documents retrieved from the knowledge base",
                },
                {
                    "field": "formatted_text",
                    "type": "string",
                    "helper_text": "Knowledge base outputs formatted for input to a LLM",
                },
            ],
        },
        "false**(*)**(*)**chunks**(*)**true**(*)**(*)": {
            "inputs": [],
            "outputs": [
                {
                    "field": "chunks",
                    "type": "vec<string>",
                    "helper_text": "Semantically similar chunks retrieved from the knowledge base",
                },
                {
                    "field": "formatted_text",
                    "type": "string",
                    "helper_text": "Knowledge base outputs formatted for input to a LLM",
                },
            ],
        },
        "(*)**(*)**(*)**(*)**true**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "context",
                    "type": "string",
                    "value": "",
                    "helper_text": "Additional context to pass to the query analysis and qa steps",
                }
            ],
            "outputs": [],
        },
        "(*)**(*)**(*)**(*)**(*)**(*)**true**(*)": {
            "inputs": [
                {
                    "field": "document_db_filter",
                    "type": "string",
                    "value": "",
                    "helper_text": "Filter the documents returned from the knowledge base",
                }
            ],
            "outputs": [],
        },
        "(*)**(*)**(*)**(*)**(*)**(*)**(*)**(dynamic)": {
            "inputs": [
                {
                    "field": "segmentation_method",
                    "type": "enum<string>",
                    "value": "words",
                    "helper_text": "The method to break text into units before chunking. 'words': splits by word; 'sentences': splits by sentence boundary; 'paragraphs': splits by blank line/paragraph.",
                }
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = [
        "do_advanced_qa",
        "enable_filter",
        "rerank_documents",
        "retrieval_unit",
        "enable_context",
        "format_context_for_llm",
        "enable_document_db_filter",
        "splitter_method",
    ]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Generate a temporary vector database at run-time and retrieve the most relevant pieces from the documents based on the query.",
        do_advanced_qa: bool | ToolInput = False,
        enable_filter: bool | ToolInput = False,
        rerank_documents: bool | ToolInput = False,
        retrieval_unit: str | ToolInput = "chunks",
        enable_context: bool | ToolInput = False,
        format_context_for_llm: bool | ToolInput = False,
        enable_document_db_filter: bool | ToolInput = False,
        splitter_method: str | ToolInput = "markdown",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(do_advanced_qa, ToolInput):
            if do_advanced_qa.type == "static":
                params["do_advanced_qa"] = do_advanced_qa.value
            else:
                raise ValueError(f"do_advanced_qa cannot be a dynamic input")
        else:
            params["do_advanced_qa"] = do_advanced_qa
        if isinstance(enable_filter, ToolInput):
            if enable_filter.type == "static":
                params["enable_filter"] = enable_filter.value
            else:
                raise ValueError(f"enable_filter cannot be a dynamic input")
        else:
            params["enable_filter"] = enable_filter
        if isinstance(rerank_documents, ToolInput):
            if rerank_documents.type == "static":
                params["rerank_documents"] = rerank_documents.value
            else:
                raise ValueError(f"rerank_documents cannot be a dynamic input")
        else:
            params["rerank_documents"] = rerank_documents
        if isinstance(retrieval_unit, ToolInput):
            if retrieval_unit.type == "static":
                params["retrieval_unit"] = retrieval_unit.value
            else:
                raise ValueError(f"retrieval_unit cannot be a dynamic input")
        else:
            params["retrieval_unit"] = retrieval_unit
        if isinstance(enable_context, ToolInput):
            if enable_context.type == "static":
                params["enable_context"] = enable_context.value
            else:
                raise ValueError(f"enable_context cannot be a dynamic input")
        else:
            params["enable_context"] = enable_context
        if isinstance(format_context_for_llm, ToolInput):
            if format_context_for_llm.type == "static":
                params["format_context_for_llm"] = format_context_for_llm.value
            else:
                raise ValueError(f"format_context_for_llm cannot be a dynamic input")
        else:
            params["format_context_for_llm"] = format_context_for_llm
        if isinstance(enable_document_db_filter, ToolInput):
            if enable_document_db_filter.type == "static":
                params["enable_document_db_filter"] = enable_document_db_filter.value
            else:
                raise ValueError(f"enable_document_db_filter cannot be a dynamic input")
        else:
            params["enable_document_db_filter"] = enable_document_db_filter
        if isinstance(splitter_method, ToolInput):
            if splitter_method.type == "static":
                params["splitter_method"] = splitter_method.value
            else:
                raise ValueError(f"splitter_method cannot be a dynamic input")
        else:
            params["splitter_method"] = splitter_method

        super().__init__(
            tool_type="semantic_search",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if do_advanced_qa is not None:
            if isinstance(do_advanced_qa, ToolInput):
                self.inputs["do_advanced_qa"] = {
                    "type": do_advanced_qa.type,
                    "value": do_advanced_qa.value or do_advanced_qa.description,
                }
            else:
                self.inputs["do_advanced_qa"] = {
                    "type": "static",
                    "value": do_advanced_qa,
                }
        if enable_filter is not None:
            if isinstance(enable_filter, ToolInput):
                self.inputs["enable_filter"] = {
                    "type": enable_filter.type,
                    "value": enable_filter.value or enable_filter.description,
                }
            else:
                self.inputs["enable_filter"] = {
                    "type": "static",
                    "value": enable_filter,
                }
        if rerank_documents is not None:
            if isinstance(rerank_documents, ToolInput):
                self.inputs["rerank_documents"] = {
                    "type": rerank_documents.type,
                    "value": rerank_documents.value or rerank_documents.description,
                }
            else:
                self.inputs["rerank_documents"] = {
                    "type": "static",
                    "value": rerank_documents,
                }
        if retrieval_unit is not None:
            if isinstance(retrieval_unit, ToolInput):
                self.inputs["retrieval_unit"] = {
                    "type": retrieval_unit.type,
                    "value": retrieval_unit.value or retrieval_unit.description,
                }
            else:
                self.inputs["retrieval_unit"] = {
                    "type": "static",
                    "value": retrieval_unit,
                }
        if enable_context is not None:
            if isinstance(enable_context, ToolInput):
                self.inputs["enable_context"] = {
                    "type": enable_context.type,
                    "value": enable_context.value or enable_context.description,
                }
            else:
                self.inputs["enable_context"] = {
                    "type": "static",
                    "value": enable_context,
                }
        if format_context_for_llm is not None:
            if isinstance(format_context_for_llm, ToolInput):
                self.inputs["format_context_for_llm"] = {
                    "type": format_context_for_llm.type,
                    "value": format_context_for_llm.value
                    or format_context_for_llm.description,
                }
            else:
                self.inputs["format_context_for_llm"] = {
                    "type": "static",
                    "value": format_context_for_llm,
                }
        if enable_document_db_filter is not None:
            if isinstance(enable_document_db_filter, ToolInput):
                self.inputs["enable_document_db_filter"] = {
                    "type": enable_document_db_filter.type,
                    "value": enable_document_db_filter.value
                    or enable_document_db_filter.description,
                }
            else:
                self.inputs["enable_document_db_filter"] = {
                    "type": "static",
                    "value": enable_document_db_filter,
                }
        if splitter_method is not None:
            if isinstance(splitter_method, ToolInput):
                self.inputs["splitter_method"] = {
                    "type": splitter_method.type,
                    "value": splitter_method.value or splitter_method.description,
                }
            else:
                self.inputs["splitter_method"] = {
                    "type": "static",
                    "value": splitter_method,
                }

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "SemanticSearchTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("knowledge_base")
class KnowledgeBaseTool(Tool):
    """
    Semantically query a knowledge base that can contain files, scraped URLs, and data from synced integrations (e.g., Google Drive).

    ## Inputs
    ### Common Inputs
        alpha: The alpha value for the retrieval
        answer_multiple_questions: Extract separate questions from the query and retrieve content separately for each question to improve search performance
        do_advanced_qa: Use additional LLM calls to analyze each document to improve answer correctness
        do_nl_metadata_query: Do a natural language metadata query
        enable_context: Enable context
        enable_document_db_filter: Enable the document DB filter
        enable_filter: Filter the content returned from the knowledge base
        expand_query: Expand query to improve semantic search
        expand_query_terms: Expand query terms to improve semantic search
        format_context_for_llm: Format the context for the LLM
        knowledge_base: Select an existing knowledge base
        max_docs_per_query: The number of relevant chunks to be returned
        query: The query will be used to search documents for relevant pieces semantically.
        rerank_documents: Rerank the documents returned from the knowledge base
        retrieval_unit: The unit of retrieval
        score_cutoff: The score cutoff
        show_intermediate_steps: Show intermediate steps
        transform_query: Transform the query for better semantic search
    ### When do_advanced_qa = True
        advanced_search_mode: The mode to use for the advanced search
        qa_model_name: The model to use for the QA
    ### When enable_context = True
        context: Additional context to pass to the query analysis and qa steps
    ### When enable_document_db_filter = True
        document_db_filter: Filter the documents returned from the knowledge base
    ### When enable_filter = True
        filter: Filter the content returned from the knowledge base
    ### When rerank_documents = True
        rerank_model: Refine the initial ranking of returned chunks based on relevancy
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "alpha",
            "helper_text": "The alpha value for the retrieval",
            "value": 0.5,
            "type": "float",
        },
        {
            "field": "answer_multiple_questions",
            "helper_text": "Extract separate questions from the query and retrieve content separately for each question to improve search performance",
            "value": False,
            "type": "bool",
        },
        {
            "field": "do_advanced_qa",
            "helper_text": "Use additional LLM calls to analyze each document to improve answer correctness",
            "value": False,
            "type": "bool",
        },
        {
            "field": "do_nl_metadata_query",
            "helper_text": "Do a natural language metadata query",
            "value": False,
            "type": "bool",
        },
        {
            "field": "enable_context",
            "helper_text": "Enable context",
            "value": False,
            "type": "bool",
        },
        {
            "field": "enable_document_db_filter",
            "helper_text": "Enable the document DB filter",
            "value": False,
            "type": "bool",
        },
        {
            "field": "enable_filter",
            "helper_text": "Filter the content returned from the knowledge base",
            "value": False,
            "type": "bool",
        },
        {
            "field": "expand_query",
            "helper_text": "Expand query to improve semantic search",
            "value": False,
            "type": "bool",
        },
        {
            "field": "expand_query_terms",
            "helper_text": "Expand query terms to improve semantic search",
            "value": False,
            "type": "bool",
        },
        {
            "field": "format_context_for_llm",
            "helper_text": "Format the context for the LLM",
            "value": False,
            "type": "bool",
        },
        {
            "field": "knowledge_base",
            "helper_text": "Select an existing knowledge base",
            "value": {},
            "type": "knowledge_base",
        },
        {
            "field": "max_docs_per_query",
            "helper_text": "The number of relevant chunks to be returned",
            "value": 10,
            "type": "int32",
        },
        {
            "field": "query",
            "helper_text": "The query will be used to search documents for relevant pieces semantically.",
            "value": "",
            "type": "string",
        },
        {
            "field": "rerank_documents",
            "helper_text": "Rerank the documents returned from the knowledge base",
            "value": False,
            "type": "bool",
        },
        {
            "field": "retrieval_unit",
            "helper_text": "The unit of retrieval",
            "value": "chunks",
            "type": "enum<string>",
        },
        {
            "field": "score_cutoff",
            "helper_text": "The score cutoff",
            "value": 0,
            "type": "float",
        },
        {
            "field": "show_intermediate_steps",
            "helper_text": "Show intermediate steps",
            "value": False,
            "type": "bool",
        },
        {
            "field": "transform_query",
            "helper_text": "Transform the query for better semantic search",
            "value": False,
            "type": "bool",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "true**(*)**(*)**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "qa_model_name",
                    "type": "enum<string>",
                    "value": "gpt-4o-mini",
                    "helper_text": "The model to use for the QA",
                },
                {
                    "field": "advanced_search_mode",
                    "type": "enum<string>",
                    "value": "accurate",
                    "helper_text": "The mode to use for the advanced search",
                },
            ],
            "outputs": [
                {
                    "field": "response",
                    "type": "string",
                    "helper_text": "The response from the knowledge base",
                },
                {
                    "field": "citation_metadata",
                    "type": "vec<string>",
                    "helper_text": "Citation metadata for knowledge base outputs, used for showing sources in LLM responses",
                },
            ],
        },
        "(*)**true**(*)**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "filter",
                    "type": "string",
                    "value": "",
                    "helper_text": "Filter the content returned from the knowledge base",
                }
            ],
            "outputs": [
                {
                    "field": "citation_metadata",
                    "type": "vec<string>",
                    "helper_text": "Citation metadata for knowledge base outputs, used for showing sources in LLM responses",
                }
            ],
        },
        "(*)**(*)**true**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "rerank_model",
                    "type": "enum<string>",
                    "value": "cohere/rerank-english-v3.0",
                    "helper_text": "Refine the initial ranking of returned chunks based on relevancy",
                }
            ],
            "outputs": [],
        },
        "false**(*)**(*)**documents**(*)**false**(*)": {
            "inputs": [],
            "outputs": [
                {
                    "field": "documents",
                    "type": "vec<string>",
                    "helper_text": "The documents returned from the knowledge base",
                },
                {
                    "field": "citation_metadata",
                    "type": "vec<string>",
                    "helper_text": "Citation metadata for knowledge base outputs, used for showing sources in LLM responses",
                },
            ],
        },
        "false**(*)**(*)**chunks**(*)**false**(*)": {
            "inputs": [],
            "outputs": [
                {
                    "field": "chunks",
                    "type": "vec<string>",
                    "helper_text": "Semantically similar chunks retrieved from the knowledge base.",
                },
                {
                    "field": "citation_metadata",
                    "type": "vec<string>",
                    "helper_text": "Citation metadata for knowledge base outputs, used for showing sources in LLM responses",
                },
            ],
        },
        "false**(*)**(*)**documents**(*)**true**(*)": {
            "inputs": [],
            "outputs": [
                {
                    "field": "documents",
                    "type": "vec<string>",
                    "helper_text": "Semantically similar documents retrieved from the knowledge base.",
                },
                {
                    "field": "citation_metadata",
                    "type": "vec<string>",
                    "helper_text": "Citation metadata for knowledge base outputs, used for showing sources in LLM responses",
                },
                {
                    "field": "formatted_text",
                    "type": "string",
                    "helper_text": "Knowledge base outputs formatted for input to a LLM",
                },
            ],
        },
        "false**(*)**(*)**chunks**(*)**true**(*)": {
            "inputs": [],
            "outputs": [
                {
                    "field": "chunks",
                    "type": "vec<string>",
                    "helper_text": "Semantically similar chunks retrieved from the knowledge base.",
                },
                {
                    "field": "citation_metadata",
                    "type": "vec<string>",
                    "helper_text": "Citation metadata for knowledge base outputs, used for showing sources in LLM responses",
                },
                {
                    "field": "formatted_text",
                    "type": "string",
                    "helper_text": "Knowledge base outputs formatted for input to a LLM",
                },
            ],
        },
        "(*)**(*)**(*)**(*)**true**(*)**(*)": {
            "inputs": [
                {
                    "field": "context",
                    "type": "string",
                    "value": "",
                    "helper_text": "Additional context to pass to the query analysis and qa steps",
                }
            ],
            "outputs": [
                {
                    "field": "citation_metadata",
                    "type": "vec<string>",
                    "helper_text": "Citation metadata for knowledge base outputs, used for showing sources in LLM responses",
                }
            ],
        },
        "(*)**(*)**(*)**(*)**(*)**(*)**true": {
            "inputs": [
                {
                    "field": "document_db_filter",
                    "type": "string",
                    "value": "",
                    "helper_text": "Filter the documents returned from the knowledge base",
                }
            ],
            "outputs": [
                {
                    "field": "citation_metadata",
                    "type": "vec<string>",
                    "helper_text": "Citation metadata for knowledge base outputs, used for showing sources in LLM responses",
                }
            ],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = [
        "do_advanced_qa",
        "enable_filter",
        "rerank_documents",
        "retrieval_unit",
        "enable_context",
        "format_context_for_llm",
        "enable_document_db_filter",
    ]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Semantically query a knowledge base that can contain files, scraped URLs, and data from synced integrations (e.g., Google Drive).",
        do_advanced_qa: bool | ToolInput = False,
        enable_filter: bool | ToolInput = False,
        rerank_documents: bool | ToolInput = False,
        retrieval_unit: str | ToolInput = "chunks",
        enable_context: bool | ToolInput = False,
        format_context_for_llm: bool | ToolInput = False,
        enable_document_db_filter: bool | ToolInput = False,
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(do_advanced_qa, ToolInput):
            if do_advanced_qa.type == "static":
                params["do_advanced_qa"] = do_advanced_qa.value
            else:
                raise ValueError(f"do_advanced_qa cannot be a dynamic input")
        else:
            params["do_advanced_qa"] = do_advanced_qa
        if isinstance(enable_filter, ToolInput):
            if enable_filter.type == "static":
                params["enable_filter"] = enable_filter.value
            else:
                raise ValueError(f"enable_filter cannot be a dynamic input")
        else:
            params["enable_filter"] = enable_filter
        if isinstance(rerank_documents, ToolInput):
            if rerank_documents.type == "static":
                params["rerank_documents"] = rerank_documents.value
            else:
                raise ValueError(f"rerank_documents cannot be a dynamic input")
        else:
            params["rerank_documents"] = rerank_documents
        if isinstance(retrieval_unit, ToolInput):
            if retrieval_unit.type == "static":
                params["retrieval_unit"] = retrieval_unit.value
            else:
                raise ValueError(f"retrieval_unit cannot be a dynamic input")
        else:
            params["retrieval_unit"] = retrieval_unit
        if isinstance(enable_context, ToolInput):
            if enable_context.type == "static":
                params["enable_context"] = enable_context.value
            else:
                raise ValueError(f"enable_context cannot be a dynamic input")
        else:
            params["enable_context"] = enable_context
        if isinstance(format_context_for_llm, ToolInput):
            if format_context_for_llm.type == "static":
                params["format_context_for_llm"] = format_context_for_llm.value
            else:
                raise ValueError(f"format_context_for_llm cannot be a dynamic input")
        else:
            params["format_context_for_llm"] = format_context_for_llm
        if isinstance(enable_document_db_filter, ToolInput):
            if enable_document_db_filter.type == "static":
                params["enable_document_db_filter"] = enable_document_db_filter.value
            else:
                raise ValueError(f"enable_document_db_filter cannot be a dynamic input")
        else:
            params["enable_document_db_filter"] = enable_document_db_filter

        super().__init__(
            tool_type="knowledge_base",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if do_advanced_qa is not None:
            if isinstance(do_advanced_qa, ToolInput):
                self.inputs["do_advanced_qa"] = {
                    "type": do_advanced_qa.type,
                    "value": do_advanced_qa.value or do_advanced_qa.description,
                }
            else:
                self.inputs["do_advanced_qa"] = {
                    "type": "static",
                    "value": do_advanced_qa,
                }
        if enable_filter is not None:
            if isinstance(enable_filter, ToolInput):
                self.inputs["enable_filter"] = {
                    "type": enable_filter.type,
                    "value": enable_filter.value or enable_filter.description,
                }
            else:
                self.inputs["enable_filter"] = {
                    "type": "static",
                    "value": enable_filter,
                }
        if rerank_documents is not None:
            if isinstance(rerank_documents, ToolInput):
                self.inputs["rerank_documents"] = {
                    "type": rerank_documents.type,
                    "value": rerank_documents.value or rerank_documents.description,
                }
            else:
                self.inputs["rerank_documents"] = {
                    "type": "static",
                    "value": rerank_documents,
                }
        if retrieval_unit is not None:
            if isinstance(retrieval_unit, ToolInput):
                self.inputs["retrieval_unit"] = {
                    "type": retrieval_unit.type,
                    "value": retrieval_unit.value or retrieval_unit.description,
                }
            else:
                self.inputs["retrieval_unit"] = {
                    "type": "static",
                    "value": retrieval_unit,
                }
        if enable_context is not None:
            if isinstance(enable_context, ToolInput):
                self.inputs["enable_context"] = {
                    "type": enable_context.type,
                    "value": enable_context.value or enable_context.description,
                }
            else:
                self.inputs["enable_context"] = {
                    "type": "static",
                    "value": enable_context,
                }
        if format_context_for_llm is not None:
            if isinstance(format_context_for_llm, ToolInput):
                self.inputs["format_context_for_llm"] = {
                    "type": format_context_for_llm.type,
                    "value": format_context_for_llm.value
                    or format_context_for_llm.description,
                }
            else:
                self.inputs["format_context_for_llm"] = {
                    "type": "static",
                    "value": format_context_for_llm,
                }
        if enable_document_db_filter is not None:
            if isinstance(enable_document_db_filter, ToolInput):
                self.inputs["enable_document_db_filter"] = {
                    "type": enable_document_db_filter.type,
                    "value": enable_document_db_filter.value
                    or enable_document_db_filter.description,
                }
            else:
                self.inputs["enable_document_db_filter"] = {
                    "type": "static",
                    "value": enable_document_db_filter,
                }

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "KnowledgeBaseTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("knowledge_base_loader")
class KnowledgeBaseLoaderTool(Tool):
    """
    Load data into an existing knowledge base.

    ## Inputs
    ### Common Inputs
        document_type: Scrape sub-pages of the provided link
        knowledge_base: The knowledge base to load data into
        rescrape_frequency: The frequency to rescrape the URL
    ### File
        documents: The file to be added to the selected knowledge base. Note: to convert text to file, use the Text to File node
    ### Recursive URL
        load_sitemap: Load URLs to crawl from a sitemap. If the URL is a sitemap, it will be used directly. If the URL is not a sitemap, the sitemap will be fetched automatically.
        max_depth: The maximum depth of the URL to crawl
        max_recursive_urls: The maximum number of recursive URLs to scrape
        same_domain_only: Whether to only crawl links from the same domain
        url: The raw URL link (e.g., https://vectorshift.ai/)
    ### URL
        max_recursive_urls: The maximum number of recursive URLs to scrape
        url: The raw URL link (e.g., https://vectorshift.ai/)
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "document_type",
            "helper_text": "Scrape sub-pages of the provided link",
            "value": "File",
            "type": "enum<string>",
        },
        {
            "field": "knowledge_base",
            "helper_text": "The knowledge base to load data into",
            "value": {},
            "type": "knowledge_base",
        },
        {
            "field": "rescrape_frequency",
            "helper_text": "The frequency to rescrape the URL",
            "value": "Never",
            "type": "enum<string>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "URL": {
            "inputs": [
                {
                    "field": "max_recursive_urls",
                    "type": "int32",
                    "value": 10,
                    "helper_text": "The maximum number of recursive URLs to scrape",
                },
                {
                    "field": "url",
                    "type": "string",
                    "value": "",
                    "helper_text": "The raw URL link (e.g., https://vectorshift.ai/)",
                },
            ],
            "outputs": [],
        },
        "File": {
            "inputs": [
                {
                    "field": "documents",
                    "type": "vec<file>",
                    "value": [""],
                    "helper_text": "The file to be added to the selected knowledge base. Note: to convert text to file, use the Text to File node",
                }
            ],
            "outputs": [],
        },
        "Recursive URL": {
            "inputs": [
                {
                    "field": "max_recursive_urls",
                    "type": "int32",
                    "value": 10,
                    "helper_text": "The maximum number of recursive URLs to scrape",
                    "label": "Max urls to crawl (max 800)",
                },
                {
                    "field": "url",
                    "type": "string",
                    "value": "",
                    "helper_text": "The raw URL link (e.g., https://vectorshift.ai/)",
                },
                {
                    "field": "max_depth",
                    "type": "int32",
                    "value": 5,
                    "helper_text": "The maximum depth of the URL to crawl",
                    "label": "Max depth to crawl",
                },
                {
                    "field": "same_domain_only",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to only crawl links from the same domain",
                    "label": "Same domain only",
                },
                {
                    "field": "load_sitemap",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Load URLs to crawl from a sitemap. If the URL is a sitemap, it will be used directly. If the URL is not a sitemap, the sitemap will be fetched automatically.",
                    "label": "Load sitemap",
                },
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["document_type"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Load data into an existing knowledge base.",
        document_type: str | ToolInput = "File",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(document_type, ToolInput):
            if document_type.type == "static":
                params["document_type"] = document_type.value
            else:
                raise ValueError(f"document_type cannot be a dynamic input")
        else:
            params["document_type"] = document_type

        super().__init__(
            tool_type="knowledge_base_loader",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if document_type is not None:
            if isinstance(document_type, ToolInput):
                self.inputs["document_type"] = {
                    "type": document_type.type,
                    "value": document_type.value or document_type.description,
                }
            else:
                self.inputs["document_type"] = {
                    "type": "static",
                    "value": document_type,
                }

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "KnowledgeBaseLoaderTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("map")
class MapTool(Tool):
    """


    ## Inputs
    ### Common Inputs
        function: The function input
        inputs: The inputs input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "function",
            "helper_text": "The function input",
            "value": "",
            "type": "string",
        },
        {
            "field": "inputs",
            "helper_text": "The inputs input",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="map",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "MapTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("merge")
class MergeTool(Tool):
    """
    Recombine paths created by a condition node. Note: if you are not using a condition node, you shouldn’t use a merge node

    ## Inputs
    ### Common Inputs
        function: The function to apply to the input fields
        type: The expected type of the input and output fields
    ### When function = 'first' and type = '<T>'
        fields: The fields input
    ### When function = 'join' and type = '<T>'
        fields: The fields input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "function",
            "helper_text": "The function to apply to the input fields",
            "value": "first",
            "type": "enum<string>",
        },
        {
            "field": "type",
            "helper_text": "The expected type of the input and output fields",
            "value": "string",
            "type": "enum<string>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "first**<T>": {
            "inputs": [
                {"field": "fields", "type": "vec<<T>>", "value": [""]},
                {
                    "field": "function",
                    "type": "enum<string>",
                    "value": "first",
                    "helper_text": "The function to apply to the input fields",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "<T>",
                    "helper_text": "The Text from the path based on the condition node",
                }
            ],
        },
        "join**<T>": {
            "inputs": [
                {"field": "fields", "type": "vec<<T>>", "value": [""]},
                {
                    "field": "function",
                    "type": "enum<string>",
                    "value": "join",
                    "helper_text": "The function to apply to the output fields",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "vec<<T>>",
                    "helper_text": "The Text from the path based on the condition node",
                }
            ],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["function", "type"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Recombine paths created by a condition node. Note: if you are not using a condition node, you shouldn’t use a merge node",
        function: str | ToolInput = "first",
        type: str | ToolInput = "string",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(function, ToolInput):
            if function.type == "static":
                params["function"] = function.value
            else:
                raise ValueError(f"function cannot be a dynamic input")
        else:
            params["function"] = function
        if isinstance(type, ToolInput):
            if type.type == "static":
                params["type"] = type.value
            else:
                raise ValueError(f"type cannot be a dynamic input")
        else:
            params["type"] = type

        super().__init__(
            tool_type="merge",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if function is not None:
            if isinstance(function, ToolInput):
                self.inputs["function"] = {
                    "type": function.type,
                    "value": function.value or function.description,
                }
            else:
                self.inputs["function"] = {"type": "static", "value": function}
        if type is not None:
            if isinstance(type, ToolInput):
                self.inputs["type"] = {
                    "type": type.type,
                    "value": type.value or type.description,
                }
            else:
                self.inputs["type"] = {"type": "static", "value": type}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "MergeTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("condition")
class ConditionTool(Tool):
    """
    Specify a series of conditions and execute different paths based on the value of the conditions.

    ## Inputs
    ### Common Inputs
        conditions: The conditions input
        outputs: The outputs input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "conditions",
            "helper_text": "The conditions input",
            "value": [],
            "type": "vec<Dict[str, Any]>",
        },
        {
            "field": "outputs",
            "helper_text": "The outputs input",
            "value": {},
            "type": "map<string, string>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Specify a series of conditions and execute different paths based on the value of the conditions.",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="condition",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "ConditionTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("nl_to_sql")
class NlToSqlTool(Tool):
    """
    Convert natural language queries to SQL queries.

    ## Inputs
    ### Common Inputs
        db_dialect: The database dialect to use
        model: The model to use for the conversion
        schema: The schema of the database
        text: The natural language query to convert to SQL
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "db_dialect",
            "helper_text": "The database dialect to use",
            "value": "PostgreSQL",
            "type": "enum<string>",
        },
        {
            "field": "model",
            "helper_text": "The model to use for the conversion",
            "value": "gpt-4o",
            "type": "enum<string>",
        },
        {
            "field": "schema",
            "helper_text": "The schema of the database",
            "value": "",
            "type": "string",
        },
        {
            "field": "text",
            "helper_text": "The natural language query to convert to SQL",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Convert natural language queries to SQL queries.",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="nl_to_sql",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "NlToSqlTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("read_json_values")
class ReadJsonValuesTool(Tool):
    """
    Read values from a JSON object based on a provided key(s).

    ## Inputs
    ### Common Inputs
        json_string: The JSON you want to read from
        keys: Define the name(s) of the JSON keys from the JSON that you want to read
        processed_outputs: The processed_outputs input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "json_string",
            "helper_text": "The JSON you want to read from",
            "value": "",
            "type": "string",
        },
        {
            "field": "keys",
            "helper_text": "Define the name(s) of the JSON keys from the JSON that you want to read",
            "value": [],
            "type": "vec<Dict[str, Any]>",
        },
        {
            "field": "processed_outputs",
            "helper_text": "The processed_outputs input",
            "value": {},
            "type": "map<string, string>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Read values from a JSON object based on a provided key(s).",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="read_json_values",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "ReadJsonValuesTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("write_json_value")
class WriteJsonValueTool(Tool):
    """
    Update a specific value in a JSON.

    ## Inputs
    ### Common Inputs
        fields: The fields input
        selected: Whether to update the JSON value or create a new JSON
    ### old
        json_string: The JSON to update
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "fields",
            "helper_text": "The fields input",
            "value": [],
            "type": "vec<Dict[str, Any]>",
        },
        {
            "field": "selected",
            "helper_text": "Whether to update the JSON value or create a new JSON",
            "value": "new",
            "type": "enum<string>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "old": {
            "inputs": [
                {
                    "field": "json_string",
                    "type": "string",
                    "value": "",
                    "helper_text": "The JSON to update",
                }
            ],
            "outputs": [],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["selected"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Update a specific value in a JSON.",
        selected: str | ToolInput = "new",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(selected, ToolInput):
            if selected.type == "static":
                params["selected"] = selected.value
            else:
                raise ValueError(f"selected cannot be a dynamic input")
        else:
            params["selected"] = selected

        super().__init__(
            tool_type="write_json_value",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if selected is not None:
            if isinstance(selected, ToolInput):
                self.inputs["selected"] = {
                    "type": selected.type,
                    "value": selected.value or selected.description,
                }
            else:
                self.inputs["selected"] = {"type": "static", "value": selected}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "WriteJsonValueTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("api")
class ApiTool(Tool):
    """
    Make an API request to a given URL.

    ## Inputs
    ### Common Inputs
        files: Files to include in the API request
        headers: Headers to include in the API request
        is_raw_json: Whether to return the raw JSON response from the API
        method: Choose the API Method desired (GET, POST, PUT, DELETE, PATCH)
        query_params: Query parameters to include in the API request
        url: Target URL for the API Request
    ### When is_raw_json = False
        body_params: The body parameters to include in the API request
    ### When is_raw_json = True
        raw_json: The raw JSON request to the API
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "files",
            "helper_text": "Files to include in the API request",
            "value": [],
            "type": "vec<Dict[str, Any]>",
        },
        {
            "field": "headers",
            "helper_text": "Headers to include in the API request",
            "value": [],
            "type": "vec<Dict[str, Any]>",
        },
        {
            "field": "is_raw_json",
            "helper_text": "Whether to return the raw JSON response from the API",
            "value": False,
            "type": "bool",
        },
        {
            "field": "method",
            "helper_text": "Choose the API Method desired (GET, POST, PUT, DELETE, PATCH)",
            "value": "GET",
            "type": "enum<string>",
        },
        {
            "field": "query_params",
            "helper_text": "Query parameters to include in the API request",
            "value": [],
            "type": "vec<Dict[str, Any]>",
        },
        {
            "field": "url",
            "helper_text": "Target URL for the API Request",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "true": {
            "inputs": [
                {
                    "field": "raw_json",
                    "type": "string",
                    "value": "",
                    "helper_text": "The raw JSON request to the API",
                    "label": "Raw JSON",
                    "order": 7,
                }
            ],
            "outputs": [],
        },
        "false": {
            "inputs": [
                {
                    "field": "body_params",
                    "type": "vec<Dict[str, Any]>",
                    "value": [],
                    "helper_text": "The body parameters to include in the API request",
                    "label": "Body Parameters",
                    "component": {"type": "table"},
                    "order": 7,
                }
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["is_raw_json"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Make an API request to a given URL.",
        headers: List[Any] | ToolInput = [],
        method: str | ToolInput = "GET",
        url: str | ToolInput = "",
        is_raw_json: bool | ToolInput = False,
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(is_raw_json, ToolInput):
            if is_raw_json.type == "static":
                params["is_raw_json"] = is_raw_json.value
            else:
                raise ValueError(f"is_raw_json cannot be a dynamic input")
        else:
            params["is_raw_json"] = is_raw_json

        super().__init__(
            tool_type="api",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if headers is not None:
            if isinstance(headers, ToolInput):
                self.inputs["headers"] = {
                    "type": headers.type,
                    "value": headers.value or headers.description,
                }
            else:
                self.inputs["headers"] = {"type": "static", "value": headers}
        if method is not None:
            if isinstance(method, ToolInput):
                self.inputs["method"] = {
                    "type": method.type,
                    "value": method.value or method.description,
                }
            else:
                self.inputs["method"] = {"type": "static", "value": method}
        if url is not None:
            if isinstance(url, ToolInput):
                self.inputs["url"] = {
                    "type": url.type,
                    "value": url.value or url.description,
                }
            else:
                self.inputs["url"] = {"type": "static", "value": url}
        if is_raw_json is not None:
            if isinstance(is_raw_json, ToolInput):
                self.inputs["is_raw_json"] = {
                    "type": is_raw_json.type,
                    "value": is_raw_json.value or is_raw_json.description,
                }
            else:
                self.inputs["is_raw_json"] = {"type": "static", "value": is_raw_json}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "ApiTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("url_loader")
class UrlLoaderTool(Tool):
    """
    Scrape content from a URL.

    ## Inputs
    ### Common Inputs
        provider: The provider to use for the URL loader
        url: The URL to load
    ### When provider = 'modal' and use_actions = True
        actions: The browser actions to perform on the URL
    ### When provider = 'modal'
        ai_enhance_content: Whether to enhance the content
        recursive: Whether to recursively load the URL
        use_actions: Perform browser actions to interact with the input website
        use_personal_api_key: Whether to use a personal API key
    ### When provider = 'apify'
        api_key: The API key to use
        recursive: Whether to recursively load the URL
    ### When provider = 'jina' and use_personal_api_key = True
        api_key: The API key to use
    ### When provider = 'modal' and use_personal_api_key = True
        apify_key: The API key to use
    ### When provider = 'modal' and recursive = True
        load_sitemap: Load URLs to crawl from a sitemap. If the URL is a sitemap, it will be used directly. If the URL is not a sitemap, the sitemap will be fetched automatically.
        url_limit: The maximum number of URLs to load
    ### When provider = 'apify' and recursive = True
        url_limit: The maximum number of URLs to load
    ### When provider = 'jina'
        use_personal_api_key: Whether to use a personal API key
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "provider",
            "helper_text": "The provider to use for the URL loader",
            "value": "modal",
            "type": "enum<string>",
        },
        {
            "field": "url",
            "helper_text": "The URL to load",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "jina**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "use_personal_api_key",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to use a personal API key",
                    "label": "Use personal API key",
                    "component": {"type": "bool"},
                }
            ],
            "outputs": [],
            "inputs_sort_order": ["provider", "url", "use_personal_api_key", "api_key"],
        },
        "apify**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "recursive",
                    "type": "bool",
                    "value": False,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                    "helper_text": "Whether to recursively load the URL",
                    "label": "Recursive",
                    "component": {"type": "bool"},
                },
                {
                    "field": "api_key",
                    "type": "string",
                    "value": "",
                    "helper_text": "The API key to use",
                    "label": "API key",
                    "component": {"type": "password"},
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
            ],
            "outputs": [],
            "inputs_sort_order": [
                "provider",
                "url",
                "recursive",
                "url_limit",
                "api_key",
            ],
        },
        "modal**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "recursive",
                    "type": "bool",
                    "value": False,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                    "helper_text": "Whether to recursively load the URL",
                    "label": "Recursive",
                    "component": {"type": "bool"},
                },
                {
                    "field": "use_personal_api_key",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to use a personal API key",
                    "label": "Use personal API key",
                    "component": {"type": "bool"},
                },
                {
                    "field": "ai_enhance_content",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to enhance the content",
                    "label": "AI enhance content",
                    "component": {"type": "bool"},
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
                {
                    "field": "use_actions",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Perform browser actions to interact with the input website",
                    "label": "Use browser actions",
                    "component": {"type": "bool"},
                    "banner_text": "This feature is only supported for the default provider and with recursive disabled",
                    "agent_field_type": "dynamic",
                    "is_hidden_in_agent": True,
                    "disable_conversion": True,
                },
            ],
            "outputs": [],
            "inputs_sort_order": [
                "provider",
                "url",
                "use_actions",
                "actions",
                "recursive",
                "url_limit",
                "load_sitemap",
                "use_personal_api_key",
                "apify_key",
                "ai_enhance_content",
            ],
        },
        "modal**true**(*)**(*)": {
            "inputs": [
                {
                    "field": "apify_key",
                    "type": "string",
                    "value": "",
                    "helper_text": "The API key to use",
                    "label": "API key",
                    "component": {"type": "password"},
                    "agent_field_type": "static",
                    "disable_conversion": True,
                }
            ],
            "outputs": [],
        },
        "modal**(*)**true**(*)": {
            "inputs": [
                {
                    "field": "actions",
                    "type": "vec<any>",
                    "value": [],
                    "helper_text": "The browser actions to perform on the URL",
                    "label": "Actions",
                    "agent_field_type": "dynamic",
                    "is_hidden_in_agent": True,
                    "disable_conversion": True,
                }
            ],
            "outputs": [],
        },
        "modal**(*)**(*)**true": {
            "inputs": [
                {
                    "field": "url_limit",
                    "type": "int32",
                    "value": 10,
                    "helper_text": "The maximum number of URLs to load",
                    "label": "URL limit",
                    "component": {"type": "int32"},
                },
                {
                    "field": "load_sitemap",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Load URLs to crawl from a sitemap. If the URL is a sitemap, it will be used directly. If the URL is not a sitemap, the sitemap will be fetched automatically.",
                    "label": "Load sitemap",
                    "component": {"type": "bool"},
                    "agent_field_type": "dynamic",
                },
            ],
            "outputs": [],
        },
        "jina**true**(*)**(*)": {
            "inputs": [
                {
                    "field": "api_key",
                    "type": "string",
                    "value": "",
                    "helper_text": "The API key to use",
                    "label": "API key",
                    "component": {"type": "password"},
                    "agent_field_type": "static",
                    "disable_conversion": True,
                }
            ],
            "outputs": [],
        },
        "apify**(*)**(*)**true": {
            "inputs": [
                {
                    "field": "url_limit",
                    "type": "int32",
                    "value": 10,
                    "helper_text": "The maximum number of URLs to load",
                    "label": "URL limit",
                    "component": {"type": "int32"},
                }
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["provider", "use_personal_api_key", "use_actions", "recursive"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Scrape content from a URL.",
        ai_enhance_content: bool | ToolInput = False,
        api_key: str | ToolInput = "",
        apify_key: str | ToolInput = "",
        provider: str | ToolInput = "modal",
        use_personal_api_key: bool | ToolInput = False,
        use_actions: bool | ToolInput = False,
        recursive: bool | ToolInput = False,
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(provider, ToolInput):
            if provider.type == "static":
                params["provider"] = provider.value
            else:
                raise ValueError(f"provider cannot be a dynamic input")
        else:
            params["provider"] = provider
        if isinstance(use_personal_api_key, ToolInput):
            if use_personal_api_key.type == "static":
                params["use_personal_api_key"] = use_personal_api_key.value
            else:
                raise ValueError(f"use_personal_api_key cannot be a dynamic input")
        else:
            params["use_personal_api_key"] = use_personal_api_key
        if isinstance(use_actions, ToolInput):
            if use_actions.type == "static":
                params["use_actions"] = use_actions.value
            else:
                raise ValueError(f"use_actions cannot be a dynamic input")
        else:
            params["use_actions"] = use_actions
        if isinstance(recursive, ToolInput):
            if recursive.type == "static":
                params["recursive"] = recursive.value
            else:
                raise ValueError(f"recursive cannot be a dynamic input")
        else:
            params["recursive"] = recursive

        super().__init__(
            tool_type="url_loader",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if ai_enhance_content is not None:
            if isinstance(ai_enhance_content, ToolInput):
                self.inputs["ai_enhance_content"] = {
                    "type": ai_enhance_content.type,
                    "value": ai_enhance_content.value or ai_enhance_content.description,
                }
            else:
                self.inputs["ai_enhance_content"] = {
                    "type": "static",
                    "value": ai_enhance_content,
                }
        if api_key is not None:
            if isinstance(api_key, ToolInput):
                self.inputs["api_key"] = {
                    "type": api_key.type,
                    "value": api_key.value or api_key.description,
                }
            else:
                self.inputs["api_key"] = {"type": "static", "value": api_key}
        if apify_key is not None:
            if isinstance(apify_key, ToolInput):
                self.inputs["apify_key"] = {
                    "type": apify_key.type,
                    "value": apify_key.value or apify_key.description,
                }
            else:
                self.inputs["apify_key"] = {"type": "static", "value": apify_key}
        if provider is not None:
            if isinstance(provider, ToolInput):
                self.inputs["provider"] = {
                    "type": provider.type,
                    "value": provider.value or provider.description,
                }
            else:
                self.inputs["provider"] = {"type": "static", "value": provider}
        if use_personal_api_key is not None:
            if isinstance(use_personal_api_key, ToolInput):
                self.inputs["use_personal_api_key"] = {
                    "type": use_personal_api_key.type,
                    "value": use_personal_api_key.value
                    or use_personal_api_key.description,
                }
            else:
                self.inputs["use_personal_api_key"] = {
                    "type": "static",
                    "value": use_personal_api_key,
                }
        if use_actions is not None:
            if isinstance(use_actions, ToolInput):
                self.inputs["use_actions"] = {
                    "type": use_actions.type,
                    "value": use_actions.value or use_actions.description,
                }
            else:
                self.inputs["use_actions"] = {"type": "static", "value": use_actions}
        if recursive is not None:
            if isinstance(recursive, ToolInput):
                self.inputs["recursive"] = {
                    "type": recursive.type,
                    "value": recursive.value or recursive.description,
                }
            else:
                self.inputs["recursive"] = {"type": "static", "value": recursive}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "UrlLoaderTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("wikipedia")
class WikipediaTool(Tool):
    """
    Query Wikipedia to return relevant articles

    ## Inputs
    ### Common Inputs
        chunk_text: Whether to chunk the text
        query: The Wikipedia query
    ### When chunk_text = True
        chunk_overlap: The overlap of the chunks
        chunk_size: The size of the chunks to create
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "chunk_text",
            "helper_text": "Whether to chunk the text",
            "value": False,
            "type": "bool",
        },
        {
            "field": "query",
            "helper_text": "The Wikipedia query",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "true": {
            "inputs": [
                {
                    "field": "chunk_size",
                    "type": "int32",
                    "value": 512,
                    "helper_text": "The size of the chunks to create",
                },
                {
                    "field": "chunk_overlap",
                    "type": "int32",
                    "value": 0,
                    "helper_text": "The overlap of the chunks",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "vec<string>",
                    "helper_text": "List of raw text from the Wikipedia article",
                }
            ],
        },
        "false": {
            "inputs": [],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "The raw text from the Wikipedia article",
                }
            ],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["chunk_text"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Query Wikipedia to return relevant articles",
        chunk_text: bool | ToolInput = False,
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(chunk_text, ToolInput):
            if chunk_text.type == "static":
                params["chunk_text"] = chunk_text.value
            else:
                raise ValueError(f"chunk_text cannot be a dynamic input")
        else:
            params["chunk_text"] = chunk_text

        super().__init__(
            tool_type="wikipedia",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if chunk_text is not None:
            if isinstance(chunk_text, ToolInput):
                self.inputs["chunk_text"] = {
                    "type": chunk_text.type,
                    "value": chunk_text.value or chunk_text.description,
                }
            else:
                self.inputs["chunk_text"] = {"type": "static", "value": chunk_text}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "WikipediaTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("youtube")
class YoutubeTool(Tool):
    """
    Get the transcript of a youtube video.

    ## Inputs
    ### Common Inputs
        chunk_text: Whether to chunk the text
        url: The YouTube URL to get the transcript of
    ### When chunk_text = True
        chunk_overlap: The overlap of the chunks
        chunk_size: The size of the chunks to create
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "chunk_text",
            "helper_text": "Whether to chunk the text",
            "value": False,
            "type": "bool",
        },
        {
            "field": "url",
            "helper_text": "The YouTube URL to get the transcript of",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "true": {
            "inputs": [
                {
                    "field": "chunk_size",
                    "type": "int32",
                    "value": 512,
                    "helper_text": "The size of the chunks to create",
                },
                {
                    "field": "chunk_overlap",
                    "type": "int32",
                    "value": 0,
                    "helper_text": "The overlap of the chunks",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "vec<string>",
                    "helper_text": "List of raw text from the YouTube transcript",
                }
            ],
        },
        "false": {
            "inputs": [],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "The raw text from the YouTube transcript",
                }
            ],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["chunk_text"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Get the transcript of a youtube video.",
        chunk_text: bool | ToolInput = False,
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(chunk_text, ToolInput):
            if chunk_text.type == "static":
                params["chunk_text"] = chunk_text.value
            else:
                raise ValueError(f"chunk_text cannot be a dynamic input")
        else:
            params["chunk_text"] = chunk_text

        super().__init__(
            tool_type="youtube",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if chunk_text is not None:
            if isinstance(chunk_text, ToolInput):
                self.inputs["chunk_text"] = {
                    "type": chunk_text.type,
                    "value": chunk_text.value or chunk_text.description,
                }
            else:
                self.inputs["chunk_text"] = {"type": "static", "value": chunk_text}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "YoutubeTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("arxiv")
class ArxivTool(Tool):
    """
    Query ARXIV to return relevant articles

    ## Inputs
    ### Common Inputs
        chunk_text: Whether to chunk the text
        query: The ARXIV query
    ### When chunk_text = True
        chunk_overlap: The overlap of the chunks
        chunk_size: The size of the chunks to create
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "chunk_text",
            "helper_text": "Whether to chunk the text",
            "value": False,
            "type": "bool",
        },
        {
            "field": "query",
            "helper_text": "The ARXIV query",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "true": {
            "inputs": [
                {
                    "field": "chunk_size",
                    "type": "int32",
                    "value": 512,
                    "helper_text": "The size of the chunks to create",
                },
                {
                    "field": "chunk_overlap",
                    "type": "int32",
                    "value": 0,
                    "helper_text": "The overlap of the chunks",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "vec<string>",
                    "helper_text": "List of raw text from the ARXIV article",
                }
            ],
        },
        "false": {
            "inputs": [],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "The raw text from the ARXIV article",
                }
            ],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["chunk_text"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Query ARXIV to return relevant articles",
        chunk_text: bool | ToolInput = False,
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(chunk_text, ToolInput):
            if chunk_text.type == "static":
                params["chunk_text"] = chunk_text.value
            else:
                raise ValueError(f"chunk_text cannot be a dynamic input")
        else:
            params["chunk_text"] = chunk_text

        super().__init__(
            tool_type="arxiv",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if chunk_text is not None:
            if isinstance(chunk_text, ToolInput):
                self.inputs["chunk_text"] = {
                    "type": chunk_text.type,
                    "value": chunk_text.value or chunk_text.description,
                }
            else:
                self.inputs["chunk_text"] = {"type": "static", "value": chunk_text}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "ArxivTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("serp_api")
class SerpApiTool(Tool):
    """
    Query the SERPAPI Google search API

    ## Inputs
    ### Common Inputs
        api_key: SERP API key
        query: The web search query
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "api_key",
            "helper_text": "SERP API key",
            "value": "",
            "type": "string",
        },
        {
            "field": "query",
            "helper_text": "The web search query",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Query the SERPAPI Google search API",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="serp_api",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "SerpApiTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("you_dot_com")
class YouDotComTool(Tool):
    """
    Query the You.com search API

    ## Inputs
    ### Common Inputs
        api_key: You.com API key
        loader_type: Select the loader type: General or News
        query: The search query
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "api_key",
            "helper_text": "You.com API key",
            "value": "",
            "type": "string",
        },
        {
            "field": "loader_type",
            "helper_text": "Select the loader type: General or News",
            "value": "YOU_DOT_COM",
            "type": "enum<string>",
        },
        {
            "field": "query",
            "helper_text": "The search query",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "YOU_DOT_COM": {"inputs": [], "outputs": [], "title": "You.com Web Search"},
        "YOU_DOT_COM_NEWS": {
            "inputs": [],
            "outputs": [],
            "title": "You.com Search News",
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["loader_type"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Query the You.com search API",
        loader_type: str | ToolInput = "YOU_DOT_COM",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(loader_type, ToolInput):
            if loader_type.type == "static":
                params["loader_type"] = loader_type.value
            else:
                raise ValueError(f"loader_type cannot be a dynamic input")
        else:
            params["loader_type"] = loader_type

        super().__init__(
            tool_type="you_dot_com",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if loader_type is not None:
            if isinstance(loader_type, ToolInput):
                self.inputs["loader_type"] = {
                    "type": loader_type.type,
                    "value": loader_type.value or loader_type.description,
                }
            else:
                self.inputs["loader_type"] = {"type": "static", "value": loader_type}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "YouDotComTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("exa_ai")
class ExaAiTool(Tool):
    """
    Query the Exa search API

    ## Inputs
    ### Common Inputs
        loader_type: Select the loader type: General, Companies, or Research Papers
        query: The search query
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "loader_type",
            "helper_text": "Select the loader type: General, Companies, or Research Papers",
            "value": "EXA_AI_SEARCH",
            "type": "enum<string>",
        },
        {
            "field": "query",
            "helper_text": "The search query",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "EXA_AI_SEARCH": {"inputs": [], "outputs": [], "title": "Exa AI Web Search"},
        "EXA_AI_SEARCH_COMPANIES": {
            "inputs": [],
            "outputs": [],
            "title": "Exa AI Companies",
        },
        "EXA_AI_SEARCH_RESEARCH_PAPERS": {
            "inputs": [],
            "outputs": [],
            "title": "Exa AI Research Papers",
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["loader_type"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Query the Exa search API",
        loader_type: str | ToolInput = "EXA_AI_SEARCH",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(loader_type, ToolInput):
            if loader_type.type == "static":
                params["loader_type"] = loader_type.value
            else:
                raise ValueError(f"loader_type cannot be a dynamic input")
        else:
            params["loader_type"] = loader_type

        super().__init__(
            tool_type="exa_ai",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if loader_type is not None:
            if isinstance(loader_type, ToolInput):
                self.inputs["loader_type"] = {
                    "type": loader_type.type,
                    "value": loader_type.value or loader_type.description,
                }
            else:
                self.inputs["loader_type"] = {"type": "static", "value": loader_type}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "ExaAiTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("google_search")
class GoogleSearchTool(Tool):
    """
    Query the Google Search search API

    ## Inputs
    ### Common Inputs
        location: The location of the search
        num_results: The number of results to return
        query: The Google search query
        search_type: Select the search type: Web, Image, Hotels, Events, or News
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "location",
            "helper_text": "The location of the search",
            "value": "us",
            "type": "enum<string>",
        },
        {
            "field": "num_results",
            "helper_text": "The number of results to return",
            "value": 10,
            "type": "int32",
        },
        {
            "field": "query",
            "helper_text": "The Google search query",
            "value": "",
            "type": "string",
        },
        {
            "field": "search_type",
            "helper_text": "Select the search type: Web, Image, Hotels, Events, or News",
            "value": "web",
            "type": "enum<string>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Query the Google Search search API",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="google_search",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "GoogleSearchTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("google_alert_rss_reader")
class GoogleAlertRssReaderTool(Tool):
    """
    Read the contents from a Google Alert RSS feed

    ## Inputs
    ### Common Inputs
        feed_link: The link of the Google Alert RSS feed you want to read
        timeframe: The publish dates of the items in the feed to read
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "feed_link",
            "helper_text": "The link of the Google Alert RSS feed you want to read",
            "value": "",
            "type": "string",
        },
        {
            "field": "timeframe",
            "helper_text": "The publish dates of the items in the feed to read",
            "value": "all",
            "type": "enum<string>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Read the contents from a Google Alert RSS feed",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="google_alert_rss_reader",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "GoogleAlertRssReaderTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("rss_feed_reader")
class RssFeedReaderTool(Tool):
    """
    Read the contents from an RSS feed

    ## Inputs
    ### Common Inputs
        entries: The number of entries you want to fetch
        timeframe: The publish dates of the items in the feed to read
        url: The link of the RSS feed you want to read
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "entries",
            "helper_text": "The number of entries you want to fetch",
            "value": 10,
            "type": "int32",
        },
        {
            "field": "timeframe",
            "helper_text": "The publish dates of the items in the feed to read",
            "value": "all",
            "type": "enum<string>",
        },
        {
            "field": "url",
            "helper_text": "The link of the RSS feed you want to read",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Read the contents from an RSS feed",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="rss_feed_reader",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "RssFeedReaderTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("csv_query")
class CsvQueryTool(Tool):
    """
    Utilizes an LLM agent to query CSV(s). Delimeter for the CSV must be commas.

    ## Inputs
    ### Common Inputs
        csv: The CSV to be queried (file must be a CSV). Note: Ensure connecting node is of type File not text
        query: The question you want to be answered by the CSV
        stream: Whether to stream the results of the query
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "csv",
            "helper_text": "The CSV to be queried (file must be a CSV). Note: Ensure connecting node is of type File not text",
            "value": None,
            "type": "file",
        },
        {
            "field": "query",
            "helper_text": "The question you want to be answered by the CSV",
            "value": "",
            "type": "string",
        },
        {
            "field": "stream",
            "helper_text": "Whether to stream the results of the query",
            "value": False,
            "type": "bool",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Utilizes an LLM agent to query CSV(s). Delimeter for the CSV must be commas.",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="csv_query",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "CsvQueryTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("csv_reader")
class CsvReaderTool(Tool):
    """
    Read the contents from a CSV file and output a list of the data for each column.

    ## Inputs
    ### Common Inputs
        columns: Define the name(s) of the columns that you want to read
        file_type: The type of file to read.
        processed_outputs: The processed_outputs input
        selected_file: The file to read.
    ### EXCEL
        sheet: The sheet input
        sheets: The sheets input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "columns",
            "helper_text": "Define the name(s) of the columns that you want to read",
            "value": [],
            "type": "vec<Dict[str, Any]>",
        },
        {
            "field": "file_type",
            "helper_text": "The type of file to read.",
            "value": "CSV",
            "type": "enum<string>",
        },
        {
            "field": "processed_outputs",
            "helper_text": "The processed_outputs input",
            "value": {},
            "type": "map<string, string>",
        },
        {
            "field": "selected_file",
            "helper_text": "The file to read.",
            "value": None,
            "type": "file",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "CSV": {"inputs": [], "outputs": []},
        "EXCEL": {
            "inputs": [
                {"field": "sheet", "type": "enum<string>"},
                {"field": "sheets", "type": "vec<string>", "value": []},
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["file_type"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Read the contents from a CSV file and output a list of the data for each column.",
        file_type: str | ToolInput = "CSV",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(file_type, ToolInput):
            if file_type.type == "static":
                params["file_type"] = file_type.value
            else:
                raise ValueError(f"file_type cannot be a dynamic input")
        else:
            params["file_type"] = file_type

        super().__init__(
            tool_type="csv_reader",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if file_type is not None:
            if isinstance(file_type, ToolInput):
                self.inputs["file_type"] = {
                    "type": file_type.type,
                    "value": file_type.value or file_type.description,
                }
            else:
                self.inputs["file_type"] = {"type": "static", "value": file_type}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "CsvReaderTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("csv_writer")
class CsvWriterTool(Tool):
    """
    Create a CSV from data

    ## Inputs
    ### Common Inputs
        load_option: Whether to load the CSV from a file or a string.
        selected_option: Whether to create a new CSV or update an existing one.
    ### When selected_option = 'new'
        columns: The columns to write to the CSV.
    ### When selected_option = 'old' and load_option = 'file'
        columns: The columns to write to the CSV.
        selected_file: The file to update.
    ### When selected_option = 'old' and load_option = 'text'
        csv_string: The CSV string to write.
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "load_option",
            "helper_text": "Whether to load the CSV from a file or a string.",
            "value": "file",
            "type": "enum<string>",
        },
        {
            "field": "selected_option",
            "helper_text": "Whether to create a new CSV or update an existing one.",
            "value": "new",
            "type": "enum<string>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "new**(*)": {
            "inputs": [
                {
                    "field": "columns",
                    "type": "vec<Dict[str, Any]>",
                    "value": [],
                    "helper_text": "The columns to write to the CSV.",
                    "table": {
                        "name": {"helper_text": "The name of the column"},
                        "value": {"helper_text": "The value of the column"},
                    },
                }
            ],
            "outputs": [],
        },
        "old**file": {
            "inputs": [
                {
                    "field": "selected_file",
                    "type": "file",
                    "helper_text": "The file to update.",
                },
                {
                    "field": "columns",
                    "type": "vec<Dict[str, Any]>",
                    "value": [],
                    "helper_text": "The columns to write to the CSV.",
                    "table": {
                        "name": {"helper_text": "The name of the column"},
                        "value": {"helper_text": "The value of the column"},
                    },
                },
            ],
            "outputs": [],
        },
        "old**text": {
            "inputs": [
                {
                    "field": "csv_string",
                    "type": "string",
                    "value": "",
                    "helper_text": "The CSV string to write.",
                }
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["selected_option", "load_option"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Create a CSV from data",
        selected_option: str | ToolInput = "new",
        load_option: str | ToolInput = "file",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(selected_option, ToolInput):
            if selected_option.type == "static":
                params["selected_option"] = selected_option.value
            else:
                raise ValueError(f"selected_option cannot be a dynamic input")
        else:
            params["selected_option"] = selected_option
        if isinstance(load_option, ToolInput):
            if load_option.type == "static":
                params["load_option"] = load_option.value
            else:
                raise ValueError(f"load_option cannot be a dynamic input")
        else:
            params["load_option"] = load_option

        super().__init__(
            tool_type="csv_writer",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if selected_option is not None:
            if isinstance(selected_option, ToolInput):
                self.inputs["selected_option"] = {
                    "type": selected_option.type,
                    "value": selected_option.value or selected_option.description,
                }
            else:
                self.inputs["selected_option"] = {
                    "type": "static",
                    "value": selected_option,
                }
        if load_option is not None:
            if isinstance(load_option, ToolInput):
                self.inputs["load_option"] = {
                    "type": load_option.type,
                    "value": load_option.value or load_option.description,
                }
            else:
                self.inputs["load_option"] = {"type": "static", "value": load_option}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "CsvWriterTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("create_list")
class CreateListTool(Tool):
    """
    Create a list from input texts. Final list is ordered in the order of the inputs.

    ## Inputs
    ### Common Inputs
        type: The type of the list
    ### <T>
        list: Value to be added to the list
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "type",
            "helper_text": "The type of the list",
            "value": "string",
            "type": "enum<string>",
        }
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "<T>": {
            "inputs": [
                {
                    "field": "list",
                    "type": "vec<<T>>",
                    "value": ["", ""],
                    "helper_text": "Value to be added to the list",
                }
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "vec<<T>>",
                    "helper_text": "The created list",
                }
            ],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["type"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Create a list from input texts. Final list is ordered in the order of the inputs.",
        type: str | ToolInput = "string",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(type, ToolInput):
            if type.type == "static":
                params["type"] = type.value
            else:
                raise ValueError(f"type cannot be a dynamic input")
        else:
            params["type"] = type

        super().__init__(
            tool_type="create_list",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if type is not None:
            if isinstance(type, ToolInput):
                self.inputs["type"] = {
                    "type": type.type,
                    "value": type.value or type.description,
                }
            else:
                self.inputs["type"] = {"type": "static", "value": type}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "CreateListTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("combine_list")
class CombineListTool(Tool):
    """
    Combine multiple lists into one list. Final list is ordered in the order of the input lists.

    ## Inputs
    ### Common Inputs
        type: The type of the list
    ### <T>
        list: List to be combined
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "type",
            "helper_text": "The type of the list",
            "value": "string",
            "type": "enum<string>",
        }
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "<T>": {
            "inputs": [
                {
                    "field": "list",
                    "type": "vec<vec<<T>>>",
                    "value": ["", ""],
                    "helper_text": "List to be combined",
                }
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "vec<<T>>",
                    "helper_text": "The combined list",
                }
            ],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["type"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Combine multiple lists into one list. Final list is ordered in the order of the input lists.",
        type: str | ToolInput = "string",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(type, ToolInput):
            if type.type == "static":
                params["type"] = type.value
            else:
                raise ValueError(f"type cannot be a dynamic input")
        else:
            params["type"] = type

        super().__init__(
            tool_type="combine_list",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if type is not None:
            if isinstance(type, ToolInput):
                self.inputs["type"] = {
                    "type": type.type,
                    "value": type.value or type.description,
                }
            else:
                self.inputs["type"] = {"type": "static", "value": type}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "CombineListTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("list_trimmer")
class ListTrimmerTool(Tool):
    """
    Trim a list to just the sections you want. Enter enter the number of items or specify the section of the list that you want to keep.

    ## Inputs
    ### Common Inputs
        specify_section: Check this to specify a section of the list to keep. Leave unchecked to keep a specified number of items from the start.
        type: The type of the list
    ### When specify_section = True and type = '<T>'
        end_index: The ending index of the section to keep (exclusive).
        list: The list to trim
        start_index: The starting index of the section to keep (inclusive). The first item of the list is index 0.
    ### When specify_section = False and type = '<T>'
        item_to_keep: Check this to specify a section of the list to keep. Leave unchecked to keep a specified number of items.
        list: The list to trim
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "specify_section",
            "helper_text": "Check this to specify a section of the list to keep. Leave unchecked to keep a specified number of items from the start.",
            "value": False,
            "type": "bool",
        },
        {
            "field": "type",
            "helper_text": "The type of the list",
            "value": "string",
            "type": "enum<string>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "false**<T>": {
            "inputs": [
                {
                    "field": "item_to_keep",
                    "type": "int32",
                    "value": 0,
                    "helper_text": "Check this to specify a section of the list to keep. Leave unchecked to keep a specified number of items.",
                },
                {
                    "field": "list",
                    "type": "vec<<T>>",
                    "value": "",
                    "helper_text": "The list to trim",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "vec<<T>>",
                    "helper_text": "The trimmed list",
                }
            ],
        },
        "true**<T>": {
            "inputs": [
                {
                    "field": "start_index",
                    "type": "int32",
                    "value": 0,
                    "helper_text": "The starting index of the section to keep (inclusive). The first item of the list is index 0.",
                },
                {
                    "field": "end_index",
                    "type": "int32",
                    "value": 1,
                    "helper_text": "The ending index of the section to keep (exclusive).",
                },
                {
                    "field": "list",
                    "type": "vec<<T>>",
                    "value": "",
                    "helper_text": "The list to trim",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "vec<<T>>",
                    "helper_text": "The trimmed list",
                }
            ],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["specify_section", "type"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Trim a list to just the sections you want. Enter enter the number of items or specify the section of the list that you want to keep.",
        specify_section: bool | ToolInput = False,
        type: str | ToolInput = "string",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(specify_section, ToolInput):
            if specify_section.type == "static":
                params["specify_section"] = specify_section.value
            else:
                raise ValueError(f"specify_section cannot be a dynamic input")
        else:
            params["specify_section"] = specify_section
        if isinstance(type, ToolInput):
            if type.type == "static":
                params["type"] = type.value
            else:
                raise ValueError(f"type cannot be a dynamic input")
        else:
            params["type"] = type

        super().__init__(
            tool_type="list_trimmer",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if specify_section is not None:
            if isinstance(specify_section, ToolInput):
                self.inputs["specify_section"] = {
                    "type": specify_section.type,
                    "value": specify_section.value or specify_section.description,
                }
            else:
                self.inputs["specify_section"] = {
                    "type": "static",
                    "value": specify_section,
                }
        if type is not None:
            if isinstance(type, ToolInput):
                self.inputs["type"] = {
                    "type": type.type,
                    "value": type.value or type.description,
                }
            else:
                self.inputs["type"] = {"type": "static", "value": type}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "ListTrimmerTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("duplicate_list")
class DuplicateListTool(Tool):
    """
    Create a new list by duplicating a single item with the size of the new list either matching the size of another list, or a specified size.

    ## Inputs
    ### Common Inputs
        specify_list_size: Check this box if you want to manually specify the list size. In this case 'Match List Size' will not be used.
        type: The type of the list
    ### When specify_list_size = True and type = '<T>'
        input_field: Item to duplicate
        list_size: The size of the new list
    ### When specify_list_size = False and type = '<T>'
        input_field: Item to duplicate
        list_size_to_match: The size of the list you want to match
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "specify_list_size",
            "helper_text": "Check this box if you want to manually specify the list size. In this case 'Match List Size' will not be used.",
            "value": False,
            "type": "bool",
        },
        {
            "field": "type",
            "helper_text": "The type of the list",
            "value": "string",
            "type": "enum<string>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "true**<T>": {
            "inputs": [
                {
                    "field": "list_size",
                    "type": "int32",
                    "value": 1,
                    "helper_text": "The size of the new list",
                },
                {
                    "field": "input_field",
                    "type": "<T>",
                    "value": "",
                    "helper_text": "Item to duplicate",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "vec<<T>>",
                    "helper_text": "The duplicated list",
                }
            ],
        },
        "false**<T>": {
            "inputs": [
                {
                    "field": "list_size_to_match",
                    "type": "vec<string>",
                    "value": "",
                    "helper_text": "The size of the list you want to match",
                },
                {
                    "field": "input_field",
                    "type": "<T>",
                    "value": "",
                    "helper_text": "Item to duplicate",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "vec<<T>>",
                    "helper_text": "The duplicated list",
                }
            ],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["specify_list_size", "type"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Create a new list by duplicating a single item with the size of the new list either matching the size of another list, or a specified size.",
        specify_list_size: bool | ToolInput = False,
        type: str | ToolInput = "string",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(specify_list_size, ToolInput):
            if specify_list_size.type == "static":
                params["specify_list_size"] = specify_list_size.value
            else:
                raise ValueError(f"specify_list_size cannot be a dynamic input")
        else:
            params["specify_list_size"] = specify_list_size
        if isinstance(type, ToolInput):
            if type.type == "static":
                params["type"] = type.value
            else:
                raise ValueError(f"type cannot be a dynamic input")
        else:
            params["type"] = type

        super().__init__(
            tool_type="duplicate_list",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if specify_list_size is not None:
            if isinstance(specify_list_size, ToolInput):
                self.inputs["specify_list_size"] = {
                    "type": specify_list_size.type,
                    "value": specify_list_size.value or specify_list_size.description,
                }
            else:
                self.inputs["specify_list_size"] = {
                    "type": "static",
                    "value": specify_list_size,
                }
        if type is not None:
            if isinstance(type, ToolInput):
                self.inputs["type"] = {
                    "type": type.type,
                    "value": type.value or type.description,
                }
            else:
                self.inputs["type"] = {"type": "static", "value": type}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "DuplicateListTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("flatten_list")
class FlattenListTool(Tool):
    """
    Flatten list of lists into a single list. For example, [[a, b], [c, d]] becomes [a,b,c,d].

    ## Inputs
    ### Common Inputs
        type: The type of the list
    ### <T>
        list_of_lists: List of lists to be flattened
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "type",
            "helper_text": "The type of the list",
            "value": "string",
            "type": "enum<string>",
        }
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "<T>": {
            "inputs": [
                {
                    "field": "list_of_lists",
                    "type": "vec<vec<<T>>>",
                    "value": "",
                    "helper_text": "List of lists to be flattened",
                }
            ],
            "outputs": [
                {
                    "field": "flattened_list",
                    "type": "vec<<T>>",
                    "helper_text": "The flattened list",
                }
            ],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["type"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Flatten list of lists into a single list. For example, [[a, b], [c, d]] becomes [a,b,c,d].",
        type: str | ToolInput = "string",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(type, ToolInput):
            if type.type == "static":
                params["type"] = type.value
            else:
                raise ValueError(f"type cannot be a dynamic input")
        else:
            params["type"] = type

        super().__init__(
            tool_type="flatten_list",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if type is not None:
            if isinstance(type, ToolInput):
                self.inputs["type"] = {
                    "type": type.type,
                    "value": type.value or type.description,
                }
            else:
                self.inputs["type"] = {"type": "static", "value": type}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "FlattenListTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("join_list_item")
class JoinListItemTool(Tool):
    """
    Join a list of items into a single string. If join_by_newline is true, the items are joined by a newline character.

    ## Inputs
    ### Common Inputs
        join_by_newline: Separate each line in the final output with a new line
        type: The type of the list
    ### When join_by_newline = False
        join_characters: Use a specified character to join list items into a single string
    ### When type = '<T>'
        list: List of items to be joined
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "join_by_newline",
            "helper_text": "Separate each line in the final output with a new line",
            "value": False,
            "type": "bool",
        },
        {
            "field": "type",
            "helper_text": "The type of the list",
            "value": "string",
            "type": "enum<string>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "false**(*)": {
            "inputs": [
                {
                    "field": "join_characters",
                    "type": "string",
                    "value": "",
                    "helper_text": "Use a specified character to join list items into a single string",
                }
            ],
            "outputs": [],
        },
        "(*)**<T>": {
            "inputs": [
                {
                    "field": "list",
                    "type": "vec<<T>>",
                    "value": "",
                    "helper_text": "List of items to be joined",
                }
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["join_by_newline", "type"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Join a list of items into a single string. If join_by_newline is true, the items are joined by a newline character.",
        join_by_newline: bool | ToolInput = False,
        type: str | ToolInput = "string",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(join_by_newline, ToolInput):
            if join_by_newline.type == "static":
                params["join_by_newline"] = join_by_newline.value
            else:
                raise ValueError(f"join_by_newline cannot be a dynamic input")
        else:
            params["join_by_newline"] = join_by_newline
        if isinstance(type, ToolInput):
            if type.type == "static":
                params["type"] = type.value
            else:
                raise ValueError(f"type cannot be a dynamic input")
        else:
            params["type"] = type

        super().__init__(
            tool_type="join_list_item",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if join_by_newline is not None:
            if isinstance(join_by_newline, ToolInput):
                self.inputs["join_by_newline"] = {
                    "type": join_by_newline.type,
                    "value": join_by_newline.value or join_by_newline.description,
                }
            else:
                self.inputs["join_by_newline"] = {
                    "type": "static",
                    "value": join_by_newline,
                }
        if type is not None:
            if isinstance(type, ToolInput):
                self.inputs["type"] = {
                    "type": type.type,
                    "value": type.value or type.description,
                }
            else:
                self.inputs["type"] = {"type": "static", "value": type}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "JoinListItemTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("csv_to_excel")
class CsvToExcelTool(Tool):
    """
    Convert a CSV file into XLSX

    ## Inputs
    ### Common Inputs
        csv_file: The CSV file to convert.
        horizontal_alignment: The horizontal alignment of the text
        max_column_width: The maximum width of the columns
        vertical_alignment: The vertical alignment of the text
        wrap_text: Enable text wrapping
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "csv_file",
            "helper_text": "The CSV file to convert.",
            "value": None,
            "type": "file",
        },
        {
            "field": "horizontal_alignment",
            "helper_text": "The horizontal alignment of the text",
            "value": "left",
            "type": "enum<string>",
        },
        {
            "field": "max_column_width",
            "helper_text": "The maximum width of the columns",
            "value": 100,
            "type": "int32",
        },
        {
            "field": "vertical_alignment",
            "helper_text": "The vertical alignment of the text",
            "value": "top",
            "type": "enum<string>",
        },
        {
            "field": "wrap_text",
            "helper_text": "Enable text wrapping",
            "value": True,
            "type": "bool",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Convert a CSV file into XLSX",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="csv_to_excel",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "CsvToExcelTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("text_formatter")
class TextFormatterTool(Tool):
    """
    Format text based off a specified formatter

    ## Inputs
    ### Common Inputs
        formatter: The formatter to apply to the text
        text: The text to format
    ### Truncate
        max_num_token: The maximum number of tokens to truncate the text to
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "formatter",
            "helper_text": "The formatter to apply to the text",
            "value": "To Uppercase",
            "type": "enum<string>",
        },
        {
            "field": "text",
            "helper_text": "The text to format",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "Truncate": {
            "inputs": [
                {
                    "field": "max_num_token",
                    "type": "int32",
                    "value": 0,
                    "helper_text": "The maximum number of tokens to truncate the text to",
                }
            ],
            "outputs": [],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["formatter"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Format text based off a specified formatter",
        formatter: str | ToolInput = "To Uppercase",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(formatter, ToolInput):
            if formatter.type == "static":
                params["formatter"] = formatter.value
            else:
                raise ValueError(f"formatter cannot be a dynamic input")
        else:
            params["formatter"] = formatter

        super().__init__(
            tool_type="text_formatter",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if formatter is not None:
            if isinstance(formatter, ToolInput):
                self.inputs["formatter"] = {
                    "type": formatter.type,
                    "value": formatter.value or formatter.description,
                }
            else:
                self.inputs["formatter"] = {"type": "static", "value": formatter}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "TextFormatterTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("json_operations")
class JsonOperationsTool(Tool):
    """


    ## Inputs
    ### Common Inputs
        sub_type: The sub_type input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "sub_type",
            "helper_text": "The sub_type input",
            "value": "",
            "type": "string",
        }
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="json_operations",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "JsonOperationsTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("list_operations")
class ListOperationsTool(Tool):
    """


    ## Inputs
    ### Common Inputs
        sub_type: The sub_type input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "sub_type",
            "helper_text": "The sub_type input",
            "value": "",
            "type": "string",
        }
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="list_operations",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "ListOperationsTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_gmail")
class IntegrationGmailTool(Tool):
    """
    Gmail

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### When action = 'create_draft'
        attachments: Attachments to be appended.
        body: The body of the email
        format: Either html (to allow html content) or text (for plaintext content - default)
        recipients: A single email or a comma-separated list of the recipients’ emails
        subject: The subject of the email
    ### When action = 'send_email'
        attachments: Attachments to be appended.
        body: The body of the email
        format: Either html (to allow html content) or text (for plaintext content - default)
        recipients: A single email or a comma-separated list of the recipients’ emails
        subject: The subject of the email
    ### When action = 'draft_reply'
        attachments: Attachments to be appended.
        body: The body of the email
        email_id: The ID of the email (often used in conjunction with a trigger where the email ID is received from the trigger)
        format: Either html (to allow html content) or text (for plaintext content - default)
        recipients: A single email or a comma-separated list of the recipients’ emails
    ### When action = 'send_reply'
        attachments: Attachments to be appended.
        body: The body of the email
        email_id: The ID of the email (often used in conjunction with a trigger where the email ID is received from the trigger)
        format: Either html (to allow html content) or text (for plaintext content - default)
        recipients: A single email or a comma-separated list of the recipients’ emails
    ### When action = 'list_messages'
        bcc: Emails BCC'd to this address
        body: The body of the email
        category: Filter by tab (e.g. Primary, Social)
        cc: Emails CC'd to this address
        custom_params: Extra filters as raw query
        filename: Find attachments by name or type
        from: Emails sent by this address
        has: Filter by feature (e.g. attachment, drive)
        has_attachment: Only emails with attachments
        has_images: Emails containing images
        has_links: Emails containing links
        has_starred: Only starred emails
        has_unread: Only unread emails
        has_user_labels: Emails with custom labels
        in: Search within a folder (e.g. sent, spam)
        include_spam_trash: Include spam and trash emails
        is: Filter by status (e.g. read, unread, starred)
        label: Search emails with this label
        label_ids: Emails with all listed label IDs
        larger: Emails larger than this size (e.g. 5M)
        list: Emails from this mailing list
        msg_id: Search by message ID (ignores other filters)
        newer_than: Emails newer than a time (e.g. 7d, 2m)
        older_than: Emails older than a time (e.g. 7d, 2m)
        page_token: Use to fetch next page of results
        projection: Select which fields to return
        query: Raw query string to use directly. If provided, overrides all other query parameters.
        smaller: Emails smaller than this size (e.g. 5M)
        subject: The subject of the email
        to: Emails sent to this address
        use_date: Toggle to use dates
    ### When action = 'list_messages' and use_date = True and use_exact_date = False
        date_range: The date_range input
    ### When action = 'list_messages' and use_date = True and use_exact_date = True
        exact_date: The exact_date input
    ### When action = 'list_messages' and use_date = False
        num_messages: Specify the last n number of emails
    ### When action = 'list_messages' and use_date = True
        use_exact_date: Switch between exact date range and relative dates
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Gmail>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "(*)**(*)**(*)": {
            "inputs": [],
            "outputs": [],
            "variant": "common_integration_nodes",
        },
        "create_draft**(*)**(*)": {
            "inputs": [
                {
                    "field": "recipients",
                    "type": "string",
                    "value": "",
                    "label": "To",
                    "placeholder": "john@company.com, alex@company.com",
                    "helper_text": "A single email or a comma-separated list of the recipients’ emails",
                    "order": 4,
                },
                {
                    "field": "subject",
                    "type": "string",
                    "value": "",
                    "label": "Subject",
                    "placeholder": "Introduction to John",
                    "helper_text": "The subject of the email",
                    "order": 5,
                },
                {
                    "field": "body",
                    "type": "string",
                    "value": "",
                    "label": "Body",
                    "placeholder": "Hi John, …",
                    "helper_text": "The body of the email",
                    "order": 6,
                },
                {
                    "field": "format",
                    "type": "enum<string>",
                    "value": "text",
                    "label": "Format",
                    "placeholder": "html / text (default)",
                    "helper_text": "Either html (to allow html content) or text (for plaintext content - default)",
                    "component": {
                        "type": "dropdown",
                        "options": [
                            {"label": "Text", "value": "text"},
                            {"label": "HTML", "value": "html"},
                        ],
                    },
                    "agent_field_type": "static",
                    "order": 3,
                },
                {
                    "field": "attachments",
                    "type": "vec<file>",
                    "value": [],
                    "label": "Attachments",
                    "placeholder": "Attachments!",
                    "helper_text": "Attachments to be appended.",
                    "order": 7,
                },
            ],
            "outputs": [],
            "name": "create_draft",
            "task_name": "tasks.gmail.create_email_draft",
            "description": "Create (but do not send) a new email",
            "label": "Create Email Draft",
            "inputs_sort_order": [
                "integration",
                "action",
                "format",
                "recipients",
                "subject",
                "body",
                "attachments",
            ],
        },
        "send_email**(*)**(*)": {
            "inputs": [
                {
                    "field": "recipients",
                    "type": "string",
                    "value": "",
                    "label": "To",
                    "placeholder": "john@company.com, alex@company.com",
                    "helper_text": "A single email or a comma-separated list of the recipients’ emails",
                    "order": 4,
                },
                {
                    "field": "subject",
                    "type": "string",
                    "value": "",
                    "label": "Subject",
                    "placeholder": "Introduction to John",
                    "helper_text": "The subject of the email",
                    "order": 5,
                },
                {
                    "field": "body",
                    "type": "string",
                    "value": "",
                    "label": "Body",
                    "placeholder": "Hi John, …",
                    "helper_text": "The body of the email",
                    "order": 6,
                },
                {
                    "field": "format",
                    "type": "enum<string>",
                    "value": "text",
                    "label": "Format",
                    "placeholder": "html / text (default)",
                    "helper_text": "Either html (to allow html content) or text (for plaintext content - default)",
                    "component": {
                        "type": "dropdown",
                        "options": [
                            {"label": "Text", "value": "text"},
                            {"label": "HTML", "value": "html"},
                        ],
                    },
                    "agent_field_type": "static",
                    "order": 3,
                },
                {
                    "field": "attachments",
                    "type": "vec<file>",
                    "value": [],
                    "label": "Attachments",
                    "placeholder": "Attachments!",
                    "helper_text": "Attachments to be appended.",
                    "order": 7,
                },
            ],
            "outputs": [],
            "name": "send_email",
            "task_name": "tasks.gmail.send_email",
            "description": "Create and send a new email",
            "label": "Send Email",
            "inputs_sort_order": [
                "integration",
                "action",
                "format",
                "recipients",
                "subject",
                "body",
                "attachments",
            ],
        },
        "draft_reply**(*)**(*)": {
            "inputs": [
                {
                    "field": "recipients",
                    "type": "string",
                    "value": "",
                    "label": "To",
                    "placeholder": "john@company.com, alex@company.com",
                    "helper_text": "A single email or a comma-separated list of the recipients’ emails",
                    "order": 4,
                },
                {
                    "field": "body",
                    "type": "string",
                    "value": "",
                    "label": "Body",
                    "placeholder": "Hi John, …",
                    "helper_text": "The body of the email",
                    "order": 5,
                },
                {
                    "field": "format",
                    "type": "enum<string>",
                    "value": "text",
                    "label": "Format",
                    "placeholder": "html / text (default)",
                    "helper_text": "Either html (to allow html content) or text (for plaintext content - default)",
                    "component": {
                        "type": "dropdown",
                        "options": [
                            {"label": "Text", "value": "text"},
                            {"label": "HTML", "value": "html"},
                        ],
                    },
                    "agent_field_type": "static",
                    "order": 3,
                },
                {
                    "field": "email_id",
                    "type": "string",
                    "value": "",
                    "label": "Email Id",
                    "placeholder": "john@company.com",
                    "helper_text": "The ID of the email (often used in conjunction with a trigger where the email ID is received from the trigger)",
                    "order": 6,
                },
                {
                    "field": "attachments",
                    "type": "vec<file>",
                    "value": [],
                    "label": "Attachments",
                    "placeholder": "Attachments!",
                    "helper_text": "Attachments to be appended.",
                    "order": 7,
                },
            ],
            "outputs": [],
            "name": "draft_reply",
            "task_name": "tasks.gmail.draft_reply",
            "description": "Create (but do not send) a draft of a reply to an existing email",
            "label": "Draft Reply",
            "inputs_sort_order": [
                "integration",
                "action",
                "format",
                "recipients",
                "body",
                "email_id",
                "attachments",
            ],
        },
        "send_reply**(*)**(*)": {
            "inputs": [
                {
                    "field": "recipients",
                    "type": "string",
                    "value": "",
                    "label": "To",
                    "placeholder": "john@company.com, alex@company.com",
                    "helper_text": "A single email or a comma-separated list of the recipients’ emails",
                },
                {
                    "field": "body",
                    "type": "string",
                    "value": "",
                    "label": "Body",
                    "placeholder": "Hi John, …",
                    "helper_text": "The body of the email",
                },
                {
                    "field": "format",
                    "type": "enum<string>",
                    "value": "text",
                    "label": "Format",
                    "placeholder": "html / text (default)",
                    "helper_text": "Either html (to allow html content) or text (for plaintext content - default)",
                    "component": {
                        "type": "dropdown",
                        "options": [
                            {"label": "Text", "value": "text"},
                            {"label": "HTML", "value": "html"},
                        ],
                    },
                    "agent_field_type": "static",
                },
                {
                    "field": "email_id",
                    "type": "string",
                    "value": "",
                    "label": "Email Id",
                    "placeholder": "john@company.com",
                    "helper_text": "The ID of the email (often used in conjunction with a trigger where the email ID is received from the trigger)",
                },
                {
                    "field": "attachments",
                    "type": "vec<file>",
                    "value": [],
                    "label": "Attachments",
                    "placeholder": "Attachments!",
                    "helper_text": "Attachments to be appended.",
                },
            ],
            "outputs": [],
            "name": "send_reply",
            "task_name": "tasks.gmail.send_reply",
            "description": "Create and send a new reply to an existing email",
            "label": "Send Reply",
            "inputs_sort_order": [
                "integration",
                "action",
                "format",
                "recipients",
                "body",
                "email_id",
                "attachments",
            ],
        },
        "list_messages**(*)**(*)": {
            "inputs": [
                {
                    "field": "use_date",
                    "type": "bool",
                    "value": False,
                    "show_date_range": True,
                    "label": "Use Date",
                    "helper_text": "Toggle to use dates",
                    "order": 3,
                },
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "Raw Query",
                    "helper_text": "Raw query string to use directly. If provided, overrides all other query parameters.",
                },
                {
                    "field": "from",
                    "type": "string",
                    "value": "",
                    "label": "From",
                    "helper_text": "Emails sent by this address",
                },
                {
                    "field": "to",
                    "type": "string",
                    "value": "",
                    "label": "To",
                    "helper_text": "Emails sent to this address",
                },
                {
                    "field": "subject",
                    "type": "string",
                    "value": "",
                    "label": "Subject",
                    "helper_text": "Search keywords in the subject",
                },
                {
                    "field": "body",
                    "type": "string",
                    "value": "",
                    "label": "Body",
                    "helper_text": "Search text in the email body",
                },
                {
                    "field": "has_attachment",
                    "type": "enum<string>",
                    "value": "Ignore",
                    "hidden": True,
                    "helper_text": "Only emails with attachments",
                    "label": "Has Attachment",
                    "placeholder": "Ignore",
                    "component": {
                        "type": "dropdown",
                        "options": [
                            {"label": "Emails With Attachments", "value": "True"},
                            {"label": "Emails Without Attachments", "value": "False"},
                            {"label": "Ignore", "value": "Ignore"},
                        ],
                    },
                },
                {
                    "field": "has_images",
                    "type": "enum<string>",
                    "value": "Ignore",
                    "hidden": True,
                    "helper_text": "Emails containing images",
                    "label": "Has Images",
                    "placeholder": "Ignore",
                    "component": {
                        "type": "dropdown",
                        "options": [
                            {"label": "Emails With Images", "value": "True"},
                            {"label": "Emails Without Images", "value": "False"},
                            {"label": "Ignore", "value": "Ignore"},
                        ],
                    },
                },
                {
                    "field": "has_links",
                    "type": "enum<string>",
                    "value": "Ignore",
                    "hidden": True,
                    "helper_text": "Emails containing links",
                    "label": "Has Links",
                    "placeholder": "Ignore",
                    "component": {
                        "type": "dropdown",
                        "options": [
                            {"label": "Emails With Links", "value": "True"},
                            {"label": "Emails Without Links", "value": "False"},
                            {"label": "Ignore", "value": "Ignore"},
                        ],
                    },
                },
                {
                    "field": "has_starred",
                    "type": "enum<string>",
                    "value": "Ignore",
                    "hidden": True,
                    "helper_text": "Only starred emails",
                    "label": "Has Starred",
                    "placeholder": "Ignore",
                    "component": {
                        "type": "dropdown",
                        "options": [
                            {"label": "Include Starred Emails", "value": "True"},
                            {"label": "Exclude Starred Emails", "value": "False"},
                            {"label": "Ignore", "value": "Ignore"},
                        ],
                    },
                },
                {
                    "field": "has_unread",
                    "type": "enum<string>",
                    "value": "Ignore",
                    "hidden": True,
                    "helper_text": "Only unread emails",
                    "label": "Has Unread",
                    "placeholder": "Ignore",
                    "component": {
                        "type": "dropdown",
                        "options": [
                            {"label": "Include Unread Emails", "value": "True"},
                            {"label": "Exclude Unread Emails", "value": "False"},
                            {"label": "Ignore", "value": "Ignore"},
                        ],
                    },
                },
                {
                    "field": "label",
                    "type": "string",
                    "value": "",
                    "label": "Label",
                    "helper_text": "Search emails with this label",
                },
                {
                    "field": "in",
                    "type": "string",
                    "value": "",
                    "label": "Inside Folder",
                    "helper_text": "Search within a folder (e.g. sent, spam)",
                },
                {
                    "field": "is",
                    "type": "string",
                    "value": "",
                    "label": "Is",
                    "helper_text": "Filter by status (e.g. read, unread, starred)",
                },
                {
                    "field": "has",
                    "type": "string",
                    "value": "",
                    "label": "Has",
                    "helper_text": "Filter by feature (e.g. attachment, drive)",
                },
                {
                    "field": "filename",
                    "type": "string",
                    "value": "",
                    "label": "Filename",
                    "helper_text": "Find attachments by name or type",
                },
                {
                    "field": "newer_than",
                    "type": "string",
                    "value": "",
                    "label": "Newer Than",
                    "helper_text": "Emails newer than a time (e.g. 7d, 2m)",
                },
                {
                    "field": "older_than",
                    "type": "string",
                    "value": "",
                    "label": "Older Than",
                    "helper_text": "Emails older than a time (e.g. 7d, 2m)",
                },
                {
                    "field": "cc",
                    "type": "string",
                    "value": "",
                    "label": "CC",
                    "helper_text": "Emails CC'd to this address",
                },
                {
                    "field": "bcc",
                    "type": "string",
                    "value": "",
                    "label": "BCC",
                    "helper_text": "Emails BCC'd to this address",
                },
                {
                    "field": "list",
                    "type": "string",
                    "value": "",
                    "label": "List",
                    "helper_text": "Emails from this mailing list",
                },
                {
                    "field": "category",
                    "type": "string",
                    "value": "",
                    "label": "Category",
                    "helper_text": "Filter by tab (e.g. Primary, Social)",
                },
                {
                    "field": "larger",
                    "type": "string",
                    "value": "",
                    "label": "Larger",
                    "helper_text": "Emails larger than this size (e.g. 5M)",
                },
                {
                    "field": "smaller",
                    "type": "string",
                    "value": "",
                    "label": "Smaller",
                    "helper_text": "Emails smaller than this size (e.g. 5M)",
                },
                {
                    "field": "custom_params",
                    "type": "string",
                    "value": "",
                    "label": "Custom Parameters",
                    "helper_text": "Extra filters as raw query",
                },
                {
                    "field": "projection",
                    "type": "string",
                    "value": "",
                    "label": "Projection",
                    "helper_text": "Select which fields to return",
                },
                {
                    "field": "page_token",
                    "type": "string",
                    "value": "",
                    "label": "Page Token",
                    "helper_text": "Use to fetch next page of results",
                },
                {
                    "field": "label_ids",
                    "type": "string",
                    "value": "",
                    "label": "Label IDs",
                    "helper_text": "Emails with all listed label IDs",
                },
                {
                    "field": "has_user_labels",
                    "type": "enum<string>",
                    "value": "Ignore",
                    "hidden": True,
                    "helper_text": "Emails with custom labels",
                    "label": "Has User Labels",
                    "placeholder": "Ignore",
                    "component": {
                        "type": "dropdown",
                        "options": [
                            {"label": "Emails With User Labels", "value": "True"},
                            {"label": "Emails Without User Labels", "value": "False"},
                            {"label": "Ignore", "value": "Ignore"},
                        ],
                    },
                },
                {
                    "field": "include_spam_trash",
                    "type": "enum<string>",
                    "value": "Ignore",
                    "hidden": True,
                    "helper_text": "Include spam and trash emails",
                    "label": "Include Spam Trash",
                    "placeholder": "Ignore",
                    "component": {
                        "type": "dropdown",
                        "options": [
                            {"label": "Include Spam and Trash Emails", "value": "True"},
                            {
                                "label": "Exclude Spam and Trash Emails",
                                "value": "False",
                            },
                            {"label": "Ignore", "value": "Ignore"},
                        ],
                    },
                },
                {
                    "field": "msg_id",
                    "type": "string",
                    "value": "",
                    "label": "Message ID",
                    "helper_text": "Search by message ID (ignores other filters)",
                },
            ],
            "outputs": [
                {
                    "field": "email_ids",
                    "type": "vec<string>",
                    "helper_text": "The IDs of the retrieved emails",
                },
                {
                    "field": "email_subjects",
                    "type": "vec<string>",
                    "helper_text": "The subjects of the retrieved emails",
                },
                {
                    "field": "email_dates",
                    "type": "vec<string>",
                    "helper_text": "The sent dates of the retrieved emails",
                },
                {
                    "field": "email_bodies",
                    "type": "vec<string>",
                    "helper_text": "The content of the retrieved emails",
                },
                {
                    "field": "sender_addresses",
                    "type": "vec<string>",
                    "helper_text": "The email addresses of the senders",
                },
                {
                    "field": "email_display_names",
                    "type": "vec<string>",
                    "helper_text": "The display names of the senders",
                },
                {
                    "field": "recipient_addresses",
                    "type": "vec<string>",
                    "helper_text": "The email addresses of the recipients",
                },
                {
                    "field": "attachments",
                    "type": "vec<vec<file>>",
                    "helper_text": "The attachments of the retrieved emails",
                },
            ],
            "variant": "get_integration_nodes",
            "name": "list_messages",
            "task_name": "tasks.gmail.list_messages",
            "description": "Get emails from Gmail",
            "label": "Get Emails",
            "inputs_sort_order": [
                "integration",
                "action",
                "use_date",
                "use_exact_date",
                "date_range",
                "exact_date",
                "num_messages",
                "query",
                "from",
                "to",
                "subject",
                "body",
                "has_attachment",
            ],
        },
        "list_messages**false**(*)": {
            "inputs": [
                {
                    "field": "num_messages",
                    "type": "int32",
                    "value": 10,
                    "show_date_range": True,
                    "label": "Number of Emails",
                    "helper_text": "Specify the last n number of emails",
                    "order": 5,
                }
            ],
            "outputs": [],
        },
        "list_messages**true**(*)": {
            "inputs": [
                {
                    "field": "use_exact_date",
                    "type": "bool",
                    "value": False,
                    "show_date_range": True,
                    "label": "Use Exact Date",
                    "helper_text": "Switch between exact date range and relative dates",
                    "order": 4,
                }
            ],
            "outputs": [],
        },
        "list_messages**true**false": {
            "inputs": [
                {
                    "field": "date_range",
                    "type": "Dict[str, Any]",
                    "label": "Date Range",
                    "value": {
                        "date_type": "Last",
                        "date_value": 1,
                        "date_period": "Months",
                    },
                    "show_date_range": True,
                    "component": {"type": "date_range"},
                }
            ],
            "outputs": [],
        },
        "list_messages**true**true": {
            "inputs": [
                {
                    "field": "exact_date",
                    "type": "Dict[str, Any]",
                    "label": "Exact date",
                    "value": {"start": "", "end": ""},
                    "show_date_range": True,
                    "component": {"type": "date_range"},
                }
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["action", "use_date", "use_exact_date"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Gmail",
        format: str | ToolInput = "text",
        action: str | ToolInput = "",
        use_date: bool | ToolInput = False,
        use_exact_date: bool | ToolInput = False,
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action
        if isinstance(use_date, ToolInput):
            if use_date.type == "static":
                params["use_date"] = use_date.value
            else:
                raise ValueError(f"use_date cannot be a dynamic input")
        else:
            params["use_date"] = use_date
        if isinstance(use_exact_date, ToolInput):
            if use_exact_date.type == "static":
                params["use_exact_date"] = use_exact_date.value
            else:
                raise ValueError(f"use_exact_date cannot be a dynamic input")
        else:
            params["use_exact_date"] = use_exact_date

        super().__init__(
            tool_type="integration_gmail",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if format is not None:
            if isinstance(format, ToolInput):
                self.inputs["format"] = {
                    "type": format.type,
                    "value": format.value or format.description,
                }
            else:
                self.inputs["format"] = {"type": "static", "value": format}
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}
        if use_date is not None:
            if isinstance(use_date, ToolInput):
                self.inputs["use_date"] = {
                    "type": use_date.type,
                    "value": use_date.value or use_date.description,
                }
            else:
                self.inputs["use_date"] = {"type": "static", "value": use_date}
        if use_exact_date is not None:
            if isinstance(use_exact_date, ToolInput):
                self.inputs["use_exact_date"] = {
                    "type": use_exact_date.type,
                    "value": use_exact_date.value or use_exact_date.description,
                }
            else:
                self.inputs["use_exact_date"] = {
                    "type": "static",
                    "value": use_exact_date,
                }

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationGmailTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_copper")
class IntegrationCopperTool(Tool):
    """
    Copper

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### create_lead
        email: The email of the lead
        name: The name of the lead
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Copper>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "create_lead": {
            "inputs": [
                {
                    "field": "name",
                    "type": "string",
                    "value": "",
                    "label": "Name",
                    "placeholder": "John Smith",
                    "helper_text": "The name of the lead",
                },
                {
                    "field": "email",
                    "type": "string",
                    "value": "",
                    "label": "Email",
                    "placeholder": "john@company.com",
                    "helper_text": "The email of the lead",
                },
            ],
            "outputs": [],
            "name": "create_lead",
            "task_name": "tasks.copper.create_lead",
            "description": "Create a new lead",
            "label": "Create Lead",
            "variant": "default_integration_nodes",
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Copper",
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_copper",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationCopperTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_discord")
class IntegrationDiscordTool(Tool):
    """
    Discord

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### send_message
        channel_name: The name of the Discord channel
        message: The message you want to send
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Discord>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "send_message": {
            "inputs": [
                {
                    "field": "channel_name",
                    "type": "string",
                    "value": "",
                    "label": "Channel Name",
                    "placeholder": "General",
                    "helper_text": "The name of the Discord channel",
                },
                {
                    "field": "message",
                    "type": "string",
                    "value": "",
                    "label": "Message",
                    "placeholder": "Hello World!",
                    "helper_text": "The message you want to send",
                },
            ],
            "outputs": [],
            "name": "send_message",
            "task_name": "tasks.discord.send_message",
            "description": "Send a message to a specific channel",
            "label": "Send Message",
            "variant": "default_integration_nodes",
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Discord",
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_discord",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationDiscordTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_linear")
class IntegrationLinearTool(Tool):
    """
    Linear

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### create_comment
        comment: The comment on the issue
        issue_name: The name of the issue for the comment
    ### create_issue
        description: The description of the ticket
        team_name: The team within Linear
        title: The title of the issue
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Linear>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "create_issue": {
            "inputs": [
                {
                    "field": "team_name",
                    "type": "string",
                    "label": "Team",
                    "helper_text": "The team within Linear",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=team_name&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": False,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
                {
                    "field": "title",
                    "type": "string",
                    "value": "",
                    "label": "Title",
                    "placeholder": "Bug on submit button",
                    "helper_text": "The title of the issue",
                },
                {
                    "field": "description",
                    "type": "string",
                    "value": "",
                    "label": "Description",
                    "placeholder": "Clicking on submit button leads to wrong page",
                    "helper_text": "The description of the ticket",
                },
            ],
            "outputs": [],
            "name": "create_issue",
            "task_name": "tasks.linear.create_new_issue",
            "description": "Create a new issue",
            "label": "Create Issue",
            "variant": "common_integration_nodes",
        },
        "create_comment": {
            "inputs": [
                {
                    "field": "issue_name",
                    "type": "string",
                    "value": "",
                    "label": "Issue",
                    "placeholder": "Bug on submit button",
                    "helper_text": "The name of the issue for the comment",
                },
                {
                    "field": "comment",
                    "type": "string",
                    "value": "",
                    "label": "Comment",
                    "placeholder": "More users are facing this issue",
                    "helper_text": "The comment on the issue",
                },
            ],
            "outputs": [],
            "name": "create_comment",
            "task_name": "tasks.linear.create_new_comment",
            "description": "Create a new comment",
            "label": "Create Comment",
            "variant": "default_integration_nodes",
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Linear",
        team_name: Optional[str] | ToolInput = None,
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_linear",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if team_name is not None:
            if isinstance(team_name, ToolInput):
                self.inputs["team_name"] = {
                    "type": team_name.type,
                    "value": team_name.value or team_name.description,
                }
            else:
                self.inputs["team_name"] = {"type": "static", "value": team_name}
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationLinearTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_outlook")
class IntegrationOutlookTool(Tool):
    """
    Outlook

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### When action = 'create_draft'
        attachments: Attachments to be appended.
        body: The body of the email
        format: Either html (to allow html content) or text (for plaintext content - default)
        recipients: A single email or a comma-separated list of the recipients' emails
        subject: The subject of the email
    ### When action = 'send_email'
        attachments: Attachments to be appended.
        body: The body of the email
        format: Either html (to allow html content) or text (for plaintext content - default)
        recipients: A single email or a comma-separated list of the recipients' emails
        subject: The subject of the email
    ### When action = 'draft_reply'
        attachments: Attachments to be appended.
        body: The body of the email
        email_id: The ID of the email (often used in conjunction with a trigger where the email ID is received from the trigger)
        format: Either html (to allow html content) or text (for plaintext content - default)
        recipients: A single email or a comma-separated list of the recipients' emails
    ### When action = 'send_reply'
        attachments: Attachments to be appended.
        body: The body of the email
        email_id: The ID of the email (often used in conjunction with a trigger where the email ID is received from the trigger)
        format: Either html (to allow html content) or text (for plaintext content - default)
        recipients: A single email or a comma-separated list of the recipients' emails
    ### When action = 'read_email' and use_date = True and use_exact_date = False
        date_range: pick the relative date range
    ### When action = 'read_email' and use_date = True and use_exact_date = True
        exact_date: Pick the start and end dates
    ### When action = 'read_email'
        item_id: Select an email to read
        use_date: Toggle to use dates
    ### When action = 'read_email' and use_date = False
        num_messages: Specify the last n number of emails
    ### When action = 'read_email' and use_date = True
        use_exact_date: Switch between exact date range and relative dates
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Outlook>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "(*)**(*)**(*)": {
            "inputs": [],
            "outputs": [],
            "variant": "common_integration_nodes",
        },
        "create_draft**(*)**(*)": {
            "inputs": [
                {
                    "field": "recipients",
                    "type": "string",
                    "value": "",
                    "label": "Recipients",
                    "placeholder": "john@company.com, alex@company.com",
                    "helper_text": "A single email or a comma-separated list of the recipients' emails",
                },
                {
                    "field": "subject",
                    "type": "string",
                    "value": "",
                    "label": "Subject",
                    "placeholder": "Introduction to John",
                    "helper_text": "The subject of the email",
                },
                {
                    "field": "body",
                    "type": "string",
                    "value": "",
                    "label": "Body",
                    "placeholder": "Hi John, …",
                    "helper_text": "The body of the email",
                },
                {
                    "field": "format",
                    "type": "enum<string>",
                    "value": "text",
                    "label": "Format",
                    "placeholder": "html / text (default)",
                    "helper_text": "Either html (to allow html content) or text (for plaintext content - default)",
                    "component": {
                        "type": "dropdown",
                        "options": [
                            {"label": "Text", "value": "text"},
                            {"label": "HTML", "value": "html"},
                        ],
                    },
                    "agent_field_type": "static",
                },
                {
                    "field": "attachments",
                    "type": "vec<file>",
                    "value": [],
                    "label": "Attachments",
                    "placeholder": "Attachments!",
                    "helper_text": "Attachments to be appended.",
                },
            ],
            "outputs": [],
            "name": "create_draft",
            "task_name": "tasks.outlook.create_email_draft",
            "description": "Create (but do not send) a new email",
            "label": "Create Email Draft",
            "inputs_sort_order": [
                "integration",
                "action",
                "recipients",
                "subject",
                "format",
                "body",
            ],
        },
        "send_email**(*)**(*)": {
            "inputs": [
                {
                    "field": "recipients",
                    "type": "string",
                    "value": "",
                    "label": "Recipients",
                    "placeholder": "john@company.com, alex@company.com",
                    "helper_text": "A single email or a comma-separated list of the recipients' emails",
                },
                {
                    "field": "subject",
                    "type": "string",
                    "value": "",
                    "label": "Subject",
                    "placeholder": "Introduction to John",
                    "helper_text": "The subject of the email",
                },
                {
                    "field": "body",
                    "type": "string",
                    "value": "",
                    "label": "Body",
                    "placeholder": "Hi John, …",
                    "helper_text": "The body of the email",
                },
                {
                    "field": "format",
                    "type": "enum<string>",
                    "value": "text",
                    "label": "Format",
                    "placeholder": "html / text (default)",
                    "helper_text": "Either html (to allow html content) or text (for plaintext content - default)",
                    "component": {
                        "type": "dropdown",
                        "options": [
                            {"label": "Text", "value": "text"},
                            {"label": "HTML", "value": "html"},
                        ],
                    },
                    "agent_field_type": "static",
                },
                {
                    "field": "attachments",
                    "type": "vec<file>",
                    "value": [""],
                    "label": "Attachments",
                    "placeholder": "Attachments!",
                    "helper_text": "Attachments to be appended.",
                },
            ],
            "outputs": [],
            "name": "send_email",
            "task_name": "tasks.outlook.send_email",
            "description": "Create and send a new email",
            "label": "Send Email",
            "inputs_sort_order": [
                "integration",
                "action",
                "recipients",
                "subject",
                "format",
                "body",
                "attachments",
            ],
        },
        "draft_reply**(*)**(*)": {
            "inputs": [
                {
                    "field": "email_id",
                    "type": "string",
                    "value": "",
                    "label": "Email Id",
                    "placeholder": "john@company.com",
                    "helper_text": "The ID of the email (often used in conjunction with a trigger where the email ID is received from the trigger)",
                },
                {
                    "field": "recipients",
                    "type": "string",
                    "value": "",
                    "label": "Recipients",
                    "placeholder": "john@company.com, alex@company.com",
                    "helper_text": "A single email or a comma-separated list of the recipients' emails",
                },
                {
                    "field": "body",
                    "type": "string",
                    "value": "",
                    "label": "Body",
                    "placeholder": "Hi John, …",
                    "helper_text": "The body of the email",
                },
                {
                    "field": "format",
                    "type": "enum<string>",
                    "value": "text",
                    "label": "Format",
                    "placeholder": "html / text (default)",
                    "helper_text": "Either html (to allow html content) or text (for plaintext content - default)",
                    "component": {
                        "type": "dropdown",
                        "options": [
                            {"label": "Text", "value": "text"},
                            {"label": "HTML", "value": "html"},
                        ],
                    },
                    "agent_field_type": "static",
                },
                {
                    "field": "attachments",
                    "type": "vec<file>",
                    "value": [],
                    "label": "Attachments",
                    "placeholder": "Attachments!",
                    "helper_text": "Attachments to be appended.",
                },
            ],
            "outputs": [],
            "name": "draft_reply",
            "task_name": "tasks.outlook.draft_reply",
            "description": "Create (but do not send) a draft of a reply to an existing email",
            "label": "Draft Reply",
            "inputs_sort_order": [
                "integration",
                "action",
                "email_id",
                "recipients",
                "format",
                "body",
            ],
        },
        "send_reply**(*)**(*)": {
            "inputs": [
                {
                    "field": "email_id",
                    "type": "string",
                    "value": "",
                    "label": "Email Id",
                    "placeholder": "john@company.com",
                    "helper_text": "The ID of the email (often used in conjunction with a trigger where the email ID is received from the trigger)",
                },
                {
                    "field": "recipients",
                    "type": "string",
                    "value": "",
                    "label": "Recipients",
                    "placeholder": "john@company.com, alex@company.com",
                    "helper_text": "A single email or a comma-separated list of the recipients' emails",
                },
                {
                    "field": "body",
                    "type": "string",
                    "value": "",
                    "label": "Body",
                    "placeholder": "Hi John, …",
                    "helper_text": "The body of the email",
                },
                {
                    "field": "format",
                    "type": "enum<string>",
                    "value": "text",
                    "label": "Format",
                    "placeholder": "html / text (default)",
                    "helper_text": "Either html (to allow html content) or text (for plaintext content - default)",
                    "component": {
                        "type": "dropdown",
                        "options": [
                            {"label": "Text", "value": "text"},
                            {"label": "HTML", "value": "html"},
                        ],
                    },
                    "agent_field_type": "static",
                },
                {
                    "field": "attachments",
                    "type": "vec<file>",
                    "value": [],
                    "label": "Attachments",
                    "placeholder": "Attachments!",
                    "helper_text": "Attachments to be appended.",
                },
            ],
            "outputs": [],
            "name": "send_reply",
            "task_name": "tasks.outlook.send_reply",
            "description": "Create and send a new reply to an existing email",
            "label": "Send Reply",
            "inputs_sort_order": [
                "integration",
                "action",
                "email_id",
                "recipients",
                "format",
                "body",
                "attachments",
            ],
        },
        "read_email**(*)**(*)": {
            "inputs": [
                {
                    "field": "item_id",
                    "type": "string",
                    "label": "Mailbox",
                    "helper_text": "Select an email to read",
                    "show_date_range": True,
                    "hidden": True,
                    "component": {
                        "type": "folder",
                        "dynamic_config": {
                            "metadata_endpoint": "/{prefix}/metadata/children/{inputs.integration.object_id}?parent_id={}&page={}&page_size={dynamic_config.page_size}&directory={dynamic_config.show_only_directories}&q={}",
                            "tree_endpoint": "/{prefix}/metadata/get-tree/{inputs.integration.object_id}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "show_only_directories": True,
                        },
                        "multi_select": False,
                        "select_directories": True,
                        "select_file": False,
                    },
                    "order": 1,
                },
                {
                    "field": "use_date",
                    "type": "bool",
                    "value": False,
                    "show_date_range": True,
                    "label": "Use Date",
                    "helper_text": "Toggle to use dates",
                    "hidden": True,
                    "order": 2,
                },
            ],
            "outputs": [
                {
                    "field": "email_ids",
                    "type": "vec<string>",
                    "helper_text": "The IDs of the retrieved emails",
                },
                {
                    "field": "email_subjects",
                    "type": "vec<string>",
                    "helper_text": "The subjects of the retrieved emails",
                },
                {
                    "field": "email_dates",
                    "type": "vec<string>",
                    "helper_text": "The sent dates of the retrieved emails",
                },
                {
                    "field": "email_bodies",
                    "type": "vec<string>",
                    "helper_text": "The content of the retrieved emails",
                },
                {
                    "field": "sender_addresses",
                    "type": "vec<string>",
                    "helper_text": "The email addresses of the senders",
                },
                {
                    "field": "email_labels",
                    "type": "vec<string>",
                    "helper_text": "The display names of the senders",
                },
                {
                    "field": "recipient_addresses",
                    "type": "vec<string>",
                    "helper_text": "The email addresses of the recipients",
                },
                {
                    "field": "attachments",
                    "type": "vec<vec<file>>",
                    "helper_text": "The attachments for each email",
                },
            ],
            "variant": "common_integration_file_nodes",
            "name": "read_email",
            "task_name": "tasks.outlook.read_email",
            "description": "Read emails from Outlook",
            "label": "Read Emails",
            "inputs_sort_order": [
                "integration",
                "action",
                "item_id",
                "use_date",
                "use_exact_date",
                "date_range",
                "exact_date",
                "num_messages",
            ],
        },
        "read_email**false**(*)": {
            "inputs": [
                {
                    "field": "num_messages",
                    "type": "int32",
                    "value": 10,
                    "show_date_range": True,
                    "label": "Number of Emails",
                    "helper_text": "Specify the last n number of emails",
                    "hidden": True,
                    "order": 5,
                }
            ],
            "outputs": [],
        },
        "read_email**true**(*)": {
            "inputs": [
                {
                    "field": "use_exact_date",
                    "type": "bool",
                    "value": False,
                    "show_date_range": True,
                    "label": "Use Exact Date",
                    "helper_text": "Switch between exact date range and relative dates",
                    "hidden": True,
                    "order": 3,
                }
            ],
            "outputs": [],
        },
        "read_email**true**false": {
            "inputs": [
                {
                    "field": "date_range",
                    "type": "Dict[str, Any]",
                    "value": {
                        "date_type": "Last",
                        "date_value": 1,
                        "date_period": "Months",
                    },
                    "show_date_range": True,
                    "hidden": True,
                    "label": "Date Range",
                    "placeholder": "last 3 days",
                    "helper_text": "pick the relative date range",
                    "component": {"type": "date_range"},
                    "order": 4,
                }
            ],
            "outputs": [],
        },
        "read_email**true**true": {
            "inputs": [
                {
                    "field": "exact_date",
                    "type": "Dict[str, Any]",
                    "value": {"start": "", "end": ""},
                    "show_date_range": True,
                    "hidden": True,
                    "label": "Exact Date",
                    "placeholder": "2021-01-01 12:00:00",
                    "helper_text": "Pick the start and end dates",
                    "component": {"type": "date_range"},
                    "order": 4,
                }
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["action", "use_date", "use_exact_date"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Outlook",
        format: str | ToolInput = "text",
        action: str | ToolInput = "",
        use_date: bool | ToolInput = False,
        use_exact_date: bool | ToolInput = False,
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action
        if isinstance(use_date, ToolInput):
            if use_date.type == "static":
                params["use_date"] = use_date.value
            else:
                raise ValueError(f"use_date cannot be a dynamic input")
        else:
            params["use_date"] = use_date
        if isinstance(use_exact_date, ToolInput):
            if use_exact_date.type == "static":
                params["use_exact_date"] = use_exact_date.value
            else:
                raise ValueError(f"use_exact_date cannot be a dynamic input")
        else:
            params["use_exact_date"] = use_exact_date

        super().__init__(
            tool_type="integration_outlook",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if format is not None:
            if isinstance(format, ToolInput):
                self.inputs["format"] = {
                    "type": format.type,
                    "value": format.value or format.description,
                }
            else:
                self.inputs["format"] = {"type": "static", "value": format}
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}
        if use_date is not None:
            if isinstance(use_date, ToolInput):
                self.inputs["use_date"] = {
                    "type": use_date.type,
                    "value": use_date.value or use_date.description,
                }
            else:
                self.inputs["use_date"] = {"type": "static", "value": use_date}
        if use_exact_date is not None:
            if isinstance(use_exact_date, ToolInput):
                self.inputs["use_exact_date"] = {
                    "type": use_exact_date.type,
                    "value": use_exact_date.value or use_exact_date.description,
                }
            else:
                self.inputs["use_exact_date"] = {
                    "type": "static",
                    "value": use_exact_date,
                }

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationOutlookTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_salesforce")
class IntegrationSalesforceTool(Tool):
    """
    Salesforce

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### When action = 'run_sql_query'
        sql_query: SQL Query in Salesforce Object Query Language
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Salesforce>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "run_sql_query**(*)**(*)": {
            "inputs": [
                {
                    "field": "sql_query",
                    "type": "string",
                    "value": "",
                    "label": "SQL Query",
                    "placeholder": "SELECT Id, Name, AccountNumber FROM Account",
                    "helper_text": "SQL Query in Salesforce Object Query Language",
                }
            ],
            "outputs": [{"field": "output", "type": "string"}],
            "name": "run_sql_query",
            "task_name": "tasks.salesforce.run_sql_query",
            "description": "Run a SQL query to query data",
            "label": "Run SQL Query",
            "variant": "default_integration_nodes",
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Salesforce",
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_salesforce",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationSalesforceTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_slack")
class IntegrationSlackTool(Tool):
    """
    Slack

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### When action = 'send_message'
        attachments: Attachments to be appended.
        channel: The name of the Slack channel
        message: The message you want to send
        team: The name of the Slack team
    ### When action = 'read_message'
        channel: The name of the Slack channel
        team: The name of the Slack team
        use_date: Toggle to use dates
    ### When action = 'read_message' and use_date = True and use_exact_date = False
        date_range: pick the relative date range
    ### When action = 'read_message' and use_date = True and use_exact_date = True
        exact_date: Pick the start and end dates
    ### When action = 'read_message' and use_date = False
        num_messages: Specify the last n number of messages
    ### When action = 'read_message' and use_date = True
        use_exact_date: Switch between exact date range and relative dates
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Slack>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "(*)**(*)**(*)": {
            "inputs": [],
            "outputs": [],
            "variant": "common_integration_nodes",
        },
        "send_message**(*)**(*)": {
            "inputs": [
                {
                    "field": "team",
                    "type": "string",
                    "value": "",
                    "label": "Team",
                    "placeholder": "Vectorshift",
                    "helper_text": "The name of the Slack team",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=team_name&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                    "order": 3,
                },
                {
                    "field": "channel",
                    "type": "string",
                    "value": "",
                    "label": "Channel",
                    "placeholder": "General",
                    "helper_text": "The name of the Slack channel",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=channel_name&team={inputs.team}&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                    "order": 4,
                },
                {
                    "field": "message",
                    "type": "string",
                    "value": "",
                    "label": "Message",
                    "placeholder": "Hello World!",
                    "helper_text": "The message you want to send",
                    "order": 5,
                },
                {
                    "field": "attachments",
                    "type": "vec<file>",
                    "value": [],
                    "label": "Attachments",
                    "placeholder": "Attachments!",
                    "helper_text": "Attachments to be appended.",
                },
            ],
            "outputs": [],
            "name": "send_message",
            "task_name": "tasks.slack.create_message",
            "description": "Post a new message to a specific channel",
            "label": "Send Message",
            "inputs_sort_order": [
                "integration",
                "action",
                "team",
                "channel",
                "message",
                "attachments",
            ],
        },
        "read_message**(*)**(*)": {
            "inputs": [
                {
                    "field": "team",
                    "type": "string",
                    "value": "",
                    "label": "Team",
                    "placeholder": "Vectorshift",
                    "helper_text": "The name of the Slack team",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=team_name&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
                {
                    "field": "channel",
                    "type": "string",
                    "value": "",
                    "label": "Channel",
                    "placeholder": "General",
                    "helper_text": "The name of the Slack channel",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=channel_name&team={inputs.team}&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
                {
                    "field": "use_date",
                    "type": "bool",
                    "value": False,
                    "show_date_range": True,
                    "label": "Use Date",
                    "helper_text": "Toggle to use dates",
                    "hidden": True,
                },
            ],
            "outputs": [
                {
                    "field": "message",
                    "type": "vec<string>",
                    "helper_text": "The retrieved messages",
                },
                {
                    "field": "thread_id",
                    "type": "vec<string>",
                    "helper_text": "The retrieved thread ids",
                },
                {
                    "field": "attachment_names",
                    "type": "vec<vec<string>>",
                    "helper_text": "The retrieved attachment names",
                },
                {
                    "field": "sender_id",
                    "type": "vec<string>",
                    "helper_text": "The retrieved sender ids",
                },
                {
                    "field": "thread_link",
                    "type": "vec<string>",
                    "helper_text": "The retrieved thread links",
                },
            ],
            "name": "read_message",
            "task_name": "tasks.slack.read_messages",
            "description": "Reads n messages from a channel",
            "label": "Read Message",
            "inputs_sort_order": [
                "integration",
                "action",
                "team",
                "channel",
                "use_date",
                "use_exact_date",
                "date_range",
                "exact_date",
                "num_messages",
            ],
        },
        "read_message**false**(*)": {
            "inputs": [
                {
                    "field": "num_messages",
                    "type": "int32",
                    "value": 10,
                    "show_date_range": True,
                    "label": "Number of Messages",
                    "helper_text": "Specify the last n number of messages",
                    "hidden": True,
                }
            ],
            "outputs": [],
        },
        "read_message**true**(*)": {
            "inputs": [
                {
                    "field": "use_exact_date",
                    "type": "bool",
                    "value": False,
                    "show_date_range": True,
                    "label": "Use Exact Date",
                    "helper_text": "Switch between exact date range and relative dates",
                    "hidden": True,
                }
            ],
            "outputs": [],
        },
        "read_message**true**false": {
            "inputs": [
                {
                    "field": "date_range",
                    "type": "Dict[str, Any]",
                    "value": {
                        "date_type": "Last",
                        "date_value": 1,
                        "date_period": "Months",
                    },
                    "show_data_range": True,
                    "hidden": True,
                    "label": "Date Range",
                    "placeholder": "last 3 days",
                    "helper_text": "pick the relative date range",
                    "component": {"type": "date_range"},
                }
            ],
            "outputs": [],
        },
        "read_message**true**true": {
            "inputs": [
                {
                    "field": "exact_date",
                    "type": "Dict[str, Any]",
                    "value": {"start": "", "end": ""},
                    "show_data_range": True,
                    "hidden": True,
                    "label": "Exact Date",
                    "placeholder": "2021-01-01 12:00:00",
                    "helper_text": "Pick the start and end dates",
                    "component": {"type": "date_range"},
                }
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["action", "use_date", "use_exact_date"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Slack",
        channel: str | ToolInput = "",
        team: str | ToolInput = "",
        action: str | ToolInput = "",
        use_date: bool | ToolInput = False,
        use_exact_date: bool | ToolInput = False,
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action
        if isinstance(use_date, ToolInput):
            if use_date.type == "static":
                params["use_date"] = use_date.value
            else:
                raise ValueError(f"use_date cannot be a dynamic input")
        else:
            params["use_date"] = use_date
        if isinstance(use_exact_date, ToolInput):
            if use_exact_date.type == "static":
                params["use_exact_date"] = use_exact_date.value
            else:
                raise ValueError(f"use_exact_date cannot be a dynamic input")
        else:
            params["use_exact_date"] = use_exact_date

        super().__init__(
            tool_type="integration_slack",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if channel is not None:
            if isinstance(channel, ToolInput):
                self.inputs["channel"] = {
                    "type": channel.type,
                    "value": channel.value or channel.description,
                }
            else:
                self.inputs["channel"] = {"type": "static", "value": channel}
        if team is not None:
            if isinstance(team, ToolInput):
                self.inputs["team"] = {
                    "type": team.type,
                    "value": team.value or team.description,
                }
            else:
                self.inputs["team"] = {"type": "static", "value": team}
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}
        if use_date is not None:
            if isinstance(use_date, ToolInput):
                self.inputs["use_date"] = {
                    "type": use_date.type,
                    "value": use_date.value or use_date.description,
                }
            else:
                self.inputs["use_date"] = {"type": "static", "value": use_date}
        if use_exact_date is not None:
            if isinstance(use_exact_date, ToolInput):
                self.inputs["use_exact_date"] = {
                    "type": use_exact_date.type,
                    "value": use_exact_date.value or use_exact_date.description,
                }
            else:
                self.inputs["use_exact_date"] = {
                    "type": "static",
                    "value": use_exact_date,
                }

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationSlackTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_jira")
class IntegrationJiraTool(Tool):
    """
    Jira

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: The integration input
    ### When action = 'get_issues'
        affected_version: Filter by affected version
        assignee_name: Account Name of the user to assign the issue to
        comment: The comment text to add
        comment_exact: Match comment exactly
        component: Filter by issue component
        created: Issue creation (YYYY-MM-DD)
        description: Detailed description of the issue
        description_exact: Match description exactly
        due: Due (YYYY-MM-DD)
        fix_version: Filter by fix version
        issue_summary: Search by issue summary
        issue_type: Type of issue (e.g. Task, Bug, Story)
        labels: Filter by issue labels
        project: The name of the project
        query: The query to filter issues
        reporter_name: Account Name of the user who reported the issue
        resolution: Filter by resolution status
        resolved: Resolution (YYYY-MM-DD)
        site: The name of the Jira site
        status: The status of the issue (e.g. Open, Closed, In Progress)
        summary_exact: Match summary exactly
        text: Search in all text fields
        text_exact: Match text exactly across fields
        updated: Last update (YYYY-MM-DD)
        use_date: Toggle to use dates
    ### When action = 'create_issue'
        assignee_name: Account Name of the user to assign the issue to
        description: Detailed description of the issue
        issue_type: Type of issue (e.g. Task, Bug, Story)
        project: The name of the project
        site: The name of the Jira site
        summary: A brief title or summary of the issue
    ### When action = 'add_issue_comment'
        comment: The comment text to add
        issue_key: The key of the issue to update (e.g. PROJ-123)
        project: The name of the project
        site: The name of the Jira site
    ### When action = 'get_issues' and use_date = True and use_exact_date = False
        date_range: The date_range input
    ### When action = 'get_issues' and use_date = True and use_exact_date = True
        exact_date: The exact_date input
    ### When action = 'update_issue'
        issue_key: The key of the issue to update (e.g. PROJ-123)
        project: The name of the project
        site: The name of the Jira site
        update_assignee_name: Account Name of the user to assign the issue to
        update_description: The new description for the issue
        update_issue_type: Type of issue (e.g. Task, Bug, Story)
        update_summary: The new summary for the issue
    ### When action = 'read_issue'
        issue_key: The key of the issue to update (e.g. PROJ-123)
        project: The name of the project
        site: The name of the Jira site
    ### When action = 'read_issue_comments'
        issue_key: The key of the issue to update (e.g. PROJ-123)
        project: The name of the project
        site: The name of the Jira site
    ### When action = 'get_issues' and use_date = False
        num_messages: Specify the number of issues to fetch
    ### When action = 'get_users'
        project: The name of the project
        site: The name of the Jira site
    ### When action = 'get_issues' and use_date = True
        use_exact_date: Switch between exact date range and relative dates
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "The integration input",
            "value": None,
            "type": "integration<Jira>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "create_issue**(*)**(*)": {
            "inputs": [
                {
                    "field": "site",
                    "type": "string",
                    "value": "",
                    "label": "Site",
                    "placeholder": "Vectorshift",
                    "helper_text": "The name of the Jira site",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=site_name&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                    "order": 3,
                },
                {
                    "field": "project",
                    "type": "string",
                    "value": "",
                    "label": "Project",
                    "placeholder": "Project name",
                    "helper_text": "The name of the project",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=project_name&site={inputs.site}&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                    "order": 4,
                },
                {
                    "field": "summary",
                    "label": "Summary",
                    "type": "string",
                    "value": "",
                    "placeholder": "Enter issue summary",
                    "helper_text": "A brief title or summary of the issue",
                    "order": 7,
                },
                {
                    "field": "description",
                    "label": "Description",
                    "type": "string",
                    "value": "",
                    "placeholder": "Enter detailed description",
                    "helper_text": "Detailed description of the issue",
                    "order": 8,
                },
                {
                    "field": "issue_type",
                    "label": "Issue Type",
                    "type": "string",
                    "value": "",
                    "placeholder": "Select issue type",
                    "helper_text": "Type of issue (e.g. Task, Bug, Story)",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=issue_type&project={inputs.project}&site={inputs.site}&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                    "order": 5,
                },
                {
                    "field": "assignee_name",
                    "label": "Assignee Name",
                    "type": "string",
                    "value": "",
                    "placeholder": "Select assignee",
                    "helper_text": "Account Name of the user to assign the issue to",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=assignee_name&project={inputs.project}&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                    "order": 6,
                },
            ],
            "outputs": [
                {
                    "field": "site",
                    "type": "string",
                    "value": "",
                    "label": "Site",
                    "placeholder": "Vectorshift",
                    "helper_text": "The name of the Jira site",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=site_name&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
                {
                    "field": "issue_id",
                    "type": "string",
                    "helper_text": "The ID of the created issue",
                },
                {
                    "field": "issue_key",
                    "type": "string",
                    "helper_text": "The key of the created issue",
                },
                {
                    "field": "url",
                    "type": "string",
                    "helper_text": "The URL of the created issue",
                },
                {
                    "field": "raw_data",
                    "type": "string",
                    "helper_text": "The raw response data from Jira API",
                },
            ],
            "variant": "common_integration_nodes",
            "name": "create_issue",
            "task_name": "tasks.jira.create_issue",
            "description": "Create a issue",
            "label": "Create Issue",
            "inputs_sort_order": [
                "integration",
                "action",
                "site",
                "project",
                "issue_type",
                "assignee_name",
                "summary",
                "description",
            ],
        },
        "update_issue**(*)**(*)": {
            "inputs": [
                {
                    "field": "site",
                    "type": "string",
                    "value": "",
                    "label": "Site",
                    "placeholder": "Vectorshift",
                    "helper_text": "The name of the Jira site",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=site_name&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                    "order": 3,
                },
                {
                    "field": "project",
                    "type": "string",
                    "value": "",
                    "label": "Project",
                    "placeholder": "Project name",
                    "helper_text": "The name of the project",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=project_name&site={inputs.site}&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                    "order": 4,
                },
                {
                    "field": "issue_key",
                    "label": "Issue Key",
                    "type": "string",
                    "value": "",
                    "placeholder": "Enter issue key (e.g. PROJ-123)",
                    "helper_text": "The key of the issue to update (e.g. PROJ-123)",
                    "order": 5,
                },
                {
                    "field": "update_summary",
                    "label": "Summary",
                    "type": "string",
                    "value": "",
                    "placeholder": "Enter new summary",
                    "helper_text": "The new summary for the issue",
                },
                {
                    "field": "update_description",
                    "label": "Description",
                    "type": "string",
                    "value": "",
                    "placeholder": "Enter new description",
                    "helper_text": "The new description for the issue",
                },
                {
                    "field": "update_issue_type",
                    "label": "Issue Type",
                    "type": "string",
                    "value": "",
                    "placeholder": "Select issue type",
                    "helper_text": "Type of issue (e.g. Task, Bug, Story)",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=issue_type&project={inputs.project}&site={inputs.site}&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
                {
                    "field": "update_assignee_name",
                    "label": "Assignee Name",
                    "type": "string",
                    "value": "",
                    "placeholder": "Select assignee",
                    "helper_text": "Account Name of the user to assign the issue to",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=assignee_name&project={inputs.project}&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
            ],
            "outputs": [
                {
                    "field": "issue_key",
                    "type": "string",
                    "helper_text": "The key of the updated issue",
                },
                {
                    "field": "message",
                    "type": "string",
                    "helper_text": "Success message confirming the update",
                },
                {
                    "field": "raw_data",
                    "type": "string",
                    "helper_text": "The raw response data from Jira API",
                },
            ],
            "variant": "common_integration_nodes",
            "name": "update_issue",
            "task_name": "tasks.jira.update_issue",
            "description": "Update an existing Jira issue",
            "label": "Update Issue",
            "inputs_sort_order": [
                "integration",
                "action",
                "site",
                "project",
                "update_issue_type",
                "update_assignee_name",
                "issue_key",
                "update_summary",
                "update_description",
            ],
        },
        "get_users**(*)**(*)": {
            "inputs": [
                {
                    "field": "site",
                    "type": "string",
                    "value": "",
                    "label": "Site",
                    "placeholder": "Vectorshift",
                    "helper_text": "The name of the Jira site",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=site_name&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                    "order": 3,
                },
                {
                    "field": "project",
                    "type": "string",
                    "value": "",
                    "label": "Project",
                    "placeholder": "Project name",
                    "helper_text": "The name of the project",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=project_name&site={inputs.site}&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                    "order": 4,
                },
            ],
            "outputs": [
                {
                    "field": "account_id",
                    "type": "vec<string>",
                    "helper_text": "The account IDs of the users in the project",
                },
                {
                    "field": "email",
                    "type": "vec<string>",
                    "helper_text": "The email addresses of the users in the project",
                },
                {
                    "field": "display_name",
                    "type": "vec<string>",
                    "helper_text": "The display names of the users in the project",
                },
                {
                    "field": "active",
                    "type": "vec<bool>",
                    "helper_text": "The active status of the users in the project",
                },
                {
                    "field": "raw_data",
                    "type": "string",
                    "helper_text": "The raw response data from Jira API",
                },
            ],
            "variant": "common_integration_nodes",
            "name": "get_users",
            "task_name": "tasks.jira.get_users",
            "description": "Get users from a Jira project",
            "label": "Get Users",
            "inputs_sort_order": ["integration", "action", "site", "project"],
        },
        "read_issue**(*)**(*)": {
            "inputs": [
                {
                    "field": "site",
                    "type": "string",
                    "value": "",
                    "label": "Site",
                    "placeholder": "Vectorshift",
                    "helper_text": "The name of the Jira site",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=site_name&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                    "order": 3,
                },
                {
                    "field": "project",
                    "type": "string",
                    "value": "",
                    "label": "Project",
                    "placeholder": "Project name",
                    "helper_text": "The name of the project",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=project_name&site={inputs.site}&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                    "order": 4,
                },
                {
                    "field": "issue_key",
                    "label": "Issue Key",
                    "type": "string",
                    "value": "",
                    "placeholder": "Enter issue key (e.g. PROJ-123)",
                    "helper_text": "The key of the issue to retrieve (e.g. PROJ-123)",
                    "order": 5,
                },
            ],
            "outputs": [
                {
                    "field": "issue_id",
                    "type": "string",
                    "helper_text": "The unique identifier of the issues",
                },
                {
                    "field": "issue_key",
                    "type": "string",
                    "helper_text": "The key of the issues (e.g. PROJ-123)",
                },
                {
                    "field": "summary",
                    "type": "string",
                    "helper_text": "The summary/title of the issues",
                },
                {
                    "field": "description",
                    "type": "string",
                    "helper_text": "The description of the issues",
                },
                {
                    "field": "comments",
                    "type": "vec<string>",
                    "helper_text": "The comments of the issues",
                },
                {
                    "field": "issue_attachments",
                    "type": "vec<file>",
                    "helper_text": "The attachments of the issues",
                },
                {
                    "field": "created_date",
                    "type": "string",
                    "helper_text": "The date and time when the issues was created",
                },
                {
                    "field": "updated_date",
                    "type": "string",
                    "helper_text": "The date and time when the issues was last updated",
                },
                {
                    "field": "status",
                    "type": "string",
                    "helper_text": "The current status of the issues",
                },
                {
                    "field": "browser_url",
                    "type": "string",
                    "helper_text": "The URL to view the issues in browser",
                },
                {
                    "field": "issue_type",
                    "type": "string",
                    "helper_text": "The type of the issues",
                },
                {
                    "field": "assignee_id",
                    "type": "string",
                    "helper_text": "The account ID of the assignees",
                },
                {
                    "field": "assignee_name",
                    "type": "string",
                    "helper_text": "The display name of the assignees",
                },
                {
                    "field": "assignee_email",
                    "type": "string",
                    "helper_text": "The email address of the assignees",
                },
                {
                    "field": "reporter_id",
                    "type": "string",
                    "helper_text": "The account ID of the reporters",
                },
                {
                    "field": "reporter_name",
                    "type": "string",
                    "helper_text": "The display name of the reporters",
                },
                {
                    "field": "reporter_email",
                    "type": "string",
                    "helper_text": "The email address of the reporters",
                },
                {
                    "field": "raw_data",
                    "type": "string",
                    "helper_text": "The raw response data from Jira API",
                },
            ],
            "variant": "common_integration_nodes",
            "name": "read_issue",
            "task_name": "tasks.jira.read_issue",
            "description": "Retrieve details of an existing Jira issue",
            "label": "Read Issue",
            "inputs_sort_order": [
                "integration",
                "action",
                "site",
                "project",
                "issue_key",
            ],
        },
        "read_issue_comments**(*)**(*)": {
            "inputs": [
                {
                    "field": "site",
                    "type": "string",
                    "value": "",
                    "label": "Site",
                    "placeholder": "Vectorshift",
                    "helper_text": "The name of the Jira site",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=site_name&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                    "order": 3,
                },
                {
                    "field": "project",
                    "type": "string",
                    "value": "",
                    "label": "Project",
                    "placeholder": "Project name",
                    "helper_text": "The name of the project",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=project_name&site={inputs.site}&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                    "order": 4,
                },
                {
                    "field": "issue_key",
                    "label": "Issue Key",
                    "type": "string",
                    "value": "",
                    "placeholder": "Enter issue key (e.g. PROJ-123)",
                    "helper_text": "The key of the issue to get comments for (e.g. PROJ-123)",
                    "order": 5,
                },
            ],
            "outputs": [
                {
                    "field": "comment_id",
                    "type": "vec<string>",
                    "helper_text": "Array of comment IDs",
                },
                {
                    "field": "body",
                    "type": "vec<string>",
                    "helper_text": "Array of comment bodies",
                },
                {
                    "field": "created_date",
                    "type": "vec<string>",
                    "helper_text": "Array of comment creation dates",
                },
                {
                    "field": "updated_date",
                    "type": "vec<string>",
                    "helper_text": "Array of comment update dates",
                },
                {
                    "field": "author_id",
                    "type": "vec<string>",
                    "helper_text": "Array of comment author account IDs",
                },
                {
                    "field": "author_email",
                    "type": "vec<string>",
                    "helper_text": "Array of comment author email addresses",
                },
                {
                    "field": "author_name",
                    "type": "vec<string>",
                    "helper_text": "Array of comment author display names",
                },
                {
                    "field": "total",
                    "type": "int32",
                    "helper_text": "Total number of comments",
                },
                {
                    "field": "raw_data",
                    "type": "string",
                    "helper_text": "The raw response data from Jira API",
                },
            ],
            "variant": "common_integration_nodes",
            "name": "read_issue_comments",
            "task_name": "tasks.jira.read_issue_comments",
            "description": "Get all comments for a Jira issue",
            "label": "Read Issue Comments",
        },
        "add_issue_comment**(*)**(*)": {
            "inputs": [
                {
                    "field": "site",
                    "type": "string",
                    "value": "",
                    "label": "Site",
                    "placeholder": "Vectorshift",
                    "helper_text": "The name of the Jira site",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=site_name&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                    "order": 3,
                },
                {
                    "field": "project",
                    "type": "string",
                    "value": "",
                    "label": "Project",
                    "placeholder": "Project name",
                    "helper_text": "The name of the project",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=project_name&site={inputs.site}&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                    "order": 4,
                },
                {
                    "field": "issue_key",
                    "label": "Issue Key",
                    "type": "string",
                    "value": "",
                    "placeholder": "Enter issue key (e.g. PROJ-123)",
                    "helper_text": "The key of the issue to add comment to (e.g. PROJ-123)",
                    "order": 6,
                },
                {
                    "field": "comment",
                    "label": "Comment",
                    "type": "string",
                    "value": "",
                    "placeholder": "Enter your comment",
                    "helper_text": "The comment text to add",
                    "order": 5,
                },
            ],
            "outputs": [
                {
                    "field": "comment_id",
                    "label": "Comment Id",
                    "type": "string",
                    "helper_text": "ID of the newly created comment",
                },
                {
                    "field": "created_date",
                    "label": "Created Dates",
                    "type": "string",
                    "helper_text": "Creation date of the comment",
                },
                {
                    "field": "updated_date",
                    "type": "string",
                    "helper_text": "Last update date of the comment",
                },
                {
                    "field": "message",
                    "type": "string",
                    "helper_text": "Success message",
                },
                {
                    "field": "raw_data",
                    "type": "string",
                    "helper_text": "The raw response data from Jira API",
                },
            ],
            "variant": "common_integration_nodes",
            "name": "add_issue_comment",
            "task_name": "tasks.jira.add_issue_comment",
            "description": "Add a comment to a Jira issue",
            "label": "Add Issue Comment",
            "inputs_sort_order": [
                "integration",
                "action",
                "site",
                "project",
                "issue_key",
                "comment",
            ],
        },
        "get_issues**(*)**(*)": {
            "inputs": [
                {
                    "field": "site",
                    "type": "string",
                    "value": "",
                    "label": "Site",
                    "placeholder": "Vectorshift",
                    "helper_text": "The name of the Jira site",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=site_name&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                    "order": 3,
                },
                {
                    "field": "use_date",
                    "type": "bool",
                    "value": False,
                    "show_date_range": True,
                    "label": "Use Date",
                    "helper_text": "Toggle to use dates",
                    "order": 7,
                },
                {
                    "field": "project",
                    "type": "string",
                    "value": "",
                    "label": "Project",
                    "placeholder": "Project name",
                    "helper_text": "The name of the project",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=project_name&site={inputs.site}&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                    "order": 4,
                },
                {
                    "field": "issue_type",
                    "label": "Issue Type",
                    "type": "string",
                    "hidden": True,
                    "value": "",
                    "placeholder": "Select issue type",
                    "helper_text": "Type of issue (e.g. Task, Bug, Story)",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=issue_type&project={inputs.project}&site={inputs.site}&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                    "order": 5,
                },
                {
                    "field": "assignee_name",
                    "label": "Assignee Name",
                    "type": "string",
                    "hidden": True,
                    "value": "",
                    "placeholder": "Select assignee",
                    "helper_text": "Account Name of the user to assign the issue to",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=assignee_name&project={inputs.project}&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
                {
                    "field": "status",
                    "type": "string",
                    "value": "",
                    "label": "Status",
                    "placeholder": "Open",
                    "helper_text": "The status of the issue (e.g. Open, Closed, In Progress)",
                },
                {
                    "field": "reporter_name",
                    "label": "Reporter Name",
                    "type": "string",
                    "value": "",
                    "placeholder": "Select reporter",
                    "helper_text": "Account Name of the user who reported the issue",
                },
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "Query",
                    "placeholder": "Query",
                    "helper_text": "The query to filter issues",
                },
                {
                    "field": "issue_summary",
                    "type": "string",
                    "value": "",
                    "label": "Summary",
                    "placeholder": "Summary",
                    "helper_text": "Search by issue summary",
                },
                {
                    "field": "summary_exact",
                    "type": "string",
                    "value": "",
                    "label": "Summary Exact",
                    "placeholder": "Summary Exact",
                    "helper_text": "Match summary exactly",
                },
                {
                    "field": "description",
                    "type": "string",
                    "value": "",
                    "label": "Description",
                    "placeholder": "Description",
                    "helper_text": "Search in issue description",
                },
                {
                    "field": "description_exact",
                    "type": "string",
                    "value": "",
                    "label": "Description Exact",
                    "placeholder": "Description Exact",
                    "helper_text": "Match description exactly",
                },
                {
                    "field": "comment",
                    "type": "string",
                    "value": "",
                    "label": "Comment",
                    "placeholder": "Comment",
                    "helper_text": "Search in issue comments",
                },
                {
                    "field": "comment_exact",
                    "type": "string",
                    "value": "",
                    "label": "Comment Exact",
                    "placeholder": "Comment Exact",
                    "helper_text": "Match comment exactly",
                },
                {
                    "field": "text",
                    "type": "string",
                    "value": "",
                    "label": "Text",
                    "placeholder": "Text",
                    "helper_text": "Search in all text fields",
                },
                {
                    "field": "text_exact",
                    "type": "string",
                    "value": "",
                    "label": "Text Exact",
                    "placeholder": "Text Exact",
                    "helper_text": "Match text exactly across fields",
                },
                {
                    "field": "labels",
                    "type": "string",
                    "value": "",
                    "label": "Labels",
                    "placeholder": "Labels",
                    "helper_text": "Filter by issue labels",
                },
                {
                    "field": "fix_version",
                    "type": "string",
                    "value": "",
                    "label": "Fix Version",
                    "placeholder": "Fix Version",
                    "helper_text": "Filter by fix version",
                },
                {
                    "field": "affected_version",
                    "type": "string",
                    "value": "",
                    "label": "Affected Version",
                    "placeholder": "Affected Version",
                    "helper_text": "Filter by affected version",
                },
                {
                    "field": "component",
                    "type": "string",
                    "value": "",
                    "label": "Component",
                    "placeholder": "Component",
                    "helper_text": "Filter by issue component",
                },
                {
                    "field": "resolution",
                    "type": "string",
                    "value": "",
                    "label": "Resolution",
                    "placeholder": "Resolution",
                    "helper_text": "Filter by resolution status",
                },
                {
                    "field": "created",
                    "type": "string",
                    "value": "",
                    "label": "Created",
                    "placeholder": "YYYY-MM-DD",
                    "helper_text": "Issue creation (YYYY-MM-DD)",
                },
                {
                    "field": "updated",
                    "type": "string",
                    "value": "",
                    "label": "Updated",
                    "placeholder": "YYYY-MM-DD",
                    "helper_text": "Last update (YYYY-MM-DD)",
                },
                {
                    "field": "resolved",
                    "type": "string",
                    "value": "",
                    "label": "Resolved",
                    "placeholder": "YYYY-MM-DD",
                    "helper_text": "Resolution (YYYY-MM-DD)",
                },
                {
                    "field": "due",
                    "type": "string",
                    "value": "",
                    "label": "Due",
                    "placeholder": "YYYY-MM-DD",
                    "helper_text": "Due (YYYY-MM-DD)",
                },
            ],
            "outputs": [
                {
                    "field": "issue_ids",
                    "type": "vec<string>",
                    "helper_text": "The unique identifier of the issue",
                },
                {
                    "field": "issue_keys",
                    "type": "vec<string>",
                    "helper_text": "The key of the issue (e.g. PROJ-123)",
                },
                {
                    "field": "summaries",
                    "type": "vec<string>",
                    "helper_text": "The summary/title of the issue",
                },
                {
                    "field": "descriptions",
                    "type": "vec<string>",
                    "helper_text": "The description of the issue",
                },
                {
                    "field": "comments",
                    "type": "vec<vec<string>>",
                    "helper_text": "The comments of the issue",
                },
                {
                    "field": "issue_attachments",
                    "type": "vec<file>",
                    "helper_text": "The attachments of the issue",
                },
                {
                    "field": "created_dates",
                    "type": "vec<string>",
                    "helper_text": "The date and time when the issue was created",
                },
                {
                    "field": "updated_dates",
                    "type": "vec<string>",
                    "helper_text": "The date and time when the issue was last updated",
                },
                {
                    "field": "statuses",
                    "type": "vec<string>",
                    "helper_text": "The current status of the issue",
                },
                {
                    "field": "browser_urls",
                    "type": "vec<string>",
                    "helper_text": "The URL to view the issue in browser",
                },
                {
                    "field": "issue_types",
                    "type": "vec<string>",
                    "helper_text": "The type of the issue",
                },
                {
                    "field": "assignee_ids",
                    "type": "vec<string>",
                    "helper_text": "The account ID of the assignee",
                },
                {
                    "field": "assignee_names",
                    "type": "vec<string>",
                    "helper_text": "The display name of the assignee",
                },
                {
                    "field": "assignee_emails",
                    "type": "vec<string>",
                    "helper_text": "The email address of the assignee",
                },
                {
                    "field": "reporter_ids",
                    "type": "vec<string>",
                    "helper_text": "The account ID of the reporter",
                },
                {
                    "field": "reporter_names",
                    "type": "vec<string>",
                    "helper_text": "The display name of the reporter",
                },
                {
                    "field": "reporter_emails",
                    "type": "vec<string>",
                    "helper_text": "The email address of the reporter",
                },
                {
                    "field": "raw_data",
                    "type": "string",
                    "helper_text": "The raw response data from Jira API",
                },
            ],
            "variant": "get_integration_nodes",
            "name": "get_issues",
            "task_name": "tasks.jira.get_issues",
            "description": "Get all issues for a Jira project",
            "label": "Get Issues",
            "inputs_sort_order": [
                "integration",
                "action",
                "site",
                "project",
                "issue_type",
                "status",
                "assignee_name",
                "use_date",
                "use_exact_date",
                "date_range",
                "exact_date",
                "num_messages",
                "reporter_name",
                "query",
                "issue_summary",
                "summary_exact",
                "description",
                "description_exact",
                "comment",
                "comment_exact",
                "text",
                "text_exact",
                "labels",
                "fix_version",
                "affected_version",
                "component",
                "resolution",
                "created",
                "updated",
                "resolved",
                "due",
            ],
        },
        "get_issues**false**(*)": {
            "inputs": [
                {
                    "field": "num_messages",
                    "type": "int32",
                    "value": 10,
                    "show_date_range": True,
                    "label": "Number of Issues",
                    "helper_text": "Specify the number of issues to fetch",
                    "order": 6,
                }
            ],
            "outputs": [],
        },
        "get_issues**true**(*)": {
            "inputs": [
                {
                    "field": "use_exact_date",
                    "type": "bool",
                    "value": False,
                    "show_date_range": True,
                    "label": "Use Exact Date",
                    "helper_text": "Switch between exact date range and relative dates",
                    "order": 8,
                }
            ],
            "outputs": [],
        },
        "get_issues**true**false": {
            "inputs": [
                {
                    "field": "date_range",
                    "label": "Date Range",
                    "type": "Dict[str, Any]",
                    "value": {
                        "date_type": "Last",
                        "date_value": 1,
                        "date_period": "Months",
                    },
                    "show_date_range": True,
                    "order": 9,
                }
            ],
            "outputs": [],
        },
        "get_issues**true**true": {
            "inputs": [
                {
                    "field": "exact_date",
                    "label": "Exact date",
                    "type": "Dict[str, Any]",
                    "value": {"start": "", "end": ""},
                    "show_date_range": True,
                    "order": 9,
                }
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["action", "use_date", "use_exact_date"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Jira",
        assignee_name: str | ToolInput = "",
        issue_type: str | ToolInput = "",
        project: str | ToolInput = "",
        site: str | ToolInput = "",
        update_assignee_name: str | ToolInput = "",
        update_issue_type: str | ToolInput = "",
        action: str | ToolInput = "",
        use_date: bool | ToolInput = False,
        use_exact_date: bool | ToolInput = False,
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action
        if isinstance(use_date, ToolInput):
            if use_date.type == "static":
                params["use_date"] = use_date.value
            else:
                raise ValueError(f"use_date cannot be a dynamic input")
        else:
            params["use_date"] = use_date
        if isinstance(use_exact_date, ToolInput):
            if use_exact_date.type == "static":
                params["use_exact_date"] = use_exact_date.value
            else:
                raise ValueError(f"use_exact_date cannot be a dynamic input")
        else:
            params["use_exact_date"] = use_exact_date

        super().__init__(
            tool_type="integration_jira",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if assignee_name is not None:
            if isinstance(assignee_name, ToolInput):
                self.inputs["assignee_name"] = {
                    "type": assignee_name.type,
                    "value": assignee_name.value or assignee_name.description,
                }
            else:
                self.inputs["assignee_name"] = {
                    "type": "static",
                    "value": assignee_name,
                }
        if issue_type is not None:
            if isinstance(issue_type, ToolInput):
                self.inputs["issue_type"] = {
                    "type": issue_type.type,
                    "value": issue_type.value or issue_type.description,
                }
            else:
                self.inputs["issue_type"] = {"type": "static", "value": issue_type}
        if project is not None:
            if isinstance(project, ToolInput):
                self.inputs["project"] = {
                    "type": project.type,
                    "value": project.value or project.description,
                }
            else:
                self.inputs["project"] = {"type": "static", "value": project}
        if site is not None:
            if isinstance(site, ToolInput):
                self.inputs["site"] = {
                    "type": site.type,
                    "value": site.value or site.description,
                }
            else:
                self.inputs["site"] = {"type": "static", "value": site}
        if update_assignee_name is not None:
            if isinstance(update_assignee_name, ToolInput):
                self.inputs["update_assignee_name"] = {
                    "type": update_assignee_name.type,
                    "value": update_assignee_name.value
                    or update_assignee_name.description,
                }
            else:
                self.inputs["update_assignee_name"] = {
                    "type": "static",
                    "value": update_assignee_name,
                }
        if update_issue_type is not None:
            if isinstance(update_issue_type, ToolInput):
                self.inputs["update_issue_type"] = {
                    "type": update_issue_type.type,
                    "value": update_issue_type.value or update_issue_type.description,
                }
            else:
                self.inputs["update_issue_type"] = {
                    "type": "static",
                    "value": update_issue_type,
                }
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}
        if use_date is not None:
            if isinstance(use_date, ToolInput):
                self.inputs["use_date"] = {
                    "type": use_date.type,
                    "value": use_date.value or use_date.description,
                }
            else:
                self.inputs["use_date"] = {"type": "static", "value": use_date}
        if use_exact_date is not None:
            if isinstance(use_exact_date, ToolInput):
                self.inputs["use_exact_date"] = {
                    "type": use_exact_date.type,
                    "value": use_exact_date.value or use_exact_date.description,
                }
            else:
                self.inputs["use_exact_date"] = {
                    "type": "static",
                    "value": use_exact_date,
                }

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationJiraTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_sugar_crm")
class IntegrationSugarCrmTool(Tool):
    """
    SugarCRM

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### get_records
        filter: To filter records within module
        module: Your existing module on SugarCRM
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<SugarCRM>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "get_records": {
            "inputs": [
                {
                    "field": "module",
                    "type": "string",
                    "value": "",
                    "label": "Module",
                    "placeholder": "customer_support",
                    "helper_text": "Your existing module on SugarCRM",
                },
                {
                    "field": "filter",
                    "type": "string",
                    "value": "",
                    "label": "Filter",
                    "placeholder": "Name = 'John'",
                    "helper_text": "To filter records within module",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "any",
                    "helper_text": "The retrieved output",
                }
            ],
            "name": "get_records",
            "task_name": "tasks.sugar_crm.get_records",
            "description": "Fetch records",
            "label": "Get Records",
            "variant": "default_integration_nodes",
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "SugarCRM",
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_sugar_crm",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationSugarCrmTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_github")
class IntegrationGithubTool(Tool):
    """
    Github

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### create_pr
        base: Base branch for the PR - branch to which changes should be applied
        body: A description of the PR
        head: Head branch of the PR - branch containing changes you want to integrate
        owner_name: Github username of the repo owner (user or organization)
        repo_name: Name of the repository to read from
        title: The title of the PR
    ### update_pr
        body: A description of the PR
        owner_name: Github username of the repo owner (user or organization)
        pull_number: The number of the PR
        repo_name: Name of the repository to read from
        title: The title of the PR
    ### read_file
        branch_name: Name of the branch to read the file from
        file_name: Full path name of the file to read
        repo_name: Name of the repository to read from
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Github>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "(*)": {"inputs": [], "outputs": [], "variant": "common_integration_nodes"},
        "read_file": {
            "inputs": [
                {
                    "field": "repo_name",
                    "type": "string",
                    "agent_field_type": "static",
                    "label": "Repository Name",
                    "helper_text": "Name of the repository to read from",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=repo_name&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": False,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
                {
                    "field": "branch_name",
                    "type": "string",
                    "value": "",
                    "label": "Branch Name",
                    "placeholder": "main",
                    "helper_text": "Name of the branch to read the file from",
                },
                {
                    "field": "file_name",
                    "type": "string",
                    "value": "",
                    "label": "File Name",
                    "placeholder": "server/chat-commands/info.ts",
                    "helper_text": "Full path name of the file to read",
                },
            ],
            "outputs": [
                {"field": "output", "type": "string", "helper_text": "File contents"}
            ],
            "name": "read_file",
            "task_name": "tasks.github.read_file",
            "description": "Download a file from Github",
            "label": "Read a File",
            "inputs_sort_order": [
                "integration",
                "action",
                "repo_name",
                "branch_name",
                "file_name",
            ],
        },
        "create_pr": {
            "inputs": [
                {
                    "field": "repo_name",
                    "type": "string",
                    "agent_field_type": "static",
                    "label": "Repository Name",
                    "helper_text": "Name of the repository to read from",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=repo_name&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": False,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
                {
                    "field": "owner_name",
                    "type": "string",
                    "value": "",
                    "label": "Owner Name",
                    "placeholder": "smogon",
                    "helper_text": "Github username of the repo owner (user or organization)",
                },
                {
                    "field": "base",
                    "type": "string",
                    "value": "",
                    "label": "Base",
                    "placeholder": "dev",
                    "helper_text": "Base branch for the PR - branch to which changes should be applied",
                },
                {
                    "field": "head",
                    "type": "string",
                    "value": "",
                    "label": "Head",
                    "placeholder": "bugs-151-fix-bug",
                    "helper_text": "Head branch of the PR - branch containing changes you want to integrate",
                },
                {
                    "field": "title",
                    "type": "string",
                    "value": "",
                    "label": "Title",
                    "placeholder": "Fix Bug",
                    "helper_text": "The title of the PR",
                },
                {
                    "field": "body",
                    "type": "string",
                    "value": "",
                    "label": "Body",
                    "placeholder": "Fixes existing bugs",
                    "helper_text": "A description of the PR",
                },
            ],
            "outputs": [],
            "name": "create_pr",
            "task_name": "tasks.github.create_pr",
            "description": "Create a new pull request",
            "label": "Create a Pull Request",
            "inputs_sort_order": [
                "integration",
                "action",
                "repo_name",
                "owner_name",
                "base",
                "head",
                "title",
                "body",
            ],
        },
        "update_pr": {
            "inputs": [
                {
                    "field": "repo_name",
                    "type": "string",
                    "agent_field_type": "static",
                    "label": "Repository Name",
                    "helper_text": "Name of the repository to read from",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=repo_name&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": False,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
                {
                    "field": "owner_name",
                    "type": "string",
                    "value": "",
                    "label": "Owner Name",
                    "placeholder": "smogon",
                    "helper_text": "Github username of the repo owner (user or organization)",
                },
                {
                    "field": "pull_number",
                    "type": "string",
                    "value": "",
                    "label": "Pull Number",
                    "placeholder": "123",
                    "helper_text": "The number of the PR",
                },
                {
                    "field": "title",
                    "type": "string",
                    "value": "",
                    "label": "Title",
                    "placeholder": "Add new feature",
                    "helper_text": "The title of the PR",
                },
                {
                    "field": "body",
                    "type": "string",
                    "value": "",
                    "label": "Body",
                    "placeholder": "This PR adds a new feature to the project",
                    "helper_text": "The body of the PR",
                },
            ],
            "outputs": [],
            "name": "update_pr",
            "task_name": "tasks.github.update_pr",
            "description": "Update a pull request",
            "label": "Update a Pull Request",
            "inputs_sort_order": [
                "integration",
                "action",
                "repo_name",
                "owner_name",
                "pull_number",
                "title",
                "body",
            ],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Github",
        repo_name: Optional[str] | ToolInput = None,
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_github",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if repo_name is not None:
            if isinstance(repo_name, ToolInput):
                self.inputs["repo_name"] = {
                    "type": repo_name.type,
                    "value": repo_name.value or repo_name.description,
                }
            else:
                self.inputs["repo_name"] = {"type": "static", "value": repo_name}
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationGithubTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_zendesk")
class IntegrationZendeskTool(Tool):
    """
    Zendesk

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### When action = 'get_tickets'
        assignee: Assignee of the ticket
        body: Search in the full ticket content
        brand: Filter by brand
        comment: Search in ticket comments
        comment_exact: Match comment exactly
        description: Search in the ticket description
        due: Tickets due on this date
        external_id: Search by external ID
        group: Filter by assigned group
        include: Include related data (e.g. users)
        organization: Organization of the ticket
        priority: Priority of the ticket
        requester: Requester of the ticket
        satisfaction: Customer satisfaction rating
        solved: Tickets solved on this date
        sort_by: Field to sort results by
        sort_order: Order of sorting (asc/desc)
        status: Status of the ticket
        subject: Search tickets by subject
        subject_exact: Match subject exactly
        ticket_form: Filter by ticket form
        ticket_type: Type of the ticket
        updated: Tickets updated on this date
        use_date: Toggle to use dates
    ### When action = 'get_tickets' and use_date = True and use_exact_date = False
        date_range: The date_range input
    ### When action = 'get_tickets' and use_date = True and use_exact_date = True
        exact_date: The exact_date input
    ### When action = 'get_tickets' and use_date = False
        num_messages: Specify the number of tickets to fetch
    ### When action = 'create_comment'
        public: Whether the comment should be public
        ticket_body: Body content of the ticket
        ticket_id: The ID of Zendesk ticket to update
    ### When action = 'create_ticket'
        requester_email: Email of the requester
        requester_name: Name of the requester (Required if requester email is not already registered)
        ticket_body: Body content of the ticket
        ticket_priority: Priority of the ticket
        ticket_status: Status of the ticket
        ticket_subject: Subject content of the ticket
        ticket_type: Type of the ticket
    ### When action = 'update_ticket'
        ticket_id: The ID of Zendesk ticket to update
        ticket_priority: Priority of the ticket
        ticket_status: Status of the ticket
        ticket_type: Type of the ticket
        update_ticket_assignee_id: The ID of the assignee to update the ticket to
        update_ticket_body: Body content of the ticket
        update_ticket_subject: Subject content of the ticket
    ### When action = 'read_ticket'
        ticket_id: The ID of Zendesk ticket to update
    ### When action = 'read_ticket_comments'
        ticket_id: The ID of Zendesk ticket to update
    ### When action = 'get_tickets' and use_date = True
        use_exact_date: Switch between exact date range and relative dates
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Zendesk>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "create_ticket**(*)**(*)": {
            "inputs": [
                {
                    "field": "ticket_subject",
                    "type": "string",
                    "value": "",
                    "helper_text": "Subject content of the ticket",
                    "label": "Subject",
                    "placeholder": "Incident report",
                },
                {
                    "field": "ticket_body",
                    "type": "string",
                    "value": "",
                    "helper_text": "Body content of the ticket",
                    "label": "Body",
                    "placeholder": "Clicking on submit button doens’t work",
                },
                {
                    "field": "requester_email",
                    "type": "string",
                    "value": "",
                    "helper_text": "Email of the requester",
                    "label": "Requester Email",
                    "placeholder": "john@company.com",
                },
                {
                    "field": "requester_name",
                    "type": "string",
                    "value": "",
                    "helper_text": "Name of the requester (Required if requester email is not already registered)",
                    "label": "Requester Name",
                    "placeholder": "John Smith",
                },
                {
                    "field": "ticket_priority",
                    "type": "enum<string>",
                    "value": "",
                    "helper_text": "Priority of the ticket",
                    "label": "Priority",
                    "placeholder": "High",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "options": [
                            {"label": "Low", "value": "Low"},
                            {"label": "Normal", "value": "Normal"},
                            {"label": "High", "value": "High"},
                            {"label": "Urgent", "value": "Urgent"},
                        ],
                    },
                },
                {
                    "field": "ticket_type",
                    "type": "enum<string>",
                    "value": "",
                    "helper_text": "Type of the ticket",
                    "label": "Type",
                    "placeholder": "Incident",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "options": [
                            {"label": "Question", "value": "Question"},
                            {"label": "Incident", "value": "Incident"},
                            {"label": "Problem", "value": "Problem"},
                            {"label": "Task", "value": "Task"},
                        ],
                    },
                },
                {
                    "field": "ticket_status",
                    "type": "enum<string>",
                    "value": "",
                    "helper_text": "Status of the ticket",
                    "label": "Status",
                    "placeholder": "Open",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "options": [
                            {"label": "New", "value": "New"},
                            {"label": "Open", "value": "Open"},
                            {"label": "Pending", "value": "Pending"},
                            {"label": "Hold", "value": "Hold"},
                            {"label": "Solved", "value": "Solved"},
                            {"label": "Closed", "value": "Closed"},
                        ],
                    },
                },
            ],
            "outputs": [
                {
                    "field": "ticket_id",
                    "type": "string",
                    "helper_text": "Ticket ID of the created ticket",
                },
                {
                    "field": "ticket_details",
                    "type": "string",
                    "helper_text": "Ticket details in JSON format",
                },
            ],
            "variant": "common_integration_nodes",
            "name": "create_ticket",
            "task_name": "tasks.zendesk.create_ticket",
            "description": "Create a new ticket on Zendesk",
            "label": "Create Ticket",
            "inputs_sort_order": [
                "integration",
                "action",
                "ticket_priority",
                "ticket_type",
                "ticket_status",
                "ticket_subject",
                "ticket_body",
                "requester_email",
                "requester_name",
            ],
        },
        "update_ticket**(*)**(*)": {
            "inputs": [
                {
                    "field": "ticket_id",
                    "type": "string",
                    "value": "",
                    "helper_text": "The ID of Zendesk ticket to update",
                    "label": "Ticket ID",
                    "placeholder": "123",
                },
                {
                    "field": "update_ticket_subject",
                    "type": "string",
                    "value": "",
                    "helper_text": "Subject content of the ticket",
                    "label": "Subject",
                    "placeholder": "Incident report",
                },
                {
                    "field": "update_ticket_body",
                    "type": "string",
                    "value": "",
                    "helper_text": "Body content of the ticket",
                    "label": "Body",
                    "placeholder": "Clicking on submit button not working",
                },
                {
                    "field": "update_ticket_assignee_id",
                    "type": "string",
                    "value": "",
                    "helper_text": "The ID of the assignee to update the ticket to",
                    "label": "Assignee ID",
                    "placeholder": "1234",
                },
                {
                    "field": "ticket_priority",
                    "type": "enum<string>",
                    "value": "",
                    "helper_text": "Priority of the ticket",
                    "label": "Priority",
                    "placeholder": "High",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "options": [
                            {"label": "Low", "value": "Low"},
                            {"label": "Normal", "value": "Normal"},
                            {"label": "High", "value": "High"},
                            {"label": "Urgent", "value": "Urgent"},
                        ],
                    },
                },
                {
                    "field": "ticket_type",
                    "type": "enum<string>",
                    "value": "",
                    "helper_text": "Type of the ticket",
                    "label": "Type",
                    "placeholder": "Incident",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "options": [
                            {"label": "Question", "value": "Question"},
                            {"label": "Incident", "value": "Incident"},
                            {"label": "Problem", "value": "Problem"},
                            {"label": "Task", "value": "Task"},
                        ],
                    },
                },
                {
                    "field": "ticket_status",
                    "type": "enum<string>",
                    "value": "",
                    "helper_text": "Status of the ticket",
                    "label": "Status",
                    "placeholder": "Open",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "options": [
                            {"label": "New", "value": "New"},
                            {"label": "Open", "value": "Open"},
                            {"label": "Pending", "value": "Pending"},
                            {"label": "Hold", "value": "Hold"},
                            {"label": "Solved", "value": "Solved"},
                            {"label": "Closed", "value": "Closed"},
                        ],
                    },
                },
            ],
            "outputs": [
                {
                    "field": "ticket_details",
                    "type": "string",
                    "helper_text": "Ticket details in JSON format",
                }
            ],
            "variant": "common_integration_nodes",
            "name": "update_ticket",
            "task_name": "tasks.zendesk.update_ticket",
            "description": "Update an existing ticket on Zendesk",
            "label": "Update Ticket",
            "inputs_sort_order": [
                "integration",
                "action",
                "ticket_priority",
                "ticket_type",
                "ticket_status",
                "ticket_id",
                "update_ticket_subject",
                "update_ticket_body",
                "update_ticket_assignee_id",
            ],
        },
        "create_comment**(*)**(*)": {
            "inputs": [
                {
                    "field": "ticket_id",
                    "type": "string",
                    "value": "",
                    "helper_text": "The ID of Zendesk ticket to add comment to",
                    "label": "Ticket ID",
                    "placeholder": "123",
                },
                {
                    "field": "ticket_body",
                    "type": "string",
                    "value": "",
                    "helper_text": "Content of the comment",
                    "label": "Comment Body",
                    "placeholder": "Clicking on submit button not working",
                },
                {
                    "field": "public",
                    "type": "bool",
                    "value": True,
                    "helper_text": "Whether the comment should be public",
                    "label": "Public",
                },
            ],
            "outputs": [
                {
                    "field": "ticket_details",
                    "type": "string",
                    "helper_text": "Ticket details in JSON format",
                }
            ],
            "name": "create_comment",
            "task_name": "tasks.zendesk.create_comment",
            "description": "Create a new comment on a Zendesk ticket",
            "label": "Create Comment",
            "variant": "default_integration_nodes",
            "inputs_sort_order": [
                "integration",
                "action",
                "ticket_id",
                "ticket_body",
                "public",
            ],
        },
        "read_ticket**(*)**(*)": {
            "inputs": [
                {
                    "field": "ticket_id",
                    "type": "string",
                    "value": "",
                    "helper_text": "The ID of Zendesk ticket to read",
                    "label": "Ticket ID",
                    "placeholder": "123",
                }
            ],
            "outputs": [
                {
                    "field": "ticket_subject",
                    "type": "string",
                    "helper_text": "Subject of the ticket",
                },
                {
                    "field": "ticket_body",
                    "type": "vec<string>",
                    "helper_text": "Body of the ticket",
                },
                {
                    "field": "created_at",
                    "type": "string",
                    "helper_text": "Date and time the ticket was created",
                },
                {
                    "field": "updated_at",
                    "type": "string",
                    "helper_text": "Date and time the ticket was last updated",
                },
                {
                    "field": "ticket_priority",
                    "type": "string",
                    "helper_text": "Priority of the ticket",
                },
                {
                    "field": "ticket_type",
                    "type": "string",
                    "helper_text": "Type of the ticket",
                },
                {
                    "field": "ticket_status",
                    "type": "string",
                    "helper_text": "Status of the ticket",
                },
                {
                    "field": "ticket_url",
                    "type": "string",
                    "helper_text": "URL of the ticket",
                },
                {
                    "field": "ticket_attachments",
                    "type": "vec<file>",
                    "helper_text": "Attachments of the ticket",
                },
                {
                    "field": "ticket_assignee_id",
                    "type": "string",
                    "helper_text": "ID of ticket assignee",
                },
                {
                    "field": "ticket_requester_id",
                    "type": "string",
                    "helper_text": "ID of ticket requester",
                },
                {
                    "field": "ticket_details",
                    "type": "string",
                    "helper_text": "Ticket details in JSON format",
                },
            ],
            "name": "read_ticket",
            "task_name": "tasks.zendesk.read_ticket",
            "description": "Read an existing ticket on Zendesk",
            "label": "Read Ticket",
            "variant": "default_integration_nodes",
            "inputs_sort_order": ["integration", "action", "ticket_id"],
        },
        "read_ticket_comments**(*)**(*)": {
            "inputs": [
                {
                    "field": "ticket_id",
                    "type": "string",
                    "value": "",
                    "helper_text": "ID of Zendesk ticket to read comments from",
                    "label": "Ticket ID",
                    "placeholder": "123",
                }
            ],
            "outputs": [
                {
                    "field": "ticket_comments",
                    "type": "vec<string>",
                    "helper_text": "Ticket comments in JSON format",
                },
                {
                    "field": "ticket_attachments",
                    "type": "vec<file>",
                    "helper_text": "Attachments of the ticket",
                },
                {
                    "field": "ticket_details",
                    "type": "string",
                    "helper_text": "Ticket details in JSON format",
                },
            ],
            "name": "read_ticket_comments",
            "task_name": "tasks.zendesk.read_ticket_comments",
            "description": "Read comments from an existing ticket on Zendesk",
            "label": "Read Ticket Comments",
            "variant": "default_integration_nodes",
            "inputs_sort_order": ["integration", "action", "ticket_id"],
        },
        "get_tickets**(*)**(*)": {
            "inputs": [
                {
                    "field": "use_date",
                    "type": "bool",
                    "value": False,
                    "show_date_range": True,
                    "label": "Use Date",
                    "helper_text": "Toggle to use dates",
                },
                {
                    "field": "assignee",
                    "type": "string",
                    "value": "",
                    "label": "Assignee",
                    "helper_text": "Assignee of the ticket",
                    "placeholder": "John Smith",
                },
                {
                    "field": "requester",
                    "type": "string",
                    "value": "",
                    "label": "Requester",
                    "helper_text": "Requester of the ticket",
                    "placeholder": "John Smith",
                },
                {
                    "field": "organization",
                    "type": "string",
                    "value": "",
                    "label": "Organization",
                    "helper_text": "Organization of the ticket",
                    "placeholder": "Acme Corp",
                },
                {
                    "field": "priority",
                    "type": "enum<string>",
                    "value": "",
                    "hidden": True,
                    "helper_text": "Priority of the ticket",
                    "label": "Priority",
                    "placeholder": "High",
                    "component": {
                        "type": "dropdown",
                        "options": [
                            {"label": "Low", "value": "Low"},
                            {"label": "Normal", "value": "Normal"},
                            {"label": "High", "value": "High"},
                            {"label": "Urgent", "value": "Urgent"},
                        ],
                    },
                },
                {
                    "field": "ticket_type",
                    "type": "enum<string>",
                    "value": "",
                    "hidden": True,
                    "helper_text": "Type of the ticket",
                    "label": "Type",
                    "placeholder": "Incident",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "options": [
                            {"label": "Question", "value": "Question"},
                            {"label": "Incident", "value": "Incident"},
                            {"label": "Problem", "value": "Problem"},
                            {"label": "Task", "value": "Task"},
                        ],
                    },
                },
                {
                    "field": "status",
                    "type": "enum<string>",
                    "value": "",
                    "hidden": True,
                    "helper_text": "Status of the ticket",
                    "label": "Status",
                    "placeholder": "Open",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "options": [
                            {"label": "New", "value": "New"},
                            {"label": "Open", "value": "Open"},
                            {"label": "Pending", "value": "Pending"},
                            {"label": "Hold", "value": "Hold"},
                            {"label": "Solved", "value": "Solved"},
                            {"label": "Closed", "value": "Closed"},
                        ],
                    },
                },
                {
                    "field": "subject",
                    "type": "string",
                    "value": "",
                    "label": "Subject",
                    "helper_text": "Search tickets by subject",
                    "placeholder": "Incident report",
                },
                {
                    "field": "subject_exact",
                    "type": "string",
                    "value": "",
                    "label": "Subject Exact",
                    "helper_text": "Match subject exactly",
                    "placeholder": "Incident report",
                },
                {
                    "field": "description",
                    "type": "string",
                    "value": "",
                    "label": "Description",
                    "helper_text": "Search in the ticket description",
                    "placeholder": "Clicking on submit button doesn't work",
                },
                {
                    "field": "body",
                    "type": "string",
                    "value": "",
                    "label": "Body",
                    "helper_text": "Search in the full ticket content",
                    "placeholder": "Clicking on submit button doesn't work",
                },
                {
                    "field": "comment",
                    "type": "string",
                    "value": "",
                    "label": "Comment",
                    "helper_text": "Search in ticket comments",
                    "placeholder": "Clicking on submit button doesn't work",
                },
                {
                    "field": "comment_exact",
                    "type": "string",
                    "value": "",
                    "label": "Comment Exact",
                    "helper_text": "Match comment exactly",
                    "placeholder": "Clicking on submit button doesn't work",
                },
                {
                    "field": "updated",
                    "type": "string",
                    "value": "",
                    "label": "Updated Date",
                    "helper_text": "Tickets updated on this date",
                    "placeholder": "YYYY-MM-DD",
                },
                {
                    "field": "solved",
                    "type": "string",
                    "value": "",
                    "label": "Solved Date",
                    "helper_text": "Tickets solved on this date",
                    "placeholder": "YYYY-MM-DD",
                },
                {
                    "field": "due",
                    "type": "string",
                    "value": "",
                    "label": "Due Date",
                    "helper_text": "Tickets due on this date",
                    "placeholder": "YYYY-MM-DD",
                },
                {
                    "field": "brand",
                    "type": "string",
                    "value": "",
                    "label": "Brand",
                    "helper_text": "Filter by brand",
                    "placeholder": "Acme Corp",
                },
                {
                    "field": "satisfaction",
                    "type": "enum<string>",
                    "value": "",
                    "hidden": True,
                    "helper_text": "Customer satisfaction rating",
                    "label": "Satisfaction",
                    "placeholder": "Good",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "options": [
                            {"label": "Good", "value": "good"},
                            {"label": "Bad", "value": "bad"},
                            {"label": "Offered", "value": "offered"},
                        ],
                    },
                },
                {
                    "field": "ticket_form",
                    "type": "string",
                    "value": "",
                    "label": "Ticket Form",
                    "helper_text": "Filter by ticket form",
                    "placeholder": "Support",
                },
                {
                    "field": "group",
                    "type": "string",
                    "value": "",
                    "label": "Group",
                    "helper_text": "Filter by assigned group",
                    "placeholder": "Support",
                },
                {
                    "field": "sort_by",
                    "type": "string",
                    "value": "",
                    "label": "Sort By",
                    "helper_text": "Field to sort results by",
                    "placeholder": "created_at",
                },
                {
                    "field": "sort_order",
                    "type": "string",
                    "value": "",
                    "label": "Sort Order",
                    "helper_text": "Order of sorting (asc/desc)",
                    "placeholder": "desc",
                },
                {
                    "field": "external_id",
                    "type": "string",
                    "value": "",
                    "label": "External ID",
                    "helper_text": "Search by external ID",
                    "placeholder": "123",
                },
                {
                    "field": "include",
                    "type": "string",
                    "value": "",
                    "label": "Include",
                    "helper_text": "Include related data (e.g. users)",
                    "placeholder": "users,groups,organizations",
                },
            ],
            "outputs": [
                {
                    "field": "ticket_id",
                    "type": "vec<string>",
                    "helper_text": "ID of the tickets",
                },
                {
                    "field": "ticket_subject",
                    "type": "vec<string>",
                    "helper_text": "Subject of the tickets",
                },
                {
                    "field": "ticket_body",
                    "type": "vec<string>",
                    "helper_text": "Body of the tickets",
                },
                {
                    "field": "created_at",
                    "type": "vec<string>",
                    "helper_text": "Date and time the tickets was created",
                },
                {
                    "field": "updated_at",
                    "type": "vec<string>",
                    "helper_text": "Date and time the tickets was last updated",
                },
                {
                    "field": "ticket_priority",
                    "type": "vec<string>",
                    "helper_text": "Priority of the tickets",
                },
                {
                    "field": "ticket_type",
                    "type": "vec<string>",
                    "helper_text": "Type of the tickets",
                },
                {
                    "field": "ticket_status",
                    "type": "vec<string>",
                    "helper_text": "Status of the tickets",
                },
                {
                    "field": "ticket_url",
                    "type": "vec<string>",
                    "helper_text": "URL of the tickets",
                },
                {
                    "field": "ticket_attachments",
                    "type": "vec<vec<file>>",
                    "helper_text": "Attachments of the tickets",
                },
                {
                    "field": "ticket_assignee_id",
                    "type": "vec<string>",
                    "helper_text": "ID of tickets assignee",
                },
                {
                    "field": "ticket_requester_id",
                    "type": "vec<string>",
                    "helper_text": "ID of tickets requester",
                },
                {
                    "field": "ticket_details",
                    "type": "string",
                    "helper_text": "Tickets details in JSON format",
                },
            ],
            "variant": "get_integration_nodes",
            "name": "get_tickets",
            "task_name": "tasks.zendesk.get_tickets",
            "description": "Get a list of tickets from Zendesk",
            "label": "Get Tickets",
            "inputs_sort_order": [
                "integration",
                "action",
                "use_date",
                "use_exact_date",
                "date_range",
                "exact_date",
                "num_messages",
                "ticket_subject",
                "ticket_body",
                "requester_email",
                "requester_name",
                "ticket_priority",
                "ticket_type",
                "ticket_status",
                "assignee",
                "requester",
                "organization",
                "subject",
                "subject_exact",
                "description",
                "body",
                "comment",
                "comment_exact",
                "updated",
                "solved",
                "due",
                "brand",
                "satisfaction",
                "ticket_form",
                "group",
                "sort_by",
                "sort_order",
                "external_id",
                "include",
            ],
        },
        "get_tickets**false**(*)": {
            "inputs": [
                {
                    "field": "num_messages",
                    "type": "int32",
                    "value": 10,
                    "show_date_range": True,
                    "label": "Number of Tickets",
                    "helper_text": "Specify the number of tickets to fetch",
                }
            ],
            "outputs": [],
        },
        "get_tickets**true**(*)": {
            "inputs": [
                {
                    "field": "use_exact_date",
                    "type": "bool",
                    "value": False,
                    "show_date_range": True,
                    "label": "Use Exact Date",
                    "helper_text": "Switch between exact date range and relative dates",
                }
            ],
            "outputs": [],
        },
        "get_tickets**true**false": {
            "inputs": [
                {
                    "field": "date_range",
                    "type": "Dict[str, Any]",
                    "label": "Date Range",
                    "value": {
                        "date_type": "Last",
                        "date_value": 1,
                        "date_period": "Months",
                    },
                    "show_date_range": True,
                }
            ],
            "outputs": [],
        },
        "get_tickets**true**true": {
            "inputs": [
                {
                    "field": "exact_date",
                    "type": "Dict[str, Any]",
                    "label": "Exact date",
                    "value": {"start": "", "end": ""},
                    "show_date_range": True,
                }
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["action", "use_date", "use_exact_date"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Zendesk",
        satisfaction: str | ToolInput = "",
        status: str | ToolInput = "",
        ticket_priority: str | ToolInput = "",
        ticket_status: str | ToolInput = "",
        ticket_type: str | ToolInput = "",
        action: str | ToolInput = "",
        use_date: bool | ToolInput = False,
        use_exact_date: bool | ToolInput = False,
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action
        if isinstance(use_date, ToolInput):
            if use_date.type == "static":
                params["use_date"] = use_date.value
            else:
                raise ValueError(f"use_date cannot be a dynamic input")
        else:
            params["use_date"] = use_date
        if isinstance(use_exact_date, ToolInput):
            if use_exact_date.type == "static":
                params["use_exact_date"] = use_exact_date.value
            else:
                raise ValueError(f"use_exact_date cannot be a dynamic input")
        else:
            params["use_exact_date"] = use_exact_date

        super().__init__(
            tool_type="integration_zendesk",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if satisfaction is not None:
            if isinstance(satisfaction, ToolInput):
                self.inputs["satisfaction"] = {
                    "type": satisfaction.type,
                    "value": satisfaction.value or satisfaction.description,
                }
            else:
                self.inputs["satisfaction"] = {"type": "static", "value": satisfaction}
        if status is not None:
            if isinstance(status, ToolInput):
                self.inputs["status"] = {
                    "type": status.type,
                    "value": status.value or status.description,
                }
            else:
                self.inputs["status"] = {"type": "static", "value": status}
        if ticket_priority is not None:
            if isinstance(ticket_priority, ToolInput):
                self.inputs["ticket_priority"] = {
                    "type": ticket_priority.type,
                    "value": ticket_priority.value or ticket_priority.description,
                }
            else:
                self.inputs["ticket_priority"] = {
                    "type": "static",
                    "value": ticket_priority,
                }
        if ticket_status is not None:
            if isinstance(ticket_status, ToolInput):
                self.inputs["ticket_status"] = {
                    "type": ticket_status.type,
                    "value": ticket_status.value or ticket_status.description,
                }
            else:
                self.inputs["ticket_status"] = {
                    "type": "static",
                    "value": ticket_status,
                }
        if ticket_type is not None:
            if isinstance(ticket_type, ToolInput):
                self.inputs["ticket_type"] = {
                    "type": ticket_type.type,
                    "value": ticket_type.value or ticket_type.description,
                }
            else:
                self.inputs["ticket_type"] = {"type": "static", "value": ticket_type}
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}
        if use_date is not None:
            if isinstance(use_date, ToolInput):
                self.inputs["use_date"] = {
                    "type": use_date.type,
                    "value": use_date.value or use_date.description,
                }
            else:
                self.inputs["use_date"] = {"type": "static", "value": use_date}
        if use_exact_date is not None:
            if isinstance(use_exact_date, ToolInput):
                self.inputs["use_exact_date"] = {
                    "type": use_exact_date.type,
                    "value": use_exact_date.value or use_exact_date.description,
                }
            else:
                self.inputs["use_exact_date"] = {
                    "type": "static",
                    "value": use_exact_date,
                }

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationZendeskTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_teams")
class IntegrationTeamsTool(Tool):
    """
    Teams

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### send_message
        channel_name: The name of the channel in the specified team
        message: The message you want to send
        team_name: The name of the team
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Teams>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "send_message": {
            "inputs": [
                {
                    "field": "team_name",
                    "type": "string",
                    "value": "",
                    "label": "Team",
                    "placeholder": "Vectorshift",
                    "helper_text": "The name of the team",
                    "agent_field_type": "static",
                },
                {
                    "field": "channel_name",
                    "type": "string",
                    "value": "",
                    "label": "Channel",
                    "placeholder": "General",
                    "helper_text": "The name of the channel in the specified team",
                    "agent_field_type": "static",
                },
                {
                    "field": "message",
                    "type": "string",
                    "value": "",
                    "label": "Message",
                    "placeholder": "Hello World!",
                    "helper_text": "The message you want to send",
                },
            ],
            "outputs": [],
            "name": "send_message",
            "task_name": "teams.create_message",
            "description": "Post a new message to a specific teams channel",
            "label": "Send Message",
            "variant": "default_integration_nodes",
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Teams",
        channel_name: str | ToolInput = "",
        team_name: str | ToolInput = "",
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_teams",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if channel_name is not None:
            if isinstance(channel_name, ToolInput):
                self.inputs["channel_name"] = {
                    "type": channel_name.type,
                    "value": channel_name.value or channel_name.description,
                }
            else:
                self.inputs["channel_name"] = {"type": "static", "value": channel_name}
        if team_name is not None:
            if isinstance(team_name, ToolInput):
                self.inputs["team_name"] = {
                    "type": team_name.type,
                    "value": team_name.value or team_name.description,
                }
            else:
                self.inputs["team_name"] = {"type": "static", "value": team_name}
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationTeamsTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_x")
class IntegrationXTool(Tool):
    """
    X

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### create_post
        text: The text of the post
    ### create_thread
        text: The text of the post
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<X>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "(*)": {"inputs": [], "outputs": [], "variant": "default_integration_nodes"},
        "create_post": {
            "inputs": [
                {
                    "field": "text",
                    "type": "string",
                    "value": "",
                    "label": "Text",
                    "placeholder": "Hello World!",
                    "helper_text": "The text of the post",
                }
            ],
            "outputs": [
                {
                    "field": "post_url",
                    "type": "string",
                    "helper_text": "URL of the created post",
                }
            ],
            "name": "create_post",
            "task_name": "tasks.x.create_post",
            "description": "Create a new post on X",
            "label": "Create Post",
        },
        "create_thread": {
            "inputs": [
                {
                    "field": "text",
                    "type": "string",
                    "value": "",
                    "label": "Text",
                    "placeholder": '["Post1", "Post2", "Post3"]',
                    "helper_text": "A list of text to be posted as a thread",
                }
            ],
            "outputs": [
                {
                    "field": "post_url",
                    "type": "string",
                    "helper_text": "URL of the created thread",
                }
            ],
            "name": "create_thread",
            "task_name": "tasks.x.create_thread",
            "description": "Create a new thread on X",
            "label": "Create Thread",
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "X",
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_x",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationXTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_gohighlevel")
class IntegrationGohighlevelTool(Tool):
    """
    GoHighLevel

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### create_opportunity
        contact_name: Name of the existing contact to link to the opportunity. One contact can only be linked to one opportunity.
        name: Name of the opportunity
        pipeline_name: Name of the existing pipeline to link to the opportunity
        status: Status of the opportunity (must be one of: 'open', 'won', 'lost', 'abandoned')
        value: Money value of the opportunity
    ### create_contact
        email: Email address of the contact
        first_name: First name of the contact
        last_name: Last name of the contact
        phone: Phone number of the contact
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<GoHighLevel>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "(*)": {"inputs": [], "outputs": [], "variant": "default_integration_nodes"},
        "create_contact": {
            "inputs": [
                {
                    "field": "first_name",
                    "type": "string",
                    "value": "",
                    "label": "First Name",
                    "placeholder": "John",
                    "helper_text": "First name of the contact",
                },
                {
                    "field": "last_name",
                    "type": "string",
                    "value": "",
                    "label": "Last Name",
                    "placeholder": "Doe",
                    "helper_text": "Last name of the contact",
                },
                {
                    "field": "email",
                    "type": "string",
                    "value": "",
                    "label": "Email",
                    "placeholder": "john@doe.com",
                    "helper_text": "Email address of the contact",
                },
                {
                    "field": "phone",
                    "type": "string",
                    "value": "",
                    "label": "Phone",
                    "placeholder": "+1 888-888-8888",
                    "helper_text": "Phone number of the contact",
                },
            ],
            "outputs": [],
            "name": "create_contact",
            "task_name": "tasks.gohighlevel.create_contact",
            "description": "Create a new contact on GoHighLevel",
            "label": "Create Contact",
        },
        "create_opportunity": {
            "inputs": [
                {
                    "field": "name",
                    "type": "string",
                    "value": "",
                    "label": "Name",
                    "placeholder": "First op",
                    "helper_text": "Name of the opportunity",
                },
                {
                    "field": "status",
                    "type": "string",
                    "value": "",
                    "label": "Status",
                    "placeholder": "open",
                    "helper_text": "Status of the opportunity (must be one of: 'open', 'won', 'lost', 'abandoned')",
                },
                {
                    "field": "value",
                    "type": "string",
                    "value": "",
                    "label": "Value",
                    "placeholder": "500",
                    "helper_text": "Money value of the opportunity",
                },
                {
                    "field": "pipeline_name",
                    "type": "string",
                    "value": "",
                    "label": "Pipeline Name",
                    "placeholder": "onboarding",
                    "helper_text": "Name of the existing pipeline to link to the opportunity",
                },
                {
                    "field": "contact_name",
                    "type": "string",
                    "value": "",
                    "label": "Contact Name",
                    "placeholder": "John",
                    "helper_text": "Name of the existing contact to link to the opportunity. One contact can only be linked to one opportunity.",
                },
            ],
            "outputs": [],
            "name": "create_opportunity",
            "task_name": "tasks.gohighlevel.create_opportunity",
            "description": "Create a new opportunity on GoHighLevel",
            "label": "Create Opportunity",
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "GoHighLevel",
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_gohighlevel",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationGohighlevelTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_peopledatalabs")
class IntegrationPeopledatalabsTool(Tool):
    """
    PeopleDataLabs

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### enrich_person
        company: The name, website, or social URL of a company where the person has worked
        email: Email address of the person
        first_name: First name of the person
        last_name: Last name of the person
        location: The location where a person lives (can be address, city, country, etc.)
        profile_url: Social media profile URLs for the contact (LinkedIn, Twitter, Facebook, etc.)
    ### search_companies
        company_size_ranges: Comma-separated list of company size ranges. The value should be one of the ones mentioned here: https://docs.peopledatalabs.com/docs/company-sizes
        country: Name of the country
        founded_year_range: A range representing the founding year of the company
        industries: Comma-separated list of industries
        number_of_results: Number of results to return
        tags: Comma-separated tags associated with the company
    ### search_people
        country: Name of the country
        job_company_names: Comma-separated list of company names to search within
        job_titles: Comma-separated list of job titles
        number_of_results: Number of results to return
        skills: Comma-separated list of skills to search for
    ### search_people_query
        es_query: A valid Elasticsearch query. Available Fields: https://docs.peopledatalabs.com/docs/elasticsearch-mapping
        number_of_results: Number of results to return
        sql: A valid SQL query
    ### search_companies_query
        es_query: A valid Elasticsearch query. Available Fields: https://docs.peopledatalabs.com/docs/elasticsearch-mapping
        number_of_results: Number of results to return
        sql: A valid SQL query
    ### enrich_company
        name: The name of the company
        profile: Company social media profile URL
        website: Company website URL
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<PeopleDataLabs>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "(*)": {"inputs": [], "outputs": [], "variant": "default_integration_nodes"},
        "enrich_person": {
            "inputs": [
                {
                    "field": "first_name",
                    "type": "string",
                    "value": "",
                    "label": "First Name",
                    "placeholder": "John",
                    "helper_text": "First name of the person",
                },
                {
                    "field": "last_name",
                    "type": "string",
                    "value": "",
                    "label": "Last Name",
                    "placeholder": "Doe",
                    "helper_text": "Last name of the person",
                },
                {
                    "field": "location",
                    "type": "string",
                    "value": "",
                    "label": "Location",
                    "placeholder": "San Francisco, CA",
                    "helper_text": "The location where a person lives (can be address, city, country, etc.)",
                },
                {
                    "field": "email",
                    "type": "string",
                    "value": "",
                    "label": "Email",
                    "placeholder": "john@doe.com",
                    "helper_text": "Email address of the person",
                },
                {
                    "field": "company",
                    "type": "string",
                    "value": "",
                    "label": "Company",
                    "placeholder": "Acme Corp",
                    "helper_text": "The name, website, or social URL of a company where the person has worked",
                },
                {
                    "field": "profile_url",
                    "type": "string",
                    "value": "",
                    "label": "Profile URL",
                    "placeholder": "linkedin.com/in/johnsmith",
                    "helper_text": "Social media profile URLs for the contact (LinkedIn, Twitter, Facebook, etc.)",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "Enriched person data including additional information found",
                }
            ],
            "name": "enrich_person",
            "task_name": "tasks.peopledatalabs.enrich_person",
            "description": "Enrich Person",
            "label": "Enrich Person",
        },
        "search_people": {
            "inputs": [
                {
                    "field": "country",
                    "type": "string",
                    "value": "",
                    "label": "Country",
                    "placeholder": "US",
                    "helper_text": "Name of the country",
                },
                {
                    "field": "job_titles",
                    "type": "string",
                    "value": "",
                    "label": "Job Titles",
                    "placeholder": "Software Engineer, Product Manager, CTO",
                    "helper_text": "Comma-separated list of job titles",
                },
                {
                    "field": "job_company_names",
                    "type": "string",
                    "value": "",
                    "label": "Job Company Names",
                    "placeholder": "Google, Microsoft, Apple",
                    "helper_text": "Comma-separated list of company names to search within",
                },
                {
                    "field": "skills",
                    "type": "string",
                    "value": "",
                    "label": "Skills",
                    "placeholder": "Python, Machine Learning, Leadership",
                    "helper_text": "Comma-separated list of skills to search for",
                },
                {
                    "field": "number_of_results",
                    "type": "string",
                    "value": "",
                    "label": "Number of Results",
                    "placeholder": "10",
                    "helper_text": "Number of results to return",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "List of matching people profiles",
                }
            ],
            "name": "search_people",
            "task_name": "tasks.peopledatalabs.search_people",
            "description": "Search People",
            "label": "Search People",
        },
        "search_people_query": {
            "inputs": [
                {
                    "field": "es_query",
                    "type": "string",
                    "value": "",
                    "label": "ES Query",
                    "placeholder": '{"query": {"match_all": {}}}',
                    "helper_text": "A valid Elasticsearch query. Available Fields: https://docs.peopledatalabs.com/docs/elasticsearch-mapping",
                },
                {
                    "field": "sql",
                    "type": "string",
                    "value": "",
                    "label": "SQL",
                    "placeholder": '{"query": {"match": {"job_title": "Software Engineer"}}}',
                    "helper_text": "A valid SQL query",
                },
                {
                    "field": "number_of_results",
                    "type": "string",
                    "value": "",
                    "label": "Number of Results",
                    "placeholder": "10",
                    "helper_text": "Number of results to return",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "List of matching people profiles",
                }
            ],
            "name": "search_people_query",
            "task_name": "tasks.peopledatalabs.search_people_query",
            "description": "Search People (query)",
            "label": "Search People (query)",
        },
        "enrich_company": {
            "inputs": [
                {
                    "field": "name",
                    "type": "string",
                    "value": "",
                    "label": "Name",
                    "placeholder": "Acme Corp",
                    "helper_text": "The name of the company",
                },
                {
                    "field": "profile",
                    "type": "string",
                    "value": "",
                    "label": "Profile",
                    "placeholder": "linkedin.com/company/acme-corp",
                    "helper_text": "Company social media profile URL",
                },
                {
                    "field": "website",
                    "type": "string",
                    "value": "",
                    "label": "Website",
                    "placeholder": "www.acmecorp.com",
                    "helper_text": "Company website URL",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "Enriched company data including additional information found",
                }
            ],
            "name": "enrich_company",
            "task_name": "tasks.peopledatalabs.enrich_company",
            "description": "Enrich Company",
            "label": "Enrich Company",
        },
        "search_companies": {
            "inputs": [
                {
                    "field": "tags",
                    "type": "string",
                    "value": "",
                    "label": "Tags",
                    "placeholder": "B2B, SaaS, Fintech",
                    "helper_text": "Comma-separated tags associated with the company",
                },
                {
                    "field": "industries",
                    "type": "string",
                    "value": "",
                    "label": "Industries",
                    "placeholder": "Technology, Healthcare, Finance",
                    "helper_text": "Comma-separated list of industries",
                },
                {
                    "field": "company_size_ranges",
                    "type": "string",
                    "value": "",
                    "label": "Company Size Ranges",
                    "placeholder": "1-10, 11-50, 51-200, 201-500, 501-1000, 1000+",
                    "helper_text": "Comma-separated list of company size ranges. The value should be one of the ones mentioned here: https://docs.peopledatalabs.com/docs/company-sizes",
                },
                {
                    "field": "founded_year_range",
                    "type": "string",
                    "value": "",
                    "label": "Founded Year Range",
                    "placeholder": "2015-2020",
                    "helper_text": "A range representing the founding year of the company",
                },
                {
                    "field": "country",
                    "type": "string",
                    "value": "",
                    "label": "Country",
                    "placeholder": "US",
                    "helper_text": "Name of the country",
                },
                {
                    "field": "number_of_results",
                    "type": "string",
                    "value": "",
                    "label": "Number of Results",
                    "placeholder": "10",
                    "helper_text": "Number of results to return",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "List of matching company profiles",
                }
            ],
            "name": "search_companies",
            "task_name": "tasks.peopledatalabs.search_companies",
            "description": "Search Companies",
            "label": "Search Companies",
        },
        "search_companies_query": {
            "inputs": [
                {
                    "field": "es_query",
                    "type": "string",
                    "value": "",
                    "label": "Elastic Search Query",
                    "placeholder": '{"query": {"match_all": {}}}',
                    "helper_text": "A valid Elasticsearch query. Available fields: https://docs.peopledatalabs.com/docs/elasticsearch-mapping-company",
                },
                {
                    "field": "sql",
                    "type": "string",
                    "value": "",
                    "label": "SQL Query",
                    "placeholder": "SELECT * FROM companies WHERE industry = 'Technology'",
                    "helper_text": "A valid SQL Query. Available fields: https://docs.peopledatalabs.com/docs/company-schema",
                },
                {
                    "field": "number_of_results",
                    "type": "int32",
                    "value": 10,
                    "label": "Number of Results",
                    "placeholder": "10",
                    "helper_text": "Number of results to display",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "List of matching company profiles",
                }
            ],
            "name": "search_companies_query",
            "task_name": "tasks.peopledatalabs.search_companies_query",
            "description": "Search Companies (query)",
            "label": "Search Companies (query)",
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "PeopleDataLabs",
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_peopledatalabs",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationPeopledatalabsTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_hubspot")
class IntegrationHubspotTool(Tool):
    """
    Hubspot

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### create_deal
        amount: Deal amount
        associated_object_id: The ID of the associated object
        associated_object_type: The type of the associated object
        closedate: Expected close date
        dealname: Name of the deal
        dealstage: Stage of the deal
        item_type: The item_type input
        pipeline: Deal pipeline
    ### create_company
        associated_object_id: The ID of the associated object
        associated_object_type: The type of the associated object
        city: Company city location
        domain: The domain of the company
        industry: Company industry
        item_type: The item_type input
        name: The name of the company
        phone: Company phone number'
        state: Company state location
    ### create_contact
        associated_object_id: The ID of the associated object
        associated_object_type: The type of the associated object
        company: Contact company name
        email: Contact email address
        firstname: Contact first name
        item_type: The item_type input
        lastname: Contact last name
        phone: Company phone number'
        website: Contact website
    ### create_ticket
        associated_object_id: The ID of the associated object
        associated_object_type: The type of the associated object
        hs_pipeline: Ticket pipeline
        hs_pipeline_stage: Stage in the pipeline
        hs_ticket_priority: Ticket priority level
        item_type: The item_type input
        subject: Ticket subject
    ### create_note
        associated_object_id: The ID of the associated object
        associated_object_type: The type of the associated object
        body: Content of the note
        item_type: The item_type input
    ### create_call
        associated_object_id: The ID of the associated object
        associated_object_type: The type of the associated object
        body: Content of the note
        duration: Call duration in seconds
        from_number: Caller phone number
        item_type: The item_type input
        title: Title of the call
        to_number: Recipient phone number
    ### create_task
        associated_object_id: The ID of the associated object
        associated_object_type: The type of the associated object
        body: Content of the note
        item_type: The item_type input
        priority: Task priority level
        status: Current status of the task
        subject: Ticket subject
    ### create_meeting
        associated_object_id: The ID of the associated object
        associated_object_type: The type of the associated object
        body: Content of the note
        end_time: Meeting end time
        item_type: The item_type input
        meeting_notes: Notes from the meeting
        start_time: Meeting start time
        title: Title of the call
    ### create_email
        associated_object_id: The ID of the associated object
        associated_object_type: The type of the associated object
        direction: Direction of the email (INCOMING/OUTGOING)
        item_type: The item_type input
        recipient_email: Email address of the recipient
        sender_email: Email address of the sender
        subject: Ticket subject
        text: Email body content
    ### fetch_contacts
        item_type: The item_type input
        query: Valid Hubspot Search Query - See API docs for format
    ### fetch_companies
        item_type: The item_type input
        query: Valid Hubspot Search Query - See API docs for format
    ### fetch_deals
        item_type: The item_type input
        query: Valid Hubspot Search Query - See API docs for format
    ### fetch_tickets
        item_type: The item_type input
        query: Valid Hubspot Search Query - See API docs for format
    ### fetch_notes
        item_type: The item_type input
        query: Valid Hubspot Search Query - See API docs for format
    ### fetch_calls
        item_type: The item_type input
        query: Valid Hubspot Search Query - See API docs for format
    ### fetch_tasks
        item_type: The item_type input
        query: Valid Hubspot Search Query - See API docs for format
    ### fetch_meetings
        item_type: The item_type input
        query: Valid Hubspot Search Query - See API docs for format
    ### fetch_emails
        item_type: The item_type input
        query: Valid Hubspot Search Query - See API docs for format
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Hubspot>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "(*)": {"inputs": [], "outputs": [], "variant": "default_integration_nodes"},
        "fetch_contacts": {
            "inputs": [
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "Query (JSON)",
                    "placeholder": "",
                    "helper_text": "Valid Hubspot Search Query - See API docs for format",
                },
                {
                    "field": "item_type",
                    "type": "string",
                    "value": "contact",
                    "label": "",
                    "placeholder": "",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "List of matched contacts",
                }
            ],
            "name": "fetch_contacts",
            "task_name": "tasks.hubspot.fetch_items",
            "description": "Fetch contacts from Hubspot CRM",
            "label": "Fetch Contacts",
        },
        "fetch_companies": {
            "inputs": [
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "Query (JSON)",
                    "placeholder": "",
                    "helper_text": "Valid Hubspot Search Query - See API docs for format",
                },
                {
                    "field": "item_type",
                    "type": "string",
                    "value": "company",
                    "label": "",
                    "placeholder": "",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "List of matched companies",
                }
            ],
            "name": "fetch_companies",
            "task_name": "tasks.hubspot.fetch_items",
            "description": "Fetch companies from Hubspot CRM",
            "label": "Fetch Companies",
        },
        "fetch_deals": {
            "inputs": [
                {
                    "field": "item_type",
                    "type": "string",
                    "value": "deal",
                    "label": "",
                    "placeholder": "",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "Query",
                    "placeholder": "",
                    "helper_text": "Valid Hubspot Search Query - See API docs for format",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "List of matched deals",
                }
            ],
            "name": "fetch_deals",
            "task_name": "tasks.hubspot.fetch_items",
            "description": "Fetch deals from Hubspot CRM",
            "label": "Fetch Deals",
        },
        "fetch_tickets": {
            "inputs": [
                {
                    "field": "item_type",
                    "type": "string",
                    "value": "ticket",
                    "label": "",
                    "placeholder": "",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "Query",
                    "placeholder": "",
                    "helper_text": "Valid Hubspot Search Query - See API docs for format",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "List of matched tickets",
                }
            ],
            "name": "fetch_tickets",
            "task_name": "tasks.hubspot.fetch_items",
            "description": "Fetch tickets from Hubspot CRM",
            "label": "Fetch Tickets",
        },
        "fetch_notes": {
            "inputs": [
                {
                    "field": "item_type",
                    "type": "string",
                    "value": "note",
                    "label": "",
                    "placeholder": "",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "Query",
                    "placeholder": "",
                    "helper_text": "Valid Hubspot Search Query - See API docs for format",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "List of matched notes",
                }
            ],
            "name": "fetch_notes",
            "task_name": "tasks.hubspot.fetch_items",
            "description": "Fetch notes from Hubspot CRM",
            "label": "Fetch Notes",
        },
        "fetch_calls": {
            "inputs": [
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "Query",
                    "placeholder": "",
                    "helper_text": "Valid Hubspot Search Query - See API docs for format",
                },
                {
                    "field": "item_type",
                    "type": "string",
                    "value": "call",
                    "label": "",
                    "placeholder": "",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "List of matched calls",
                }
            ],
            "name": "fetch_calls",
            "task_name": "tasks.hubspot.fetch_items",
            "description": "Fetch calls from Hubspot CRM",
            "label": "Fetch Calls",
        },
        "fetch_tasks": {
            "inputs": [
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "Query",
                    "placeholder": "",
                    "helper_text": "Valid Hubspot Search Query - See API docs for format",
                },
                {
                    "field": "item_type",
                    "type": "string",
                    "value": "task",
                    "label": "",
                    "placeholder": "",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "List of matched tasks",
                }
            ],
            "name": "fetch_tasks",
            "task_name": "tasks.hubspot.fetch_items",
            "description": "Fetch tasks from Hubspot CRM",
            "label": "Fetch Tasks",
        },
        "fetch_meetings": {
            "inputs": [
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "Query",
                    "placeholder": "",
                    "helper_text": "Valid Hubspot Search Query - See API docs for format",
                },
                {
                    "field": "item_type",
                    "type": "string",
                    "value": "meeting",
                    "label": "",
                    "placeholder": "",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "List of matched meetings",
                }
            ],
            "name": "fetch_meetings",
            "task_name": "tasks.hubspot.fetch_items",
            "description": "Fetch meetings from Hubspot CRM",
            "label": "Fetch Meetings",
        },
        "fetch_emails": {
            "inputs": [
                {
                    "field": "item_type",
                    "type": "string",
                    "value": "email",
                    "label": "",
                    "placeholder": "",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "Query",
                    "placeholder": "",
                    "helper_text": "Valid Hubspot Search Query - See API docs for format",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "List of matched emails",
                }
            ],
            "name": "fetch_emails",
            "task_name": "tasks.hubspot.fetch_items",
            "description": "Fetch emails from Hubspot CRM",
            "label": "Fetch Emails",
        },
        "create_company": {
            "inputs": [
                {
                    "field": "name",
                    "type": "string",
                    "value": "",
                    "label": "Name",
                    "placeholder": "Acme Corp",
                    "helper_text": "The name of the company",
                },
                {
                    "field": "domain",
                    "type": "string",
                    "value": "",
                    "label": "Domain",
                    "placeholder": "acme.com",
                    "helper_text": "The domain of the company",
                },
                {
                    "field": "city",
                    "type": "string",
                    "value": "",
                    "label": "City",
                    "placeholder": "Boston",
                    "helper_text": "Company city location",
                },
                {
                    "field": "industry",
                    "type": "string",
                    "value": "",
                    "label": "Industry",
                    "placeholder": "Technology",
                    "helper_text": "Company industry",
                },
                {
                    "field": "phone",
                    "type": "string",
                    "value": "",
                    "label": "Phone",
                    "placeholder": "123-456-7890",
                    "helper_text": "Company phone number'",
                },
                {
                    "field": "state",
                    "type": "string",
                    "value": "",
                    "label": "State",
                    "placeholder": "MA",
                    "helper_text": "Company state location",
                },
                {
                    "field": "associated_object_id",
                    "type": "string",
                    "value": "",
                    "label": "Associated Object ID",
                    "placeholder": "12345",
                    "helper_text": "The ID of the associated object",
                },
                {
                    "field": "associated_object_type",
                    "type": "string",
                    "value": "",
                    "label": "Associated Object Type",
                    "placeholder": "contact",
                    "helper_text": "The type of the associated object",
                },
                {
                    "field": "item_type",
                    "type": "string",
                    "value": "company",
                    "label": "",
                    "placeholder": "",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
            ],
            "outputs": [],
            "name": "create_company",
            "task_name": "tasks.hubspot.create_item",
            "description": "Create a new company on Hubspot CRM",
            "label": "Create Company",
        },
        "create_contact": {
            "inputs": [
                {
                    "field": "email",
                    "type": "string",
                    "value": "",
                    "label": "Email",
                    "placeholder": "john@doe.com",
                    "helper_text": "Contact email address",
                },
                {
                    "field": "firstname",
                    "type": "string",
                    "value": "",
                    "label": "First Name",
                    "placeholder": "John",
                    "helper_text": "Contact first name",
                },
                {
                    "field": "lastname",
                    "type": "string",
                    "value": "",
                    "label": "Last Name",
                    "placeholder": "Doe",
                    "helper_text": "Contact last name",
                },
                {
                    "field": "phone",
                    "type": "string",
                    "value": "",
                    "label": "Phone",
                    "placeholder": "+1-234-567-8900",
                    "helper_text": "Contact phone number",
                },
                {
                    "field": "company",
                    "type": "string",
                    "value": "",
                    "label": "Company",
                    "placeholder": "Acme Corp",
                    "helper_text": "Contact company name",
                },
                {
                    "field": "website",
                    "type": "string",
                    "value": "",
                    "label": "Website",
                    "placeholder": "www.example.com",
                    "helper_text": "Contact website",
                },
                {
                    "field": "associated_object_id",
                    "type": "string",
                    "value": "",
                    "label": "Associated Object ID",
                    "placeholder": "12345",
                    "helper_text": "The ID of the associated object",
                },
                {
                    "field": "associated_object_type",
                    "type": "string",
                    "value": "",
                    "label": "Associated Object Type",
                    "placeholder": "contact",
                    "helper_text": "The type of the associated object",
                },
                {
                    "field": "item_type",
                    "type": "string",
                    "value": "contact",
                    "label": "",
                    "placeholder": "",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
            ],
            "outputs": [],
            "name": "create_contact",
            "task_name": "tasks.hubspot.create_item",
            "description": "Create a new contact on Hubspot CRM",
            "label": "Create Contact",
        },
        "create_deal": {
            "inputs": [
                {
                    "field": "amount",
                    "type": "string",
                    "value": "",
                    "label": "Amount",
                    "placeholder": "10000",
                    "helper_text": "Deal amount",
                },
                {
                    "field": "closedate",
                    "type": "string",
                    "value": "",
                    "label": "Close Date",
                    "placeholder": "2025-01-01",
                    "helper_text": "Expected close date",
                },
                {
                    "field": "dealname",
                    "type": "string",
                    "value": "",
                    "label": "Deal Name",
                    "placeholder": "Enterprise Solution 2024",
                    "helper_text": "Name of the deal",
                },
                {
                    "field": "pipeline",
                    "type": "string",
                    "value": "",
                    "label": "Pipeline",
                    "placeholder": "default",
                    "helper_text": "Deal pipeline",
                },
                {
                    "field": "dealstage",
                    "type": "string",
                    "value": "",
                    "label": "Deal Stage",
                    "placeholder": "Prospect",
                    "helper_text": "Stage of the deal",
                },
                {
                    "field": "associated_object_id",
                    "type": "string",
                    "value": "",
                    "label": "Associated Object ID",
                    "placeholder": "12345",
                    "helper_text": "The ID of the associated object",
                },
                {
                    "field": "associated_object_type",
                    "type": "string",
                    "value": "",
                    "label": "Associated Object Type",
                    "placeholder": "contact",
                    "helper_text": "The type of the associated object",
                },
                {
                    "field": "item_type",
                    "type": "string",
                    "value": "deal",
                    "label": "",
                    "placeholder": "",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
            ],
            "outputs": [],
            "name": "create_deal",
            "task_name": "tasks.hubspot.create_item",
            "description": "Create a new deal on Hubspot CRM",
            "label": "Create Deal",
        },
        "create_ticket": {
            "inputs": [
                {
                    "field": "hs_pipeline",
                    "type": "string",
                    "value": "",
                    "label": "HS Pipeline",
                    "placeholder": "support",
                    "helper_text": "Ticket pipeline",
                },
                {
                    "field": "hs_pipeline_stage",
                    "type": "string",
                    "value": "",
                    "label": "HS Pipeline Stage",
                    "placeholder": "new",
                    "helper_text": "Stage in the pipeline",
                },
                {
                    "field": "hs_ticket_priority",
                    "type": "string",
                    "value": "",
                    "label": "HS Ticket Priority",
                    "placeholder": "HIGH",
                    "helper_text": "Ticket priority level",
                },
                {
                    "field": "subject",
                    "type": "string",
                    "value": "",
                    "label": "Subject",
                    "placeholder": "Technical Support Request",
                    "helper_text": "Ticket subject",
                },
                {
                    "field": "associated_object_id",
                    "type": "string",
                    "value": "",
                    "label": "Associated Object ID",
                    "placeholder": "12345",
                    "helper_text": "ID of associated object",
                },
                {
                    "field": "associated_object_type",
                    "type": "string",
                    "value": "",
                    "label": "Associated Object Type",
                    "placeholder": "CONTACT",
                    "helper_text": "Type of associated object",
                },
                {
                    "field": "item_type",
                    "type": "string",
                    "value": "ticket",
                    "label": "",
                    "placeholder": "",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
            ],
            "outputs": [],
            "name": "create_ticket",
            "task_name": "tasks.hubspot.create_item",
            "description": "Create a new ticket on Hubspot CRM",
            "label": "Create Ticket",
        },
        "create_note": {
            "inputs": [
                {
                    "field": "body",
                    "type": "string",
                    "value": "",
                    "label": "Body",
                    "placeholder": "Discussion notes from client meeting",
                    "helper_text": "Content of the note",
                },
                {
                    "field": "associated_object_id",
                    "type": "string",
                    "value": "",
                    "label": "Associated Object ID",
                    "placeholder": "12345",
                    "helper_text": "ID of associated object",
                },
                {
                    "field": "associated_object_type",
                    "type": "string",
                    "value": "",
                    "label": "Associated Object Type",
                    "placeholder": "DEAL",
                    "helper_text": "Type of associated object",
                },
                {
                    "field": "item_type",
                    "type": "string",
                    "value": "note",
                    "label": "",
                    "placeholder": "",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
            ],
            "outputs": [],
            "name": "create_note",
            "task_name": "tasks.hubspot.create_item",
            "description": "Create a new note on Hubspot CRM",
            "label": "Create Note",
        },
        "create_call": {
            "inputs": [
                {
                    "field": "body",
                    "type": "string",
                    "value": "",
                    "label": "Body",
                    "placeholder": "Discussed Q4 objectives",
                    "helper_text": "Call notes or summary",
                },
                {
                    "field": "duration",
                    "type": "string",
                    "value": "",
                    "label": "Call Duration",
                    "placeholder": "1800",
                    "helper_text": "Call duration in seconds",
                },
                {
                    "field": "title",
                    "type": "string",
                    "value": "",
                    "label": "Title",
                    "placeholder": "Q4 Planning Call",
                    "helper_text": "Title of the call",
                },
                {
                    "field": "from_number",
                    "type": "string",
                    "value": "",
                    "label": "From Number",
                    "placeholder": "+1-234-567-8900",
                    "helper_text": "Caller phone number",
                },
                {
                    "field": "to_number",
                    "type": "string",
                    "value": "",
                    "label": "To Number",
                    "placeholder": "+1-234-567-8901",
                    "helper_text": "Recipient phone number",
                },
                {
                    "field": "associated_object_id",
                    "type": "string",
                    "value": "",
                    "label": "Associated Object ID",
                    "placeholder": "12345",
                    "helper_text": "ID of associated object",
                },
                {
                    "field": "associated_object_type",
                    "type": "string",
                    "value": "",
                    "label": "Associated Object Type",
                    "placeholder": "CONTACT",
                    "helper_text": "Type of associated object",
                },
                {
                    "field": "item_type",
                    "type": "string",
                    "value": "call",
                    "label": "",
                    "placeholder": "",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
            ],
            "outputs": [],
            "name": "create_call",
            "task_name": "tasks.hubspot.create_item",
            "description": "Create a new call on Hubspot CRM",
            "label": "Create Call",
        },
        "create_task": {
            "inputs": [
                {
                    "field": "body",
                    "type": "string",
                    "value": "",
                    "label": "Body",
                    "placeholder": "Follow up on proposal",
                    "helper_text": "Task description",
                },
                {
                    "field": "status",
                    "type": "string",
                    "value": "",
                    "label": "Status",
                    "placeholder": "NOT_STARTED",
                    "helper_text": "Current status of the task",
                },
                {
                    "field": "subject",
                    "type": "string",
                    "value": "",
                    "label": "Subject",
                    "placeholder": "Send follow-up email",
                    "helper_text": "Subject of the task",
                },
                {
                    "field": "priority",
                    "type": "string",
                    "value": "",
                    "label": "Priority",
                    "placeholder": "HIGH",
                    "helper_text": "Task priority level",
                },
                {
                    "field": "associated_object_id",
                    "type": "string",
                    "value": "",
                    "label": "Associated Object ID",
                    "placeholder": "12345",
                    "helper_text": "ID of associated object",
                },
                {
                    "field": "associated_object_type",
                    "type": "string",
                    "value": "",
                    "label": "Associated Object Type",
                    "placeholder": "DEAL",
                    "helper_text": "Type of associated object",
                },
                {
                    "field": "item_type",
                    "type": "string",
                    "value": "task",
                    "label": "",
                    "placeholder": "",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
            ],
            "outputs": [],
            "name": "create_task",
            "task_name": "tasks.hubspot.create_item",
            "description": "Create a new task on Hubspot CRM",
            "label": "Create Task",
        },
        "create_meeting": {
            "inputs": [
                {
                    "field": "body",
                    "type": "string",
                    "value": "",
                    "label": "Body",
                    "placeholder": "Monthly review meeting",
                    "helper_text": "Meeting description",
                },
                {
                    "field": "title",
                    "type": "string",
                    "value": "",
                    "label": "Title",
                    "placeholder": "Monthly Review - January 2024",
                    "helper_text": "Title of the meeting",
                },
                {
                    "field": "start_time",
                    "type": "string",
                    "value": "",
                    "label": "Start Time",
                    "placeholder": "2024-01-15T10:00:00Z",
                    "helper_text": "Meeting start time",
                },
                {
                    "field": "end_time",
                    "type": "string",
                    "value": "",
                    "label": "End Time",
                    "placeholder": "2024-01-15T11:00:00Z",
                    "helper_text": "Meeting end time",
                },
                {
                    "field": "meeting_notes",
                    "type": "string",
                    "value": "",
                    "label": "Meeting Notes",
                    "placeholder": "Discussion points and action items",
                    "helper_text": "Notes from the meeting",
                },
                {
                    "field": "associated_object_id",
                    "type": "string",
                    "value": "",
                    "label": "Associated Object ID",
                    "placeholder": "12345",
                    "helper_text": "ID of associated object",
                },
                {
                    "field": "associated_object_type",
                    "type": "string",
                    "value": "",
                    "label": "Associated Object Type",
                    "placeholder": "COMPANY",
                    "helper_text": "Type of associated object",
                },
                {
                    "field": "item_type",
                    "type": "string",
                    "value": "meeting",
                    "label": "",
                    "placeholder": "",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
            ],
            "outputs": [],
            "name": "create_meeting",
            "task_name": "tasks.hubspot.create_item",
            "description": "Create a new meeting on Hubspot CRM",
            "label": "Create Meeting",
        },
        "create_email": {
            "inputs": [
                {
                    "field": "text",
                    "type": "string",
                    "value": "",
                    "label": "Text",
                    "placeholder": "valued customer...",
                    "helper_text": "Email body content",
                },
                {
                    "field": "subject",
                    "type": "string",
                    "value": "",
                    "label": "Subject",
                    "placeholder": "Follow-up from our meeting",
                    "helper_text": "Email subject line",
                },
                {
                    "field": "recipient_email",
                    "type": "string",
                    "value": "",
                    "label": "Recipient Email",
                    "placeholder": "contact@company.com",
                    "helper_text": "Email address of the recipient",
                },
                {
                    "field": "sender_email",
                    "type": "string",
                    "value": "",
                    "label": "Sender Email",
                    "placeholder": "sales@ourcompany.com",
                    "helper_text": "Email address of the sender",
                },
                {
                    "field": "direction",
                    "type": "string",
                    "value": "",
                    "label": "Direction",
                    "placeholder": "OUTGOING",
                    "helper_text": "Direction of the email (INCOMING/OUTGOING)",
                },
                {
                    "field": "associated_object_id",
                    "type": "string",
                    "value": "",
                    "label": "Associated Object ID",
                    "placeholder": "12345",
                    "helper_text": "ID of associated object",
                },
                {
                    "field": "associated_object_type",
                    "type": "string",
                    "value": "",
                    "label": "Associated Object Type",
                    "placeholder": "CONTACT",
                    "helper_text": "Type of associated object",
                },
                {
                    "field": "item_type",
                    "type": "string",
                    "value": "email",
                    "label": "",
                    "placeholder": "",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
            ],
            "outputs": [],
            "name": "create_email",
            "task_name": "tasks.hubspot.create_item",
            "description": "Create a new email on Hubspot CRM",
            "label": "Create Email",
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Hubspot",
        item_type: str | ToolInput = "contact",
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_hubspot",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if item_type is not None:
            if isinstance(item_type, ToolInput):
                self.inputs["item_type"] = {
                    "type": item_type.type,
                    "value": item_type.value or item_type.description,
                }
            else:
                self.inputs["item_type"] = {"type": "static", "value": item_type}
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationHubspotTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_snowflake")
class IntegrationSnowflakeTool(Tool):
    """
    Snowflake

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### nl
        database: Select the Database on which to perform the query
        query: SQL Query to execute
        query_agent_model: The query_agent_model input
        query_type: The query_type input
        schema: Select the schema to be used in the query
        sql_generation_model: The sql_generation_model input
        warehouse: Select the SQL Warehouse which will perform the operation
    ### raw_sql
        database: Select the Database on which to perform the query
        query: SQL Query to execute
        query_agent_model: The query_agent_model input
        query_type: The query_type input
        schema: Select the schema to be used in the query
        sql_generation_model: The sql_generation_model input
        warehouse: Select the SQL Warehouse which will perform the operation
    ### nl_agent
        database: Select the Database on which to perform the query
        query: SQL Query to execute
        query_agent_model: The query_agent_model input
        query_type: The query_type input
        schema: Select the schema to be used in the query
        sql_generation_model: The sql_generation_model input
        warehouse: Select the SQL Warehouse which will perform the operation
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Snowflake>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "(*)": {"inputs": [], "outputs": [], "variant": "common_integration_nodes"},
        "nl": {
            "inputs": [
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "SQL Query",
                    "placeholder": "select * from dummy_table",
                    "helper_text": "SQL Query to execute",
                },
                {
                    "field": "query_type",
                    "type": "string",
                    "value": "Raw SQL",
                    "hidden": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
                {
                    "field": "warehouse",
                    "type": "string",
                    "value": "",
                    "label": "Warehouse",
                    "helper_text": "Select the SQL Warehouse which will perform the operation",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=warehouse&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": False,
                            "supports_pagination": False,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
                {
                    "field": "database",
                    "type": "string",
                    "value": "",
                    "label": "Database",
                    "helper_text": "Select the Database on which to perform the query",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=database&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": False,
                            "supports_pagination": False,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
                {
                    "field": "schema",
                    "type": "string",
                    "value": "",
                    "label": "Schema",
                    "helper_text": "Select the schema to be used in the query",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=schema&database={inputs.database}&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": False,
                            "supports_pagination": False,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
                {
                    "field": "sql_generation_model",
                    "type": "string",
                    "value": "gpt-4-turbo-preview",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
                {
                    "field": "query_agent_model",
                    "type": "string",
                    "value": "gpt-4-turbo-preview",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
            ],
            "outputs": [],
            "name": "nl",
            "task_name": "tasks.tables.integrations.snowflake.query",
            "description": "Generate and execute a SQL query",
            "label": "Natural Language Query",
        },
        "raw_sql": {
            "inputs": [
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "SQL Query",
                    "placeholder": "select * from dummy_table",
                    "helper_text": "SQL Query to execute",
                },
                {
                    "field": "query_type",
                    "type": "string",
                    "value": "Raw SQL",
                    "hidden": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
                {
                    "field": "warehouse",
                    "type": "string",
                    "value": "",
                    "label": "Warehouse",
                    "helper_text": "Select the SQL Warehouse which will perform the operation",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=warehouse&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": False,
                            "supports_pagination": False,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
                {
                    "field": "database",
                    "type": "string",
                    "value": "",
                    "label": "Database",
                    "helper_text": "Select the Database on which to perform the query",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=database&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": False,
                            "supports_pagination": False,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
                {
                    "field": "schema",
                    "type": "string",
                    "value": "",
                    "label": "Schema",
                    "helper_text": "Select the schema to be used in the query",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=schema&database={inputs.database}&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": False,
                            "supports_pagination": False,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
                {
                    "field": "sql_generation_model",
                    "type": "string",
                    "value": "gpt-4-turbo-preview",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
                {
                    "field": "query_agent_model",
                    "type": "string",
                    "value": "gpt-4-turbo-preview",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
            ],
            "outputs": [],
            "name": "raw_sql",
            "task_name": "tasks.tables.integrations.snowflake.query",
            "description": "Execute a SQL query",
            "label": "Raw SQL Query",
        },
        "nl_agent": {
            "inputs": [
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "SQL Query",
                    "placeholder": "select * from dummy_table",
                    "helper_text": "SQL Query to execute",
                },
                {
                    "field": "query_type",
                    "type": "string",
                    "value": "Raw SQL",
                    "hidden": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
                {
                    "field": "warehouse",
                    "type": "string",
                    "value": "",
                    "label": "Warehouse",
                    "helper_text": "Select the SQL Warehouse which will perform the operation",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=warehouse&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": False,
                            "supports_pagination": False,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
                {
                    "field": "database",
                    "type": "string",
                    "value": "",
                    "label": "Database",
                    "helper_text": "Select the Database on which to perform the query",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=database&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": False,
                            "supports_pagination": False,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
                {
                    "field": "schema",
                    "type": "string",
                    "value": "",
                    "label": "Schema",
                    "helper_text": "Select the schema to be used in the query",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=schema&database={inputs.database}&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": False,
                            "supports_pagination": False,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
                {
                    "field": "sql_generation_model",
                    "type": "string",
                    "value": "gpt-4-turbo-preview",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
                {
                    "field": "query_agent_model",
                    "type": "string",
                    "value": "gpt-4-turbo-preview",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
            ],
            "outputs": [],
            "name": "nl_agent",
            "task_name": "tasks.tables.integrations.snowflake.query",
            "description": "Let an LLM agent query the database",
            "label": "Natural Language Agent",
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Snowflake",
        database: str | ToolInput = "",
        query_agent_model: str | ToolInput = "gpt-4-turbo-preview",
        query_type: str | ToolInput = "Raw SQL",
        schema: str | ToolInput = "",
        sql_generation_model: str | ToolInput = "gpt-4-turbo-preview",
        warehouse: str | ToolInput = "",
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_snowflake",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if database is not None:
            if isinstance(database, ToolInput):
                self.inputs["database"] = {
                    "type": database.type,
                    "value": database.value or database.description,
                }
            else:
                self.inputs["database"] = {"type": "static", "value": database}
        if query_agent_model is not None:
            if isinstance(query_agent_model, ToolInput):
                self.inputs["query_agent_model"] = {
                    "type": query_agent_model.type,
                    "value": query_agent_model.value or query_agent_model.description,
                }
            else:
                self.inputs["query_agent_model"] = {
                    "type": "static",
                    "value": query_agent_model,
                }
        if query_type is not None:
            if isinstance(query_type, ToolInput):
                self.inputs["query_type"] = {
                    "type": query_type.type,
                    "value": query_type.value or query_type.description,
                }
            else:
                self.inputs["query_type"] = {"type": "static", "value": query_type}
        if schema is not None:
            if isinstance(schema, ToolInput):
                self.inputs["schema"] = {
                    "type": schema.type,
                    "value": schema.value or schema.description,
                }
            else:
                self.inputs["schema"] = {"type": "static", "value": schema}
        if sql_generation_model is not None:
            if isinstance(sql_generation_model, ToolInput):
                self.inputs["sql_generation_model"] = {
                    "type": sql_generation_model.type,
                    "value": sql_generation_model.value
                    or sql_generation_model.description,
                }
            else:
                self.inputs["sql_generation_model"] = {
                    "type": "static",
                    "value": sql_generation_model,
                }
        if warehouse is not None:
            if isinstance(warehouse, ToolInput):
                self.inputs["warehouse"] = {
                    "type": warehouse.type,
                    "value": warehouse.value or warehouse.description,
                }
            else:
                self.inputs["warehouse"] = {"type": "static", "value": warehouse}
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationSnowflakeTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_elasticsearch")
class IntegrationElasticsearchTool(Tool):
    """
    Elasticsearch

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### search_index
        index: Elasticsearch index name
        query: Query to search over index in JSON format
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Elasticsearch>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "search_index": {
            "inputs": [
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "JSON Query",
                    "placeholder": '{"query_string": {"query": "mountain*", "fields": ["title", "description"]}}',
                    "helper_text": "Query to search over index in JSON format",
                },
                {
                    "field": "index",
                    "type": "string",
                    "value": "",
                    "label": "Index",
                    "placeholder": "my-index",
                    "helper_text": "Elasticsearch index name",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "Search results from the Elasticsearch index",
                }
            ],
            "name": "search_index",
            "task_name": "tasks.elasticsearch.search_index",
            "description": "Query your Elasticsearch index",
            "label": "Search Elasticsearch index",
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Elasticsearch",
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_elasticsearch",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationElasticsearchTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_mongodb")
class IntegrationMongodbTool(Tool):
    """
    MongoDB

    ## Inputs
    ### Common Inputs
        action: The action input
        integration: Connect to your account
    ### find
        collection: The collection on which to perform the query
        query: The MongoDB query to find all matching records
    ### find_one
        collection: The collection on which to perform the query
        query: The MongoDB query to find all matching records
    ### aggregate
        collection: The collection on which to perform the query
        query: The MongoDB query to find all matching records
    ### mongodb_nl
        collection: The collection on which to perform the query
        query: The MongoDB query to find all matching records
    ### mongodb_nl_aggregation
        collection: The collection on which to perform the query
        query: The MongoDB query to find all matching records
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "The action input",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<MongoDB>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "(*)": {"inputs": [], "outputs": [], "variant": "common_integration_nodes"},
        "find": {
            "inputs": [
                {
                    "field": "collection",
                    "type": "string",
                    "value": "",
                    "label": "Collection",
                    "helper_text": "The collection on which to perform the query",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=collection&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": False,
                            "supports_pagination": False,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "Query",
                    "placeholder": "{“name”: “John”, “age”: {“gte”: 28}}",
                    "helper_text": "The MongoDB query to find all matching records",
                },
            ],
            "outputs": [],
            "name": "find",
            "task_name": "tasks.document_dbs.mongo.query",
            "description": "Query MongoDB data",
            "label": "MongoDB Find",
        },
        "find_one": {
            "inputs": [
                {
                    "field": "collection",
                    "type": "string",
                    "value": "",
                    "label": "Collection",
                    "helper_text": "The collection on which to perform the query",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=collection&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": False,
                            "supports_pagination": False,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "Query",
                    "placeholder": "{“name”: “John”, “age”: {“gte”: 28}}",
                    "helper_text": "The MongoDB query to find all matching records",
                },
            ],
            "outputs": [],
            "name": "find_one",
            "task_name": "tasks.document_dbs.mongo.query",
            "description": "Query MongoDB data",
            "label": "MongoDB Find One",
        },
        "aggregate": {
            "inputs": [
                {
                    "field": "collection",
                    "type": "string",
                    "value": "",
                    "label": "Collection",
                    "helper_text": "The collection on which to perform the query",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=collection&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": False,
                            "supports_pagination": False,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "Query",
                    "placeholder": "{“name”: “John”, “age”: {“gte”: 28}}",
                    "helper_text": "The MongoDB query to find all matching records",
                },
            ],
            "outputs": [],
            "name": "aggregate",
            "task_name": "tasks.document_dbs.mongo.query",
            "description": "Run an Aggegation on MongoDB data",
            "label": "MongoDB Aggegate",
        },
        "mongodb_nl": {
            "inputs": [
                {
                    "field": "collection",
                    "type": "string",
                    "value": "",
                    "label": "Collection",
                    "helper_text": "The collection on which to perform the query",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=collection&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": False,
                            "supports_pagination": False,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "Query",
                    "placeholder": "{“name”: “John”, “age”: {“gte”: 28}}",
                    "helper_text": "The MongoDB query to find all matching records",
                },
            ],
            "outputs": [],
            "name": "mongodb_nl",
            "task_name": "tasks.document_dbs.mongo.query",
            "description": "Query MongoDB data with Natural Language",
            "label": "NL Query",
        },
        "mongodb_nl_aggregation": {
            "inputs": [
                {
                    "field": "collection",
                    "type": "string",
                    "value": "",
                    "label": "Collection",
                    "helper_text": "The collection on which to perform the query",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=collection&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": False,
                            "supports_pagination": False,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "Query",
                    "placeholder": "{“name”: “John”, “age”: {“gte”: 28}}",
                    "helper_text": "The MongoDB query to find all matching records",
                },
            ],
            "outputs": [],
            "name": "mongodb_nl_aggregation",
            "task_name": "tasks.document_dbs.mongo.query",
            "description": "Aggregate MongoDB data with Natural Language",
            "label": "NL Aggregation",
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "MongoDB",
        collection: str | ToolInput = "",
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_mongodb",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if collection is not None:
            if isinstance(collection, ToolInput):
                self.inputs["collection"] = {
                    "type": collection.type,
                    "value": collection.value or collection.description,
                }
            else:
                self.inputs["collection"] = {"type": "static", "value": collection}
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationMongodbTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_pinecone")
class IntegrationPineconeTool(Tool):
    """
    Pinecone

    ## Inputs
    ### Common Inputs
        action: The action input
        integration: Connect to your account
    ### query_pinecone
        embedding_model: Select the embedding model to use to embed the query
        index: The Pinecone index to query
        namespace: Select the namespace to query (queries across all namespaces if left empty)
        query: Natural Language query
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "The action input",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Pinecone>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "query_pinecone": {
            "inputs": [
                {
                    "field": "embedding_model",
                    "type": "enum<string>",
                    "value": "",
                    "label": "Embedding Model",
                    "helper_text": "Select the embedding model to use to embed the query",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "options": [
                            {
                                "label": "OpenAI Text Embedding 3 Small",
                                "value": "openai/text-embedding-3-small",
                            },
                            {
                                "label": "OpenAI Text Embedding 3 Large",
                                "value": "openai/text-embedding-3-large",
                            },
                            {
                                "label": "OpenAI Text Embedding Ada 002",
                                "value": "openai/text-embedding-ada-002",
                            },
                            {
                                "label": "Cohere Embed English v3.0",
                                "value": "cohere/embed-english-v3.0",
                            },
                            {
                                "label": "Cohere Embed Multilingual v3.0",
                                "value": "cohere/embed-multilingual-v3.0",
                            },
                            {
                                "label": "Cohere Embed English Light v3.0",
                                "value": "cohere/embed-english-light-v3.0",
                            },
                            {
                                "label": "Cohere Embed Multilingual Light v3.0",
                                "value": "cohere/embed-multilingual-light-v3.0",
                            },
                        ],
                    },
                },
                {
                    "field": "index",
                    "type": "string",
                    "value": "",
                    "label": "Index",
                    "helper_text": "The Pinecone index to query",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=index&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": False,
                            "supports_pagination": False,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
                {
                    "field": "namespace",
                    "type": "string",
                    "value": "",
                    "label": "Namespace",
                    "helper_text": "Select the namespace to query (queries across all namespaces if left empty)",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=namespace&index={inputs.index}&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": False,
                            "supports_pagination": False,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "Query",
                    "placeholder": "“Birthday parties in March”",
                    "helper_text": "Natural Language query",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "any",
                    "helper_text": "Query output in Langchain-style documents",
                }
            ],
            "name": "query_pinecone",
            "task_name": "tasks.vectordbs.integrations.pinecone.query",
            "description": "Query Pinecone data",
            "label": "Query Pinecone",
            "variant": "common_integration_nodes",
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Pinecone",
        embedding_model: str | ToolInput = "",
        index: str | ToolInput = "",
        namespace: str | ToolInput = "",
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_pinecone",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if embedding_model is not None:
            if isinstance(embedding_model, ToolInput):
                self.inputs["embedding_model"] = {
                    "type": embedding_model.type,
                    "value": embedding_model.value or embedding_model.description,
                }
            else:
                self.inputs["embedding_model"] = {
                    "type": "static",
                    "value": embedding_model,
                }
        if index is not None:
            if isinstance(index, ToolInput):
                self.inputs["index"] = {
                    "type": index.type,
                    "value": index.value or index.description,
                }
            else:
                self.inputs["index"] = {"type": "static", "value": index}
        if namespace is not None:
            if isinstance(namespace, ToolInput):
                self.inputs["namespace"] = {
                    "type": namespace.type,
                    "value": namespace.value or namespace.description,
                }
            else:
                self.inputs["namespace"] = {"type": "static", "value": namespace}
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationPineconeTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_postgres")
class IntegrationPostgresTool(Tool):
    """
    Postgres

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### nl
        query: Natural language query to be converted to SQL
        query_agent_model: The query_agent_model input
        query_type: The query_type input
        sql_generation_model: The sql_generation_model input
    ### raw_sql
        query: Natural language query to be converted to SQL
        query_agent_model: The query_agent_model input
        query_type: The query_type input
        sql_generation_model: The sql_generation_model input
    ### nl_agent
        query: Natural language query to be converted to SQL
        query_agent_model: The query_agent_model input
        query_type: The query_type input
        sql_generation_model: The sql_generation_model input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Postgres>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "(*)": {"inputs": [], "outputs": [], "variant": "default_integration_nodes"},
        "nl": {
            "inputs": [
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "Query",
                    "placeholder": "select * from dummy_table",
                    "helper_text": "Natural language query to be converted to SQL",
                },
                {
                    "field": "query_type",
                    "type": "string",
                    "value": "Raw SQL",
                    "label": "Query Type",
                    "hidden": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
                {
                    "field": "sql_generation_model",
                    "type": "string",
                    "value": "gpt-4-turbo-preview",
                    "label": "SQL Generation Model",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
                {
                    "field": "query_agent_model",
                    "type": "string",
                    "value": "gpt-4-turbo-preview",
                    "label": "Query Agent Model",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
            ],
            "outputs": [],
            "name": "nl",
            "task_name": "tasks.tables.integrations.postgres.query",
            "description": "Generate and execute a SQL query",
            "label": "Natural Language Query",
        },
        "raw_sql": {
            "inputs": [
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "Query",
                    "placeholder": "select * from dummy_table",
                    "helper_text": "SQL Query to execute",
                },
                {
                    "field": "query_type",
                    "type": "string",
                    "value": "Raw SQL",
                    "label": "Query Type",
                    "hidden": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
                {
                    "field": "sql_generation_model",
                    "type": "string",
                    "value": "gpt-4-turbo-preview",
                    "label": "SQL Generation Model",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
                {
                    "field": "query_agent_model",
                    "type": "string",
                    "value": "gpt-4-turbo-preview",
                    "label": "Query Agent Model",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
            ],
            "outputs": [],
            "name": "raw_sql",
            "task_name": "tasks.tables.integrations.postgres.query",
            "description": "Execute a SQL query",
            "label": "Raw SQL Query",
        },
        "nl_agent": {
            "inputs": [
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "Query",
                    "placeholder": "select * from dummy_table",
                    "helper_text": "Natural language query for the LLM agent to process",
                },
                {
                    "field": "query_type",
                    "type": "string",
                    "value": "Raw SQL",
                    "label": "Query Type",
                    "hidden": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
                {
                    "field": "sql_generation_model",
                    "type": "string",
                    "value": "gpt-4-turbo-preview",
                    "label": "SQL Generation Model",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
                {
                    "field": "query_agent_model",
                    "type": "string",
                    "value": "gpt-4-turbo-preview",
                    "label": "Query Agent Model",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
            ],
            "outputs": [],
            "name": "nl_agent",
            "task_name": "tasks.tables.integrations.postgres.query",
            "description": "Let an LLM agent query the database",
            "label": "Natural Language Agent",
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Postgres",
        query_agent_model: str | ToolInput = "gpt-4-turbo-preview",
        query_type: str | ToolInput = "Raw SQL",
        sql_generation_model: str | ToolInput = "gpt-4-turbo-preview",
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_postgres",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if query_agent_model is not None:
            if isinstance(query_agent_model, ToolInput):
                self.inputs["query_agent_model"] = {
                    "type": query_agent_model.type,
                    "value": query_agent_model.value or query_agent_model.description,
                }
            else:
                self.inputs["query_agent_model"] = {
                    "type": "static",
                    "value": query_agent_model,
                }
        if query_type is not None:
            if isinstance(query_type, ToolInput):
                self.inputs["query_type"] = {
                    "type": query_type.type,
                    "value": query_type.value or query_type.description,
                }
            else:
                self.inputs["query_type"] = {"type": "static", "value": query_type}
        if sql_generation_model is not None:
            if isinstance(sql_generation_model, ToolInput):
                self.inputs["sql_generation_model"] = {
                    "type": sql_generation_model.type,
                    "value": sql_generation_model.value
                    or sql_generation_model.description,
                }
            else:
                self.inputs["sql_generation_model"] = {
                    "type": "static",
                    "value": sql_generation_model,
                }
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationPostgresTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_mysql")
class IntegrationMysqlTool(Tool):
    """
    MySQL

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### nl
        query: Natural language query to be converted to SQL
        query_agent_model: The query_agent_model input
        query_type: The query_type input
        sql_generation_model: The sql_generation_model input
    ### raw_sql
        query: Natural language query to be converted to SQL
        query_agent_model: The query_agent_model input
        query_type: The query_type input
        sql_generation_model: The sql_generation_model input
    ### nl_agent
        query: Natural language query to be converted to SQL
        query_agent_model: The query_agent_model input
        query_type: The query_type input
        sql_generation_model: The sql_generation_model input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<MySQL>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "(*)": {"inputs": [], "outputs": [], "variant": "default_integration_nodes"},
        "nl": {
            "inputs": [
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "SQL Query",
                    "placeholder": "select * from dummy_table",
                    "helper_text": "Natural language query to be converted to SQL",
                },
                {
                    "field": "query_type",
                    "type": "string",
                    "value": "Raw SQL",
                    "label": "Query Type",
                    "hidden": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
                {
                    "field": "sql_generation_model",
                    "type": "string",
                    "value": "gpt-4-turbo-preview",
                    "label": "SQL Generation Model",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
                {
                    "field": "query_agent_model",
                    "type": "string",
                    "value": "gpt-4-turbo-preview",
                    "label": "Query Agent Model",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
            ],
            "outputs": [],
            "name": "nl",
            "task_name": "tasks.tables.integrations.mysql.query",
            "description": "Generate and execute a SQL query",
            "label": "Natural Language Query",
        },
        "raw_sql": {
            "inputs": [
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "SQL Query",
                    "placeholder": "select * from dummy_table",
                    "helper_text": "SQL Query to execute",
                },
                {
                    "field": "query_type",
                    "type": "string",
                    "value": "Raw SQL",
                    "label": "Query Type",
                    "hidden": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
                {
                    "field": "sql_generation_model",
                    "type": "string",
                    "value": "gpt-4-turbo-preview",
                    "label": "SQL Generation Model",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
                {
                    "field": "query_agent_model",
                    "type": "string",
                    "value": "gpt-4-turbo-preview",
                    "label": "Query Agent Model",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
            ],
            "outputs": [],
            "name": "raw_sql",
            "task_name": "tasks.tables.integrations.mysql.query",
            "description": "Execute a SQL query",
            "label": "Raw SQL Query",
        },
        "nl_agent": {
            "inputs": [
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "SQL Query",
                    "placeholder": "select * from dummy_table",
                    "helper_text": "Natural language query for the LLM agent to process",
                },
                {
                    "field": "query_type",
                    "type": "string",
                    "value": "Raw SQL",
                    "label": "Query Type",
                    "hidden": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
                {
                    "field": "sql_generation_model",
                    "type": "string",
                    "value": "gpt-4-turbo-preview",
                    "label": "SQL Generation Model",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
                {
                    "field": "query_agent_model",
                    "type": "string",
                    "value": "gpt-4-turbo-preview",
                    "label": "Query Agent Model",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
            ],
            "outputs": [],
            "name": "nl_agent",
            "task_name": "tasks.tables.integrations.mysql.query",
            "description": "Let an LLM agent query the database",
            "label": "Natural Language Agent",
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "MySQL",
        query_agent_model: str | ToolInput = "gpt-4-turbo-preview",
        query_type: str | ToolInput = "Raw SQL",
        sql_generation_model: str | ToolInput = "gpt-4-turbo-preview",
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_mysql",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if query_agent_model is not None:
            if isinstance(query_agent_model, ToolInput):
                self.inputs["query_agent_model"] = {
                    "type": query_agent_model.type,
                    "value": query_agent_model.value or query_agent_model.description,
                }
            else:
                self.inputs["query_agent_model"] = {
                    "type": "static",
                    "value": query_agent_model,
                }
        if query_type is not None:
            if isinstance(query_type, ToolInput):
                self.inputs["query_type"] = {
                    "type": query_type.type,
                    "value": query_type.value or query_type.description,
                }
            else:
                self.inputs["query_type"] = {"type": "static", "value": query_type}
        if sql_generation_model is not None:
            if isinstance(sql_generation_model, ToolInput):
                self.inputs["sql_generation_model"] = {
                    "type": sql_generation_model.type,
                    "value": sql_generation_model.value
                    or sql_generation_model.description,
                }
            else:
                self.inputs["sql_generation_model"] = {
                    "type": "static",
                    "value": sql_generation_model,
                }
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationMysqlTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_wordpress")
class IntegrationWordpressTool(Tool):
    """
    Wordpress

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### create_post
        post_content: The content of the post
        post_title: The title of the post
        wordpress_url: Wordpress domain URL
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Wordpress>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "(*)": {"inputs": [], "outputs": [], "variant": "default_integration_nodes"},
        "create_post": {
            "inputs": [
                {
                    "field": "wordpress_url",
                    "type": "string",
                    "value": "",
                    "label": "Wordpress URL",
                    "placeholder": "test.wordpress.com",
                    "helper_text": "Wordpress domain URL",
                    "agent_field_type": "static",
                },
                {
                    "field": "post_title",
                    "type": "string",
                    "value": "",
                    "label": "Post Title",
                    "placeholder": "An overview of Generative AI",
                    "helper_text": "The title of the post",
                },
                {
                    "field": "post_content",
                    "type": "string",
                    "value": "",
                    "label": "Post Content",
                    "placeholder": "This is an overview...",
                    "helper_text": "The content of the post",
                },
            ],
            "outputs": [
                {
                    "field": "post_url",
                    "type": "string",
                    "helper_text": "URL of the created WordPress post",
                }
            ],
            "name": "create_post",
            "task_name": "tasks.wordpress.create_post",
            "description": "Create post on Wordpress site",
            "label": "Post to Wordpress",
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Wordpress",
        wordpress_url: str | ToolInput = "",
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_wordpress",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if wordpress_url is not None:
            if isinstance(wordpress_url, ToolInput):
                self.inputs["wordpress_url"] = {
                    "type": wordpress_url.type,
                    "value": wordpress_url.value or wordpress_url.description,
                }
            else:
                self.inputs["wordpress_url"] = {
                    "type": "static",
                    "value": wordpress_url,
                }
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationWordpressTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_linkedin")
class IntegrationLinkedinTool(Tool):
    """
    Linkedin

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### create_text_share
        post_text: Content you wanted to post on your LinkedIn
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Linkedin>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "(*)": {"inputs": [], "outputs": [], "variant": "default_integration_nodes"},
        "create_text_share": {
            "inputs": [
                {
                    "field": "post_text",
                    "type": "string",
                    "value": "",
                    "label": "Post Text",
                    "placeholder": "“I just got a new job!”",
                    "helper_text": "Content you wanted to post on your LinkedIn",
                }
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "URL of the created LinkedIn post",
                }
            ],
            "name": "create_text_share",
            "task_name": "tasks.linkedin.create_text_share",
            "description": "Create text post on LinkedIn",
            "label": "Post to LinkedIn",
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Linkedin",
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_linkedin",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationLinkedinTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_google_calendar")
class IntegrationGoogleCalendarTool(Tool):
    """
    Google Calendar

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### When action = 'new_event'
        all_day_event: Toggle to set the event as an all-day event
        attendees: Email IDs of attendees (comma separated)
        calendar: Select the calendar to add the new event to
        description: The description of the event
        duration: The duration of the event (positive integer). Default: 30 (in minutes)
        event_name: The name of the calendar event
        location: Physical location or the meeting location (like Zoom)
        start_datetime: The start time of the calendar event (format: YYYY-MM-DD for full day event or YYYY-MM-DDTHH:MM:SS for specific time)
    ### When action = 'check_availability'
        calendar: Select the calendar to add the new event to
        end_date_and_time: The last date and end time for everyday to look for availability
        slot_duration: The duration of an individual slot to look for (in minutes). Default: 30 (in minutes)
        start_date_and_time: The first date and start time for everyday to look for availability
        timezone: IANA Time Zone code (e.g., US/Eastern)
    ### When action = 'get_events'
        calendar: Select the calendar to add the new event to
        query: Return only events that contain these keywords
        use_date: Toggle to use dates
    ### When action = 'get_events' and use_date = True and use_exact_date = False
        date_range: The date_range input
    ### When action = 'get_events' and use_date = True and use_exact_date = True
        exact_date: The exact_date input
    ### When action = 'get_events' and use_date = False
        num_messages: Specify the last n numbers of events
    ### When action = 'get_events' and use_date = True
        use_exact_date: Switch between exact date range and relative dates
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Google Calendar>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "new_event**(*)**(*)": {
            "inputs": [
                {
                    "field": "calendar",
                    "type": "string",
                    "label": "Calendar",
                    "helper_text": "Select the calendar to add the new event to",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=calendar_name&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": False,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                    "order": 3,
                },
                {
                    "field": "event_name",
                    "type": "string",
                    "value": "",
                    "label": "Event Name",
                    "placeholder": "Meeting with John Doe",
                    "helper_text": "The name of the calendar event",
                    "order": 4,
                },
                {
                    "field": "all_day_event",
                    "type": "bool",
                    "value": False,
                    "label": "All Day Event",
                    "helper_text": "Toggle to set the event as an all-day event",
                    "order": 5,
                },
                {
                    "field": "start_datetime",
                    "type": "timestamp",
                    "value": -1,
                    "label": "Start Datetime",
                    "placeholder": "2024-06-24 (full day event) or 2024-06-24T19:00:00",
                    "helper_text": "The start time of the calendar event (format: YYYY-MM-DD for full day event or YYYY-MM-DDTHH:MM:SS for specific time)",
                    "order": 6,
                },
                {
                    "field": "duration",
                    "type": "int32",
                    "value": 30,
                    "label": "Duration",
                    "placeholder": "30 minutes",
                    "helper_text": "The duration of the event (positive integer). Default: 30 (in minutes)",
                    "order": 7,
                },
                {
                    "field": "attendees",
                    "type": "string",
                    "value": "",
                    "label": "Attendees",
                    "placeholder": "abc@example.com,xyz@example.com,",
                    "helper_text": "Email IDs of attendees (comma separated)",
                    "order": 8,
                },
                {
                    "field": "location",
                    "type": "string",
                    "value": "",
                    "label": "Location",
                    "placeholder": "800 Howard St., San Francisco, CA 94103",
                    "helper_text": "Physical location or the meeting location (like Zoom)",
                    "order": 9,
                },
                {
                    "field": "description",
                    "type": "string",
                    "value": "",
                    "label": "Description",
                    "placeholder": "Monthly sync",
                    "helper_text": "The description of the event",
                    "order": 10,
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "Calendar event link",
                }
            ],
            "variant": "common_integration_nodes",
            "name": "new_event",
            "task_name": "tasks.google_calendar.create_event",
            "description": "Create a new event",
            "label": "New Event",
            "inputs_sort_order": [
                "integration",
                "action",
                "calendar",
                "event_name",
                "all_day_event",
                "start_datetime",
                "duration",
                "attendees",
                "location",
                "description",
            ],
        },
        "check_availability**(*)**(*)": {
            "inputs": [
                {
                    "field": "calendar",
                    "type": "string",
                    "label": "Calendar",
                    "helper_text": "Select the calendar to check availability",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=calendar_name&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": False,
                            "supports_pagination": False,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                    "order": 3,
                },
                {
                    "field": "start_date_and_time",
                    "type": "timestamp",
                    "value": -1,
                    "label": "Start Date & Start Work Time",
                    "placeholder": "2024-06-24",
                    "helper_text": "The first date and start time for everyday to look for availability",
                    "order": 4,
                },
                {
                    "field": "end_date_and_time",
                    "type": "timestamp",
                    "value": -1,
                    "label": "End Date & End Work Time",
                    "placeholder": "2024-06-24",
                    "helper_text": "The last date and end time for everyday to look for availability",
                    "order": 5,
                },
                {
                    "field": "slot_duration",
                    "type": "int32",
                    "value": 30,
                    "label": "Slot Duration",
                    "placeholder": "30 minutes",
                    "helper_text": "The duration of an individual slot to look for (in minutes). Default: 30 (in minutes)",
                    "order": 6,
                },
                {
                    "field": "timezone",
                    "type": "enum<string>",
                    "value": "US/Eastern",
                    "label": "Timezone",
                    "placeholder": "US/Eastern",
                    "helper_text": "IANA Time Zone code (e.g., US/Eastern)",
                    "component": {"type": "dropdown", "referenced_options": "timezone"},
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "List of available time slots",
                }
            ],
            "variant": "common_integration_nodes",
            "name": "check_availability",
            "task_name": "tasks.google_calendar.check_availability",
            "description": "Check Google calendar availability",
            "label": "Check Availability",
            "inputs_sort_order": [
                "integration",
                "action",
                "calendar",
                "start_date_and_time",
                "end_date_and_time",
                "slot_duration",
                "timezone",
            ],
        },
        "get_events**(*)**(*)": {
            "inputs": [
                {
                    "field": "calendar",
                    "type": "string",
                    "label": "Calendar",
                    "helper_text": "Select the calendar to read events from",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=calendar_name&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": False,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                    "order": 3,
                },
                {
                    "field": "use_date",
                    "type": "bool",
                    "value": False,
                    "show_date_range": True,
                    "label": "Use Date",
                    "helper_text": "Toggle to use dates",
                },
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "Query",
                    "helper_text": "Return only events that contain these keywords",
                    "placeholder": "Keywords to filter events",
                },
            ],
            "outputs": [
                {
                    "field": "event_ids",
                    "type": "vec<string>",
                    "helper_text": "List of event IDs",
                },
                {
                    "field": "summaries",
                    "type": "vec<string>",
                    "helper_text": "List of event summaries",
                },
                {
                    "field": "start_times",
                    "type": "vec<string>",
                    "helper_text": "List of event start times",
                },
                {
                    "field": "end_times",
                    "type": "vec<string>",
                    "helper_text": "List of event end times",
                },
                {
                    "field": "locations",
                    "type": "vec<string>",
                    "helper_text": "List of event locations",
                },
                {
                    "field": "organizers",
                    "type": "vec<string>",
                    "helper_text": "List of event organizers",
                },
                {
                    "field": "attendees",
                    "type": "vec<vec<string>>",
                    "helper_text": "List of event attendees",
                },
                {
                    "field": "details",
                    "type": "vec<string>",
                    "helper_text": "List of event details",
                },
            ],
            "variant": "get_integration_nodes",
            "name": "get_events",
            "task_name": "tasks.google_calendar.get_events",
            "description": "Get events from Google Calendar",
            "label": "Get Events",
            "inputs_sort_order": [
                "integration",
                "action",
                "calendar",
                "use_date",
                "use_exact_date",
                "date_range",
                "exact_date",
                "num_messages",
                "query",
            ],
        },
        "get_events**false**(*)": {
            "inputs": [
                {
                    "field": "num_messages",
                    "type": "int32",
                    "value": 10,
                    "show_date_range": True,
                    "label": "Number of Events",
                    "helper_text": "Specify the last n numbers of events",
                }
            ],
            "outputs": [],
        },
        "get_events**true**(*)": {
            "inputs": [
                {
                    "field": "use_exact_date",
                    "type": "bool",
                    "value": False,
                    "show_date_range": True,
                    "label": "Use Exact Date",
                    "helper_text": "Switch between exact date range and relative dates",
                }
            ],
            "outputs": [],
        },
        "get_events**true**false": {
            "inputs": [
                {
                    "field": "date_range",
                    "type": "Dict[str, Any]",
                    "value": {
                        "date_type": "Last",
                        "date_value": 1,
                        "date_period": "Months",
                    },
                    "show_date_range": True,
                    "hidden": True,
                    "label": "Date range",
                    "component": {"type": "date_range"},
                }
            ],
            "outputs": [],
        },
        "get_events**true**true": {
            "inputs": [
                {
                    "field": "exact_date",
                    "type": "Dict[str, Any]",
                    "value": {"start": "", "end": ""},
                    "show_date_range": True,
                    "label": "Exact date",
                    "component": {"type": "date_range"},
                }
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["action", "use_date", "use_exact_date"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Google Calendar",
        calendar: Optional[str] | ToolInput = None,
        action: str | ToolInput = "",
        use_date: bool | ToolInput = False,
        use_exact_date: bool | ToolInput = False,
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action
        if isinstance(use_date, ToolInput):
            if use_date.type == "static":
                params["use_date"] = use_date.value
            else:
                raise ValueError(f"use_date cannot be a dynamic input")
        else:
            params["use_date"] = use_date
        if isinstance(use_exact_date, ToolInput):
            if use_exact_date.type == "static":
                params["use_exact_date"] = use_exact_date.value
            else:
                raise ValueError(f"use_exact_date cannot be a dynamic input")
        else:
            params["use_exact_date"] = use_exact_date

        super().__init__(
            tool_type="integration_google_calendar",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if calendar is not None:
            if isinstance(calendar, ToolInput):
                self.inputs["calendar"] = {
                    "type": calendar.type,
                    "value": calendar.value or calendar.description,
                }
            else:
                self.inputs["calendar"] = {"type": "static", "value": calendar}
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}
        if use_date is not None:
            if isinstance(use_date, ToolInput):
                self.inputs["use_date"] = {
                    "type": use_date.type,
                    "value": use_date.value or use_date.description,
                }
            else:
                self.inputs["use_date"] = {"type": "static", "value": use_date}
        if use_exact_date is not None:
            if isinstance(use_exact_date, ToolInput):
                self.inputs["use_exact_date"] = {
                    "type": use_exact_date.type,
                    "value": use_exact_date.value or use_exact_date.description,
                }
            else:
                self.inputs["use_exact_date"] = {
                    "type": "static",
                    "value": use_exact_date,
                }

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationGoogleCalendarTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_microsoft_calendar")
class IntegrationMicrosoftCalendarTool(Tool):
    """
    Microsoft Calendar

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### new_event
        all_day_event: Toggle to set the event as an all-day event
        attendees: Email IDs of attendees (comma separated)
        body: Description or agenda of the event
        calendar: Select the calendar to add the new event to
        duration: The duration of the event in minutes. Default: 30 (in minutes)
        location: The location of the meeting
        start_datetime: The start date and time of the calendar event (format: YYYY-MM-DDTHH:MM:SS)
        subject: Name/Subject of the calendar event
    ### check_availability
        end_date_and_time: The last date and end time for everyday to look for availability
        slot_duration: The duration of an individual slot to look for (in minutes). Default: 30 (in minutes)
        start_date_and_time: The first date and start time for everyday to look for availability
        timezone: IANA Time Zone code (e.g., US/Eastern)
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Microsoft Calendar>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "(*)": {"inputs": [], "outputs": [], "variant": "common_integration_nodes"},
        "new_event": {
            "inputs": [
                {
                    "field": "calendar",
                    "type": "string",
                    "label": "Calendar",
                    "helper_text": "Select the calendar to add the new event to",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=calendar&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": False,
                            "supports_pagination": False,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
                {
                    "field": "subject",
                    "type": "string",
                    "value": "",
                    "label": "Subject",
                    "placeholder": "Sprint planning",
                    "helper_text": "Name/Subject of the calendar event",
                },
                {
                    "field": "body",
                    "type": "string",
                    "value": "",
                    "label": "Body",
                    "placeholder": "This meeting is to discuss...",
                    "helper_text": "Description or agenda of the event",
                },
                {
                    "field": "start_datetime",
                    "type": "timestamp",
                    "value": "",
                    "label": "Start Datetime",
                    "placeholder": "2024-06-24T19:00:00",
                    "helper_text": "The start date and time of the calendar event (format: YYYY-MM-DDTHH:MM:SS)",
                },
                {
                    "field": "all_day_event",
                    "type": "bool",
                    "value": False,
                    "label": "All Day Event",
                    "helper_text": "Toggle to set the event as an all-day event",
                },
                {
                    "field": "duration",
                    "type": "int32",
                    "value": 30,
                    "label": "Duration",
                    "placeholder": "30 minutes",
                    "helper_text": "The duration of the event in minutes. Default: 30 (in minutes)",
                },
                {
                    "field": "location",
                    "type": "string",
                    "value": "",
                    "label": "Location",
                    "placeholder": "800 Howard St., San Francisco, CA 94103",
                    "helper_text": "The location of the meeting",
                },
                {
                    "field": "attendees",
                    "type": "string",
                    "value": "",
                    "label": "Attendees",
                    "placeholder": "abc@example.com,xyz@example.com",
                    "helper_text": "Email IDs of attendees (comma separated)",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "Calendar event link",
                }
            ],
            "name": "new_event",
            "task_name": "tasks.microsoft_calendar.create_event",
            "description": "Create a new calendar event",
            "label": "New Event",
            "inputs_sort_order": [
                "integration",
                "action",
                "calendar",
                "subject",
                "body",
                "all_day_event",
                "start_datetime",
                "duration",
                "location",
                "attendees",
            ],
        },
        "check_availability": {
            "inputs": [
                {
                    "field": "start_date_and_time",
                    "type": "timestamp",
                    "value": "",
                    "label": "Start Date & Start Work Time",
                    "placeholder": "2024-06-24",
                    "helper_text": "The first date and start time for everyday to look for availability",
                },
                {
                    "field": "end_date_and_time",
                    "type": "timestamp",
                    "value": "",
                    "label": "End Date & End Work Time",
                    "placeholder": "2024-06-24",
                    "helper_text": "The last date and end time for everyday to look for availability",
                },
                {
                    "field": "slot_duration",
                    "type": "int32",
                    "value": "",
                    "label": "Slot duration",
                    "placeholder": "30 minutes",
                    "helper_text": "The duration of an individual slot to look for (in minutes). Default: 30 (in minutes)",
                },
                {
                    "field": "timezone",
                    "type": "enum<string>",
                    "value": "US/Eastern",
                    "label": "Timezone",
                    "placeholder": "US/Eastern",
                    "helper_text": "IANA Time Zone code (e.g., US/Eastern)",
                    "component": {"type": "dropdown", "referenced_options": "timezone"},
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "List of available time slots with start and end datetimes",
                }
            ],
            "name": "check_availability",
            "task_name": "tasks.microsoft_calendar.check_availability",
            "description": "Check Microsoft calendar availability",
            "label": "Check Availability",
            "inputs_sort_order": [
                "integration",
                "action",
                "timezone",
                "start_date_and_time",
                "end_date_and_time",
                "slot_duration",
            ],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Microsoft Calendar",
        calendar: Optional[str] | ToolInput = None,
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_microsoft_calendar",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if calendar is not None:
            if isinstance(calendar, ToolInput):
                self.inputs["calendar"] = {
                    "type": calendar.type,
                    "value": calendar.value or calendar.description,
                }
            else:
                self.inputs["calendar"] = {"type": "static", "value": calendar}
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationMicrosoftCalendarTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_mailgun")
class IntegrationMailgunTool(Tool):
    """
    Mailgun

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### send_mail
        bcc_recipients: The email(s) of the recipient(s) you want to BCC the email to
        body: The body (message) of the email
        cc_recipients: The email(s) of the recipient(s) you want to CC the email to
        domain: Your Mailgun domain
        from_email: The email of the sender of the email
        from_name: The name of the sender of the email
        recipients: The email of the recipient you want to send the email to
        subject: The subject of the email
    ### add_contact_to_mailing_list
        email: The email of the contact to be added to the list
        list_name: The list the contact will be added to
        name: The name of contact to be added to the list
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Mailgun>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "(*)": {"inputs": [], "outputs": [], "variant": "common_integration_nodes"},
        "send_mail": {
            "inputs": [
                {
                    "field": "domain",
                    "type": "string",
                    "label": "Domain",
                    "agent_field_type": "static",
                    "helper_text": "Your Mailgun domain",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=domain_name&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": False,
                            "supports_pagination": False,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
                {
                    "field": "subject",
                    "type": "string",
                    "value": "",
                    "label": "Subject",
                    "placeholder": "Important: Your Account Update",
                    "helper_text": "The subject of the email",
                },
                {
                    "field": "body",
                    "type": "string",
                    "value": "",
                    "label": "Body",
                    "placeholder": "Dear valued customer...",
                    "helper_text": "The body (message) of the email",
                },
                {
                    "field": "from_name",
                    "type": "string",
                    "value": "",
                    "label": "The name of the sender",
                    "placeholder": "John Smith",
                    "helper_text": "The name of the sender of the email",
                },
                {
                    "field": "from_email",
                    "type": "string",
                    "value": "",
                    "label": "The Email of the sender",
                    "placeholder": "john@company.com",
                    "helper_text": "The email of the sender of the email",
                },
                {
                    "field": "recipients",
                    "type": "string",
                    "value": "",
                    "label": "Recipients email address",
                    "placeholder": "recipient@example.com",
                    "helper_text": "The email of the recipient you want to send the email to",
                },
                {
                    "field": "cc_recipients",
                    "type": "string",
                    "value": "",
                    "label": "CC Recipients email address",
                    "placeholder": "cc1@example.com, cc2@example.com",
                    "helper_text": "The email(s) of the recipient(s) you want to CC the email to",
                },
                {
                    "field": "bcc_recipients",
                    "type": "string",
                    "value": "",
                    "label": "BCC Recipients email address",
                    "placeholder": "bcc1@example.com, bcc2@example.com",
                    "helper_text": "The email(s) of the recipient(s) you want to BCC the email to",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "Status of the email sending operation",
                }
            ],
            "name": "send_mail",
            "task_name": "tasks.mailgun.send_mail",
            "description": "Send mail ",
            "label": "Send mail",
        },
        "add_contact_to_mailing_list": {
            "inputs": [
                {
                    "field": "list_name",
                    "type": "string",
                    "value": "",
                    "label": "Name of the mailing list",
                    "placeholder": "newsletter-subscribers",
                    "helper_text": "The list the contact will be added to",
                    "agent_field_type": "static",
                },
                {
                    "field": "name",
                    "type": "string",
                    "value": "",
                    "label": "Name of the contact to add",
                    "placeholder": "John Smith",
                    "helper_text": "The name of contact to be added to the list",
                },
                {
                    "field": "email",
                    "type": "string",
                    "value": "",
                    "label": "Email of the contact to add",
                    "placeholder": "john@example.com",
                    "helper_text": "The email of the contact to be added to the list",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "Status of the contact addition operation",
                }
            ],
            "name": "add_contact_to_mailing_list",
            "task_name": "tasks.mailgun.add_contact_to_mailing_list",
            "description": "Adds a contact to a Mailgun Mailing list",
            "label": "Add Contact to Mailing List",
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Mailgun",
        domain: Optional[str] | ToolInput = None,
        list_name: str | ToolInput = "",
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_mailgun",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if domain is not None:
            if isinstance(domain, ToolInput):
                self.inputs["domain"] = {
                    "type": domain.type,
                    "value": domain.value or domain.description,
                }
            else:
                self.inputs["domain"] = {"type": "static", "value": domain}
        if list_name is not None:
            if isinstance(list_name, ToolInput):
                self.inputs["list_name"] = {
                    "type": list_name.type,
                    "value": list_name.value or list_name.description,
                }
            else:
                self.inputs["list_name"] = {"type": "static", "value": list_name}
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationMailgunTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_google_docs")
class IntegrationGoogleDocsTool(Tool):
    """
    Google Docs

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### read_doc_url
        doc_url: Enter the public URL of the Google Doc
    ### read_doc
        file_id: Select a File to read
    ### write_to_doc
        file_id: Select a File to read
        text: The text that will be added to the File
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Google Docs>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "(*)": {
            "inputs": [],
            "outputs": [],
            "variant": "common_integration_file_nodes",
        },
        "read_doc": {
            "inputs": [
                {
                    "field": "file_id",
                    "type": "string",
                    "hidden": True,
                    "label": "File",
                    "helper_text": "Select a File to read",
                    "component": {
                        "type": "folder",
                        "dynamic_config": {
                            "metadata_endpoint": "/{prefix}/metadata/children/{inputs.integration.object_id}?parent_id={}&page={}&page_size={dynamic_config.page_size}&directory={dynamic_config.show_only_directories}&q={}",
                            "tree_endpoint": "/{prefix}/metadata/get-tree/{inputs.integration.object_id}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "show_only_directories": False,
                        },
                        "multi_select": False,
                        "select_directories": False,
                        "select_file": True,
                    },
                    "agent_field_type": "static",
                }
            ],
            "outputs": [
                {
                    "field": "text",
                    "type": "string",
                    "helper_text": "The text content of the selected file",
                }
            ],
            "name": "read_doc",
            "task_name": "tasks.google_docs.read_doc",
            "description": "Retrieves and returns the plain text content of a user-selected Google Doc.",
            "label": "Read Google Doc",
        },
        "write_to_doc": {
            "inputs": [
                {
                    "field": "file_id",
                    "type": "string",
                    "hidden": True,
                    "label": "File",
                    "helper_text": "Select a File to append the text to",
                    "component": {
                        "type": "folder",
                        "dynamic_config": {
                            "metadata_endpoint": "/{prefix}/metadata/children/{inputs.integration.object_id}?parent_id={}&page={}&page_size={dynamic_config.page_size}&directory={dynamic_config.show_only_directories}&q={}",
                            "tree_endpoint": "/{prefix}/metadata/get-tree/{inputs.integration.object_id}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "show_only_directories": False,
                        },
                        "multi_select": False,
                        "select_directories": False,
                        "select_file": True,
                    },
                },
                {
                    "field": "text",
                    "type": "string",
                    "value": "",
                    "label": "Text",
                    "placeholder": "Hello World!",
                    "helper_text": "The text that will be added to the File",
                },
            ],
            "outputs": [],
            "name": "write_to_doc",
            "task_name": "tasks.google_docs.write_to_doc",
            "description": "Append text to an existing document",
            "label": "Append Text to Document",
        },
        "read_doc_url": {
            "inputs": [
                {
                    "field": "doc_url",
                    "type": "string",
                    "value": "",
                    "label": "Google Doc URL",
                    "helper_text": "Enter the public URL of the Google Doc",
                    "placeholder": "Enter the public URL of the Google Doc",
                    "agent_field_type": "static",
                }
            ],
            "outputs": [
                {
                    "field": "content",
                    "type": "string",
                    "helper_text": "HTML body of the Google Doc",
                }
            ],
            "variant": "default_integration_nodes",
            "banner_text": 'Ensure that the Google Docs\'s permissions is set to "Anyone with the Link"',
            "name": "read_doc_url",
            "task_name": "tasks.google_docs.read_doc_url",
            "description": "Download the contents of a publicly accessible Google Docs file using its shared URL",
            "label": "Read from Doc URL",
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Google Docs",
        doc_url: str | ToolInput = "",
        file_id: Optional[str] | ToolInput = None,
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_google_docs",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if doc_url is not None:
            if isinstance(doc_url, ToolInput):
                self.inputs["doc_url"] = {
                    "type": doc_url.type,
                    "value": doc_url.value or doc_url.description,
                }
            else:
                self.inputs["doc_url"] = {"type": "static", "value": doc_url}
        if file_id is not None:
            if isinstance(file_id, ToolInput):
                self.inputs["file_id"] = {
                    "type": file_id.type,
                    "value": file_id.value or file_id.description,
                }
            else:
                self.inputs["file_id"] = {"type": "static", "value": file_id}
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationGoogleDocsTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_microsoft")
class IntegrationMicrosoftTool(Tool):
    """
    One Drive

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### add_file
        file: Select or Upload a file
        item_id: Select the folder within your OneDrive to add the file
    ### read_file
        item_id: Select the folder within your OneDrive to add the file
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Microsoft>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "(*)": {
            "inputs": [],
            "outputs": [],
            "variant": "common_integration_file_nodes",
        },
        "add_file": {
            "inputs": [
                {
                    "field": "item_id",
                    "type": "string",
                    "hidden": True,
                    "label": "Folder",
                    "helper_text": "Select the folder within your OneDrive to add the file",
                    "component": {
                        "type": "folder",
                        "dynamic_config": {
                            "metadata_endpoint": "/{prefix}/metadata/children/{inputs.integration.object_id}?parent_id={}&page={}&page_size={dynamic_config.page_size}&directory={dynamic_config.show_only_directories}&q={}",
                            "tree_endpoint": "/{prefix}/metadata/get-tree/{inputs.integration.object_id}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "show_only_directories": True,
                        },
                        "multi_select": False,
                        "select_directories": True,
                        "select_file": False,
                    },
                    "agent_field_type": "static",
                },
                {
                    "field": "file",
                    "type": "file",
                    "value": "",
                    "label": "File",
                    "placeholder": "Select a file",
                    "helper_text": "Select or Upload a file",
                },
            ],
            "outputs": [],
            "name": "add_file",
            "task_name": "tasks.microsoft.add_file",
            "description": "Add file to OneDrive",
            "label": "Add File",
        },
        "read_file": {
            "inputs": [
                {
                    "field": "item_id",
                    "type": "string",
                    "hidden": True,
                    "label": "File",
                    "helper_text": "Select the file to read from OneDrive",
                    "component": {
                        "type": "folder",
                        "dynamic_config": {
                            "endpoint": "",
                            "query": {"field": "parent_id"},
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "show_only_directories": False,
                        },
                        "multi_select": False,
                        "select_directories": False,
                        "select_file": True,
                    },
                    "agent_field_type": "static",
                }
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "The content of the selected file",
                }
            ],
            "name": "read_file",
            "task_name": "tasks.microsoft.read_file",
            "description": "Read file from OneDrive",
            "label": "Read File",
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "One Drive",
        item_id: Optional[str] | ToolInput = None,
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_microsoft",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if item_id is not None:
            if isinstance(item_id, ToolInput):
                self.inputs["item_id"] = {
                    "type": item_id.type,
                    "value": item_id.value or item_id.description,
                }
            else:
                self.inputs["item_id"] = {"type": "static", "value": item_id}
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationMicrosoftTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_typeform")
class IntegrationTypeformTool(Tool):
    """
    Typeform

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### get_responses
        form_id: Select the form from which to get the responses
        number_of_responses: The number of responses to fetch
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Typeform>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "get_responses": {
            "inputs": [
                {
                    "field": "form_id",
                    "type": "string",
                    "value": "",
                    "hidden": True,
                    "label": "Form",
                    "helper_text": "Select the form from which to get the responses",
                    "component": {
                        "type": "folder",
                        "dynamic_config": {
                            "metadata_endpoint": "/{prefix}/metadata/children/{inputs.integration.object_id}?parent_id={}&page={}&page_size={dynamic_config.page_size}&directory={dynamic_config.show_only_directories}&q={}",
                            "tree_endpoint": "/{prefix}/metadata/get-tree/{inputs.integration.object_id}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "show_only_directories": False,
                        },
                        "multi_select": False,
                        "select_directories": False,
                        "select_file": True,
                    },
                    "agent_field_type": "static",
                },
                {
                    "field": "number_of_responses",
                    "type": "string",
                    "value": "",
                    "label": "Number of responses",
                    "placeholder": "5",
                    "helper_text": "The number of responses to fetch",
                },
            ],
            "outputs": [
                {
                    "field": "list_of_responses",
                    "type": "vec<string>",
                    "helper_text": "The responses in list format",
                }
            ],
            "name": "get_responses",
            "task_name": "tasks.typeform.get_responses",
            "description": "Get Form Responses From Typeform",
            "label": "Get Form Responses",
            "variant": "common_integration_file_nodes",
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Typeform",
        form_id: str | ToolInput = "",
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_typeform",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if form_id is not None:
            if isinstance(form_id, ToolInput):
                self.inputs["form_id"] = {
                    "type": form_id.type,
                    "value": form_id.value or form_id.description,
                }
            else:
                self.inputs["form_id"] = {"type": "static", "value": form_id}
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationTypeformTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_dropbox")
class IntegrationDropboxTool(Tool):
    """
    Dropbox

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### post_file
        file: Select or Upload a file
        folder_id: Select the folder where you want to post the file to
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Dropbox>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "post_file": {
            "inputs": [
                {
                    "field": "folder_id",
                    "type": "string",
                    "value": "",
                    "hidden": True,
                    "label": "Folder",
                    "helper_text": "Select the folder where you want to post the file to",
                    "component": {
                        "type": "folder",
                        "dynamic_config": {
                            "metadata_endpoint": "/{prefix}/metadata/children/{inputs.integration.object_id}?parent_id={}&page={}&page_size={dynamic_config.page_size}&directory={dynamic_config.show_only_directories}&q={}",
                            "tree_endpoint": "/{prefix}/metadata/get-tree/{inputs.integration.object_id}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "show_only_directories": True,
                        },
                        "multi_select": False,
                        "select_directories": True,
                        "select_file": False,
                    },
                    "agent_field_type": "static",
                },
                {
                    "field": "file",
                    "type": "file",
                    "value": "",
                    "label": "File",
                    "placeholder": "Select a file",
                    "helper_text": "Select or Upload a file",
                },
            ],
            "outputs": [],
            "name": "post_file",
            "task_name": "tasks.dropbox.post_file",
            "description": "Post file to Dropbox",
            "label": "Post file",
            "variant": "common_integration_file_nodes",
            "inputs_sort_order": ["integration", "action", "folder_id", "file"],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Dropbox",
        folder_id: str | ToolInput = "",
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_dropbox",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if folder_id is not None:
            if isinstance(folder_id, ToolInput):
                self.inputs["folder_id"] = {
                    "type": folder_id.type,
                    "value": folder_id.value or folder_id.description,
                }
            else:
                self.inputs["folder_id"] = {"type": "static", "value": folder_id}
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationDropboxTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_box")
class IntegrationBoxTool(Tool):
    """
    Box

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### upload_files
        files: The number of files to be appended. Files will be appended in successive fashion (e.g., file-1 first, then file-2, etc.)
        folder_id: Select the Folder to upload files to
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Box>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "upload_files": {
            "inputs": [
                {
                    "field": "folder_id",
                    "type": "string",
                    "value": "",
                    "hidden": True,
                    "label": "Folder",
                    "helper_text": "Select the Folder to upload files to",
                    "component": {
                        "type": "folder",
                        "dynamic_config": {
                            "metadata_endpoint": "/{prefix}/metadata/children/{inputs.integration.object_id}?parent_id={}&page={}&page_size={dynamic_config.page_size}&directory={dynamic_config.show_only_directories}&q={}",
                            "tree_endpoint": "/{prefix}/metadata/get-tree/{inputs.integration.object_id}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "show_only_directories": True,
                        },
                        "multi_select": False,
                        "select_directories": True,
                        "select_file": False,
                    },
                    "agent_field_type": "static",
                },
                {
                    "field": "files",
                    "type": "vec<file>",
                    "value": [""],
                    "label": "Files",
                    "placeholder": "Files",
                    "helper_text": "The number of files to be appended. Files will be appended in successive fashion (e.g., file-1 first, then file-2, etc.)",
                },
            ],
            "outputs": [],
            "name": "upload_files",
            "task_name": "tasks.box.upload_files",
            "description": "Upload files to Box",
            "label": "Upload files",
            "variant": "common_integration_file_nodes",
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Box",
        folder_id: str | ToolInput = "",
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_box",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if folder_id is not None:
            if isinstance(folder_id, ToolInput):
                self.inputs["folder_id"] = {
                    "type": folder_id.type,
                    "value": folder_id.value or folder_id.description,
                }
            else:
                self.inputs["folder_id"] = {"type": "static", "value": folder_id}
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationBoxTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_google_drive")
class IntegrationGoogleDriveTool(Tool):
    """
    Google Drive

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### When action = 'get_files'
        corpora: Scope to search in: 'user' (files owned/shared to user) or 'domain' (files shared to user's domain)
        drive_id: ID of the shared drive to search
        fields: Comma-separated list of fields to include in the response
        include_items_from_all_drives: Whether to include items from all drives, including shared drives
        include_labels: Comma-separated list of label IDs to include in the response
        include_permissions_for_view: Additional view's permissions to include (only 'published' supported)
        order_by: Sort order for files (e.g., 'folder,name,modifiedTime desc')
        query: Search query for filtering files (see Drive API documentation for syntax)
        spaces: Comma-separated list of spaces to search ('drive', 'appDataFolder')
        supports_all_drives: Whether the application supports both My Drives and shared drives
        use_date: Toggle to use dates
    ### When action = 'get_files' and use_date = True and use_exact_date = False
        date_range: The date_range input
    ### When action = 'read_file_url'
        drive_file_url: The URL of the drive file to read.
    ### When action = 'get_files' and use_date = True and use_exact_date = True
        exact_date: The exact_date input
    ### When action = 'save_drive'
        file: Select or Upload a file
        folder_id: Select the folder within your Google Drive to save the file
    ### When action = 'read_drive'
        file_id: Select the file to read
    ### When action = 'get_files' and use_date = False
        num_messages: Specify the number of files to fetch
    ### When action = 'get_files' and use_date = True
        use_exact_date: Switch between exact date range and relative dates
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Google Drive>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "(*)**(*)**(*)": {
            "inputs": [],
            "outputs": [],
            "variant": "common_integration_file_nodes",
        },
        "read_drive**(*)**(*)": {
            "inputs": [
                {
                    "field": "file_id",
                    "type": "string",
                    "value": "",
                    "hidden": True,
                    "label": "File",
                    "helper_text": "Select the file to read",
                    "component": {
                        "type": "folder",
                        "dynamic_config": {
                            "metadata_endpoint": "/{prefix}/metadata/children/{inputs.integration.object_id}?parent_id={}&page={}&page_size={dynamic_config.page_size}&directory={dynamic_config.show_only_directories}&q={}",
                            "tree_endpoint": "/{prefix}/metadata/get-tree/{inputs.integration.object_id}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "show_only_directories": False,
                        },
                        "multi_select": False,
                        "select_directories": False,
                        "select_file": True,
                    },
                    "agent_field_type": "static",
                }
            ],
            "outputs": [
                {
                    "field": "text",
                    "type": "string",
                    "helper_text": "The text content of the selected file",
                }
            ],
            "name": "read_drive",
            "task_name": "tasks.google_drive.read_drive",
            "description": "Download a user-selected file from their Google Drive using its file ID",
            "label": "Read file",
            "inputs_sort_order": ["integration", "action", "file_id"],
        },
        "save_drive**(*)**(*)": {
            "inputs": [
                {
                    "field": "folder_id",
                    "type": "string",
                    "value": "",
                    "hidden": True,
                    "label": "Folder",
                    "helper_text": "Select the folder within your Google Drive to save the file",
                    "component": {
                        "type": "folder",
                        "dynamic_config": {
                            "metadata_endpoint": "/{prefix}/metadata/children/{inputs.integration.object_id}?parent_id={}&page={}&page_size={dynamic_config.page_size}&directory={dynamic_config.show_only_directories}&q={}",
                            "tree_endpoint": "/{prefix}/metadata/get-tree/{inputs.integration.object_id}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "show_only_directories": True,
                        },
                        "multi_select": False,
                        "select_directories": True,
                        "select_file": False,
                    },
                    "agent_field_type": "static",
                },
                {
                    "field": "file",
                    "type": "file",
                    "value": "",
                    "label": "File",
                    "placeholder": "Select a file",
                    "helper_text": "Select or Upload a file",
                },
            ],
            "outputs": [],
            "name": "save_drive",
            "task_name": "tasks.google_drive.save_drive",
            "description": "Save a file to Google Drive",
            "label": "Save file",
            "inputs_sort_order": ["integration", "action", "folder_id", "file"],
        },
        "read_file_url**(*)**(*)": {
            "inputs": [
                {
                    "field": "drive_file_url",
                    "type": "string",
                    "value": "",
                    "helper_text": "The URL of the drive file to read.",
                    "label": "File URL",
                    "placeholder": "Enter the URL of the drive file to read.",
                    "agent_field_type": "static",
                }
            ],
            "outputs": [
                {
                    "field": "file",
                    "type": "file",
                    "label": "File",
                    "helper_text": "The file fetched from the URL.",
                }
            ],
            "variant": "default_integration_nodes",
            "banner_text": 'Ensure that the Google Drive\'s permissions is set to "Anyone with the Link"',
            "name": "read_file_url",
            "task_name": "tasks.google_drive.read_file_url",
            "description": "Download the contents of a publicly accessible Google Drive file using its shared URL",
            "label": "Read file from URL",
            "inputs_sort_order": ["integration", "action", "drive_file_url"],
        },
        "get_files**(*)**(*)": {
            "inputs": [
                {
                    "field": "use_date",
                    "type": "bool",
                    "value": False,
                    "show_date_range": True,
                    "label": "Use Date",
                    "helper_text": "Toggle to use dates",
                    "order": 4,
                },
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "Search Query",
                    "helper_text": "Search query for filtering files (see Drive API documentation for syntax)",
                    "placeholder": "",
                },
                {
                    "field": "order_by",
                    "type": "string",
                    "value": "",
                    "label": "Order By",
                    "helper_text": "Sort order for files (e.g., 'folder,name,modifiedTime desc')",
                    "placeholder": "",
                },
                {
                    "field": "corpora",
                    "type": "string",
                    "value": "",
                    "label": "Search Scope",
                    "helper_text": "Scope to search in: 'user' (files owned/shared to user) or 'domain' (files shared to user's domain)",
                    "placeholder": "Eg. User or Domain",
                },
                {
                    "field": "drive_id",
                    "type": "string",
                    "value": "",
                    "label": "Drive ID",
                    "helper_text": "ID of the shared drive to search",
                },
                {
                    "field": "fields",
                    "type": "string",
                    "value": "",
                    "label": "Fields to Include",
                    "helper_text": "Comma-separated list of fields to include in the response",
                    "placeholder": "Eg. name, id, size, etc.",
                },
                {
                    "field": "include_items_from_all_drives",
                    "type": "bool",
                    "value": True,
                    "label": "Include All Drives",
                    "helper_text": "Whether to include items from all drives, including shared drives",
                },
                {
                    "field": "include_labels",
                    "type": "string",
                    "value": "",
                    "label": "Include Labels",
                    "helper_text": "Comma-separated list of label IDs to include in the response",
                    "placeholder": "",
                },
                {
                    "field": "spaces",
                    "type": "string",
                    "value": "",
                    "label": "Spaces",
                    "helper_text": "Comma-separated list of spaces to search ('drive', 'appDataFolder')",
                    "placeholder": "Eg. drive, appDataFolder",
                },
                {
                    "field": "supports_all_drives",
                    "type": "bool",
                    "value": True,
                    "label": "Supports All Drives",
                    "helper_text": "Whether the application supports both My Drives and shared drives",
                    "placeholder": "",
                },
                {
                    "field": "include_permissions_for_view",
                    "type": "string",
                    "value": "",
                    "label": "Include Permissions View",
                    "helper_text": "Additional view's permissions to include (only 'published' supported)",
                    "placeholder": "",
                },
            ],
            "outputs": [
                {
                    "field": "files",
                    "type": "vec<file>",
                    "helper_text": "The files of the retrieved files",
                    "label": "Files",
                }
            ],
            "variant": "get_integration_nodes",
            "name": "get_files",
            "task_name": "tasks.google_drive.get_files",
            "description": "Search for and return a list of files from the user's Google Drive that match the specified filters",
            "label": "Get Files",
            "inputs_sort_order": [
                "integration",
                "action",
                "use_date",
                "use_exact_date",
                "date_range",
                "exact_date",
                "num_messages",
                "query",
                "order_by",
                "corpora",
                "drive_id",
                "fields",
                "include_items_from_all_drives",
                "include_labels",
                "spaces",
                "supports_all_drives",
                "include_permissions_for_view",
            ],
        },
        "get_files**false**(*)": {
            "inputs": [
                {
                    "field": "num_messages",
                    "type": "int32",
                    "value": 10,
                    "show_date_range": True,
                    "label": "Number of Files",
                    "helper_text": "Specify the number of files to fetch",
                }
            ],
            "outputs": [],
        },
        "get_files**true**(*)": {
            "inputs": [
                {
                    "field": "use_exact_date",
                    "type": "bool",
                    "value": False,
                    "show_date_range": True,
                    "label": "Use Exact Date",
                    "helper_text": "Switch between exact date range and relative dates",
                }
            ],
            "outputs": [],
        },
        "get_files**true**false": {
            "inputs": [
                {
                    "field": "date_range",
                    "type": "Dict[str, Any]",
                    "value": {
                        "date_type": "Last",
                        "date_value": 1,
                        "date_period": "Months",
                    },
                    "show_date_range": True,
                    "label": "Date range",
                    "component": {"type": "date_range"},
                    "order": 6,
                }
            ],
            "outputs": [],
        },
        "get_files**true**true": {
            "inputs": [
                {
                    "field": "exact_date",
                    "type": "Dict[str, Any]",
                    "value": {"start": "", "end": ""},
                    "show_date_range": True,
                    "label": "Exact date",
                    "component": {"type": "date_range"},
                    "order": 7,
                }
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["action", "use_date", "use_exact_date"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Google Drive",
        drive_file_url: str | ToolInput = "",
        file_id: str | ToolInput = "",
        folder_id: str | ToolInput = "",
        action: str | ToolInput = "",
        use_date: bool | ToolInput = False,
        use_exact_date: bool | ToolInput = False,
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action
        if isinstance(use_date, ToolInput):
            if use_date.type == "static":
                params["use_date"] = use_date.value
            else:
                raise ValueError(f"use_date cannot be a dynamic input")
        else:
            params["use_date"] = use_date
        if isinstance(use_exact_date, ToolInput):
            if use_exact_date.type == "static":
                params["use_exact_date"] = use_exact_date.value
            else:
                raise ValueError(f"use_exact_date cannot be a dynamic input")
        else:
            params["use_exact_date"] = use_exact_date

        super().__init__(
            tool_type="integration_google_drive",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if drive_file_url is not None:
            if isinstance(drive_file_url, ToolInput):
                self.inputs["drive_file_url"] = {
                    "type": drive_file_url.type,
                    "value": drive_file_url.value or drive_file_url.description,
                }
            else:
                self.inputs["drive_file_url"] = {
                    "type": "static",
                    "value": drive_file_url,
                }
        if file_id is not None:
            if isinstance(file_id, ToolInput):
                self.inputs["file_id"] = {
                    "type": file_id.type,
                    "value": file_id.value or file_id.description,
                }
            else:
                self.inputs["file_id"] = {"type": "static", "value": file_id}
        if folder_id is not None:
            if isinstance(folder_id, ToolInput):
                self.inputs["folder_id"] = {
                    "type": folder_id.type,
                    "value": folder_id.value or folder_id.description,
                }
            else:
                self.inputs["folder_id"] = {"type": "static", "value": folder_id}
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}
        if use_date is not None:
            if isinstance(use_date, ToolInput):
                self.inputs["use_date"] = {
                    "type": use_date.type,
                    "value": use_date.value or use_date.description,
                }
            else:
                self.inputs["use_date"] = {"type": "static", "value": use_date}
        if use_exact_date is not None:
            if isinstance(use_exact_date, ToolInput):
                self.inputs["use_exact_date"] = {
                    "type": use_exact_date.type,
                    "value": use_exact_date.value or use_exact_date.description,
                }
            else:
                self.inputs["use_exact_date"] = {
                    "type": "static",
                    "value": use_exact_date,
                }

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationGoogleDriveTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_google_sheets")
class IntegrationGoogleSheetsTool(Tool):
    """
    Google Sheets

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: The integration input
    ### When action = 'write_to_sheet' and endpoint_0 = '[endpoint_0.<A>]'
        [<A>.inputs]: The [<A>.inputs] input
    ### When action = 'write_list_to_column' and endpoint_0 = '[endpoint_0.<A>]'
        [<A>.inputs]: The [<A>.inputs] input
    ### When action = 'update_rows' and endpoint_0 = '[endpoint_0.<A>]'
        [<A>.inputs]: The [<A>.inputs] input
    ### When action = 'extract_to_table'
        add_columns_manually: Add data points for some columns manually instead of having them extracted by the AI model.
        additional_context: Additional context for the AI model to extract the table.
        extract_multiple_rows: If checked, it will extract multiple rows of data. If unchecked, it will extract a single row.
        model: The model to use for the Google Sheets integration
        provider: The provider to use for the Google Sheets integration
        sheet_id: Select the Sheet to read from
        text_for_extraction: The text to extract the table from
    ### When action = 'update_rows'
        condition: Conditional Operator
        sheet_id: Select the Sheet to read from
    ### When action = 'extract_to_table' and add_columns_manually = True
        manual_columns: Pass in data to column names manually.
    ### When action = 'read_sheet'
        sheet_id: Select the Sheet to read from
    ### When action = 'read_sheet_url'
        sheet_id: Select the Sheet to read from
        sheet_url: Enter the URL of your Google Spreadsheet
    ### When action = 'write_to_sheet'
        sheet_id: Select the Sheet to read from
    ### When action = 'write_list_to_column'
        sheet_id: Select the Sheet to read from
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "The integration input",
            "value": None,
            "type": "integration<Google Sheets>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "read_sheet**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "sheet_id",
                    "type": "string",
                    "value": "",
                    "agent_field_type": "static",
                    "hidden": True,
                    "label": "Sheet",
                    "helper_text": "Select the Sheet to read from",
                    "component": {
                        "type": "folder",
                        "dynamic_config": {
                            "metadata_endpoint": "/{prefix}/metadata/children/{inputs.integration.object_id}?parent_id={}&page={}&page_size={dynamic_config.page_size}&directory={dynamic_config.show_only_directories}&q={}",
                            "tree_endpoint": "/{prefix}/metadata/get-tree/{inputs.integration.object_id}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "show_only_directories": False,
                        },
                        "multi_select": False,
                        "select_directories": False,
                        "select_file": True,
                    },
                }
            ],
            "outputs": [],
            "name": "read_sheet",
            "task_name": "tasks.google_sheets.read_sheet",
            "description": "Read specified columns from the selected sheet",
            "label": "Read from Sheet",
            "variant": "common_integration_file_nodes",
            "inputs_sort_order": ["integration", "action", "sheet_id"],
        },
        "read_sheet**(*)**[endpoint_0.<A>]**(*)": {
            "inputs": [],
            "outputs": [{"field": "[<A>.outputs]", "type": ""}],
        },
        "read_sheet_url**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "sheet_url",
                    "type": "string",
                    "value": "",
                    "agent_field_type": "static",
                    "label": "Workbook URL",
                    "helper_text": "Enter the URL of your Google Spreadsheet",
                    "order": 3,
                },
                {
                    "field": "sheet_id",
                    "type": "string",
                    "value": "",
                    "agent_field_type": "static",
                    "hidden": True,
                    "label": "Sheet",
                    "helper_text": "Select the Sheet to read from",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/integrations/item/{inputs.integration.object_id}?field=read_sheet_url&parent_id={inputs.sheet_url}"
                        },
                    },
                    "order": 4,
                },
            ],
            "outputs": [],
            "banner_text": 'Ensure that the Google Sheet\'s permissions is set to "Anyone with the Link"',
            "name": "read_sheet_url",
            "task_name": "tasks.google_sheets.read_sheet_url",
            "description": "Read specified columns from the provided sheet URL",
            "label": "Read from Sheet URL",
            "variant": "common_integration_nodes",
            "inputs_sort_order": ["integration", "action", "sheet_url", "sheet_id"],
        },
        "read_sheet_url**(*)**(*)**[endpoint_1.<B>]": {
            "inputs": [],
            "outputs": [{"field": "[<B>.outputs]", "type": ""}],
        },
        "write_to_sheet**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "sheet_id",
                    "type": "string",
                    "value": "",
                    "agent_field_type": "static",
                    "hidden": True,
                    "label": "Sheet",
                    "helper_text": "Select the Sheet to read from",
                    "component": {
                        "type": "folder",
                        "dynamic_config": {
                            "metadata_endpoint": "/{prefix}/metadata/children/{inputs.integration.object_id}?parent_id={}&page={}&page_size={dynamic_config.page_size}&directory={dynamic_config.show_only_directories}&q={}",
                            "tree_endpoint": "/{prefix}/metadata/get-tree/{inputs.integration.object_id}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "show_only_directories": False,
                        },
                        "multi_select": False,
                        "select_directories": False,
                        "select_file": True,
                    },
                }
            ],
            "outputs": [],
            "name": "write_to_sheet",
            "task_name": "tasks.google_sheets.write_to_sheet",
            "description": "Add a new row in the selected sheet",
            "label": "Add New Row",
            "variant": "common_integration_file_nodes",
            "inputs_sort_order": ["integration", "action", "sheet_id"],
        },
        "write_to_sheet**(*)**[endpoint_0.<A>]**(*)": {
            "inputs": [{"field": "[<A>.inputs]", "type": ""}],
            "outputs": [],
        },
        "write_list_to_column**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "sheet_id",
                    "type": "string",
                    "value": "",
                    "hidden": True,
                    "agent_field_type": "static",
                    "label": "Sheet",
                    "helper_text": "Select the Sheet to read from",
                    "component": {
                        "type": "folder",
                        "dynamic_config": {
                            "metadata_endpoint": "/{prefix}/metadata/children/{inputs.integration.object_id}?parent_id={}&page={}&page_size={dynamic_config.page_size}&directory={dynamic_config.show_only_directories}&q={}",
                            "tree_endpoint": "/{prefix}/metadata/get-tree/{inputs.integration.object_id}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "show_only_directories": False,
                        },
                        "multi_select": False,
                        "select_directories": False,
                        "select_file": True,
                    },
                }
            ],
            "outputs": [],
            "name": "write_list_to_column",
            "task_name": "tasks.google_sheets.write_list_to_column",
            "description": "Fill specified columns with the input values (inputs can be list)",
            "label": "Column List Writer",
            "variant": "common_integration_file_nodes",
            "inputs_sort_order": ["integration", "action", "sheet_id"],
        },
        "write_list_to_column**(*)**[endpoint_0.<A>]**(*)": {
            "inputs": [{"field": "[<A>.inputs]", "type": ""}],
            "outputs": [],
        },
        "update_rows**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "sheet_id",
                    "type": "string",
                    "value": "",
                    "hidden": True,
                    "label": "Sheet",
                    "agent_field_type": "static",
                    "helper_text": "Select the Sheet to read from",
                    "component": {
                        "type": "folder",
                        "dynamic_config": {
                            "metadata_endpoint": "/{prefix}/metadata/children/{inputs.integration.object_id}?parent_id={}&page={}&page_size={dynamic_config.page_size}&directory={dynamic_config.show_only_directories}&q={}",
                            "tree_endpoint": "/{prefix}/metadata/get-tree/{inputs.integration.object_id}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "show_only_directories": False,
                        },
                        "multi_select": False,
                        "select_directories": False,
                        "select_file": True,
                    },
                },
                {
                    "field": "condition",
                    "type": "string",
                    "value": "",
                    "label": "Conditional Operator",
                    "placeholder": "",
                    "helper_text": "Conditional Operator",
                },
            ],
            "outputs": [],
            "name": "update_rows",
            "task_name": "tasks.google_sheets.update_rows",
            "description": "Update the rows matching the specified search values",
            "label": "Update Rows",
            "operation": "update",
            "variant": "google_sheet",
            "inputs_sort_order": ["integration", "action", "sheet_id", "condition"],
        },
        "update_rows**(*)**[endpoint_0.<A>]**(*)": {
            "inputs": [{"field": "[<A>.inputs]", "type": ""}],
            "outputs": [],
        },
        "extract_to_table**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "sheet_id",
                    "type": "string",
                    "value": "",
                    "hidden": True,
                    "label": "Sheet",
                    "helper_text": "Select the Sheet to read from",
                    "component": {
                        "type": "folder",
                        "dynamic_config": {
                            "metadata_endpoint": "/{prefix}/metadata/children/{inputs.integration.object_id}?parent_id={}&page={}&page_size={dynamic_config.page_size}&directory={dynamic_config.show_only_directories}&q={}",
                            "tree_endpoint": "/{prefix}/metadata/get-tree/{inputs.integration.object_id}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "show_only_directories": False,
                        },
                        "multi_select": False,
                        "select_directories": False,
                        "select_file": True,
                    },
                },
                {
                    "field": "provider",
                    "type": "enum<string>",
                    "value": "openai",
                    "label": "Provider",
                    "placeholder": "OpenAI",
                    "helper_text": "The provider to use for the Google Sheets integration",
                    "component": {
                        "type": "dropdown",
                        "options": [
                            {"label": "OpenAI", "value": "openai"},
                            {"label": "Anthropic", "value": "anthropic"},
                            {"label": "Cohere", "value": "cohere"},
                            {"label": "Perplexity", "value": "perplexity"},
                            {"label": "Google", "value": "google"},
                            {"label": "Open Source", "value": "together"},
                            {"label": "AWS", "value": "bedrock"},
                            {"label": "Azure", "value": "azure"},
                            {"label": "xAI", "value": "xai"},
                            {"label": "Custom", "value": "custom"},
                        ],
                    },
                    "agent_field_type": "static",
                },
                {
                    "field": "model",
                    "type": "enum<string>",
                    "value": "gpt-4o",
                    "label": "Model",
                    "placeholder": "GPT-4o",
                    "helper_text": "The model to use for the Google Sheets integration",
                    "component": {
                        "type": "dropdown",
                        "referenced_options": "llm_models",
                    },
                    "agent_field_type": "static",
                },
                {
                    "field": "text_for_extraction",
                    "type": "string",
                    "value": "",
                    "label": "Text for Extraction",
                    "placeholder": "Extract the table from the following text",
                    "helper_text": "The text to extract the table from",
                },
                {
                    "field": "extract_multiple_rows",
                    "type": "bool",
                    "value": True,
                    "label": "Extract Multiple Rows",
                    "helper_text": "If checked, it will extract multiple rows of data. If unchecked, it will extract a single row.",
                },
                {
                    "field": "add_columns_manually",
                    "type": "bool",
                    "value": False,
                    "label": "Add Columns Manually",
                    "helper_text": "Add data points for some columns manually instead of having them extracted by the AI model.",
                },
                {
                    "field": "additional_context",
                    "type": "string",
                    "value": "",
                    "label": "Additional Context",
                    "placeholder": "Additional context for the AI model to extract the table.",
                    "helper_text": "Additional context for the AI model to extract the table.",
                },
            ],
            "outputs": [
                {
                    "field": "table",
                    "type": "file",
                    "helper_text": "The table extracted from the text",
                }
            ],
            "name": "extract_to_table",
            "task_name": "tasks.google_sheets.extract_to_table",
            "description": "Extract data from text to a table with AI",
            "label": "Extract to Table",
            "variant": "google_sheet",
            "inputs_sort_order": [
                "integration",
                "action",
                "sheet_id",
                "text_for_extraction",
                "additional_context",
                "extract_multiple_rows",
                "add_columns_manually",
                "manual_columns",
                "provider",
                "model",
            ],
        },
        "extract_to_table**false**(*)**(*)": {"inputs": [], "outputs": []},
        "extract_to_table**true**(*)**(*)": {
            "inputs": [
                {
                    "field": "manual_columns",
                    "type": "vec<Dict[str, Any]>",
                    "value": [],
                    "label": "Manual Columns",
                    "placeholder": "Manual Columns",
                    "helper_text": "Pass in data to column names manually.",
                    "component": {"type": "table"},
                }
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["action", "add_columns_manually", "endpoint_0", "endpoint_1"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Google Sheets",
        model: str | ToolInput = "gpt-4o",
        provider: str | ToolInput = "openai",
        sheet_id: str | ToolInput = "",
        sheet_url: str | ToolInput = "",
        action: str | ToolInput = "",
        add_columns_manually: bool | ToolInput = False,
        endpoint_0: Any | ToolInput = None,
        endpoint_1: Any | ToolInput = None,
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action
        if isinstance(add_columns_manually, ToolInput):
            if add_columns_manually.type == "static":
                params["add_columns_manually"] = add_columns_manually.value
            else:
                raise ValueError(f"add_columns_manually cannot be a dynamic input")
        else:
            params["add_columns_manually"] = add_columns_manually
        if isinstance(endpoint_0, ToolInput):
            if endpoint_0.type == "static":
                params["endpoint_0"] = endpoint_0.value
            else:
                raise ValueError(f"endpoint_0 cannot be a dynamic input")
        else:
            params["endpoint_0"] = endpoint_0
        if isinstance(endpoint_1, ToolInput):
            if endpoint_1.type == "static":
                params["endpoint_1"] = endpoint_1.value
            else:
                raise ValueError(f"endpoint_1 cannot be a dynamic input")
        else:
            params["endpoint_1"] = endpoint_1

        super().__init__(
            tool_type="integration_google_sheets",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if model is not None:
            if isinstance(model, ToolInput):
                self.inputs["model"] = {
                    "type": model.type,
                    "value": model.value or model.description,
                }
            else:
                self.inputs["model"] = {"type": "static", "value": model}
        if provider is not None:
            if isinstance(provider, ToolInput):
                self.inputs["provider"] = {
                    "type": provider.type,
                    "value": provider.value or provider.description,
                }
            else:
                self.inputs["provider"] = {"type": "static", "value": provider}
        if sheet_id is not None:
            if isinstance(sheet_id, ToolInput):
                self.inputs["sheet_id"] = {
                    "type": sheet_id.type,
                    "value": sheet_id.value or sheet_id.description,
                }
            else:
                self.inputs["sheet_id"] = {"type": "static", "value": sheet_id}
        if sheet_url is not None:
            if isinstance(sheet_url, ToolInput):
                self.inputs["sheet_url"] = {
                    "type": sheet_url.type,
                    "value": sheet_url.value or sheet_url.description,
                }
            else:
                self.inputs["sheet_url"] = {"type": "static", "value": sheet_url}
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}
        if add_columns_manually is not None:
            if isinstance(add_columns_manually, ToolInput):
                self.inputs["add_columns_manually"] = {
                    "type": add_columns_manually.type,
                    "value": add_columns_manually.value
                    or add_columns_manually.description,
                }
            else:
                self.inputs["add_columns_manually"] = {
                    "type": "static",
                    "value": add_columns_manually,
                }
        if endpoint_0 is not None:
            if isinstance(endpoint_0, ToolInput):
                self.inputs["endpoint_0"] = {
                    "type": endpoint_0.type,
                    "value": endpoint_0.value or endpoint_0.description,
                }
            else:
                self.inputs["endpoint_0"] = {"type": "static", "value": endpoint_0}
        if endpoint_1 is not None:
            if isinstance(endpoint_1, ToolInput):
                self.inputs["endpoint_1"] = {
                    "type": endpoint_1.type,
                    "value": endpoint_1.value or endpoint_1.description,
                }
            else:
                self.inputs["endpoint_1"] = {"type": "static", "value": endpoint_1}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationGoogleSheetsTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_airtable")
class IntegrationAirtableTool(Tool):
    """
    Airtable

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        base_id: Name of the Airtable base
        integration: The integration input
        table_id: Name of the table in the selected base
    ### When action = 'new_record' and endpoint_0 = '[endpoint_0.<A>]'
        [<A>.inputs]: The [<A>.inputs] input
    ### When action = 'write_list_to_column' and endpoint_0 = '[endpoint_0.<A>]'
        [<A>.inputs]: The [<A>.inputs] input
    ### When action = 'update_records' and endpoint_0 = '[endpoint_0.<A>]'
        [<A>.inputs]: The [<A>.inputs] input
    ### When action = 'update_records'
        condition: Conditional Operator
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "base_id",
            "helper_text": "Name of the Airtable base",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "The integration input",
            "value": None,
            "type": "integration<Airtable>",
        },
        {
            "field": "table_id",
            "helper_text": "Name of the table in the selected base",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "(*)**(*)": {
            "inputs": [],
            "outputs": [],
            "variant": "common_integration_nodes",
        },
        "read_table**(*)": {
            "inputs": [],
            "outputs": [],
            "name": "read_table",
            "task_name": "tasks.airtable.read_table",
            "description": "Read specified columns from the selected table",
            "label": "Read Table",
            "inputs_sort_order": ["integration", "action", "base_id", "table_id"],
        },
        "read_table**[endpoint_0.<A>]": {
            "inputs": [],
            "outputs": [{"field": "[<A>.outputs]", "type": ""}],
        },
        "new_record**(*)": {
            "inputs": [],
            "outputs": [],
            "name": "new_record",
            "task_name": "tasks.airtable.write_to_table",
            "description": "Add new record in an Airtable database",
            "label": "Add New Record",
            "inputs_sort_order": ["integration", "action", "base_id", "table_id"],
        },
        "new_record**[endpoint_0.<A>]": {
            "inputs": [{"field": "[<A>.inputs]", "type": ""}],
            "outputs": [],
        },
        "write_list_to_column**(*)": {
            "inputs": [],
            "outputs": [],
            "name": "write_list_to_column",
            "task_name": "tasks.airtable.write_list_to_column",
            "description": "Fill specified columns empty cells with the input values (inputs can be list)",
            "label": "Column List Writer",
            "inputs_sort_order": ["integration", "action", "base_id", "table_id"],
        },
        "write_list_to_column**[endpoint_0.<A>]": {
            "inputs": [{"field": "[<A>.inputs]", "type": ""}],
            "outputs": [],
        },
        "update_records**(*)": {
            "inputs": [
                {
                    "field": "condition",
                    "type": "string",
                    "value": "",
                    "label": "Conditional Operator",
                    "placeholder": "",
                    "helper_text": "Conditional Operator",
                }
            ],
            "outputs": [],
            "name": "update_records",
            "task_name": "tasks.airtable.update_records",
            "description": "Update the records matching the specified search values in a table",
            "label": "Update Records",
            "operation": "update",
            "inputs_sort_order": [
                "integration",
                "action",
                "base_id",
                "table_id",
                "condition",
            ],
        },
        "update_records**[endpoint_0.<A>]": {
            "inputs": [{"field": "[<A>.inputs]", "type": ""}],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["action", "endpoint_0"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Airtable",
        base_id: str | ToolInput = "",
        table_id: str | ToolInput = "",
        action: str | ToolInput = "",
        endpoint_0: Any | ToolInput = None,
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action
        if isinstance(endpoint_0, ToolInput):
            if endpoint_0.type == "static":
                params["endpoint_0"] = endpoint_0.value
            else:
                raise ValueError(f"endpoint_0 cannot be a dynamic input")
        else:
            params["endpoint_0"] = endpoint_0

        super().__init__(
            tool_type="integration_airtable",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if base_id is not None:
            if isinstance(base_id, ToolInput):
                self.inputs["base_id"] = {
                    "type": base_id.type,
                    "value": base_id.value or base_id.description,
                }
            else:
                self.inputs["base_id"] = {"type": "static", "value": base_id}
        if table_id is not None:
            if isinstance(table_id, ToolInput):
                self.inputs["table_id"] = {
                    "type": table_id.type,
                    "value": table_id.value or table_id.description,
                }
            else:
                self.inputs["table_id"] = {"type": "static", "value": table_id}
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}
        if endpoint_0 is not None:
            if isinstance(endpoint_0, ToolInput):
                self.inputs["endpoint_0"] = {
                    "type": endpoint_0.type,
                    "value": endpoint_0.value or endpoint_0.description,
                }
            else:
                self.inputs["endpoint_0"] = {"type": "static", "value": endpoint_0}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationAirtableTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_notion")
class IntegrationNotionTool(Tool):
    """
    Notion

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### When action = 'write_to_database' and endpoint_0 = '[endpoint_0.<A>]'
        [<A>.inputs]: The [<A>.inputs] input
    ### When action = 'create_new_page' and endpoint_0 = '[endpoint_0.<A>]'
        [<A>.inputs]: The [<A>.inputs] input
    ### When action = 'create_new_block' and endpoint_0 = '[endpoint_0.<A>]'
        [<A>.inputs]: The [<A>.inputs] input
    ### When action = 'update_database' and endpoint_0 = '[endpoint_0.<A>]'
        [<A>.inputs]: The [<A>.inputs] input
    ### When action = 'update_database'
        condition: Conditional Operator
        item_id: Select the page to read
    ### When action = 'read_page'
        item_id: Select the page to read
    ### When action = 'write_to_database'
        item_id: Select the page to read
    ### When action = 'create_new_page'
        item_id: Select the page to read
    ### When action = 'create_new_block'
        item_id: Select the page to read
    ### When action = 'read_database'
        item_id: Select the page to read
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Notion>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "read_page**(*)": {
            "inputs": [
                {
                    "field": "item_id",
                    "type": "string",
                    "agent_field_type": "static",
                    "disable_conversion": True,
                    "value": "",
                    "label": "Page",
                    "placeholder": "Choose a page",
                    "helper_text": "Select the page to read",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=page&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                }
            ],
            "outputs": [],
            "name": "read_page",
            "task_name": "tasks.notion.read_page",
            "description": "Read an existing Notion page",
            "label": "Read Notion page",
            "variant": "common_integration_nodes",
            "inputs_sort_order": ["integration", "action", "item_id"],
        },
        "read_page**[endpoint_0.<A>]": {
            "inputs": [],
            "outputs": [{"field": "[<A>.outputs]", "type": ""}],
        },
        "write_to_database**(*)": {
            "inputs": [
                {
                    "field": "item_id",
                    "type": "string",
                    "agent_field_type": "static",
                    "disable_conversion": True,
                    "value": "",
                    "label": "Database",
                    "placeholder": "Choose a database",
                    "helper_text": "Select Notion Database",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=database&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                }
            ],
            "outputs": [],
            "name": "write_to_database",
            "task_name": "tasks.notion.write_to_database",
            "description": "Add a page to an existing Notion database",
            "label": "Write to Database",
            "variant": "common_integration_nodes",
            "inputs_sort_order": ["integration", "action", "item_id"],
        },
        "write_to_database**[endpoint_0.<A>]": {
            "inputs": [{"field": "[<A>.inputs]", "type": ""}],
            "outputs": [],
        },
        "create_new_page**(*)": {
            "inputs": [
                {
                    "field": "item_id",
                    "type": "string",
                    "agent_field_type": "static",
                    "disable_conversion": True,
                    "value": "",
                    "label": "Page",
                    "placeholder": "Choose a Page",
                    "helper_text": "Select Notion Database",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=page&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                }
            ],
            "outputs": [],
            "name": "create_new_page",
            "task_name": "tasks.notion.create_new_page",
            "description": "Create a new page on an existing Notion page",
            "label": "Create New Page",
            "variant": "common_integration_nodes",
            "inputs_sort_order": ["integration", "action", "item_id"],
        },
        "create_new_page**[endpoint_0.<A>]": {
            "inputs": [{"field": "[<A>.inputs]", "type": ""}],
            "outputs": [],
        },
        "create_new_block**(*)": {
            "inputs": [
                {
                    "field": "item_id",
                    "type": "string",
                    "agent_field_type": "static",
                    "disable_conversion": True,
                    "value": "",
                    "label": "Page",
                    "placeholder": "Choose a Page",
                    "helper_text": "Select Notion Page",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=page&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                }
            ],
            "outputs": [],
            "name": "create_new_block",
            "task_name": "tasks.notion.create_new_block",
            "description": "Write to an existing Notion page",
            "label": "Create New Block",
            "variant": "common_integration_nodes",
            "inputs_sort_order": ["integration", "action", "item_id"],
        },
        "create_new_block**[endpoint_0.<A>]": {
            "inputs": [{"field": "[<A>.inputs]", "type": ""}],
            "outputs": [],
        },
        "update_database**(*)": {
            "inputs": [
                {
                    "field": "item_id",
                    "type": "string",
                    "agent_field_type": "static",
                    "disable_conversion": True,
                    "value": "",
                    "label": "Database",
                    "placeholder": "Choose a database",
                    "helper_text": "Select Notion Database",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=database&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
                {
                    "field": "condition",
                    "type": "string",
                    "value": "",
                    "label": "Conditional Operator",
                    "placeholder": "",
                    "helper_text": "Conditional Operator",
                },
            ],
            "outputs": [],
            "name": "update_database",
            "task_name": "tasks.notion.update_database",
            "description": "Update a Notion database",
            "label": "Database Updater",
            "operation": "update",
            "variant": "common_integration_nodes",
            "inputs_sort_order": ["integration", "action", "item_id", "condition"],
        },
        "update_database**[endpoint_0.<A>]": {
            "inputs": [{"field": "[<A>.inputs]", "type": ""}],
            "outputs": [],
        },
        "read_database**(*)": {
            "inputs": [
                {
                    "field": "item_id",
                    "type": "string",
                    "agent_field_type": "static",
                    "disable_conversion": True,
                    "value": "",
                    "label": "Database",
                    "placeholder": "Choose a database",
                    "helper_text": "Select Notion Database",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=database&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": True,
                            "supports_pagination": True,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                }
            ],
            "outputs": [],
            "name": "read_database",
            "task_name": "tasks.notion.read_database",
            "description": "Read pages from a Notion database",
            "label": "Database Reader",
            "variant": "common_integration_nodes",
            "inputs_sort_order": ["integration", "action", "item_id"],
        },
        "read_database**[endpoint_0.<A>]": {
            "inputs": [],
            "outputs": [{"field": "[<A>.outputs]", "type": ""}],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["action", "endpoint_0"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Notion",
        item_id: str | ToolInput = "",
        action: str | ToolInput = "",
        endpoint_0: Any | ToolInput = None,
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action
        if isinstance(endpoint_0, ToolInput):
            if endpoint_0.type == "static":
                params["endpoint_0"] = endpoint_0.value
            else:
                raise ValueError(f"endpoint_0 cannot be a dynamic input")
        else:
            params["endpoint_0"] = endpoint_0

        super().__init__(
            tool_type="integration_notion",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if item_id is not None:
            if isinstance(item_id, ToolInput):
                self.inputs["item_id"] = {
                    "type": item_id.type,
                    "value": item_id.value or item_id.description,
                }
            else:
                self.inputs["item_id"] = {"type": "static", "value": item_id}
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}
        if endpoint_0 is not None:
            if isinstance(endpoint_0, ToolInput):
                self.inputs["endpoint_0"] = {
                    "type": endpoint_0.type,
                    "value": endpoint_0.value or endpoint_0.description,
                }
            else:
                self.inputs["endpoint_0"] = {"type": "static", "value": endpoint_0}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationNotionTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_databricks")
class IntegrationDatabricksTool(Tool):
    """
    Databricks

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        catalog_name: Select the name of the Catalog
        integration: The integration input
        schema_name: Select the name of the Schema
        table_name: Select the name of Table to insert the row
        warehouse_id: Select the ID of the Warehouse to perform the action
    ### When action = 'insert_row' and endpoint_0 = '[endpoint_0.<A>]'
        [<A>.inputs]: The [<A>.inputs] input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "catalog_name",
            "helper_text": "Select the name of the Catalog",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "The integration input",
            "value": None,
            "type": "integration<Databricks>",
        },
        {
            "field": "schema_name",
            "helper_text": "Select the name of the Schema",
            "value": "",
            "type": "string",
        },
        {
            "field": "table_name",
            "helper_text": "Select the name of Table to insert the row",
            "value": "",
            "type": "string",
        },
        {
            "field": "warehouse_id",
            "helper_text": "Select the ID of the Warehouse to perform the action",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "insert_row**(*)": {
            "inputs": [],
            "outputs": [],
            "name": "insert_row",
            "task_name": "tasks.databricks.insert_row",
            "description": "Insert a new row into a Databricks Table",
            "label": "Insert A Row",
            "variant": "common_integration_nodes",
            "inputs_sort_order": [
                "integration",
                "action",
                "warehouse_id",
                "catalog_name",
                "schema_name",
                "table_name",
            ],
        },
        "insert_row**[endpoint_0.<A>]": {
            "inputs": [{"field": "[<A>.inputs]", "type": ""}],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["action", "endpoint_0"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Databricks",
        catalog_name: str | ToolInput = "",
        schema_name: str | ToolInput = "",
        table_name: str | ToolInput = "",
        warehouse_id: str | ToolInput = "",
        action: str | ToolInput = "",
        endpoint_0: Any | ToolInput = None,
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action
        if isinstance(endpoint_0, ToolInput):
            if endpoint_0.type == "static":
                params["endpoint_0"] = endpoint_0.value
            else:
                raise ValueError(f"endpoint_0 cannot be a dynamic input")
        else:
            params["endpoint_0"] = endpoint_0

        super().__init__(
            tool_type="integration_databricks",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if catalog_name is not None:
            if isinstance(catalog_name, ToolInput):
                self.inputs["catalog_name"] = {
                    "type": catalog_name.type,
                    "value": catalog_name.value or catalog_name.description,
                }
            else:
                self.inputs["catalog_name"] = {"type": "static", "value": catalog_name}
        if schema_name is not None:
            if isinstance(schema_name, ToolInput):
                self.inputs["schema_name"] = {
                    "type": schema_name.type,
                    "value": schema_name.value or schema_name.description,
                }
            else:
                self.inputs["schema_name"] = {"type": "static", "value": schema_name}
        if table_name is not None:
            if isinstance(table_name, ToolInput):
                self.inputs["table_name"] = {
                    "type": table_name.type,
                    "value": table_name.value or table_name.description,
                }
            else:
                self.inputs["table_name"] = {"type": "static", "value": table_name}
        if warehouse_id is not None:
            if isinstance(warehouse_id, ToolInput):
                self.inputs["warehouse_id"] = {
                    "type": warehouse_id.type,
                    "value": warehouse_id.value or warehouse_id.description,
                }
            else:
                self.inputs["warehouse_id"] = {"type": "static", "value": warehouse_id}
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}
        if endpoint_0 is not None:
            if isinstance(endpoint_0, ToolInput):
                self.inputs["endpoint_0"] = {
                    "type": endpoint_0.type,
                    "value": endpoint_0.value or endpoint_0.description,
                }
            else:
                self.inputs["endpoint_0"] = {"type": "static", "value": endpoint_0}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationDatabricksTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_weaviate")
class IntegrationWeaviateTool(Tool):
    """
    Weaviate

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### query_weaviate
        collection: Select the Weaviate collection to query
        embedding_model: Select the embedding model to use to embed the query
        properties: Comma-separated list of keywords to use
        query: Natural Language Query
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Weaviate>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "query_weaviate": {
            "inputs": [
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "Query",
                    "placeholder": "“Fish species in the South Pacific Ocean”",
                    "helper_text": "Natural Language Query",
                },
                {
                    "field": "embedding_model",
                    "type": "enum<string>",
                    "value": "",
                    "label": "Embedding Model",
                    "placeholder": "Select Embedding Model",
                    "helper_text": "Select the embedding model to use to embed the query",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "options": [
                            {
                                "label": "OpenAI Text Embedding 3 Small",
                                "value": "openai/text-embedding-3-small",
                            },
                            {
                                "label": "OpenAI Text Embedding 3 Large",
                                "value": "openai/text-embedding-3-large",
                            },
                            {
                                "label": "OpenAI Text Embedding Ada 002",
                                "value": "openai/text-embedding-ada-002",
                            },
                            {
                                "label": "Cohere Embed English v3.0",
                                "value": "cohere/embed-english-v3.0",
                            },
                            {
                                "label": "Cohere Embed Multilingual v3.0",
                                "value": "cohere/embed-multilingual-v3.0",
                            },
                            {
                                "label": "Cohere Embed English Light v3.0",
                                "value": "cohere/embed-english-light-v3.0",
                            },
                            {
                                "label": "Cohere Embed Multilingual Light v3.0",
                                "value": "cohere/embed-multilingual-light-v3.0",
                            },
                        ],
                    },
                },
                {
                    "field": "collection",
                    "type": "string",
                    "value": "",
                    "label": "Collection",
                    "placeholder": "Collection",
                    "helper_text": "Select the Weaviate collection to query",
                    "agent_field_type": "static",
                    "component": {
                        "type": "dropdown",
                        "dynamic_config": {
                            "endpoint": "/{prefix}/item/{inputs.integration.object_id}?field=collection&page={}&page_size={dynamic_config.page_size}&q={}",
                            "page_size": 25,
                            "supports_search": False,
                            "supports_pagination": False,
                            "refreshable": True,
                            "useSameEndpointForRefresh": True,
                        },
                    },
                },
                {
                    "field": "properties",
                    "type": "string",
                    "value": "",
                    "label": "Properties",
                    "placeholder": "Properties",
                    "helper_text": "Comma-separated list of keywords to use",
                },
            ],
            "outputs": [],
            "name": "query_weaviate",
            "task_name": "tasks.vectordbs.integrations.weaviate.query",
            "description": "Query Weaviate data",
            "label": "Query Weaviate",
            "variant": "common_integration_nodes",
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Weaviate",
        collection: str | ToolInput = "",
        embedding_model: str | ToolInput = "",
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_weaviate",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if collection is not None:
            if isinstance(collection, ToolInput):
                self.inputs["collection"] = {
                    "type": collection.type,
                    "value": collection.value or collection.description,
                }
            else:
                self.inputs["collection"] = {"type": "static", "value": collection}
        if embedding_model is not None:
            if isinstance(embedding_model, ToolInput):
                self.inputs["embedding_model"] = {
                    "type": embedding_model.type,
                    "value": embedding_model.value or embedding_model.description,
                }
            else:
                self.inputs["embedding_model"] = {
                    "type": "static",
                    "value": embedding_model,
                }
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationWeaviateTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_bland_ai")
class IntegrationBlandAiTool(Tool):
    """
    Bland AI

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### call_a_number
        first_sentence: The first sentence the AI should speak during the call
        model: LLM model that the AI should use
        pathway_id: This is the pathway ID for the pathway you have created on your dev portal.
        phone_number: The phone number of the contact you want to call
        task: The objective you want the AI to accomplish during the call
        temperature: A value between 0 and 1 that controls the randomness of the LLM. 0 will cause more deterministic outputs while 1 will cause more random
        transfer_number: A phone number that the agent can transfer to under specific conditions - such as being asked to speak to a human or supervisor
        wait_for_greeting: When checked, the agent will wait for the call recipient to speak first before responding
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Bland AI>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "call_a_number": {
            "inputs": [
                {
                    "field": "phone_number",
                    "type": "string",
                    "value": "",
                    "label": "Phone Number",
                    "placeholder": "+1 6173149183",
                    "helper_text": "The phone number of the contact you want to call",
                },
                {
                    "field": "task",
                    "type": "string",
                    "value": "",
                    "label": "Task",
                    "placeholder": "Get the user's name and email",
                    "helper_text": "The objective you want the AI to accomplish during the call",
                },
                {
                    "field": "first_sentence",
                    "type": "string",
                    "value": "",
                    "label": "Enter First Sentence (Optional)",
                    "placeholder": "Hello, this is...",
                    "helper_text": "The first sentence the AI should speak during the call",
                },
                {
                    "field": "model",
                    "type": "enum<string>",
                    "value": "enhanced",
                    "label": "Select Model",
                    "placeholder": "enhanced",
                    "helper_text": "LLM model that the AI should use",
                    "hidden": True,
                    "is_hidden_in_agent": True,
                    "agent_field_type": "static",
                    "disable_conversion": True,
                },
                {
                    "field": "pathway_id",
                    "type": "string",
                    "value": "",
                    "label": "Enter Pathway ID (Optional)",
                    "placeholder": "pathway_123",
                    "helper_text": "This is the pathway ID for the pathway you have created on your dev portal.",
                },
                {
                    "field": "temperature",
                    "type": "string",
                    "value": "",
                    "label": "Enter Temperature",
                    "placeholder": "0.7",
                    "helper_text": "A value between 0 and 1 that controls the randomness of the LLM. 0 will cause more deterministic outputs while 1 will cause more random",
                },
                {
                    "field": "transfer_number",
                    "type": "string",
                    "value": "",
                    "label": "Enter Transfer Number (Optional)",
                    "placeholder": "+12223334444",
                    "helper_text": "A phone number that the agent can transfer to under specific conditions - such as being asked to speak to a human or supervisor",
                },
                {
                    "field": "wait_for_greeting",
                    "type": "bool",
                    "value": False,
                    "label": "Select Wait for Greeting",
                    "placeholder": "false",
                    "helper_text": "When checked, the agent will wait for the call recipient to speak first before responding",
                },
            ],
            "outputs": [],
            "name": "call_a_number",
            "task_name": "tasks.bland_ai.call_a_number",
            "description": "Call a number using AI phone caller",
            "label": "Call a number",
            "variant": "bland_ai",
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Bland AI",
        model: str | ToolInput = "enhanced",
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_bland_ai",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if model is not None:
            if isinstance(model, ToolInput):
                self.inputs["model"] = {
                    "type": model.type,
                    "value": model.value or model.description,
                }
            else:
                self.inputs["model"] = {"type": "static", "value": model}
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationBlandAiTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_algolia")
class IntegrationAlgoliaTool(Tool):
    """
    Algolia

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### search_index
        index: An index where the data used by Algolia is stored
        query: Keyword to be searched in the index
        return_mode: Choose between returning as chunks or JSON
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Algolia>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "search_index": {
            "inputs": [
                {
                    "field": "query",
                    "type": "string",
                    "value": "",
                    "label": "Query",
                    "placeholder": "“iPhone 16”",
                    "helper_text": "Keyword to be searched in the index",
                },
                {
                    "field": "index",
                    "type": "string",
                    "value": "",
                    "label": "Index",
                    "placeholder": "database",
                    "helper_text": "An index where the data used by Algolia is stored",
                },
                {
                    "field": "return_mode",
                    "type": "enum<string>",
                    "value": "json",
                    "label": "Return Mode",
                    "agent_field_type": "static",
                    "placeholder": "Choose between returning as chunks or JSON",
                    "helper_text": "Choose between returning as chunks or JSON",
                    "component": {
                        "type": "dropdown",
                        "options": [
                            {"label": "JSON", "value": "json"},
                            {"label": "Chunks", "value": "chunks"},
                        ],
                    },
                },
            ],
            "outputs": [],
            "name": "search_index",
            "task_name": "tasks.algolia.search_index",
            "description": "Query your Algolia index",
            "label": "Search Algolia index",
            "variant": "common_integration_nodes",
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Algolia",
        return_mode: str | ToolInput = "json",
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_algolia",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if return_mode is not None:
            if isinstance(return_mode, ToolInput):
                self.inputs["return_mode"] = {
                    "type": return_mode.type,
                    "value": return_mode.value or return_mode.description,
                }
            else:
                self.inputs["return_mode"] = {"type": "static", "value": return_mode}
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationAlgoliaTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("integration_apollo")
class IntegrationApolloTool(Tool):
    """
    Apollo

    ## Inputs
    ### Common Inputs
        action: Select the action to perform
        integration: Connect to your account
    ### fetch_companies
        company_name: Name of the company to search
        keywords: Comma separated list of keywords the company should be associated with
        location: Location of the company headquarters
        max_size: Maximum number of employees in the company
        min_size: Minimum number of employees in the company
        num_results: Limit number of results
    ### enrich_contact
        company_name: Name of the company to search
        domain: Company domain
        first_name_input: Contact's first name
        last_name_input: Contact's last name
        linkedin_url_input: Contact's LinkedIn URL
    ### enrich_company
        domain: Company domain
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "Select the action to perform",
            "value": "",
            "type": "string",
        },
        {
            "field": "integration",
            "helper_text": "Connect to your account",
            "value": None,
            "type": "integration<Apollo>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "(*)": {"inputs": [], "outputs": [], "variant": "default_integration_nodes"},
        "fetch_companies": {
            "inputs": [
                {
                    "field": "company_name",
                    "type": "string",
                    "value": "",
                    "label": "Company Name",
                    "placeholder": "VectorShift",
                    "helper_text": "Name of the company to search",
                },
                {
                    "field": "keywords",
                    "type": "string",
                    "value": "",
                    "label": "Keywords",
                    "placeholder": "AI, automation",
                    "helper_text": "Comma separated list of keywords the company should be associated with",
                },
                {
                    "field": "min_size",
                    "type": "string",
                    "value": "",
                    "label": "Min Size",
                    "placeholder": "10",
                    "helper_text": "Minimum number of employees in the company",
                },
                {
                    "field": "max_size",
                    "type": "string",
                    "value": "",
                    "label": "Max Size",
                    "placeholder": "100",
                    "helper_text": "Maximum number of employees in the company",
                },
                {
                    "field": "location",
                    "type": "string",
                    "value": "",
                    "label": "Location",
                    "placeholder": "California, US",
                    "helper_text": "Location of the company headquarters",
                },
                {
                    "field": "num_results",
                    "type": "string",
                    "value": "",
                    "label": "Number of Results",
                    "placeholder": "10",
                    "helper_text": "Limit number of results",
                },
            ],
            "outputs": [
                {
                    "field": "company_names",
                    "type": "string",
                    "helper_text": 'A list of company names e.g., ["VectorShift","VectorShift Studios"]',
                },
                {
                    "field": "websites",
                    "type": "string",
                    "helper_text": 'A list of websites e.g., ["http://www.vectorshift.ai","http://www.vectorshiftstudios.com"]',
                },
                {
                    "field": "domains",
                    "type": "string",
                    "helper_text": 'A list of domains e.g., ["vectorshift.ai","vectorshiftstudios.com"]',
                },
                {
                    "field": "linkedin_urls",
                    "type": "string",
                    "helper_text": 'A list of Linkedin URLs e.g., ["http://www.linkedin.com/company/vectorshift","http://www.linkedin.com/company/vectorshift-studios"]',
                },
            ],
            "name": "fetch_companies",
            "task_name": "tasks.apollo.fetch_companies",
            "description": "Search for companies via Apollo api",
            "label": "Search Companies",
        },
        "enrich_company": {
            "inputs": [
                {
                    "field": "domain",
                    "type": "string",
                    "value": "",
                    "label": "Domain",
                    "placeholder": "google.com",
                    "helper_text": "Company domain",
                }
            ],
            "outputs": [
                {
                    "field": "company_name",
                    "type": "string",
                    "helper_text": "The company name e.g., Google",
                },
                {
                    "field": "country",
                    "type": "string",
                    "helper_text": "The company’s headquartered country e.g., United States",
                },
                {
                    "field": "website",
                    "type": "string",
                    "helper_text": "The company’s website e.g., http://www.google.com",
                },
                {
                    "field": "industry",
                    "type": "string",
                    "helper_text": "The company’s industry e.g., information technology & services",
                },
                {
                    "field": "annual_revenue",
                    "type": "string",
                    "helper_text": "The company’s annual revenue e.g., 766400000000.0",
                },
                {
                    "field": "total_funding",
                    "type": "string",
                    "helper_text": "The company’s total funding e.g., 3000000000000.0",
                },
                {
                    "field": "num_employees",
                    "type": "string",
                    "helper_text": "The total number of employees e.g., 289000",
                },
                {
                    "field": "linkedin_url",
                    "type": "string",
                    "helper_text": "The company’s Linkedin URL e.g., http://www.linkedin.com/company/google",
                },
            ],
            "name": "enrich_company",
            "task_name": "tasks.apollo.enrich_company",
            "description": "Enrich company information via Apollo api",
            "label": "Enrich Company Information",
        },
        "enrich_contact": {
            "inputs": [
                {
                    "field": "domain",
                    "type": "string",
                    "value": "",
                    "label": "Domain",
                    "placeholder": "google.com",
                    "helper_text": "Contact's company domain",
                },
                {
                    "field": "first_name_input",
                    "type": "string",
                    "value": "",
                    "label": "First Name",
                    "placeholder": "Sundar",
                    "helper_text": "Contact's first name",
                },
                {
                    "field": "last_name_input",
                    "type": "string",
                    "value": "",
                    "label": "Last Name",
                    "placeholder": "Pichai",
                    "helper_text": "Contact's last name",
                },
                {
                    "field": "company_name",
                    "type": "string",
                    "value": "",
                    "label": "Company Name",
                    "placeholder": "Google",
                    "helper_text": "Contact's company name",
                },
                {
                    "field": "linkedin_url_input",
                    "type": "string",
                    "value": "",
                    "label": "LinkedIn URL",
                    "placeholder": "https://www.linkedin.com/in/sundarpichai",
                    "helper_text": "Contact's LinkedIn URL",
                },
            ],
            "outputs": [
                {
                    "field": "first_name",
                    "type": "string",
                    "helper_text": "The first name e.g., Sundar",
                },
                {
                    "field": "last_name",
                    "type": "string",
                    "helper_text": "The last name e.g., Pichai",
                },
                {
                    "field": "job_title",
                    "type": "string",
                    "helper_text": "The person’s title e.g., CEO",
                },
                {
                    "field": "phone_number",
                    "type": "string",
                    "helper_text": "The person’s phone number+10000000000",
                },
                {
                    "field": "email",
                    "type": "string",
                    "helper_text": "The person’s email address e.g., sundar@google.com",
                },
                {
                    "field": "linkedin_url",
                    "type": "string",
                    "helper_text": "The person’s Linkedin e.g., https://www.linkedin.com/in/sundarpichai",
                },
            ],
            "name": "enrich_contact",
            "task_name": "tasks.apollo.enrich_contact",
            "description": "Enrich a contact via Apollo api",
            "label": "Enrich Contact Details",
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["action"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Apollo",
        action: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(action, ToolInput):
            if action.type == "static":
                params["action"] = action.value
            else:
                raise ValueError(f"action cannot be a dynamic input")
        else:
            params["action"] = action

        super().__init__(
            tool_type="integration_apollo",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if action is not None:
            if isinstance(action, ToolInput):
                self.inputs["action"] = {
                    "type": action.type,
                    "value": action.value or action.description,
                }
            else:
                self.inputs["action"] = {"type": "static", "value": action}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationApolloTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("zapier")
class ZapierTool(Tool):
    """


    ## Inputs
    ### Common Inputs
        payload: Text/JSON payload to deliver
        webhook_url: the Zapier URL to deliver the payload to
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "payload",
            "helper_text": "Text/JSON payload to deliver",
            "value": "",
            "type": "string",
        },
        {
            "field": "webhook_url",
            "helper_text": "the Zapier URL to deliver the payload to",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="zapier",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "ZapierTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("make")
class MakeTool(Tool):
    """


    ## Inputs
    ### Common Inputs
        payload: Text/JSON payload to deliver
        webhook_url: the Make URL to deliver the payload to
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "payload",
            "helper_text": "Text/JSON payload to deliver",
            "value": "",
            "type": "string",
        },
        {
            "field": "webhook_url",
            "helper_text": "the Make URL to deliver the payload to",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="make",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "MakeTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("text_manipulation")
class TextManipulationTool(Tool):
    """


    ## Inputs
    ### Common Inputs
        sub_type: The sub_type input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "sub_type",
            "helper_text": "The sub_type input",
            "value": "",
            "type": "string",
        }
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="text_manipulation",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "TextManipulationTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("file_operations")
class FileOperationsTool(Tool):
    """


    ## Inputs
    ### Common Inputs
        sub_type: The sub_type input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "sub_type",
            "helper_text": "The sub_type input",
            "value": "",
            "type": "string",
        }
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="file_operations",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "FileOperationsTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("ai_operations")
class AiOperationsTool(Tool):
    """


    ## Inputs
    ### Common Inputs
        sub_type: The sub_type input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "sub_type",
            "helper_text": "The sub_type input",
            "value": "",
            "type": "string",
        }
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="ai_operations",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "AiOperationsTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("file_to_text")
class FileToTextTool(Tool):
    """
    Convert data from type File to type Text

    ## Inputs
    ### Common Inputs
        chunk_text: Whether to chunk the text into smaller pieces.
        file: The file to convert to text.
        file_parser: The type of file parser to use.
        loader_type: The type of file to load.
    ### When chunk_text = True
        chunk_overlap: The overlap of each chunk of text.
        chunk_size: The size of each chunk of text.
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "chunk_text",
            "helper_text": "Whether to chunk the text into smaller pieces.",
            "value": False,
            "type": "bool",
        },
        {
            "field": "file",
            "helper_text": "The file to convert to text.",
            "value": None,
            "type": "file",
        },
        {
            "field": "file_parser",
            "helper_text": "The type of file parser to use.",
            "value": "default",
            "type": "enum<string>",
        },
        {
            "field": "loader_type",
            "helper_text": "The type of file to load.",
            "value": "File",
            "type": "enum<string>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "true": {
            "inputs": [
                {
                    "field": "chunk_size",
                    "type": "int32",
                    "value": 1024,
                    "helper_text": "The size of each chunk of text.",
                },
                {
                    "field": "chunk_overlap",
                    "type": "int32",
                    "value": 400,
                    "helper_text": "The overlap of each chunk of text.",
                },
            ],
            "outputs": [
                {
                    "field": "processed_text",
                    "type": "vec<string>",
                    "helper_text": "The text as a list of chunks.",
                }
            ],
        },
        "false": {
            "inputs": [],
            "outputs": [
                {
                    "field": "processed_text",
                    "type": "string",
                    "helper_text": "The text as a string.",
                }
            ],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["chunk_text"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Convert data from type File to type Text",
        chunk_text: bool | ToolInput = False,
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(chunk_text, ToolInput):
            if chunk_text.type == "static":
                params["chunk_text"] = chunk_text.value
            else:
                raise ValueError(f"chunk_text cannot be a dynamic input")
        else:
            params["chunk_text"] = chunk_text

        super().__init__(
            tool_type="file_to_text",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if chunk_text is not None:
            if isinstance(chunk_text, ToolInput):
                self.inputs["chunk_text"] = {
                    "type": chunk_text.type,
                    "value": chunk_text.value or chunk_text.description,
                }
            else:
                self.inputs["chunk_text"] = {"type": "static", "value": chunk_text}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "FileToTextTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("code_execution")
class CodeExecutionTool(Tool):
    """


    ## Inputs
    ### Common Inputs
        code: The code input
        language: The language input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "code",
            "helper_text": "The code input",
            "value": "",
            "type": "string",
        },
        {
            "field": "language",
            "helper_text": "The language input",
            "value": 0,
            "type": "enum<int32>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="code_execution",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "CodeExecutionTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("chunking")
class ChunkingTool(Tool):
    """
    Split text into chunks. Supports different chunking strategies like markdown-aware, sentence-based, or dynamic sizing.

    ## Inputs
    ### Common Inputs
        chunk_overlap: The overlap of each chunk of text.
        chunk_size: The size of each chunk of text.
        splitter_method: Strategy for grouping segmented text into final chunks. 'sentence': groups sentences; 'markdown': respects Markdown structure (headers, code); 'dynamic': optimizes breaks for size using chosen segmentation method.
        text: The text to chunk
    ### dynamic
        segmentation_method: The method to break text into units before chunking. 'words': splits by word; 'sentences': splits by sentence boundary; 'paragraphs': splits by blank line/paragraph.
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "chunk_overlap",
            "helper_text": "The overlap of each chunk of text.",
            "value": 0,
            "type": "int32",
        },
        {
            "field": "chunk_size",
            "helper_text": "The size of each chunk of text.",
            "value": 512,
            "type": "int32",
        },
        {
            "field": "splitter_method",
            "helper_text": "Strategy for grouping segmented text into final chunks. 'sentence': groups sentences; 'markdown': respects Markdown structure (headers, code); 'dynamic': optimizes breaks for size using chosen segmentation method.",
            "value": "markdown",
            "type": "enum<string>",
        },
        {
            "field": "text",
            "helper_text": "The text to chunk",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "dynamic": {
            "inputs": [
                {
                    "field": "segmentation_method",
                    "type": "enum<string>",
                    "value": "words",
                    "helper_text": "The method to break text into units before chunking. 'words': splits by word; 'sentences': splits by sentence boundary; 'paragraphs': splits by blank line/paragraph.",
                }
            ],
            "outputs": [],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["splitter_method"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Split text into chunks. Supports different chunking strategies like markdown-aware, sentence-based, or dynamic sizing.",
        splitter_method: str | ToolInput = "markdown",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(splitter_method, ToolInput):
            if splitter_method.type == "static":
                params["splitter_method"] = splitter_method.value
            else:
                raise ValueError(f"splitter_method cannot be a dynamic input")
        else:
            params["splitter_method"] = splitter_method

        super().__init__(
            tool_type="chunking",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if splitter_method is not None:
            if isinstance(splitter_method, ToolInput):
                self.inputs["splitter_method"] = {
                    "type": splitter_method.type,
                    "value": splitter_method.value or splitter_method.description,
                }
            else:
                self.inputs["splitter_method"] = {
                    "type": "static",
                    "value": splitter_method,
                }

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "ChunkingTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("notifications")
class NotificationsTool(Tool):
    """


    ## Inputs
    ### Common Inputs
        sub_type: The sub_type input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "sub_type",
            "helper_text": "The sub_type input",
            "value": "",
            "type": "string",
        }
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="notifications",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "NotificationsTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("custom_smtp_email_sender")
class CustomSmtpEmailSenderTool(Tool):
    """
    Send emails via SMTP

    ## Inputs
    ### Common Inputs
        connection_type: Security type: SSL, TLS, or STARTTLS
        email_body: Email content
        email_subject: Subject line of the email
        recipient_email: Recipient email address(es), comma-separated
        send_as_html: Send email in HTML format
        sender_email: Sender email address
        sender_name: Display name for sender (optional)
        sender_password: SMTP server password
        smtp_server: SMTP server hostname or IP
        smtp_server_port: SMTP server port (25, 465, 587)
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "connection_type",
            "helper_text": "Security type: SSL, TLS, or STARTTLS",
            "value": "SSL",
            "type": "enum<string>",
        },
        {
            "field": "email_body",
            "helper_text": "Email content",
            "value": "",
            "type": "string",
        },
        {
            "field": "email_subject",
            "helper_text": "Subject line of the email",
            "value": "",
            "type": "string",
        },
        {
            "field": "recipient_email",
            "helper_text": "Recipient email address(es), comma-separated",
            "value": "",
            "type": "string",
        },
        {
            "field": "send_as_html",
            "helper_text": "Send email in HTML format",
            "value": "",
            "type": "bool",
        },
        {
            "field": "sender_email",
            "helper_text": "Sender email address",
            "value": "",
            "type": "string",
        },
        {
            "field": "sender_name",
            "helper_text": "Display name for sender (optional)",
            "value": "",
            "type": "string",
        },
        {
            "field": "sender_password",
            "helper_text": "SMTP server password",
            "value": "",
            "type": "string",
        },
        {
            "field": "smtp_server",
            "helper_text": "SMTP server hostname or IP",
            "value": "",
            "type": "string",
        },
        {
            "field": "smtp_server_port",
            "helper_text": "SMTP server port (25, 465, 587)",
            "value": 465,
            "type": "int32",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Send emails via SMTP",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="custom_smtp_email_sender",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "CustomSmtpEmailSenderTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("email_notification")
class EmailNotificationTool(Tool):
    """
    Send email notifications from no-reply@vectorshiftmail.com

    ## Inputs
    ### Common Inputs
        email_body: Email content
        email_subject: Subject line of the email
        recipient_email: Recipient email address(es), comma-separated
        send_as_html: Send email in HTML format
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "email_body",
            "helper_text": "Email content",
            "value": "",
            "type": "string",
        },
        {
            "field": "email_subject",
            "helper_text": "Subject line of the email",
            "value": "",
            "type": "string",
        },
        {
            "field": "recipient_email",
            "helper_text": "Recipient email address(es), comma-separated",
            "value": "",
            "type": "string",
        },
        {
            "field": "send_as_html",
            "helper_text": "Send email in HTML format",
            "value": "",
            "type": "bool",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Send email notifications from no-reply@vectorshiftmail.com",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="email_notification",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "EmailNotificationTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("sms_notification")
class SmsNotificationTool(Tool):
    """
    Send text message notifications.

    ## Inputs
    ### Common Inputs
        message: SMS message content
        phone_number: US phone number in country code (+1)
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "message",
            "helper_text": "SMS message content",
            "value": "",
            "type": "string",
        },
        {
            "field": "phone_number",
            "helper_text": "US phone number in country code (+1)",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Send text message notifications.",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="sms_notification",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "SmsNotificationTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("ai_filter_list")
class AiFilterListTool(Tool):
    """
    Filter items in a list given a specific AI condition. Example, Filter (Red, White, Boat) by whether it is a color: (Red, White)

    ## Inputs
    ### Common Inputs
        ai_condition: Write in natural language the condition to filter each item in the list
        filter_by: The items to filter the list by
        list_to_filter: The list to filter
        model: The specific model for filtering
        output_blank_value: If true, output a blank value for values that do not meet the filter condition. If false, nothing will be outputted
        provider: The model provider
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "ai_condition",
            "helper_text": "Write in natural language the condition to filter each item in the list",
            "value": "",
            "type": "string",
        },
        {
            "field": "filter_by",
            "helper_text": "The items to filter the list by",
            "value": "",
            "type": "vec<string>",
        },
        {
            "field": "list_to_filter",
            "helper_text": "The list to filter",
            "value": "",
            "type": "vec<string>",
        },
        {
            "field": "model",
            "helper_text": "The specific model for filtering",
            "value": "gpt-4o",
            "type": "enum<string>",
        },
        {
            "field": "output_blank_value",
            "helper_text": "If true, output a blank value for values that do not meet the filter condition. If false, nothing will be outputted",
            "value": False,
            "type": "bool",
        },
        {
            "field": "provider",
            "helper_text": "The model provider",
            "value": "openai",
            "type": "enum<string>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Filter items in a list given a specific AI condition. Example, Filter (Red, White, Boat) by whether it is a color: (Red, White)",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="ai_filter_list",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "AiFilterListTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("filter_list")
class FilterListTool(Tool):
    """
    Filter a list given a specific condition. Example, Filter (Red, White, Blue) by (100, 95, 80)>90 is (Red, White)

    ## Inputs
    ### Common Inputs
        condition_type: The type of condition to apply
        condition_value: The value to compare the list items against
        output_blank_value: If true, output a blank value for values that do not meet the filter condition. If false, nothing will be outputted
        type: The type of the list
    ### <T>
        filter_by: The items to filter the list by
        list_to_filter: The list to filter
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "condition_type",
            "helper_text": "The type of condition to apply",
            "value": "IsEmpty",
            "type": "enum<string>",
        },
        {
            "field": "condition_value",
            "helper_text": "The value to compare the list items against",
            "value": "",
            "type": "string",
        },
        {
            "field": "output_blank_value",
            "helper_text": "If true, output a blank value for values that do not meet the filter condition. If false, nothing will be outputted",
            "value": False,
            "type": "bool",
        },
        {
            "field": "type",
            "helper_text": "The type of the list",
            "value": "string",
            "type": "enum<string>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "<T>": {
            "inputs": [
                {
                    "field": "list_to_filter",
                    "type": "vec<<T>>",
                    "value": "",
                    "helper_text": "The list to filter",
                },
                {
                    "field": "filter_by",
                    "type": "vec<<T>>",
                    "value": "",
                    "helper_text": "The items to filter the list by",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "vec<<T>>",
                    "helper_text": "The filtered list",
                }
            ],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["type"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Filter a list given a specific condition. Example, Filter (Red, White, Blue) by (100, 95, 80)>90 is (Red, White)",
        type: str | ToolInput = "string",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(type, ToolInput):
            if type.type == "static":
                params["type"] = type.value
            else:
                raise ValueError(f"type cannot be a dynamic input")
        else:
            params["type"] = type

        super().__init__(
            tool_type="filter_list",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if type is not None:
            if isinstance(type, ToolInput):
                self.inputs["type"] = {
                    "type": type.type,
                    "value": type.value or type.description,
                }
            else:
                self.inputs["type"] = {"type": "static", "value": type}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "FilterListTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("sales_data_enrichment")
class SalesDataEnrichmentTool(Tool):
    """


    ## Inputs
    ### Common Inputs
        sub_type: The sub_type input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "sub_type",
            "helper_text": "The sub_type input",
            "value": "",
            "type": "string",
        }
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="sales_data_enrichment",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "SalesDataEnrichmentTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("email_validator")
class EmailValidatorTool(Tool):
    """
    Validate an email address

    ## Inputs
    ### Common Inputs
        email_to_validate: The email you want to validate
        model: The validation model to use
    ### custom-validator
        api_key: The API key to use
        provider: The validation provider to use
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "email_to_validate",
            "helper_text": "The email you want to validate",
            "value": "",
            "type": "string",
        },
        {
            "field": "model",
            "helper_text": "The validation model to use",
            "value": "regex",
            "type": "enum<string>",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "custom-validator": {
            "inputs": [
                {
                    "field": "provider",
                    "type": "enum<string>",
                    "value": "hunter",
                    "helper_text": "The validation provider to use",
                },
                {
                    "field": "api_key",
                    "type": "string",
                    "value": "",
                    "helper_text": "The API key to use",
                },
            ],
            "outputs": [],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["model"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Validate an email address",
        model: str | ToolInput = "regex",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(model, ToolInput):
            if model.type == "static":
                params["model"] = model.value
            else:
                raise ValueError(f"model cannot be a dynamic input")
        else:
            params["model"] = model

        super().__init__(
            tool_type="email_validator",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if model is not None:
            if isinstance(model, ToolInput):
                self.inputs["model"] = {
                    "type": model.type,
                    "value": model.value or model.description,
                }
            else:
                self.inputs["model"] = {"type": "static", "value": model}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "EmailValidatorTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("combine_text")
class CombineTextTool(Tool):
    """
    Combine text inputs into a singular output.

    ## Inputs
    ### Common Inputs
        text: The text to combine
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "text",
            "helper_text": "The text to combine",
            "value": ["", ""],
            "type": "vec<string>",
        }
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Combine text inputs into a singular output.",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="combine_text",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "CombineTextTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("find_and_replace")
class FindAndReplaceTool(Tool):
    """
    Find and replace words in a given text.

    ## Inputs
    ### Common Inputs
        replacements: The replacements input
        text_to_manipulate: The text to find and replace words in
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "replacements",
            "helper_text": "The replacements input",
            "value": [],
            "type": "vec<Dict[str, Any]>",
        },
        {
            "field": "text_to_manipulate",
            "helper_text": "The text to find and replace words in",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Find and replace words in a given text.",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="find_and_replace",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "FindAndReplaceTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("ai_fill_pdf")
class AiFillPdfTool(Tool):
    """
    Fill out a PDF with form fields using AI. The AI will understand and fill each field using provided context. To convert your PDF to have fillable input fields, use: https://www.sejda.com/pdf-forms

    ## Inputs
    ### Common Inputs
        context: Context used by LLM to fill PDF fields
        file: The PDF with form fields to be filled
        model: The specific model for filling the PDF
        provider: The model provider
        select_pages: Whether to select specific pages to fill
    ### When select_pages = True
        selected_pages: PDF page range
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "context",
            "helper_text": "Context used by LLM to fill PDF fields",
            "value": "",
            "type": "string",
        },
        {
            "field": "file",
            "helper_text": "The PDF with form fields to be filled",
            "value": None,
            "type": "file",
        },
        {
            "field": "model",
            "helper_text": "The specific model for filling the PDF",
            "value": "gpt-4o",
            "type": "enum<string>",
        },
        {
            "field": "provider",
            "helper_text": "The model provider",
            "value": "openai",
            "type": "enum<string>",
        },
        {
            "field": "select_pages",
            "helper_text": "Whether to select specific pages to fill",
            "value": False,
            "type": "bool",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "true": {
            "inputs": [
                {
                    "field": "selected_pages",
                    "type": "string",
                    "value": "",
                    "helper_text": "PDF page range",
                }
            ],
            "outputs": [],
        },
        "false": {"inputs": [], "outputs": []},
    }

    # List of parameters that affect configuration
    _PARAMS = ["select_pages"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Fill out a PDF with form fields using AI. The AI will understand and fill each field using provided context. To convert your PDF to have fillable input fields, use: https://www.sejda.com/pdf-forms",
        select_pages: bool | ToolInput = False,
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(select_pages, ToolInput):
            if select_pages.type == "static":
                params["select_pages"] = select_pages.value
            else:
                raise ValueError(f"select_pages cannot be a dynamic input")
        else:
            params["select_pages"] = select_pages

        super().__init__(
            tool_type="ai_fill_pdf",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if select_pages is not None:
            if isinstance(select_pages, ToolInput):
                self.inputs["select_pages"] = {
                    "type": select_pages.type,
                    "value": select_pages.value or select_pages.description,
                }
            else:
                self.inputs["select_pages"] = {"type": "static", "value": select_pages}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "AiFillPdfTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("extract_to_table")
class ExtractToTableTool(Tool):
    """
    Extract data to a CSV using AI

    ## Inputs
    ### Common Inputs
        add_columns_manually: Add data points for some columns manually instead of having them extracted by the AI model.
        additional_context: Provide any additional context that may help the AI model extract the data.
        extract_multiple_rows: Choose the mode of extraction. If checked, it will extract multiple rows of data. If unchecked, it will extract a single row.
        file: Your file should contain headers in the first row.
        manual_columns: Pass in data to column names manually.
        model: The specific model for extracting the table
        provider: The model provider
        text_for_extraction: Text to extract table from
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "add_columns_manually",
            "helper_text": "Add data points for some columns manually instead of having them extracted by the AI model.",
            "value": False,
            "type": "bool",
        },
        {
            "field": "additional_context",
            "helper_text": "Provide any additional context that may help the AI model extract the data.",
            "value": "",
            "type": "string",
        },
        {
            "field": "extract_multiple_rows",
            "helper_text": "Choose the mode of extraction. If checked, it will extract multiple rows of data. If unchecked, it will extract a single row.",
            "value": True,
            "type": "bool",
        },
        {
            "field": "file",
            "helper_text": "Your file should contain headers in the first row.",
            "value": "",
            "type": "file",
        },
        {
            "field": "manual_columns",
            "helper_text": "Pass in data to column names manually.",
            "value": [],
            "type": "vec<Dict[str, Any]>",
        },
        {
            "field": "model",
            "helper_text": "The specific model for extracting the table",
            "value": "gpt-4o",
            "type": "enum<string>",
        },
        {
            "field": "provider",
            "helper_text": "The model provider",
            "value": "openai",
            "type": "enum<string>",
        },
        {
            "field": "text_for_extraction",
            "helper_text": "Text to extract table from",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Extract data to a CSV using AI",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="extract_to_table",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "ExtractToTableTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("sort_csv")
class SortCsvTool(Tool):
    """
    Sort a CSV based on a column

    ## Inputs
    ### Common Inputs
        file: The CSV file to sort.
        has_headers: Whether the CSV has headers.
        is_file_variable: Whether the file is a variable.
        reverse_sort: Whether to reverse the sort.
    ### When is_file_variable = True
        column_index: The index of the column to sort by.
    ### When is_file_variable = False and has_headers = False
        column_index: The index of the column to sort by.
    ### When is_file_variable = False and has_headers = True
        column_to_sort_by: The column to sort by.
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "file",
            "helper_text": "The CSV file to sort.",
            "value": None,
            "type": "file",
        },
        {
            "field": "has_headers",
            "helper_text": "Whether the CSV has headers.",
            "value": True,
            "type": "bool",
        },
        {
            "field": "is_file_variable",
            "helper_text": "Whether the file is a variable.",
            "value": False,
            "type": "bool",
        },
        {
            "field": "reverse_sort",
            "helper_text": "Whether to reverse the sort.",
            "value": False,
            "type": "bool",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "true**(*)": {
            "inputs": [
                {
                    "field": "column_index",
                    "type": "int32",
                    "value": 0,
                    "helper_text": "The index of the column to sort by.",
                }
            ],
            "outputs": [],
        },
        "false**true": {
            "inputs": [
                {
                    "field": "column_to_sort_by",
                    "type": "enum<string>",
                    "value": "",
                    "helper_text": "The column to sort by.",
                }
            ],
            "outputs": [],
        },
        "false**false": {
            "inputs": [
                {
                    "field": "column_index",
                    "type": "int32",
                    "value": 0,
                    "helper_text": "The index of the column to sort by.",
                }
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["is_file_variable", "has_headers"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Sort a CSV based on a column",
        is_file_variable: bool | ToolInput = False,
        has_headers: bool | ToolInput = True,
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(is_file_variable, ToolInput):
            if is_file_variable.type == "static":
                params["is_file_variable"] = is_file_variable.value
            else:
                raise ValueError(f"is_file_variable cannot be a dynamic input")
        else:
            params["is_file_variable"] = is_file_variable
        if isinstance(has_headers, ToolInput):
            if has_headers.type == "static":
                params["has_headers"] = has_headers.value
            else:
                raise ValueError(f"has_headers cannot be a dynamic input")
        else:
            params["has_headers"] = has_headers

        super().__init__(
            tool_type="sort_csv",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if is_file_variable is not None:
            if isinstance(is_file_variable, ToolInput):
                self.inputs["is_file_variable"] = {
                    "type": is_file_variable.type,
                    "value": is_file_variable.value or is_file_variable.description,
                }
            else:
                self.inputs["is_file_variable"] = {
                    "type": "static",
                    "value": is_file_variable,
                }
        if has_headers is not None:
            if isinstance(has_headers, ToolInput):
                self.inputs["has_headers"] = {
                    "type": has_headers.type,
                    "value": has_headers.value or has_headers.description,
                }
            else:
                self.inputs["has_headers"] = {"type": "static", "value": has_headers}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "SortCsvTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("trigger_outlook")
class TriggerOutlookTool(Tool):
    """
    Outlook Trigger

    ## Inputs
    ### Common Inputs
        event: The event input
        integration: The integration input
        item_id: Select the Trigger
        trigger_enabled: Enable/Disable Automation
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "event",
            "helper_text": "The event input",
            "value": "",
            "type": "enum<string>",
        },
        {
            "field": "integration",
            "helper_text": "The integration input",
            "value": None,
            "type": "integration<Outlook>",
        },
        {
            "field": "item_id",
            "helper_text": "Select the Trigger",
            "value": "",
            "type": "string",
        },
        {
            "field": "trigger_enabled",
            "helper_text": "Enable/Disable Automation",
            "value": True,
            "type": "bool",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "new_email": {
            "inputs": [],
            "outputs": [
                {"field": "email_id", "type": "string"},
                {"field": "subject", "type": "string"},
                {"field": "sender_email", "type": "string"},
                {"field": "recipient_email", "type": "string"},
                {"field": "received_time", "type": "string"},
                {"field": "contents_of_email", "type": "string"},
                {"field": "attachments", "type": "vec<file>"},
            ],
            "name": "new_email",
            "task_name": "tasks.outlook.new_email",
            "description": "Triggers when new email appears in the specified mailbox",
            "label": "New Email",
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["event"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Outlook Trigger",
        event: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(event, ToolInput):
            if event.type == "static":
                params["event"] = event.value
            else:
                raise ValueError(f"event cannot be a dynamic input")
        else:
            params["event"] = event

        super().__init__(
            tool_type="trigger_outlook",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if event is not None:
            if isinstance(event, ToolInput):
                self.inputs["event"] = {
                    "type": event.type,
                    "value": event.value or event.description,
                }
            else:
                self.inputs["event"] = {"type": "static", "value": event}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "TriggerOutlookTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("trigger_gmail")
class TriggerGmailTool(Tool):
    """
    Gmail Trigger

    ## Inputs
    ### Common Inputs
        event: The event input
        integration: The integration input
        item_id: Select the Trigger
        trigger_enabled: Enable/Disable Automation
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "event",
            "helper_text": "The event input",
            "value": "",
            "type": "enum<string>",
        },
        {
            "field": "integration",
            "helper_text": "The integration input",
            "value": None,
            "type": "integration<Gmail>",
        },
        {
            "field": "item_id",
            "helper_text": "Select the Trigger",
            "value": "",
            "type": "string",
        },
        {
            "field": "trigger_enabled",
            "helper_text": "Enable/Disable Automation",
            "value": True,
            "type": "bool",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "new_email": {
            "inputs": [],
            "outputs": [
                {"field": "email_id", "type": "string"},
                {"field": "subject", "type": "string"},
                {"field": "sender_email", "type": "string"},
                {"field": "recipient_email", "type": "string"},
                {"field": "received_time", "type": "string"},
                {"field": "contents_of_email", "type": "string"},
                {"field": "attachments", "type": "vec<file>"},
            ],
            "name": "new_email",
            "task_name": "tasks.gmail.new_email",
            "description": "Triggers when new email appears in the specified mailbox",
            "label": "New Email",
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["event"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Gmail Trigger",
        event: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(event, ToolInput):
            if event.type == "static":
                params["event"] = event.value
            else:
                raise ValueError(f"event cannot be a dynamic input")
        else:
            params["event"] = event

        super().__init__(
            tool_type="trigger_gmail",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if event is not None:
            if isinstance(event, ToolInput):
                self.inputs["event"] = {
                    "type": event.type,
                    "value": event.value or event.description,
                }
            else:
                self.inputs["event"] = {"type": "static", "value": event}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "TriggerGmailTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("trigger_cron")
class TriggerCronTool(Tool):
    """
    Cron Trigger

    ## Inputs
    ### Common Inputs
        event: The event input
        integration: The integration input
        item_id: Custom cron expression
        timezone: Timezone for the cron trigger
        trigger_enabled: Enable/Disable Automation
    ### monthly
        day_of_month: Day of the month to trigger
        time_of_day: Time of day to trigger (HH:MM)
    ### weekly
        day_of_week: Day of the week to trigger
        time_of_day: Time of day to trigger (HH:MM)
    ### daily
        time_of_day: Time of day to trigger (HH:MM)
        trigger_on_weekends: Trigger on weekends
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "event",
            "helper_text": "The event input",
            "value": "",
            "type": "enum<string>",
        },
        {
            "field": "integration",
            "helper_text": "The integration input",
            "value": {"object_type": 20, "object_id": "6809a715ad4615eeb652a551"},
            "type": "integration<Cron>",
        },
        {
            "field": "item_id",
            "helper_text": "Custom cron expression",
            "value": "0 0 * * *",
            "type": "string",
        },
        {
            "field": "timezone",
            "helper_text": "Timezone for the cron trigger",
            "value": "UTC",
            "type": "enum<string>",
        },
        {
            "field": "trigger_enabled",
            "helper_text": "Enable/Disable Automation",
            "value": True,
            "type": "bool",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "daily": {
            "inputs": [
                {
                    "field": "time_of_day",
                    "type": "string",
                    "value": "00:00",
                    "label": "Time of day",
                    "placeholder": "HH:MM",
                    "helper_text": "Time of day to trigger (HH:MM)",
                },
                {
                    "field": "trigger_on_weekends",
                    "type": "bool",
                    "value": False,
                    "label": "Trigger on weekends",
                    "helper_text": "Trigger on weekends",
                },
            ],
            "outputs": [],
            "name": "daily",
            "task_name": "tasks.cron.daily",
            "description": "Triggers once a day at a specified time",
            "label": "Daily",
        },
        "weekly": {
            "inputs": [
                {
                    "field": "day_of_week",
                    "type": "enum<string>",
                    "value": "Monday",
                    "label": "Day of the week",
                    "placeholder": "Select a day",
                    "helper_text": "Day of the week to trigger",
                },
                {
                    "field": "time_of_day",
                    "type": "string",
                    "value": "00:00",
                    "label": "Time of day",
                    "placeholder": "HH:MM",
                    "helper_text": "Time of day to trigger (HH:MM)",
                },
            ],
            "outputs": [],
            "name": "weekly",
            "task_name": "tasks.cron.weekly",
            "description": "Triggers once a week on a specified day and time",
            "label": "Weekly",
        },
        "monthly": {
            "inputs": [
                {
                    "field": "day_of_month",
                    "type": "int32",
                    "value": 1,
                    "label": "Day of the month",
                    "placeholder": "Select a day",
                    "helper_text": "Day of the month to trigger",
                },
                {
                    "field": "time_of_day",
                    "type": "string",
                    "value": "00:00",
                    "label": "Time of day",
                    "placeholder": "HH:MM",
                    "helper_text": "Time of day to trigger (HH:MM)",
                },
            ],
            "outputs": [],
            "name": "monthly",
            "task_name": "tasks.cron.monthly",
            "description": "Triggers once a month on a specified day and time",
            "label": "Monthly",
        },
        "custom": {
            "inputs": [],
            "outputs": [],
            "name": "custom",
            "task_name": "tasks.cron.custom",
            "description": "Triggers based on a custom cron expression",
            "label": "Custom Cron Expression",
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["event"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Cron Trigger",
        event: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(event, ToolInput):
            if event.type == "static":
                params["event"] = event.value
            else:
                raise ValueError(f"event cannot be a dynamic input")
        else:
            params["event"] = event

        super().__init__(
            tool_type="trigger_cron",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if event is not None:
            if isinstance(event, ToolInput):
                self.inputs["event"] = {
                    "type": event.type,
                    "value": event.value or event.description,
                }
            else:
                self.inputs["event"] = {"type": "static", "value": event}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "TriggerCronTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("trigger_slack")
class TriggerSlackTool(Tool):
    """
    Slack Trigger

    ## Inputs
    ### Common Inputs
        channel: The name of the Slack channel
        event: The event input
        integration: The integration input
        item_id: The item_id input
        team: The name of the Slack team
        trigger_enabled: Enable/Disable Automation
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "channel",
            "helper_text": "The name of the Slack channel",
            "value": "",
            "type": "string",
        },
        {
            "field": "event",
            "helper_text": "The event input",
            "value": "",
            "type": "enum<string>",
        },
        {
            "field": "integration",
            "helper_text": "The integration input",
            "value": None,
            "type": "integration<Slack>",
        },
        {
            "field": "item_id",
            "helper_text": "The item_id input",
            "value": "",
            "type": "string",
        },
        {
            "field": "team",
            "helper_text": "The name of the Slack team",
            "value": "",
            "type": "string",
        },
        {
            "field": "trigger_enabled",
            "helper_text": "Enable/Disable Automation",
            "value": True,
            "type": "bool",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "new_message": {
            "inputs": [],
            "outputs": [
                {
                    "field": "message",
                    "type": "string",
                    "helper_text": "The content of the message",
                },
                {
                    "field": "message_id",
                    "type": "string",
                    "helper_text": "Unique identifier for the message",
                },
                {
                    "field": "timestamp",
                    "type": "string",
                    "helper_text": "When the message was sent",
                },
                {
                    "field": "user_name",
                    "type": "string",
                    "helper_text": "Display name of the message sender",
                },
                {
                    "field": "user_id",
                    "type": "string",
                    "helper_text": "Unique identifier of the message sender",
                },
                {
                    "field": "attachments",
                    "type": "vec<file>",
                    "helper_text": "Files attached to the message",
                },
                {
                    "field": "channel_id",
                    "type": "string",
                    "helper_text": "Unique identifier of the channel where the message was sent",
                },
                {
                    "field": "channel_name",
                    "type": "string",
                    "helper_text": "Name of the channel where the message was sent",
                },
                {
                    "field": "permalink",
                    "type": "string",
                    "helper_text": "Direct link to access this message",
                },
            ],
            "name": "new_message",
            "task_name": "tasks.slack.new_message",
            "description": "Triggers when new message appears in the specified channel",
            "label": "New Message",
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["event"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Slack Trigger",
        event: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(event, ToolInput):
            if event.type == "static":
                params["event"] = event.value
            else:
                raise ValueError(f"event cannot be a dynamic input")
        else:
            params["event"] = event

        super().__init__(
            tool_type="trigger_slack",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if event is not None:
            if isinstance(event, ToolInput):
                self.inputs["event"] = {
                    "type": event.type,
                    "value": event.value or event.description,
                }
            else:
                self.inputs["event"] = {"type": "static", "value": event}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "TriggerSlackTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("knowledge_base_actions")
class KnowledgeBaseActionsTool(Tool):
    """


    ## Inputs
    ### Common Inputs
        sub_type: The sub_type input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "sub_type",
            "helper_text": "The sub_type input",
            "value": "",
            "type": "string",
        }
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="knowledge_base_actions",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "KnowledgeBaseActionsTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("knowledge_base_sync")
class KnowledgeBaseSyncTool(Tool):
    """
    Automatically trigger a sync to the integrations in the selected knowledge base

    ## Inputs
    ### Common Inputs
        knowledge_base: The knowledge base to sync
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "knowledge_base",
            "helper_text": "The knowledge base to sync",
            "value": {},
            "type": "knowledge_base",
        }
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Automatically trigger a sync to the integrations in the selected knowledge base",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="knowledge_base_sync",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "KnowledgeBaseSyncTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("knowledge_base_create")
class KnowledgeBaseCreateTool(Tool):
    """
    Dynamically create a Knowledge Base with configured options

    ## Inputs
    ### Common Inputs
        analyze_documents: To analyze document contents and enrich them when parsing
        apify_key: Apify API Key for scraping URLs (optional)
        chunk_overlap: The overlap of the chunks to store in the knowledge base
        chunk_size: The size of the chunks to store in the knowledge base
        collection_name: The name of the collection to store the knowledge base in
        embedding_model: LLM model to use for embedding documents in the KB
        embedding_provider: The embedding provider to use
        file_processing_implementation: The file processing implementation to use
        is_hybrid: Whether to create a hybrid knowledge base
        name: The name of the knowledge base
        precision: The precision to use for the knowledge base
        segmentation_method: The method to break text into units before chunking. 'words': splits by word; 'sentences': splits by sentence boundary; 'paragraphs': splits by blank line/paragraph.
        sharded: Whether to shard the knowledge base
        splitter_method: Strategy for grouping segmented text into final chunks. 'sentence': groups sentences; 'markdown': respects Markdown structure (headers, code); 'dynamic': optimizes breaks for size using chosen segmentation method.
        vector_db_provider: The vector database provider to use
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "analyze_documents",
            "helper_text": "To analyze document contents and enrich them when parsing",
            "value": False,
            "type": "bool",
        },
        {
            "field": "apify_key",
            "helper_text": "Apify API Key for scraping URLs (optional)",
            "value": "",
            "type": "string",
        },
        {
            "field": "chunk_overlap",
            "helper_text": "The overlap of the chunks to store in the knowledge base",
            "value": 0,
            "type": "int32",
        },
        {
            "field": "chunk_size",
            "helper_text": "The size of the chunks to store in the knowledge base",
            "value": 400,
            "type": "int32",
        },
        {
            "field": "collection_name",
            "helper_text": "The name of the collection to store the knowledge base in",
            "value": "text-embedding-3-small",
            "type": "string",
        },
        {
            "field": "embedding_model",
            "helper_text": "LLM model to use for embedding documents in the KB",
            "value": "text-embedding-3-small",
            "type": "string",
        },
        {
            "field": "embedding_provider",
            "helper_text": "The embedding provider to use",
            "value": "openai",
            "type": "string",
        },
        {
            "field": "file_processing_implementation",
            "helper_text": "The file processing implementation to use",
            "value": "default",
            "type": "string",
        },
        {
            "field": "is_hybrid",
            "helper_text": "Whether to create a hybrid knowledge base",
            "value": False,
            "type": "bool",
        },
        {
            "field": "name",
            "helper_text": "The name of the knowledge base",
            "value": "",
            "type": "string",
        },
        {
            "field": "precision",
            "helper_text": "The precision to use for the knowledge base",
            "value": "Float16",
            "type": "string",
        },
        {
            "field": "segmentation_method",
            "helper_text": "The method to break text into units before chunking. 'words': splits by word; 'sentences': splits by sentence boundary; 'paragraphs': splits by blank line/paragraph.",
            "value": "words",
            "type": "enum<string>",
        },
        {
            "field": "sharded",
            "helper_text": "Whether to shard the knowledge base",
            "value": True,
            "type": "bool",
        },
        {
            "field": "splitter_method",
            "helper_text": "Strategy for grouping segmented text into final chunks. 'sentence': groups sentences; 'markdown': respects Markdown structure (headers, code); 'dynamic': optimizes breaks for size using chosen segmentation method.",
            "value": "markdown",
            "type": "enum<string>",
        },
        {
            "field": "vector_db_provider",
            "helper_text": "The vector database provider to use",
            "value": "qdrant",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "advanced": {
            "inputs": [
                {
                    "field": "segmentation_method",
                    "type": "enum<string>",
                    "value": "words",
                    "helper_text": "The method to break text into units before chunking. 'words': splits by word; 'sentences': splits by sentence boundary; 'paragraphs': splits by blank line/paragraph.",
                }
            ],
            "outputs": [],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["splitter_method"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Dynamically create a Knowledge Base with configured options",
        splitter_method: str | ToolInput = "markdown",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(splitter_method, ToolInput):
            if splitter_method.type == "static":
                params["splitter_method"] = splitter_method.value
            else:
                raise ValueError(f"splitter_method cannot be a dynamic input")
        else:
            params["splitter_method"] = splitter_method

        super().__init__(
            tool_type="knowledge_base_create",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if splitter_method is not None:
            if isinstance(splitter_method, ToolInput):
                self.inputs["splitter_method"] = {
                    "type": splitter_method.type,
                    "value": splitter_method.value or splitter_method.description,
                }
            else:
                self.inputs["splitter_method"] = {
                    "type": "static",
                    "value": splitter_method,
                }

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "KnowledgeBaseCreateTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("share_object")
class ShareObjectTool(Tool):
    """
    Share a VectorShift object with another user

    ## Inputs
    ### Common Inputs
        object_type: The object_type input
        org_name: Enter the name of the organization of the user (leave blank if not part of org)
        user_identifier: Enter the username or email of the user you want to share with
    ### knowledge_base
        object: The object input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "object_type",
            "helper_text": "The object_type input",
            "value": "knowledge_base",
            "type": "enum<string>",
        },
        {
            "field": "org_name",
            "helper_text": "Enter the name of the organization of the user (leave blank if not part of org)",
            "value": "",
            "type": "string",
        },
        {
            "field": "user_identifier",
            "helper_text": "Enter the username or email of the user you want to share with",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "knowledge_base": {
            "inputs": [{"field": "object", "type": "knowledge_base"}],
            "outputs": [],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["object_type"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Share a VectorShift object with another user",
        object_type: str | ToolInput = "knowledge_base",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(object_type, ToolInput):
            if object_type.type == "static":
                params["object_type"] = object_type.value
            else:
                raise ValueError(f"object_type cannot be a dynamic input")
        else:
            params["object_type"] = object_type

        super().__init__(
            tool_type="share_object",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if object_type is not None:
            if isinstance(object_type, ToolInput):
                self.inputs["object_type"] = {
                    "type": object_type.type,
                    "value": object_type.value or object_type.description,
                }
            else:
                self.inputs["object_type"] = {"type": "static", "value": object_type}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "ShareObjectTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("rename_file")
class RenameFileTool(Tool):
    """
    Rename an existing file, assigning a new name along with the file extension

    ## Inputs
    ### Common Inputs
        file: The file to rename.
        new_name: The new name of the file, including its extension (e.g., file.txt, file.pdf, file.csv)
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "file",
            "helper_text": "The file to rename.",
            "value": None,
            "type": "file",
        },
        {
            "field": "new_name",
            "helper_text": "The new name of the file, including its extension (e.g., file.txt, file.pdf, file.csv)",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Rename an existing file, assigning a new name along with the file extension",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="rename_file",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "RenameFileTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("start_flag")
class StartFlagTool(Tool):
    """
    Start Flag

    ## Inputs
        None
    """

    # Common inputs
    _COMMON_INPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Start Flag",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="start_flag",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "StartFlagTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("talk")
class TalkTool(Tool):
    """
    Send a given message at a stage in a conversation.

    ## Inputs
    ### Common Inputs
        is_iframe: The is_iframe input
        variant: The variant input
    ### When variant = 'card'
        button: The button input
        content: The text to send to the user.
        description: The card’s description.
        image_url: The image to be sent at this step in the conversation.
        title: The card’s title.
    ### When variant = 'carousel'
        cards: The cards input
    ### When variant = 'message' and is_iframe = False
        content: The text to send to the user.
    ### When variant = 'message' and is_iframe = True
        content: The text to send to the user.
    ### When variant = 'image'
        image_url: The image to be sent at this step in the conversation.
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "is_iframe",
            "helper_text": "The is_iframe input",
            "value": False,
            "type": "bool",
        },
        {
            "field": "variant",
            "helper_text": "The variant input",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "message**false": {
            "title": "Message",
            "documentation_url": "https://docs.vectorshift.ai/platform/pipelines/conversational/talk/message",
            "helper_text": "Send a given message at a stage in a conversation.",
            "short_description": "Send a given message at a stage in a conversation.",
            "inputs": [
                {
                    "field": "content",
                    "type": "string",
                    "helper_text": "The text to send to the user.",
                    "value": "",
                },
                {"field": "variant", "type": "string", "value": "message"},
            ],
            "outputs": [],
        },
        "message**true": {
            "title": "Message",
            "documentation_url": "https://docs.vectorshift.ai/platform/pipelines/conversational/talk/message",
            "helper_text": "Send a given message at a stage in a conversation.",
            "short_description": "Send a given iframe at a stage in a conversation.",
            "inputs": [
                {
                    "field": "content",
                    "type": "string",
                    "helper_text": "The text to send to the user.",
                    "value": "<iframe src='ENTER_URL_HERE' width='320px' height='400px'></iframe>",
                },
                {"field": "variant", "type": "string", "value": "message"},
            ],
            "outputs": [],
            "banner_text": "Please add your url in 'ENTER_URL_HERE'. Iframe width should be 320px",
        },
        "image**(*)": {
            "title": "Image",
            "documentation_url": "https://docs.vectorshift.ai/platform/pipelines/conversational/talk/image",
            "helper_text": "Send an image in chat at this step in the conversation.",
            "short_description": "Send an image in chat at this step in the conversation.",
            "inputs": [
                {"field": "variant", "type": "string", "value": "image"},
                {
                    "field": "image_url",
                    "type": "image",
                    "helper_text": "The image to be sent at this step in the conversation.",
                },
            ],
            "outputs": [],
        },
        "card**(*)": {
            "title": "Card",
            "documentation_url": "https://docs.vectorshift.ai/platform/pipelines/conversational/talk/card",
            "helper_text": "Send a card (a component with image, title, description, and button) in chat at this step in the conversation.",
            "short_description": "Send a card (a component with image, title, description, and button) in chat at this step in the conversation.",
            "inputs": [
                {"field": "variant", "type": "string", "value": "card"},
                {"field": "content", "type": "string", "value": "This is content"},
                {
                    "field": "title",
                    "type": "string",
                    "value": "",
                    "helper_text": "The card’s title.",
                },
                {
                    "field": "description",
                    "type": "string",
                    "value": "",
                    "helper_text": "The card’s description.",
                },
                {
                    "field": "button",
                    "type": "Dict[str, Any]",
                    "value": {
                        "id": "asfkwewkfmdke",
                        "name": "Submit",
                        "url": "https://vectorshift.ai/",
                        "actionType": "Link",
                    },
                    "table": {
                        "name": {"helper_text": "The name of the button."},
                        "url": {
                            "helper_text": "The URL to navigate to when the button is clicked."
                        },
                        "actionType": {
                            "helper_text": "Select the action to occur when the button is clicked."
                        },
                    },
                },
                {
                    "field": "image_url",
                    "type": "image",
                    "helper_text": "The card’s image.",
                },
            ],
            "outputs": [],
        },
        "carousel**(*)": {
            "title": "Carousel",
            "documentation_url": "https://docs.vectorshift.ai/platform/pipelines/conversational/talk/carousel",
            "helper_text": "Send a carousel (a gallery of multiple cards) in chat at this step in the conversation.",
            "short_description": "Send a carousel (a gallery of multiple cards) in chat at this step in the conversation.",
            "inputs": [
                {"field": "variant", "type": "string", "value": "carousel"},
                {
                    "field": "cards",
                    "type": "vec<Dict[str, Any] }>",
                    "value": [
                        {
                            "id": "afgj3rf4fmo3i4jrf43rgfm",
                            "title": "Card 1",
                            "description": "This is a description",
                            "image_url": {},
                            "button": {
                                "id": "fref43jrfn",
                                "name": "Submit",
                                "url": "https://vectorshift.ai/",
                                "actionType": "Link",
                            },
                        }
                    ],
                    "table": {
                        "title": {"helper_text": "The card’s title."},
                        "description": {"helper_text": "The card’s description."},
                        "image_url": {"helper_text": "The card’s image URL."},
                        "button": {
                            "name": {"helper_text": "The name of the button."},
                            "url": {
                                "helper_text": "The URL to navigate to when the button is clicked."
                            },
                            "actionType": {
                                "helper_text": "Select the action to occur when the button is clicked."
                            },
                        },
                    },
                },
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["variant", "is_iframe"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Send a given message at a stage in a conversation.",
        variant: str | ToolInput = "",
        is_iframe: bool | ToolInput = False,
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(variant, ToolInput):
            if variant.type == "static":
                params["variant"] = variant.value
            else:
                raise ValueError(f"variant cannot be a dynamic input")
        else:
            params["variant"] = variant
        if isinstance(is_iframe, ToolInput):
            if is_iframe.type == "static":
                params["is_iframe"] = is_iframe.value
            else:
                raise ValueError(f"is_iframe cannot be a dynamic input")
        else:
            params["is_iframe"] = is_iframe

        super().__init__(
            tool_type="talk",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if variant is not None:
            if isinstance(variant, ToolInput):
                self.inputs["variant"] = {
                    "type": variant.type,
                    "value": variant.value or variant.description,
                }
            else:
                self.inputs["variant"] = {"type": "static", "value": variant}
        if is_iframe is not None:
            if isinstance(is_iframe, ToolInput):
                self.inputs["is_iframe"] = {
                    "type": is_iframe.type,
                    "value": is_iframe.value or is_iframe.description,
                }
            else:
                self.inputs["is_iframe"] = {"type": "static", "value": is_iframe}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "TalkTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("listen")
class ListenTool(Tool):
    """
    Listen for user input at a stage in the conversation.

    ## Inputs
    ### Common Inputs
        variant: The variant input
    ### button
        allow_user_message: The allow_user_message input
        buttons: The buttons input
        processed_outputs: The processed_outputs input
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "variant",
            "helper_text": "The variant input",
            "value": "",
            "type": "string",
        }
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "button": {
            "title": "Button",
            "documentation_url": "https://docs.vectorshift.ai/platform/pipelines/conversational/listen/button",
            "helper_text": "Present users with clickable buttons during a conversation at this step and wait for the user to select one.",
            "short_description": "Present users with clickable buttons during a conversation at this step and wait for the user to select one.",
            "inputs": [
                {
                    "field": "buttons",
                    "type": "vec<Dict[str, Any]>",
                    "value": [{"name": "Button 1", "id": "8awi58eyqirm8ik9aq3"}],
                },
                {
                    "field": "processed_outputs",
                    "type": "map<string, string>",
                    "value": {"button_1": "path"},
                },
                {"field": "variant", "type": "string", "value": "button"},
                {"field": "allow_user_message", "type": "bool", "value": False},
            ],
            "outputs": [{"field": "[processed_outputs]", "type": ""}],
        },
        "capture": {
            "title": "Capture",
            "documentation_url": "https://docs.vectorshift.ai/platform/pipelines/conversational/listen/capture",
            "helper_text": "The conversation will pause at this step in the conversation and wait for the user to respond in chat. The user response will be stored in the capture response variable.",
            "short_description": "The conversation will pause at this step in the conversation and wait for the user to respond in chat. The user response will be stored in the capture response variable.",
            "inputs": [{"field": "variant", "type": "string", "value": "capture"}],
            "outputs": [
                {
                    "field": "response",
                    "type": "string",
                    "value": "",
                    "helper_text": "The user message.",
                }
            ],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["variant"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Listen for user input at a stage in the conversation.",
        variant: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(variant, ToolInput):
            if variant.type == "static":
                params["variant"] = variant.value
            else:
                raise ValueError(f"variant cannot be a dynamic input")
        else:
            params["variant"] = variant

        super().__init__(
            tool_type="listen",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if variant is not None:
            if isinstance(variant, ToolInput):
                self.inputs["variant"] = {
                    "type": variant.type,
                    "value": variant.value or variant.description,
                }
            else:
                self.inputs["variant"] = {"type": "static", "value": variant}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "ListenTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("add_node")
class AddNodeTool(Tool):
    """
    Add Node

    ## Inputs
        None
    """

    # Common inputs
    _COMMON_INPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Add Node",
        **kwargs,
    ):
        # Initialize with params
        params = {}

        super().__init__(
            tool_type="add_node",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "AddNodeTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("convert_type")
class ConvertTypeTool(Tool):
    """
    Convert value from source type to target type.

    ## Inputs
    ### Common Inputs
        source_type: The type of the value to convert.
        target_type: The type to convert the value to.
        value: The value to convert
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "source_type",
            "helper_text": "The type of the value to convert.",
            "value": "string",
            "type": "enum<string>",
        },
        {
            "field": "target_type",
            "helper_text": "The type to convert the value to.",
            "value": "int32",
            "type": "enum<string>",
        },
        {
            "field": "value",
            "helper_text": "The value to convert",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "int32": {
            "inputs": [
                {
                    "field": "target_type",
                    "type": "enum<string>",
                    "value": "int32",
                    "helper_text": "The type to convert the value to.",
                }
            ],
            "outputs": [
                {
                    "field": "converted_value",
                    "type": "int32",
                    "helper_text": "The converted value in Integer type",
                }
            ],
        },
        "float": {
            "inputs": [
                {
                    "field": "target_type",
                    "type": "enum<string>",
                    "value": "float",
                    "helper_text": "The type to convert the value to.",
                }
            ],
            "outputs": [
                {
                    "field": "converted_value",
                    "type": "float",
                    "helper_text": "The converted value in Decimal type",
                }
            ],
        },
        "bool": {
            "inputs": [
                {
                    "field": "target_type",
                    "type": "enum<string>",
                    "value": "bool",
                    "helper_text": "The type to convert the value to.",
                }
            ],
            "outputs": [
                {
                    "field": "converted_value",
                    "type": "bool",
                    "helper_text": "The converted value in Boolean type",
                }
            ],
        },
        "timestamp": {
            "inputs": [
                {
                    "field": "target_type",
                    "type": "enum<string>",
                    "value": "timestamp",
                    "helper_text": "The type to convert the value to.",
                }
            ],
            "outputs": [
                {
                    "field": "converted_value",
                    "type": "timestamp",
                    "helper_text": "The converted value in Timestamp type",
                }
            ],
            "banner_text": "Timestamp format: YYYY-MM-DDTHH:MM:SS",
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["target_type"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Convert value from source type to target type.",
        target_type: str | ToolInput = "int32",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(target_type, ToolInput):
            if target_type.type == "static":
                params["target_type"] = target_type.value
            else:
                raise ValueError(f"target_type cannot be a dynamic input")
        else:
            params["target_type"] = target_type

        super().__init__(
            tool_type="convert_type",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if target_type is not None:
            if isinstance(target_type, ToolInput):
                self.inputs["target_type"] = {
                    "type": target_type.type,
                    "value": target_type.value or target_type.description,
                }
            else:
                self.inputs["target_type"] = {"type": "static", "value": target_type}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "ConvertTypeTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("set_variable")
class SetVariableTool(Tool):
    """
    Set a variable to a new value

    ## Inputs
    ### Common Inputs
        scope: The scope of the variable
        variable_id: The ID of the variable to set
        variable_set_id: The ID of the variable set
    ### When variable_set_id = '[variable_sets._id.<A>]' and scope = '<Scope>' and variable_id = '<VariableId>'
        value: The new value to set the variable to
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "scope",
            "helper_text": "The scope of the variable",
            "value": "",
            "type": "string",
        },
        {
            "field": "variable_id",
            "helper_text": "The ID of the variable to set",
            "value": "",
            "type": "string",
        },
        {
            "field": "variable_set_id",
            "helper_text": "The ID of the variable set",
            "value": "",
            "type": "string",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "[variable_sets._id.<A>]**<Scope>**<VariableId>": {
            "inputs": [
                {
                    "field": "value",
                    "type": "{<A>.variables.<Scope>.<VariableId>.data_type}",
                    "helper_text": "The new value to set the variable to",
                }
            ],
            "outputs": [],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["variable_set_id", "scope", "variable_id"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Set a variable to a new value",
        variable_set_id: str | ToolInput = "",
        scope: str | ToolInput = "",
        variable_id: str | ToolInput = "",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(variable_set_id, ToolInput):
            if variable_set_id.type == "static":
                params["variable_set_id"] = variable_set_id.value
            else:
                raise ValueError(f"variable_set_id cannot be a dynamic input")
        else:
            params["variable_set_id"] = variable_set_id
        if isinstance(scope, ToolInput):
            if scope.type == "static":
                params["scope"] = scope.value
            else:
                raise ValueError(f"scope cannot be a dynamic input")
        else:
            params["scope"] = scope
        if isinstance(variable_id, ToolInput):
            if variable_id.type == "static":
                params["variable_id"] = variable_id.value
            else:
                raise ValueError(f"variable_id cannot be a dynamic input")
        else:
            params["variable_id"] = variable_id

        super().__init__(
            tool_type="set_variable",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if variable_set_id is not None:
            if isinstance(variable_set_id, ToolInput):
                self.inputs["variable_set_id"] = {
                    "type": variable_set_id.type,
                    "value": variable_set_id.value or variable_set_id.description,
                }
            else:
                self.inputs["variable_set_id"] = {
                    "type": "static",
                    "value": variable_set_id,
                }
        if scope is not None:
            if isinstance(scope, ToolInput):
                self.inputs["scope"] = {
                    "type": scope.type,
                    "value": scope.value or scope.description,
                }
            else:
                self.inputs["scope"] = {"type": "static", "value": scope}
        if variable_id is not None:
            if isinstance(variable_id, ToolInput):
                self.inputs["variable_id"] = {
                    "type": variable_id.type,
                    "value": variable_id.value or variable_id.description,
                }
            else:
                self.inputs["variable_id"] = {"type": "static", "value": variable_id}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "SetVariableTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


@Tool.register_tool_type("list_deduplicator")
class ListDeduplicatorTool(Tool):
    """
    Remove duplicate items from a list. Outputs a list of unique items.

    ## Inputs
    ### Common Inputs
        type: The type of the list
    ### <T>
        list: The list to deduplicate
    """

    # Common inputs
    _COMMON_INPUTS = [
        {
            "field": "type",
            "helper_text": "The type of the list",
            "value": "string",
            "type": "enum<string>",
        }
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "<T>": {
            "inputs": [
                {
                    "field": "list",
                    "type": "vec<<T>>",
                    "value": [],
                    "helper_text": "The list to deduplicate",
                }
            ],
            "outputs": [
                {
                    "field": "unique_items",
                    "type": "vec<<T>>",
                    "helper_text": "The list of unique items",
                }
            ],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["type"]

    def __init__(
        self,
        id: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_description: str = "Remove duplicate items from a list. Outputs a list of unique items.",
        type: str | ToolInput = "string",
        **kwargs,
    ):
        # Initialize with params
        params = {}
        if isinstance(type, ToolInput):
            if type.type == "static":
                params["type"] = type.value
            else:
                raise ValueError(f"type cannot be a dynamic input")
        else:
            params["type"] = type

        super().__init__(
            tool_type="list_deduplicator",
            params=params,
            id=id,
            tool_name=tool_name,
            tool_description=tool_description,
        )

        # Set static input values
        if type is not None:
            if isinstance(type, ToolInput):
                self.inputs["type"] = {
                    "type": type.type,
                    "value": type.value or type.description,
                }
            else:
                self.inputs["type"] = {"type": "static", "value": type}

        # Update any additional static inputs
        if kwargs:
            self.update_inputs(**kwargs)

        # Add dynamic inputs
        self.add_dynamic_inputs()

        # add task name
        self.set_tool_task_name()

    @classmethod
    def from_dict(cls, data: dict) -> "ListDeduplicatorTool":
        """Create a tool instance from a dictionary."""
        inputs = data.get("value", {}).get("inputs", {})
        inputs = {k: v.get("value") for k, v in inputs.items()}
        id = data.get("id", None)
        name = data.get("name", None)
        description = data.get("description", None)
        return cls(**inputs, id=id, tool_name=name, tool_description=description)


__all__ = [
    "AppendFilesTool",
    "StickyNoteTool",
    "CustomGroupTool",
    "TransformationTool",
    "ChatFileReaderTool",
    "PipelineTool",
    "AgentTool",
    "ChatMemoryTool",
    "LlmTool",
    "InputTool",
    "OutputTool",
    "CategorizerTool",
    "ExtractDataTool",
    "DataCollectorTool",
    "ScorerTool",
    "SpeechToTextTool",
    "FileSaveTool",
    "ImageGenTool",
    "FileTool",
    "GetListItemTool",
    "LlmOpenAiVisionTool",
    "LlmGoogleVisionTool",
    "SplitTextTool",
    "SummarizerTool",
    "TextTool",
    "TextToFileTool",
    "TimeTool",
    "TranslatorTool",
    "TtsElevenLabsTool",
    "TtsOpenAiTool",
    "AiAudioOperationsTool",
    "AiTextToSpeechTool",
    "AiSpeechToTextTool",
    "AiImageOperationsTool",
    "AiImageToTextTool",
    "AiTextToImageTool",
    "LlmAnthropicVisionTool",
    "SemanticSearchTool",
    "KnowledgeBaseTool",
    "KnowledgeBaseLoaderTool",
    "MapTool",
    "MergeTool",
    "ConditionTool",
    "NlToSqlTool",
    "ReadJsonValuesTool",
    "WriteJsonValueTool",
    "ApiTool",
    "UrlLoaderTool",
    "WikipediaTool",
    "YoutubeTool",
    "ArxivTool",
    "SerpApiTool",
    "YouDotComTool",
    "ExaAiTool",
    "GoogleSearchTool",
    "GoogleAlertRssReaderTool",
    "RssFeedReaderTool",
    "CsvQueryTool",
    "CsvReaderTool",
    "CsvWriterTool",
    "CreateListTool",
    "CombineListTool",
    "ListTrimmerTool",
    "DuplicateListTool",
    "FlattenListTool",
    "JoinListItemTool",
    "CsvToExcelTool",
    "TextFormatterTool",
    "JsonOperationsTool",
    "ListOperationsTool",
    "IntegrationGmailTool",
    "IntegrationCopperTool",
    "IntegrationDiscordTool",
    "IntegrationLinearTool",
    "IntegrationOutlookTool",
    "IntegrationSalesforceTool",
    "IntegrationSlackTool",
    "IntegrationJiraTool",
    "IntegrationSugarCrmTool",
    "IntegrationGithubTool",
    "IntegrationZendeskTool",
    "IntegrationTeamsTool",
    "IntegrationXTool",
    "IntegrationGohighlevelTool",
    "IntegrationPeopledatalabsTool",
    "IntegrationHubspotTool",
    "IntegrationSnowflakeTool",
    "IntegrationElasticsearchTool",
    "IntegrationMongodbTool",
    "IntegrationPineconeTool",
    "IntegrationPostgresTool",
    "IntegrationMysqlTool",
    "IntegrationWordpressTool",
    "IntegrationLinkedinTool",
    "IntegrationGoogleCalendarTool",
    "IntegrationMicrosoftCalendarTool",
    "IntegrationMailgunTool",
    "IntegrationGoogleDocsTool",
    "IntegrationMicrosoftTool",
    "IntegrationTypeformTool",
    "IntegrationDropboxTool",
    "IntegrationBoxTool",
    "IntegrationGoogleDriveTool",
    "IntegrationGoogleSheetsTool",
    "IntegrationAirtableTool",
    "IntegrationNotionTool",
    "IntegrationDatabricksTool",
    "IntegrationWeaviateTool",
    "IntegrationBlandAiTool",
    "IntegrationAlgoliaTool",
    "IntegrationApolloTool",
    "ZapierTool",
    "MakeTool",
    "TextManipulationTool",
    "FileOperationsTool",
    "AiOperationsTool",
    "FileToTextTool",
    "CodeExecutionTool",
    "ChunkingTool",
    "NotificationsTool",
    "CustomSmtpEmailSenderTool",
    "EmailNotificationTool",
    "SmsNotificationTool",
    "AiFilterListTool",
    "FilterListTool",
    "SalesDataEnrichmentTool",
    "EmailValidatorTool",
    "CombineTextTool",
    "FindAndReplaceTool",
    "AiFillPdfTool",
    "ExtractToTableTool",
    "SortCsvTool",
    "TriggerOutlookTool",
    "TriggerGmailTool",
    "TriggerCronTool",
    "TriggerSlackTool",
    "KnowledgeBaseActionsTool",
    "KnowledgeBaseSyncTool",
    "KnowledgeBaseCreateTool",
    "ShareObjectTool",
    "RenameFileTool",
    "StartFlagTool",
    "TalkTool",
    "ListenTool",
    "AddNodeTool",
    "ConvertTypeTool",
    "SetVariableTool",
    "ListDeduplicatorTool",
]
