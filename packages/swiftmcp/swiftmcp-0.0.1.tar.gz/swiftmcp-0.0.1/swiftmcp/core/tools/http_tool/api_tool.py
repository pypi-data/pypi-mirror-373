import json
from os import getenv
from typing import Any, Dict, List, Union
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel

from . import ssrf_proxy
from .tool_bundle import ApiToolBundle

API_TOOL_DEFAULT_TIMEOUT = (
    int(getenv('API_TOOL_DEFAULT_CONNECT_TIMEOUT', '10')),
    int(getenv('API_TOOL_DEFAULT_READ_TIMEOUT', '60'))
)


class ApiTool(BaseModel):
    api_bundle: ApiToolBundle

    def assembling_request(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assemble request headers and validate required parameters.
        
        Args:
            parameters: Tool parameters
            
        Returns:
            Request headers
            
        Raises:
            ValueError: If required parameters are missing
        """
        headers = {}

        if self.api_bundle.parameters:
            for parameter in self.api_bundle.parameters:
                if parameter.required and parameter.name not in parameters:
                    raise ValueError(f"Missing required parameter {parameter.name}")

                if parameter.default is not None and parameter.name not in parameters:
                    parameters[parameter.name] = parameter.default

        return headers

    @staticmethod
    def get_parameter_value(parameter: Dict[str, Any], parameters: Dict[str, Any]) -> Any:
        """
        Get parameter value from parameters dict or schema default.
        
        Args:
            parameter: Parameter definition
            parameters: Provided parameters
            
        Returns:
            Parameter value
        """
        if parameter['name'] in parameters:
            return parameters[parameter['name']]
        elif parameter.get('required', False):
            raise ValueError(f"Missing required parameter {parameter['name']}")
        else:
            return (parameter.get('schema', {}) or {}).get('default', '')

    def do_http_request(self, url: str, method: str, headers: Dict[str, Any],
                        parameters: Dict[str, Any]) -> httpx.Response:
        """
        Do http request depending on api bundle.
        
        Args:
            url: Request URL
            method: HTTP method
            headers: Request headers
            parameters: Request parameters
            
        Returns:
            HTTP response
        """
        method = method.lower()

        params = {}
        path_params = {}
        body = {}
        cookies = {}

        # Handle query, path, header, and cookie parameters
        for parameter in self.api_bundle.openapi.get('parameters', []):
            value = self.get_parameter_value(parameter, parameters)
            if parameter['in'] == 'path':
                path_params[parameter['name']] = value
            elif parameter['in'] == 'query' and value != '':
                params[parameter['name']] = value
            elif parameter['in'] == 'cookie':
                cookies[parameter['name']] = value
            elif parameter['in'] == 'header':
                headers[parameter['name']] = value

        # Handle request body
        if 'requestBody' in self.api_bundle.openapi and self.api_bundle.openapi['requestBody'] is not None:
            if 'content' in self.api_bundle.openapi['requestBody']:
                for content_type in self.api_bundle.openapi['requestBody']['content']:
                    headers['Content-Type'] = content_type
                    body_schema = self.api_bundle.openapi['requestBody']['content'][content_type]['schema']
                    required = body_schema.get('required', [])
                    properties = body_schema.get('properties', {})
                    
                    for name, property_def in properties.items():
                        if name in parameters:
                            # Convert type
                            body[name] = self._convert_body_property_type(property_def, parameters[name])
                        elif name in required:
                            raise ValueError(
                                f"Missing required parameter {name} in operation {self.api_bundle.operation_id}"
                            )
                        elif 'default' in property_def:
                            body[name] = property_def['default']
                        else:
                            body[name] = None
                    break

        # Replace path parameters in URL
        for name, value in path_params.items():
            url = url.replace(f'{{{name}}}', str(value))

        # Process body based on content type
        if 'Content-Type' in headers:
            if headers['Content-Type'] == 'application/json':
                body = json.dumps(body)
            elif headers['Content-Type'] == 'application/x-www-form-urlencoded':
                body = urlencode(body)

        # Make HTTP request
        if method in ('get', 'head', 'post', 'put', 'delete', 'patch'):
            return getattr(ssrf_proxy, method)(
                url, 
                params=params, 
                headers=headers, 
                cookies=cookies, 
                data=body,
                timeout=API_TOOL_DEFAULT_TIMEOUT, 
                follow_redirects=True
            )
        else:
            raise ValueError(f'Invalid http method {method}')

    def _convert_body_property_any_of(self, property_def: Dict[str, Any], value: Any, 
                                      any_of: List[Dict[str, Any]], max_recursive: int = 10) -> Any:
        """
        Convert body property with anyOf schema.
        
        Args:
            property_def: Property schema
            value: Property value
            any_of: anyOf schema options
            max_recursive: Maximum recursion depth
            
        Returns:
            Converted value
        """
        if max_recursive <= 0:
            raise Exception("Max recursion depth reached")
            
        for option in any_of or []:
            try:
                if 'type' in option:
                    # Attempt to convert the value based on the type.
                    option_type = option['type']
                    if option_type in ('integer', 'int'):
                        return int(value)
                    elif option_type == 'number':
                        return float(value) if '.' in str(value) else int(value)
                    elif option_type == 'string':
                        return str(value)
                    elif option_type == 'boolean':
                        if str(value).lower() in ('true', '1'):
                            return True
                        elif str(value).lower() in ('false', '0'):
                            return False
                        else:
                            continue  # Not a boolean, try next option
                    elif option_type == 'null' and not value:
                        return None
                    else:
                        continue  # Unsupported type, try next option
                elif 'anyOf' in option and isinstance(option['anyOf'], list):
                    # Recursive call to handle nested anyOf
                    return self._convert_body_property_any_of(
                        property_def, value, option['anyOf'], max_recursive - 1
                    )
            except (ValueError, TypeError):
                continue  # Conversion failed, try next option
        
        # If no option succeeded, return the value as is
        return value

    def _convert_body_property_type(self, property_def: Dict[str, Any], value: Any) -> Any:
        """
        Convert body property type.
        
        Args:
            property_def: Property schema
            value: Property value
            
        Returns:
            Converted value
        """
        try:
            if 'type' in property_def:
                prop_type = property_def['type']
                if prop_type in ('integer', 'int'):
                    return int(value)
                elif prop_type == 'number':
                    # Check if it is a float
                    return float(value) if '.' in str(value) else int(value)
                elif prop_type == 'string':
                    return str(value)
                elif prop_type == 'boolean':
                    return bool(value)
                elif prop_type == 'null':
                    return None if value is None else value
                elif prop_type in ('object', 'array'):
                    if isinstance(value, str):
                        try:
                            # An array str like '[1,2]' also can convert to list [1,2] through json.loads
                            # json not support single quote, but we can support it
                            value = value.replace("'", '"')
                            return json.loads(value)
                        except (ValueError, json.JSONDecodeError):
                            return value
                    elif isinstance(value, (dict, list)):
                        return value
                    else:
                        return value
                else:
                    raise ValueError(f"Invalid type {prop_type} for property {property_def}")
            elif 'anyOf' in property_def and isinstance(property_def['anyOf'], list):
                return self._convert_body_property_any_of(property_def, value, property_def['anyOf'])
        except (ValueError, TypeError):
            # If conversion fails, return the original value
            return value
        
        # If we can't determine the type, return the original value
        return value

    def validate_and_parse_response(self, response: Union[httpx.Response, Any]) -> str:
        """
        Validate and parse the response.
        
        Args:
            response: HTTP response
            
        Returns:
            Parsed response as string
        """
        if not isinstance(response, httpx.Response):
            raise ValueError(f'Invalid response type {type(response)}')

        if response.status_code >= 400:
            raise ValueError(f"Request failed with status code {response.status_code} and {response.text}")
            
        if not response.content:
            return 'Empty response from the tool, please check your parameters and try again.'
            
        try:
            response_data = response.json()
            try:
                return json.dumps(response_data, ensure_ascii=False)
            except Exception:
                return json.dumps(response_data)
        except Exception:
            return response.text