from typing import Optional, List, Dict, Any

from pydantic import BaseModel

from .tool_entities import ToolParameter


class ApiToolBundle(BaseModel):
    """
    This class is used to store the schema information of an API based tool, 
    such as the URL, the method, the parameters, etc.
    """
    # Server URL
    server_url: str
    # HTTP method
    method: str
    # Summary/description of the operation
    summary: Optional[str] = None
    # Operation ID
    operation_id: str
    # Input parameters
    parameters: Optional[List[ToolParameter]] = None
    # Return values
    returns: Optional[List[ToolParameter]] = None
    # Author of the tool
    author: str = ""
    # Icon for the tool
    icon: Optional[str] = None
    # OpenAPI operation definition
    openapi: Dict[str, Any]