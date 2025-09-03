import base64
from enum import Enum
import mimetypes
import os
from typing import Optional

from pydantic import BaseModel

from vectorshift.request import request_client, async_request_client

from pydantic import BaseModel
from typing import List, Optional

class InterfaceFilterObjectType(Enum):
    knowledge_base = 0
    knowledge_base_document = 1
    integration = 2
    integration_item = 3
    knowledge_base_folder = 4

class InterfaceFilterSelectionMode(Enum):
    deselect = 0
    select = 1

class InterfaceFilterItem(BaseModel):
    object_id: Optional[str] = None
    item_id: Optional[str] = None
    document_id: Optional[str] = None
    is_integration_item_directory: Optional[bool] = None
    object_type: InterfaceFilterObjectType

class InterfaceFilter(BaseModel):
    filter_items: List[InterfaceFilterItem]
    selection_mode: InterfaceFilterSelectionMode

class Chatbot:
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        pipeline_id: str,
        deployment_options: Optional[dict] = None,
        access_config: Optional[dict] = None,
        twilio_config: Optional[dict] = None,
        slack_config: Optional[dict] = None,
        deployed: bool = False,
        input: Optional[str] = None,
        output: Optional[str] = None,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.pipeline_id = pipeline_id
        self.deployment_options = deployment_options
        self.access_config = access_config
        self.twilio_config = twilio_config
        self.slack_config = slack_config
        self.deployed = deployed
        self.input = input
        self.output = output

    @classmethod
    def new(
        cls,
        name: str,
        description: str,
        pipeline_id: str,
        deployment_options: Optional[dict] = None,
        access_config: Optional[dict] = None,
        twilio_config: Optional[dict] = None,
        slack_config: Optional[dict] = None,
        input_node_name: Optional[str] = None,
        output_node_name: Optional[str] = None,
    ) -> 'Chatbot':
        """
        Creates a new chatbot instance.
        
        Args:
            name (str): The name of the new chatbot.
            description (str): The description of the new chatbot.
            pipeline_id (str): The ID of the pipeline to use for this chatbot.
            deployment_options (Optional[dict]): Configuration options for deployment.
            access_config (Optional[dict]): Access configuration settings.
            twilio_config (Optional[dict]): Twilio integration configuration.
            slack_config (Optional[dict]): Slack integration configuration.
            input_node_name (Optional[str]): The name of the input node in the pipeline to map the chatbot's input.
            output_node_name (Optional[str]): The name of the output node in the pipeline to map the chatbot's output.
            
        Returns:
            Chatbot: A new Chatbot instance.
            
        Raises:
            Exception: If the chatbot couldn't be created.
        """
        data = {
            "name": name,
            "description": description,
            "pipeline": {
                "id": pipeline_id
            },
            "deployment_options": deployment_options or {},
            "access_config": access_config or {},
            "twilio_config": twilio_config or {},
            "slack_config": slack_config or {},
            "input": input_node_name or "",
            "output": output_node_name or "",
            "deployed": False,
        }

        response = request_client.request("POST", "/chatbot", json=data)
        return cls(
            response["id"],
            name,
            description,
            pipeline_id,
            deployment_options,
            access_config,
            twilio_config,
            slack_config,
            input_node_name,
            output_node_name,
        )

    @classmethod
    async def anew(
        cls,
        name: str,
        description: str,
        pipeline_id: str,
        deployment_options: Optional[dict] = None,
        access_config: Optional[dict] = None,
        twilio_config: Optional[dict] = None,
        slack_config: Optional[dict] = None,
        input_node_name: Optional[str] = None,
        output_node_name: Optional[str] = None,
    ) -> 'Chatbot':
        """
        Async version of new - Creates a new chatbot instance.
        
        Args:
            name (str): The name of the new chatbot.
            description (str): The description of the new chatbot.
            pipeline_id (str): The ID of the pipeline to use for this chatbot.
            deployment_options (Optional[dict]): Configuration options for deployment.
            access_config (Optional[dict]): Access configuration settings.
            twilio_config (Optional[dict]): Twilio integration configuration.
            slack_config (Optional[dict]): Slack integration configuration.
            input_node_name (Optional[str]): The name of the input node in the pipeline to map the chatbot's input.
            output_node_name (Optional[str]): The name of the output node in the pipeline to map the chatbot's output.
            
        Returns:
            Chatbot: A new Chatbot instance.
            
        Raises:
            Exception: If the chatbot couldn't be created.
        """
        data = {
            "name": name,
            "description": description,
            "pipeline": {
                "id": pipeline_id
            },
            "deployment_options": deployment_options or {},
            "access_config": access_config or {},
            "twilio_config": twilio_config or {},
            "slack_config": slack_config or {},
            "input": input_node_name or "",
            "output": output_node_name or "",
            "deployed": False,
        }

        response = await async_request_client.arequest("POST", "/chatbot", json=data)
        return cls(
            response["id"],
            name,
            description,
            pipeline_id,
            deployment_options,
            access_config,
            twilio_config,
            slack_config,
            input_node_name,
            output_node_name,
        )
    
    @classmethod
    def fetch(
        cls,
        id: Optional[str] = None,
        name: Optional[str] = None,
        username: Optional[str] = None,
        org_name: Optional[str] = None,
    ) -> 'Chatbot':
        """Fetches an existing chatbot.
        
        Args:
            id (Optional[str]): The unique identifier of the chatbot to fetch.
            name (Optional[str]): The name of the chatbot to fetch.
            username (Optional[str]): The username of the chatbot owner.
            org_name (Optional[str]): The organization name of the chatbot owner.
            
        Returns:
            Chatbot: The fetched Chatbot instance.
            
        Raises:
            ValueError: If neither id nor name is provided.
            Exception: If the chatbot couldn't be fetched.
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
        response = request_client.request("GET", f"/chatbot", query=query)
        obj = response['object']
        return cls(
            obj['_id'],
            obj['name'],
            obj['description'],
            obj['pipeline']["object_id"],
            obj['deployment_options'],
            obj['access_config'],
            obj['twilio_config'],
            obj['slack_config'],
            obj['deployed'],
            obj['input'],
            obj['output'],
        )

    @classmethod
    async def afetch(
        cls,
        id: Optional[str] = None,
        name: Optional[str] = None,
        username: Optional[str] = None,
        org_name: Optional[str] = None,
    ) -> 'Chatbot':
        """Async version of fetch - Fetches an existing chatbot.
        
        Args:
            id (Optional[str]): The unique identifier of the chatbot to fetch.
            name (Optional[str]): The name of the chatbot to fetch.
            username (Optional[str]): The username of the chatbot owner.
            org_name (Optional[str]): The organization name of the chatbot owner.
            
        Returns:
            Chatbot: The fetched Chatbot instance.
            
        Raises:
            ValueError: If neither id nor name is provided.
            Exception: If the chatbot couldn't be fetched.
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
        response = await async_request_client.arequest("GET", f"/chatbot", query=query)
        obj = response['object']
        return cls(
            obj['_id'],
            obj['name'],
            obj['description'],
            obj['pipeline']["object_id"],
            obj['deployment_options'],
            obj['access_config'],
            obj['twilio_config'],
            obj['slack_config'],
            obj['deployed'],
            obj['input'],
            obj['output'],
        )

    def delete(self) -> dict:
        """Deletes an existing chatbot.
        
        Returns:
            dict: A dictionary containing the status of the deletion operation.
            
        Raises:
            Exception: If the chatbot couldn't be deleted.
        """
        response = request_client.request("DELETE", f"/chatbot/{self.id}")
        return response

    async def adelete(self) -> dict:
        """Async version of delete - Deletes an existing chatbot.
        
        Returns:
            dict: A dictionary containing the status of the deletion operation.
            
        Raises:
            Exception: If the chatbot couldn't be deleted.
        """
        response = await async_request_client.arequest("DELETE", f"/chatbot/{self.id}")
        return response
    
    def run(
        self,
        input: str,
        input_type: str = "text", 
        conversation_id: Optional[str] = None,
        stream: bool = False,
        filter: Optional[InterfaceFilter] = None,
    ) -> dict:
        """Runs the chatbot with the provided input.
        
        Args:
            input (str): The input to send to the chatbot. This can be text content or a file path to an audio file,
                         depending on the input_type parameter.
            input_type (str, optional): The type of input being provided. Can be "text" or "audio". Defaults to "text".
            conversation_id (Optional[str], optional): The ID of an existing conversation to continue. 
                                                      If None, a new conversation will be started. Defaults to None.
            stream (bool, optional): Whether to stream the response. If True, returns a generator that yields
                                    response chunks. (Useful if the output node has a streaming response coming from an LLM node). 
                                    If False, returns the complete response. Defaults to False.
        
        Returns:
            Union[dict, Generator]: If stream is False, returns a dictionary containing the conversation_id, 
                                   output_message, status, and follow_up_questions (if requested).
                                   If stream is True, returns a generator that yields response chunks.
        
        Raises:
            Exception: If the chatbot run fails.
        """
        data = {}

        if input_type == "text":
            data["text"] = input
        elif input_type == "audio":
            try:
                with open(input, "rb") as audio_file:
                    audio_bytes = audio_file.read()
                    data["audio"] = base64.b64encode(audio_bytes).decode('utf-8')
            except OSError as e:
                raise Exception(f"Failed to read audio file: {e}")
        
        if conversation_id is not None:
            data["conversation_id"] = conversation_id
        
        if filter is not None:
            data["filter"] = filter.model_dump()

        if stream:
            data["stream"] = True
            return request_client.stream_request("POST", f"/chatbot/{self.id}/run", json=data)
        else:
            return request_client.request("POST", f"/chatbot/{self.id}/run", json=data)

    async def arun(
        self,
        input: str,
        input_type: str = "text", 
        conversation_id: Optional[str] = None,
        stream: bool = False,
        filter: Optional[InterfaceFilter] = None,
    ) -> dict:
        """Async version of run - Runs the chatbot with the provided input.
        
        Args:
            input (str): The input to send to the chatbot. This can be text content or a file path to an audio file,
                         depending on the input_type parameter.
            input_type (str, optional): The type of input being provided. Can be "text" or "audio". Defaults to "text".
            conversation_id (Optional[str], optional): The ID of an existing conversation to continue. 
                                                      If None, a new conversation will be started. Defaults to None.
            stream (bool, optional): Whether to stream the response. If True, returns a generator that yields
                                    response chunks. (Useful if the output node has a streaming response coming from an LLM node). 
                                    If False, returns the complete response. Defaults to False.
        
        Returns:
            Union[dict, Generator]: If stream is False, returns a dictionary containing the conversation_id, 
                                   output_message, status, and follow_up_questions (if requested).
                                   If stream is True, returns a generator that yields response chunks.
        
        Raises:
            Exception: If the chatbot run fails.
        """
        data = {}

        if input_type == "text":
            data["text"] = input
        elif input_type == "audio":
            try:
                with open(input, "rb") as audio_file:
                    audio_bytes = audio_file.read()
                    data["audio"] = base64.b64encode(audio_bytes).decode('utf-8')
            except OSError as e:
                raise Exception(f"Failed to read audio file: {e}")
        
        if conversation_id is not None:
            data["conversation_id"] = conversation_id
        
        if filter is not None:
            data["filter"] = filter.model_dump()

        if stream:
            data["stream"] = True
            return await async_request_client.astream_request("POST", f"/chatbot/{self.id}/run", json=data)
        else:
            return await async_request_client.arequest("POST", f"/chatbot/{self.id}/run", json=data)
    
    def upload_files(
        self,
        file_paths: List[str],
        conversation_id: Optional[str] = None,
        message_index: Optional[int] = None,
    ) -> dict:
        """Upload files to a chatbot conversation.
        
        This function is useful only if the underlying pipeline of the chatbot contains a chat file reader node.
        Files can be uploaded to start a new conversation or to an existing conversation (conversation_id should 
        be provided in this case). After the file is uploaded, chat file reader node will return responses taking 
        context from the uploaded file(s).
        
        Args:
            file_paths (List[str]): List of file paths to upload.
            conversation_id (Optional[str], optional): ID of an existing conversation to upload files to.
                                                      If None, a new conversation will be created. Defaults to None.
        
        Returns:
            dict: A dictionary containing:
                - conversation_id: ID of the conversation
                - knowledge_base_id: ID of the temporary knowledge base created to store the uploaded files
                - uploaded_files: Information about the uploaded files (name, mime_type)
                - document_id: Unique identifier of each file uploaded in the knowledge base
        Raises:
            Exception: If the file upload fails.
        """
        data = {}
        files = []
        
        for file_path in file_paths:
            try:
                with open(file_path, 'rb') as file:
                    file_content = file.read()
                    file_name = os.path.basename(file_path)
                    mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
                    files.append(('files', (file_name, file_content, mime_type)))
            except OSError as e:
                raise Exception(f"Failed to read file {file_path}: {e}")
        
        if conversation_id is not None:
            data["conversation_id"] = conversation_id
        
        data["message_index"] = message_index or 0
        
        response = request_client.request("POST", f"/chatbot/{self.id}/upload", json=data, files=files)
        return response

    async def aupload_files(
        self,
        file_paths: List[str],
        conversation_id: Optional[str] = None,
        message_index: Optional[int] = None,
    ) -> dict:
        """Async version of upload_files - Upload files to a chatbot conversation.
        
        This function is useful only if the underlying pipeline of the chatbot contains a chat file reader node.
        Files can be uploaded to start a new conversation or to an existing conversation (conversation_id should 
        be provided in this case). After the file is uploaded, chat file reader node will return responses taking 
        context from the uploaded file(s).
        
        Args:
            file_paths (List[str]): List of file paths to upload.
            conversation_id (Optional[str], optional): ID of an existing conversation to upload files to.
                                                      If None, a new conversation will be created. Defaults to None.
        
        Returns:
            dict: A dictionary containing:
                - conversation_id: ID of the conversation
                - knowledge_base_id: ID of the temporary knowledge base created to store the uploaded files
                - uploaded_files: Information about the uploaded files (name, mime_type)
                - document_id: Unique identifier of each file uploaded in the knowledge base
        
        Raises:
            Exception: If the file upload fails.
        """
        data = {}
        files = []
        
        for file_path in file_paths:
            try:
                with open(file_path, 'rb') as file:
                    file_content = file.read()
                    file_name = os.path.basename(file_path)
                    mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
                    files.append(('files', (file_name, file_content, mime_type)))
            except OSError as e:
                raise Exception(f"Failed to read file {file_path}: {e}")
        
        if conversation_id is not None:
            data["conversation_id"] = conversation_id
        
        data["message_index"] = message_index or 0
        
        response = await async_request_client.arequest("POST", f"/chatbot/{self.id}/upload", json=data, files=files)
        return response
