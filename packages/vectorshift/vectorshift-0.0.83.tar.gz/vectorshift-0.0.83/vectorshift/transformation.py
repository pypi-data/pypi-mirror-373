from typing import Any, Optional, Dict
from vectorshift.request import request_client, async_request_client


class Transformation:
    def __init__(
        self,
        id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        function_name: Optional[str] = None,
        inputs: Optional[Dict[str, str]] = None,
        outputs: Optional[Dict[str, str]] = None,
        function: Optional[str] = None,
        branch_id: Optional[str] = None,
        version: Optional[Dict[str, int]] = None,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.function_name = function_name
        self.inputs = inputs or {}
        self.outputs = outputs or {}
        self.function = function
        self.branch_id = branch_id
        self.version = version

    @classmethod
    def fetch(
        cls,
        id: Optional[str] = None,
        name: Optional[str] = None,
        username: Optional[str] = None,
        org_name: Optional[str] = None,
    ) -> 'Transformation':
        """Fetches an existing transformation.
        
        Args:
            id (Optional[str]): The unique identifier of the transformation to fetch.
            name (Optional[str]): The name of the transformation to fetch.
            username (Optional[str]): The username of the transformation owner.
            org_name (Optional[str]): The organization name of the transformation owner.
            
        Returns:
            Transformation: The fetched Transformation instance.
            
        Raises:
            ValueError: If neither id nor name is provided.
            Exception: If the transformation couldn't be fetched.
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
            
        response = request_client.request("GET", "/transformation", query=query)
        obj = response['object']
        
        return cls.from_json(obj)

    @classmethod
    async def afetch(
        cls,
        id: Optional[str] = None,
        name: Optional[str] = None,
        username: Optional[str] = None,
        org_name: Optional[str] = None,
    ) -> 'Transformation':
        """Async version of fetch - Fetches an existing transformation.
        
        Args:
            id (Optional[str]): The unique identifier of the transformation to fetch.
            name (Optional[str]): The name of the transformation to fetch.
            username (Optional[str]): The username of the transformation owner.
            org_name (Optional[str]): The organization name of the transformation owner.
            
        Returns:
            Transformation: The fetched Transformation instance.
            
        Raises:
            ValueError: If neither id nor name is provided.
            Exception: If the transformation couldn't be fetched.
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
            
        response = await async_request_client.arequest("GET", "/transformation", query=query)
        obj = response['object']
        
        return cls.from_json(obj)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Transformation':
        """Create a Transformation instance from a JSON dictionary."""
        return cls(
            id=data.get('_id'),
            name=data.get('name'),
            description=data.get('description'),
            function_name=data.get('function_name'),
            inputs=data.get('inputs', {}),
            outputs=data.get('outputs', {}),
            function=data.get('function'),
            branch_id=data.get('mainBranch'),
            version=data.get('version'),
        )


    @classmethod
    def new(
        cls,
        name: str,
        description: str = "",
        function_name: str = "",
        inputs: Dict[str, Any] = None,
        outputs: Dict[str, Any] = None,
        function: str = "",
    ) -> 'Transformation':
        """Create a new transformation with the specified parameters.
        
        Args:
            name: The name of the transformation.
            description: Description of the transformation.
            function_name: Name of the function.
            inputs: Dictionary of input definitions.
            outputs: Dictionary of output definitions.
            function: The function code as a string.
            
        Returns:
            A new Transformation instance.
        """
        data = {
            "name": name,
            "description": description,
            "function_name": function_name,
            "inputs": inputs or {},
            "outputs": outputs or {},
            "function": function,
        }
        
        response = request_client.request("POST", "/transformation", json=data)
        
        return cls(
            id=response["id"],
            name=name,
            description=description,
            function_name=function_name,
            inputs=inputs or {},
            outputs=outputs or {},
            function=function,
            branch_id=response.get("branch_id"),
            version=response.get("version"),
        )

    @classmethod
    async def anew(
        cls,
        name: str,
        description: str = "",
        function_name: str = "",
        inputs: Dict[str, Any] = None,
        outputs: Dict[str, Any] = None,
        function: str = "",
    ) -> 'Transformation':
        """Async version of new - Create a new transformation with the specified parameters.
        
        Args:
            name: The name of the transformation.
            description: Description of the transformation.
            function_name: Name of tshe function.
            inputs: Dictionary of input definitions.
            outputs: Dictionary of output definitions.
            function: The function code as a string.
            
        Returns:
            A new Transformation instance.
        """
        data = {
            "name": name,
            "description": description,
            "function_name": function_name,
            "inputs": inputs or {},
            "outputs": outputs or {},
            "function": function,
        }
        
        response = await async_request_client.arequest("POST", "/transformation", json=data)
        
        return cls(
            id=response["id"],
            name=name,
            description=description,
            function_name=function_name,
            inputs=inputs or {},
            outputs=outputs or {},
            function=function,
            branch_id=response.get("branch_id"),
            version=response.get("version"),
        )
    
    def run(self, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run the transformation with the specified inputs.
        
        Args:
            inputs: Dictionary of input values for the transformation.
            
        Returns:
            Dictionary containing the transformation execution results.
        """
        data = {
            "inputs": inputs or {}
        }
        
        response = request_client.request("POST", f"/transformation/{self.id}/run", json=data)
        
        return response

    async def arun(self, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """Async version of run - Run the transformation with the specified inputs.
        
        Args:
            inputs: Dictionary of input values for the transformation.
            
        Returns:
            Dictionary containing the transformation execution results.
        """
        data = {
            "inputs": inputs or {}
        }
        
        response = await async_request_client.arequest("POST", f"/transformation/{self.id}/run", json=data)
        
        return response