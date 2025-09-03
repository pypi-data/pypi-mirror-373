from bson import ObjectId
from typing import Any, Optional, AsyncGenerator
from pathlib import Path
import io
import asyncio
from vectorshift.pipeline.graph import PipelineGraph
from vectorshift.pipeline.node import Node
from vectorshift.request import request_client, async_request_client

class Pipeline:
    def __init__(self, nodes: list[Node] = None, id: str = None, branch_id: Optional[str] = None, inputs: dict[str, Any] = None, outputs: dict[str, Any] = None):
        self.id = id
        self.nodes = nodes if nodes else []
        self.branch_id = branch_id
        self.inputs = inputs or {}
        self.outputs = outputs or {}

    def _build_pipeline_graph(self, nodes: list[Node]) -> PipelineGraph:
        """Build and validate a pipeline graph from nodes."""
        graph = PipelineGraph.new(nodes)
        graph.validate()
        graph.populate_node_canvas_metadata()
        return graph

    def _prepare_pipeline_data(self, nodes: list[Node] = None) -> dict[str, Any]:
        """Prepare pipeline data structure from nodes."""
        if nodes is None:
            nodes = self.nodes
            
        data = {
            "nodes": {},
            "canvas_metadata": {
                "nodes": {},
                "edges": []
            },
            "inputs": {},
            "outputs": {}
        }

        node_type_counter = {}

        for node in nodes:
            node_name = node.name or f"{node.node_type}_{node_type_counter.get(node.node_type, 0)}"
            node_data = {
                "id": node.id,
                "name": node_name,
                "type": node.node_type,
                "inputs": self.serialize_inputs(node.inputs),
                "outputs": node.outputs,
                "task_name": node.task_name,
                "execution_mode": node.execution_mode or "normal"
            }
            if node.cyclic_inputs:
                node_data["cyclic_inputs"] = node.cyclic_inputs
            if node.node_type == "input":
                data["inputs"][node_name] = node.inputs.get("input_type", "string")
            elif node.node_type == "output":
                data["outputs"][node_name] = node.inputs.get("output_type", "string")
            data["nodes"][node.id] = node_data
            node_type_counter[node.node_type] = node_type_counter.get(node.node_type, 0) + 1
        
        graph = self._build_pipeline_graph(nodes)

        data["canvas_metadata"]["nodes"] = {
            node_id: metadata.model_dump() 
            for node_id, metadata in graph.node_canvas_metadata.items()
        }
        
        data["canvas_metadata"]["edges"] = [
            edge.model_dump() 
            for edge in graph.edges
        ]
        
        return data

    def _prepare_file_inputs(self, inputs: dict[str, Any]) -> tuple[dict[str, Any], list, list]:
        """Prepare file inputs for pipeline execution."""
        pipeline_inputs = {}
        files = []
        open_files = []
        
        for input_name, input_value in inputs.items():
            if input_name in self.inputs:
                if self.inputs[input_name] == "file" and isinstance(input_value, Path):
                    file = open(input_value, "rb")
                    open_files.append(file)
                    files.append((input_name, file))
                elif self.inputs[input_name] == "file" and isinstance(input_value, bytes):
                    file = io.BytesIO(input_value)
                    open_files.append(file)
                    files.append((input_name, file))
                elif self.inputs[input_name] == "file" and isinstance(input_value, io.BufferedReader):
                    open_files.append(input_value)
                    files.append((input_name, input_value))
                else:
                    pipeline_inputs[input_name] = input_value
        
        return pipeline_inputs, files, open_files

    @classmethod
    def new(cls, name: str, nodes: list[Node] = []):
        """
        Create a new pipeline with the specified parameters.
        
        Args:
            name: The name of the pipeline.
            nodes: List of nodes to include in the pipeline.
            
        Returns:
            A new Pipeline instance.
        """
        instance = cls(nodes=nodes)
        data = instance._prepare_pipeline_data(nodes)
        data["name"] = name
        response = request_client.request("POST", "/pipeline", json=data)
        return cls(
            nodes=nodes,
            id=response["id"],
            branch_id=response["branch_id"],
            inputs = data['inputs'],
            outputs = data['outputs']
        )
    
    @classmethod
    def serialize_inputs(cls, inputs: dict[str, Any]) -> dict[str, Any]:
        serialized_inputs = {}
        for input_name, input_value in inputs.items():
            if hasattr(input_value, 'to_dict'):
                serialized_inputs[input_name] = input_value.to_dict()
            else:
                serialized_inputs[input_name] = input_value
        return serialized_inputs

    def add_node(self, node: Node):
        """
        Add a node to the pipeline.

        Args:
            node: The node to add to the pipeline.

        Returns:
            A dictionary containing the status of the addition operation.
        """
        self.nodes.append(node)

    def save(self):
        """Save the pipeline with its current configuration.

        Updates the pipeline in the database with the current nodes, inputs and outputs configuration.

        Returns:
            dict: A dictionary containing the status of the save operation.

        Raises:
            Exception: If the pipeline update fails.
        """
        data = self._prepare_pipeline_data()
        data["branch_id"] = self.branch_id
        response = request_client.request("POST", f"/update/pipeline/{self.id}", json=data)
        return response

    def run(self, inputs: dict[str, Any], stream: bool = False) -> dict[str, Any]:
        """
        Run the pipeline with the specified inputs.
        
        Args:
            inputs: Dictionary of input values for the pipeline.
            stream: Whether to stream the response. (Set true only when pipeline has an output node with a streaming llm input)
            
        Returns:
            Union[dict[str, Any], Generator]: A dictionary containing pipeline outputs and run_id. If stream is True, returns a generator that yields response chunks.
        
        Raises:
            Exception: If the pipeline execution fails.
        """
        pipeline_inputs, files, open_files = self._prepare_file_inputs(inputs)

        data = {
            "inputs": pipeline_inputs
        }
        try:
            if stream:
                data["stream"] = True
                return request_client.stream_request("POST", f"/pipeline/{self.id}/run", json=data, files=files)
            else:
                return request_client.request("POST", f"/pipeline/{self.id}/run", json=data, files=files)
        finally:
            for file in open_files:
                file.close()

    def bulk_run(self, inputs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Run the pipeline with a list of specified inputs.
        
        Args:
            inputs: List of dictionaries of input values for the pipeline.
            
        Returns:
            A list of dictionaries containing the run_id and outputs for each set of inputs.

        Raises:
            Exception: If the pipeline execution fails.
        """
        files = []
        open_files = []
        bulk_run_inputs = []

        for run_inputs in inputs:
            pipeline_inputs, run_files, run_open_files = self._prepare_file_inputs(run_inputs)
            files.extend(run_files)
            open_files.extend(run_open_files)
            bulk_run_inputs.append({"inputs": pipeline_inputs})

        try:
            return request_client.request("POST", f"/pipeline/{self.id}/bulk-run", json={"runs": bulk_run_inputs}, files=files)
        finally:
            for file in open_files:
                file.close()

    async def arun(self, inputs: dict[str, Any], stream: bool = False) -> dict[str, Any]:
        """
        Async version of run - Run the pipeline with the specified inputs.
        
        Args:
            inputs: Dictionary of input values for the pipeline.
            stream: Whether to stream the response. (Set true only when pipeline has an output node with a streaming llm input)
            
        Returns:
            Union[dict[str, Any], AsyncGenerator]: A dictionary containing pipeline outputs and run_id. If stream is True, returns an async generator that yields response chunks.
        
        Raises:
            Exception: If the pipeline execution fails.
        """
        pipeline_inputs, files, open_files = self._prepare_file_inputs(inputs)

        data = {
            "inputs": pipeline_inputs
        }

        try:
            if stream:
                data["stream"] = True
                return async_request_client.astream_request("POST", f"/pipeline/{self.id}/run", json=data, files=files)
            else:
                return await async_request_client.arequest("POST", f"/pipeline/{self.id}/run", json=data, files=files)
        finally:
            for file in open_files:
                file.close()

    async def abulk_run(self, inputs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Async version of bulk_run - Run the pipeline with a list of specified inputs.
        
        Args:
            inputs: List of dictionaries of input values for the pipeline.
            
        Returns:
            A list of dictionaries containing the run_id and outputs for each set of inputs.

        Raises:
            Exception: If the pipeline execution fails.
        """
        files = []
        open_files = []
        bulk_run_inputs = []

        for run_inputs in inputs:
            pipeline_inputs, run_files, run_open_files = self._prepare_file_inputs(run_inputs)
            files.extend(run_files)
            open_files.extend(run_open_files)
            bulk_run_inputs.append({"inputs": pipeline_inputs})

        try:
            return await async_request_client.arequest("POST", f"/pipeline/{self.id}/bulk-run", json={"runs": bulk_run_inputs}, files=files)
        finally:
            for file in open_files:
                file.close()

    @classmethod
    async def anew(cls, name: str, nodes: list[Node] = []):
        """
        Async version of new - Create a new pipeline with the specified parameters.
        
        Args:
            name: The name of the pipeline.
            nodes: List of nodes to include in the pipeline.
            
        Returns:
            A new Pipeline instance.
        """
        instance = cls(nodes=nodes)
        data = instance._prepare_pipeline_data(nodes)
        data["name"] = name

        response = await async_request_client.arequest("POST", "/pipeline", json=data)

        return cls(
            nodes=nodes,
            id=response["id"],
            branch_id=response["branch_id"]
        )

    async def aadd_node(self, node: Node):
        """
        Async version of add_node - Add a node to the pipeline.

        Args:
            node: The node to add to the pipeline.

        Returns:
            A dictionary containing the status of the addition operation.
        """
        self.nodes.append(node)
        data = self._prepare_pipeline_data()
        data["branch_id"] = self.branch_id

        response = await async_request_client.arequest("POST", f"/update/pipeline/{self.id}", json=data)

        return response

    async def asave(self):
        """
        Async version of save - Save the pipeline with its current configuration.

        Returns:
            dict: A dictionary containing the status of the save operation.

        Raises:
            Exception: If the pipeline update fails.
        """
        data = self._prepare_pipeline_data()
        data["branch_id"] = self.branch_id
        response = await async_request_client.arequest("POST", f"/update/pipeline/{self.id}", json=data)
        return response

    @classmethod
    def fetch(
        cls,
        id: Optional[str] = None,
        name: Optional[str] = None,
        username: Optional[str] = None,
        org_name: Optional[str] = None,
    ) -> 'Pipeline':
        """Fetches an existing pipeline.
        
        Args:
            id (Optional[str]): The unique identifier of the pipeline to fetch.
            name (Optional[str]): The name of the pipeline to fetch.
            username (Optional[str]): The username of the pipeline owner.
            org_name (Optional[str]): The organization name of the pipeline owner.
            
        Returns:
            Pipeline: The fetched Pipeline instance.
            
        Raises:
            ValueError: If neither id nor name is provided.
            Exception: If the pipeline couldn't be fetched.
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
        response = request_client.request("GET", f'/pipeline', query=query)

        obj = response['object']
        
        return cls.from_json(obj)
    
    def delete(self):
        """Deletes an existing pipeline.
        
        Returns:
            dict: A dictionary containing the status of the deletion operation.
            
        Raises:
            Exception: If the pipeline couldn't be deleted.
        """
        response = request_client.request("DELETE", f"/pipeline/{self.id}")
        return response

    @classmethod
    async def afetch(
        cls,
        id: Optional[str] = None,
        name: Optional[str] = None,
        username: Optional[str] = None,
        org_name: Optional[str] = None,
    ) -> 'Pipeline':
        """Async version of fetch - Fetches an existing pipeline.
        
        Args:
            id (Optional[str]): The unique identifier of the pipeline to fetch.
            name (Optional[str]): The name of the pipeline to fetch.
            username (Optional[str]): The username of the pipeline owner.
            org_name (Optional[str]): The organization name of the pipeline owner.
            
        Returns:
            Pipeline: The fetched Pipeline instance.
            
        Raises:
            ValueError: If neither id nor name is provided.
            Exception: If the pipeline couldn't be fetched.
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
        response = await async_request_client.arequest("GET", f'/pipeline', query=query)

        obj = response['object']
        
        return cls.from_json(obj)
    
    async def adelete(self):
        """Async version of delete - Deletes an existing pipeline.
        
        Returns:
            dict: A dictionary containing the status of the deletion operation.
            
        Raises:
            Exception: If the pipeline couldn't be deleted.
        """
        response = await async_request_client.arequest("DELETE", f"/pipeline/{self.id}")
        return response

    @classmethod
    def from_json(cls, data: dict) -> 'Pipeline':
        nodes = [Node.from_json(node_data) for node_data in data.get('nodes', {}).values()]
        inputs, outputs = {}, {}
        for node in nodes:
            if node.node_type == "input":
                inputs[node.name] = node.inputs.get("input_type", "string")
            elif node.node_type == "output":
                outputs[node.name] = node.inputs.get("output_type", "string")
        return cls(nodes=nodes, id=data.get('_id'), branch_id=data.get('mainBranch'), inputs=inputs, outputs=outputs)