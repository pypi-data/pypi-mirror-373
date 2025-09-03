import io
from pathlib import Path
from typing import Any, Dict, Optional

from bson import ObjectId
from pydantic import BaseModel
from vectorshift.agent.tool import Tool
from vectorshift.request import request_client, async_request_client


class DetectPII(BaseModel):
    name: bool = False
    email: bool = False
    phone_number: bool = False
    ssn: bool = False
    credit_card_number: bool = False


class LLMInfo(BaseModel):
    provider: str
    model_id: str
    api_key: Optional[str] = None
    fine_tuned_model_id: Optional[str] = None
    endpoint: Optional[str] = None
    deployment_id: Optional[str] = None
    stream_response: bool = False
    json_output: bool = True
    show_source: bool = False
    show_confidence: bool = False
    enable_tools: bool = True
    toxic_input_filtration: bool = False
    detect_pii: Optional[DetectPII] = None
    base_url: Optional[str] = None
    max_retries: Optional[int] = None
    retry_interval_ms: Optional[int] = None


class IOConfig(BaseModel):
    io_type: str
    description: Optional[str] = ""


class Agent:
    def __init__(
        self,
        id: str,
        name: str,
        llm_info: LLMInfo,
        branch_id: Optional[str] = None,
        tools: list[Tool] = [],
        instructions: Optional[str] = None,
        inputs: Dict[str, IOConfig] = {},
        outputs: Dict[str, IOConfig] = {},
    ):
        self.id = id
        self.name = name
        self.branch_id = branch_id
        self.llm_info = llm_info
        self.tools = tools or []
        self.instructions = instructions or ""
        self.inputs = inputs
        self.outputs = outputs

    @classmethod
    def new(
        cls,
        name: str,
        llm_info: LLMInfo,
        tools: list[Tool] = [],
        instructions: Optional[str] = None,
        inputs: Optional[Dict[str, IOConfig]] = None,
        outputs: Optional[Dict[str, IOConfig]] = None,
    ):
        """
        Create a new agent with the specified parameters.

        Args:
            name: The name of the agent.
            llm_info: Configuration for the language model to use.
            tools: List of tools available to the agent.
            instructions: Instructions for the agent.
            inputs: Dictionary mapping input names to their configurations.
            outputs: Dictionary mapping output names to their configurations.

        Returns:
            A new Agent instance.

        Raises:
            Exception: If the agent creation fails.
        """
        data = {
            "name": name,
            "llm_client_key": llm_info.model_dump(),
            "tools": {
                tool.id: {
                    "id": tool.id,
                    "name": tool.name,
                    "description": tool.description,
                    "value": {
                        "node_type": tool.tool_type,
                        "inputs": cls.serialize_inputs(tool.inputs),
                        "task_name": tool.task_name,
                    },
                }
                for tool in tools
            },
            "instructions": instructions or "",
            "inputs": {
                f"input_{ObjectId()}": {
                    "name": name,
                    "io_type": config.io_type,
                    "description": config.description,
                }
                for name, config in (inputs or {}).items()
            },
            "outputs": {
                f"output_{ObjectId()}": {
                    "name": name,
                    "io_type": config.io_type,
                    "description": config.description,
                }
                for name, config in (outputs or {}).items()
            },
        }

        response = request_client.request("POST", "/agent", json=data)
        return cls(
            id=response["id"],
            name=name,
            branch_id=response["branch_id"],
            llm_info=llm_info,
            tools=tools,
            instructions=instructions,
            inputs=inputs,
            outputs=outputs,
        )

    @classmethod
    async def anew(
        cls,
        name: str,
        llm_info: LLMInfo,
        tools: list[Tool] = [],
        instructions: Optional[str] = None,
        inputs: Optional[Dict[str, IOConfig]] = None,
        outputs: Optional[Dict[str, IOConfig]] = None,
    ):
        """
        Async version of new - Create a new agent with the specified parameters.

        Args:
            name: The name of the agent.
            llm_info: Configuration for the language model to use.
            tools: List of tools available to the agent.
            instructions: Instructions for the agent.
            inputs: Dictionary mapping input names to their configurations.
            outputs: Dictionary mapping output names to their configurations.

        Returns:
            A new Agent instance.

        Raises:
            Exception: If the agent creation fails.
        """
        data = {
            "name": name,
            "llm_client_key": llm_info.model_dump(),
            "tools": {
                tool.id: {
                    "id": tool.id,
                    "name": tool.name,
                    "description": tool.description,
                    "value": {
                        "node_type": tool.tool_type,
                        "inputs": cls.serialize_inputs(tool.inputs),
                        "task_name": tool.task_name,
                    },
                }
                for tool in tools
            },
            "instructions": instructions or "",
            "inputs": {
                f"input_{ObjectId()}": {
                    "name": name,
                    "io_type": config.io_type,
                    "description": config.description,
                }
                for name, config in (inputs or {}).items()
            },
            "outputs": {
                f"output_{ObjectId()}": {
                    "name": name,
                    "io_type": config.io_type,
                    "description": config.description,
                }
                for name, config in (outputs or {}).items()
            },
        }

        response = await async_request_client.arequest("POST", "/agent", json=data)
        return cls(
            id=response["id"],
            name=name,
            branch_id=response["branch_id"],
            llm_info=llm_info,
            tools=tools,
            instructions=instructions,
            inputs=inputs,
            outputs=outputs,
        )

    def add_tool(self, tool: Tool):
        """Add a tool to the agent."""
        self.tools.append(tool)

    def update_instructions(self, instructions: str):
        """Update the instructions for the agent."""
        self.instructions = instructions

    def update_llm_info(self, llm_info: LLMInfo):
        """Update the LLM configuration for the agent."""
        self.llm_info = llm_info

    @classmethod
    def serialize_inputs(cls, inputs: dict[str, Any]) -> dict[str, Any]:
        serialized_inputs = {}
        for input_name, input_value in inputs.items():
            if isinstance(input_value, dict):
                input_type = input_value.get("type")
                input_value = input_value.get("value")
                if hasattr(input_value, "to_dict"):
                    serialized_inputs[input_name] = {"type": input_type, "value": input_value.to_dict()}
                else:
                    serialized_inputs[input_name] = {"type": input_type, "value": input_value}
            else:
                raise ValueError(f"Invalid tool input value: {input_value}")
        return serialized_inputs

    @classmethod
    def fetch(
        cls,
        id: Optional[str] = None,
        name: Optional[str] = None,
        username: Optional[str] = None,
        org_name: Optional[str] = None,
    ) -> "Agent":
        """Fetches an existing agent.

        Args:
            id (Optional[str]): The unique identifier of the agent to fetch.
            name (Optional[str]): The name of the agent to fetch.
            username (Optional[str]): The username of the agent owner.
            org_name (Optional[str]): The organization name of the agent owner.

        Returns:
            Agent: The fetched Agent instance.

        Raises:
            ValueError: If neither id nor name is provided.
            Exception: If the agent couldn't be fetched.
        """
        if id is None and name is None:
            raise ValueError("Either id or name must be provided")
        query = {}
        if id is not None:
            query["id"] = id
        if name is not None:
            query["name"] = name
        if username is not None:
            query["username"] = username
        if org_name is not None:
            query["org_name"] = org_name
        response = request_client.request("GET", "/agent", query=query)

        obj = response["object"]

        return cls.from_json(obj)

    @classmethod
    def from_json(cls, data: dict) -> "Agent":
        """Create an agent instance from a JSON dictionary."""
        # Parse LLM info
        llm_data = data.get("llm_client_key", {})
        llm_info = LLMInfo(**llm_data)

        # Parse tools
        tools = []
        for tool_data in data.get("tools", []):
            tool = Tool.from_json(tool_data)
            tools.append(tool)

        # Parse inputs and outputs
        inputs = {}
        outputs = {}

        for input_id, input_data in data.get("inputs", {}).items():
            inputs[input_data.get("name", input_id)] = IOConfig(
                io_type=input_data.get("io_type", "string"),
                description=input_data.get("description"),
            )

        for output_id, output_data in data.get("outputs", {}).items():
            outputs[output_data.get("name", output_id)] = IOConfig(
                io_type=output_data.get("io_type", "string"),
                description=output_data.get("description"),
            )

        return cls(
            id=data.get("_id"),
            name=data.get("name"),
            branch_id=data.get("mainBranch"),
            llm_info=llm_info,
            tools=tools,
            instructions=data.get("instructions", ""),
            inputs=inputs,
            outputs=outputs,
        )

    def delete(self):
        """Deletes an existing agent.

        Returns:
            dict: A dictionary containing the status of the deletion operation.

        Raises:
            Exception: If the agent couldn't be deleted.
        """
        response = request_client.request("DELETE", f"/agent/{self.id}")
        return response

    async def adelete(self):
        """Async version of delete - Deletes an existing agent.

        Returns:
            dict: A dictionary containing the status of the deletion operation.

        Raises:
            Exception: If the agent couldn't be deleted.
        """
        response = await async_request_client.arequest("DELETE", f"/agent/{self.id}")
        return response

    def _prepare_file_inputs(
        self, inputs: dict[str, Any]
    ) -> tuple[dict[str, Any], list, list]:
        """Prepare file inputs for agent execution."""
        agent_inputs = {}
        files = []
        open_files = []

        for input_name, input_value in inputs.items():
            if input_name in self.inputs:
                if self._check_file_input_type(input_name) and isinstance(
                    input_value, Path
                ):
                    file = open(input_value, "rb")
                    open_files.append(file)
                    files.append((input_name, file))
                elif self._check_file_input_type(input_name) and isinstance(
                    input_value, bytes
                ):
                    file = io.BytesIO(input_value)
                    open_files.append(file)
                    files.append((input_name, file))
                elif self._check_file_input_type(input_name) and isinstance(
                    input_value, io.BufferedReader
                ):
                    open_files.append(input_value)
                    files.append((input_name, input_value))
                else:
                    agent_inputs[input_name] = input_value

        return agent_inputs, files, open_files

    def _check_file_input_type(self, input_name: str) -> bool:
        """Check if the input is of file type."""
        return (
            self.inputs[input_name].io_type == "file"
            or self.inputs[input_name].io_type == "audio"
            or self.inputs[input_name].io_type == "image"
        )

    def run(
        self, inputs: dict[str, Any], additional_instructions: Optional[str] = None
    ) -> dict[str, Any]:
        """Run the agent with the specified inputs.

        Args:
            inputs: Dictionary of input values for the agent.
            stream: Whether to stream the response. (Set true only when agent has an output node with a streaming llm input)

        Returns:
            Union[dict[str, Any], Generator]: A dictionary containing agent outputs and run_id.
            If stream is True, returns a generator that yields response chunks.

        Raises:
            Exception: If the agent execution fails.
        """
        agent_inputs, files, open_files = self._prepare_file_inputs(inputs)

        data = {
            "inputs": agent_inputs,
        }
        if additional_instructions:
            data["additional_instructions"] = additional_instructions

        try:
            return request_client.request(
                "POST", f"/agent/{self.id}/run", json=data, files=files
            )
        finally:
            for file in open_files:
                file.close()

    async def arun(
        self, inputs: dict[str, Any], additional_instructions: Optional[str] = None
    ) -> dict[str, Any]:
        """Async version of run - Run the agent with the specified inputs.

        Args:
            inputs: Dictionary of input values for the agent.
            additional_instructions: Optional additional instructions to override the agent's default instructions.

        Returns:
            dict[str, Any]: A dictionary containing agent outputs and run_id.

        Raises:
            Exception: If the agent execution fails.
        """
        agent_inputs, files, open_files = self._prepare_file_inputs(inputs)

        data = {
            "inputs": agent_inputs,
        }
        if additional_instructions:
            data["additional_instructions"] = additional_instructions

        try:
            return await async_request_client.arequest(
                "POST", f"/agent/{self.id}/run", json=data, files=files
            )
        finally:
            for file in open_files:
                file.close()

    def save(self):
        """Save the agent with its current configuration.

        Updates the agent on the server with the current name, LLM configuration, tools,
        instructions, inputs and outputs.

        Returns:
            dict: A dictionary containing the status of the save operation.

        Raises:
            Exception: If the agent update fails.
        """
        data = {
            "name": self.name,
            "branch_id": self.branch_id,
            "llm_client_key": self.llm_info.model_dump(),
            "tools": {
                tool.id: {
                    "id": tool.id,
                    "name": tool.name,
                    "description": tool.description,
                    "value": {
                        "node_type": tool.tool_type,
                        "inputs": self.serialize_inputs(tool.inputs),
                        "task_name": tool.task_name,
                    },
                }
                for tool in self.tools
            },
            "instructions": self.instructions,
            "inputs": {
                f"input_{ObjectId()}": {
                    "name": name,
                    "io_type": config.io_type,
                    "description": config.description,
                }
                for name, config in self.inputs.items()
            },
            "outputs": {
                f"output_{ObjectId()}": {
                    "name": name,
                    "io_type": config.io_type,
                    "description": config.description,
                }
                for name, config in self.outputs.items()
            },
        }

        response = request_client.request("POST", f"/update/agent/{self.id}", json=data)

        return response

    async def asave(self):
        """Async version of save - Save the agent with its current configuration.

        Updates the agent on the server with the current name, LLM configuration, tools,
        instructions, inputs and outputs.

        Returns:
            dict: A dictionary containing the status of the save operation.

        Raises:
            Exception: If the agent update fails.
        """
        data = {
            "name": self.name,
            "branch_id": self.branch_id,
            "llm_client_key": self.llm_info.model_dump(),
            "tools": {
                tool.id: {
                    "id": tool.id,
                    "name": tool.name,
                    "description": tool.description,
                    "value": {
                        "node_type": tool.tool_type,
                        "inputs": self.serialize_inputs(tool.inputs),
                        "task_name": tool.task_name,
                    },
                }
                for tool in self.tools
            },
            "instructions": self.instructions,
            "inputs": {
                f"input_{ObjectId()}": {
                    "name": name,
                    "io_type": config.io_type,
                    "description": config.description,
                }
                for name, config in self.inputs.items()
            },
            "outputs": {
                f"output_{ObjectId()}": {
                    "name": name,
                    "io_type": config.io_type,
                    "description": config.description,
                }
                for name, config in self.outputs.items()
            },
        }

        response = await async_request_client.arequest(
            "POST", f"/update/agent/{self.id}", json=data
        )

        return response

    @classmethod
    async def afetch(
        cls,
        id: Optional[str] = None,
        name: Optional[str] = None,
        username: Optional[str] = None,
        org_name: Optional[str] = None,
    ) -> "Agent":
        """Async version of fetch - Fetches an existing agent.

        Args:
            id (Optional[str]): The unique identifier of the agent to fetch.
            name (Optional[str]): The name of the agent to fetch.
            username (Optional[str]): The username of the agent owner.
            org_name (Optional[str]): The organization name of the agent owner.

        Returns:
            Agent: The fetched Agent instance.

        Raises:
            ValueError: If neither id nor name is provided.
            Exception: If the agent couldn't be fetched.
        """
        if id is None and name is None:
            raise ValueError("Either id or name must be provided")
        query = {}
        if id is not None:
            query["id"] = id
        if name is not None:
            query["name"] = name
        if username is not None:
            query["username"] = username
        if org_name is not None:
            query["org_name"] = org_name
        response = await async_request_client.arequest("GET", "/agent", query=query)

        obj = response["object"]

        return cls.from_json(obj)