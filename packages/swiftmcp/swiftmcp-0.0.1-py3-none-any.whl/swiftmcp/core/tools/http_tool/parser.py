import re
import uuid
from typing import Any, Dict, List, Tuple, Optional
from json import dumps as json_dumps
from json import loads as json_loads
from json.decoder import JSONDecodeError

import json
from requests import get
from yaml import YAMLError, safe_load

from .tool_entities import MultilingualText, ToolParameter
from .tool_bundle import ApiToolBundle


def parser_tool(json_data: dict) -> None:
    """Simple tool parser example"""
    base_url = json_data["servers"][0]["url"]
    route_path = list(json_data["paths"].keys())[0]
    url = base_url + route_path
    tool_description = json_data["paths"][route_path]["post"]["description"]
    # Placeholder for future implementation
    pass


class ApiBasedToolSchemaParser:
    """Parser for API-based tool schemas"""
    
    @staticmethod
    def parse_openapi_to_tool_bundle(openapi: dict, extra_info: Optional[dict] = None, 
                                     warning: Optional[dict] = None) -> List[ApiToolBundle]:
        """
        Parse OpenAPI specification to tool bundles.
        
        Args:
            openapi: OpenAPI specification dictionary
            extra_info: Additional information to include
            warning: Warning messages dictionary
            
        Returns:
            List of ApiToolBundle objects
        """
        warning = warning or {}
        extra_info = extra_info or {}

        # Set description to extra_info
        extra_info['description'] = openapi['info'].get('description', '')

        if len(openapi['servers']) == 0:
            raise ValueError('No server found in the OpenAPI specification.')

        server_url = openapi['servers'][0]['url']

        # List all interfaces
        interfaces = []
        for path, path_item in openapi['paths'].items():
            methods = ['get', 'post', 'put', 'delete', 'patch', 'head', 'options', 'trace']
            for method in methods:
                if method in path_item:
                    interfaces.append({
                        'path': path,
                        'method': method,
                        'operation': path_item[method],
                    })

        # Process all operations
        bundles = []
        for interface in interfaces:
            # Convert parameters
            parameters = []
            if 'parameters' in interface['operation']:
                for parameter in interface['operation']['parameters']:
                    tool_parameter = ToolParameter(
                        name=parameter['name'],
                        label=MultilingualText(
                            en_US=parameter['name'],
                            zh_Hans=parameter['name']
                        ),
                        human_description=MultilingualText(
                            en_US=parameter.get('description', ''),
                            zh_Hans=parameter.get('description', '')
                        ),
                        type=ToolParameter.ToolParameterType.STRING,
                        required=parameter.get('required', False),
                        form=ToolParameter.ToolParameterForm.LLM,
                        llm_description=parameter.get('description'),
                        default=parameter['schema']['default'] if 'schema' in parameter and 'default' in parameter['schema'] else None,
                    )
                   
                    # Check if there is a type
                    param_type = ApiBasedToolSchemaParser._get_tool_parameter_type(parameter)
                    if param_type:
                        tool_parameter.type = param_type

                    parameters.append(tool_parameter)
            
            # Handle request body
            if 'requestBody' in interface['operation']:
                parameters.extend(ApiBasedToolSchemaParser._parse_request_body(interface))

            # Handle responses (returns)
            returns = ApiBasedToolSchemaParser._parse_responses(interface, openapi)

            # Check if parameters are duplicated
            parameters_count = {}
            for parameter in parameters:
                parameters_count[parameter.name] = parameters_count.get(parameter.name, 0) + 1
                
            for name, count in parameters_count.items():
                if count > 1:
                    warning['duplicated_parameter'] = f'Parameter {name} is duplicated.'

            # Ensure operation ID exists
            if 'operationId' not in interface['operation']:
                interface['operation']['operationId'] = ApiBasedToolSchemaParser._generate_operation_id(
                    interface['path'], interface['method']
                )

            bundles.append(ApiToolBundle(
                server_url=server_url + interface['path'],
                method=interface['method'],
                summary=interface['operation'].get('description') or interface['operation'].get('summary'),
                operation_id=interface['operation']['operationId'],
                parameters=parameters,
                returns=returns,
                author='',
                icon=None,
                openapi=interface['operation'],
            ))

        return bundles
    
    @staticmethod
    def _parse_request_body(interface: dict) -> List[ToolParameter]:
        """Parse request body parameters"""
        parameters = []
        request_body = interface['operation']['requestBody']
        
        if 'content' not in request_body:
            return parameters

        for content_type, content in request_body['content'].items():
            # Handle schema references
            if 'schema' in content:
                if '$ref' in content['schema']:
                    # Resolve reference
                    root = ApiBasedToolSchemaParser._resolve_reference(
                        content['schema']['$ref'], interface['operation']
                    )
                    interface['operation']['requestBody']['content'][content_type]['schema'] = root

                # Parse body parameters
                if 'schema' in interface['operation']['requestBody']['content'][content_type]:
                    body_schema = interface['operation']['requestBody']['content'][content_type]['schema']
                    required = body_schema.get('required', [])
                    properties = body_schema.get('properties', {})
                    
                    for name, property_def in properties.items():
                        # Determine parameter type
                        type_flag = ApiBasedToolSchemaParser._get_property_type_flag(property_def.get('type'))
                        
                        tool_param = ToolParameter(
                            name=name,
                            label=MultilingualText(en_US=name, zh_Hans=name),
                            human_description=MultilingualText(
                                en_US=property_def.get('description', ''),
                                zh_Hans=property_def.get('description', '')
                            ),
                            type=type_flag,
                            required=name in required,
                            form=ToolParameter.ToolParameterForm.LLM,
                            llm_description=property_def.get('description', ''),
                            default=property_def.get('default', None),
                        )

                        # Check if there is a type
                        typ = ApiBasedToolSchemaParser._get_tool_parameter_type(property_def)
                        if typ:
                            tool_param.type = typ
                        parameters.append(tool_param)
        
        return parameters

    @staticmethod
    def _parse_responses(interface: dict, openapi: dict) -> List[ToolParameter]:
        """Parse response parameters"""
        returns = []
        if 'responses' not in interface['operation']:
            return returns

        responses = interface['operation']['responses']
        if '200' not in responses:
            return returns

        if 'content' not in responses['200']:
            return returns

        for content_type, content in responses['200']['content'].items():
            # Handle schema references
            if 'schema' in content:
                if '$ref' in content['schema']:
                    # Resolve reference
                    root = ApiBasedToolSchemaParser._resolve_reference(
                        content['schema']['$ref'], openapi
                    )
                    # Note: There was a typo in the original code ('responsed' instead of 'responses')
                    interface['operation']['responses']['200']['content'][content_type]['schema'] = root

                # Parse response schema
                if 'schema' in interface['operation']['responses']['200']['content'][content_type]:
                    body_schema = interface['operation']['responses']['200']['content'][content_type]['schema']
                    required = body_schema.get('required', [])
                    properties = body_schema.get('properties', {})
                    
                    for name, property_def in properties.items():
                        tool_param = ToolParameter(
                            name=name,
                            label=MultilingualText(en_US=name, zh_Hans=name),
                            human_description=MultilingualText(
                                en_US=property_def.get('description', ''),
                                zh_Hans=property_def.get('description', '')
                            ),
                            type=ToolParameter.ToolParameterType.STRING,
                            required=name in required,
                            form=ToolParameter.ToolParameterForm.LLM,
                            llm_description=property_def.get('description', ''),
                            default=property_def.get('default', None),
                        )
                        
                        # Check if there is a type
                        typ = ApiBasedToolSchemaParser._get_tool_parameter_type(property_def)
                        if typ:
                            tool_param.type = typ
                        returns.append(tool_param)
        
        return returns

    @staticmethod
    def _resolve_reference(ref: str, root: dict) -> dict:
        """Resolve a JSON reference"""
        reference = ref.split('/')[1:]
        for ref_part in reference:
            root = root[ref_part]
        return root

    @staticmethod
    def _get_property_type_flag(type_str: Optional[str]) -> ToolParameter.ToolParameterType:
        """Get ToolParameterType from string"""
        type_mapping = {
            'int': ToolParameter.ToolParameterType.INT,
            'bool': ToolParameter.ToolParameterType.BOOL,
            'number': ToolParameter.ToolParameterType.NUMBER,
            'float': ToolParameter.ToolParameterType.FLOAT,
            'string': ToolParameter.ToolParameterType.STRING,
        }
        return type_mapping.get(type_str, ToolParameter.ToolParameterType.STRING)

    @staticmethod
    def _generate_operation_id(path: str, method: str) -> str:
        """Generate an operation ID from path and method"""
        # Remove leading slash
        if path.startswith('/'):
            path = path[1:]
        # Remove special characters
        path = re.sub(r'[^a-zA-Z0-9_-]', '', path)
        # Use UUID if path is empty
        if not path:
            path = str(uuid.uuid4())
        return f'{path}_{method}'

    @staticmethod
    def _get_tool_parameter_type(parameter: dict) -> Optional[ToolParameter.ToolParameterType]:
        """Get tool parameter type from parameter definition"""
        parameter = parameter or {}
        typ = None
        
        if 'type' in parameter:
            typ = parameter['type']
        elif 'schema' in parameter and 'type' in parameter['schema']:
            typ = parameter['schema']['type']
        
        type_mapping = {
            'integer': ToolParameter.ToolParameterType.NUMBER,
            'number': ToolParameter.ToolParameterType.NUMBER,
            'boolean': ToolParameter.ToolParameterType.BOOLEAN,
            'string': ToolParameter.ToolParameterType.STRING
        }
        
        return type_mapping.get(typ)

    @staticmethod
    def parse_openapi_yaml_to_tool_bundle(yaml: str, extra_info: Optional[dict] = None, 
                                          warning: Optional[dict] = None) -> List[ApiToolBundle]:
        """
        Parse OpenAPI YAML to tool bundle.
        
        Args:
            yaml: The YAML string
            extra_info: Additional information to include
            warning: Warning messages dictionary
            
        Returns:
            List of ApiToolBundle objects
        """
        warning = warning or {}
        extra_info = extra_info or {}

        openapi: dict = safe_load(yaml)
        if openapi is None:
            raise ValueError('Invalid OpenAPI YAML.')
            
        return ApiBasedToolSchemaParser.parse_openapi_to_tool_bundle(
            openapi, extra_info=extra_info, warning=warning
        )
    
    @staticmethod
    def parse_swagger_to_openapi(swagger: dict, extra_info: Optional[dict] = None, 
                                 warning: Optional[dict] = None) -> dict:
        """
        Parse Swagger specification to OpenAPI.
        
        Args:
            swagger: The Swagger dictionary
            extra_info: Additional information to include
            warning: Warning messages dictionary
            
        Returns:
            OpenAPI dictionary
        """
        warning = warning or {}
        extra_info = extra_info or {}

        # Convert swagger to openapi
        info = swagger.get('info', {
            'title': 'Swagger',
            'description': 'Swagger',
            'version': '1.0.0'
        })

        servers = swagger.get('servers', [])
        if len(servers) == 0:
            raise ValueError('No server found in the Swagger specification.')

        openapi = {
            'openapi': '3.0.0',
            'info': {
                'title': info.get('title', 'Swagger'),
                'description': info.get('description', 'Swagger'),
                'version': info.get('version', '1.0.0')
            },
            'servers': swagger['servers'],
            'paths': {},
            'components': {
                'schemas': {}
            }
        }

        # Check paths
        if 'paths' not in swagger or len(swagger['paths']) == 0:
            raise ValueError('No paths found in the Swagger specification.')

        # Convert paths
        for path, path_item in swagger['paths'].items():
            openapi['paths'][path] = {}
            for method, operation in path_item.items():
                if 'operationId' not in operation:
                    raise ValueError(f'No operationId found in operation {method} {path}.')
                
                if not operation.get('summary') and not operation.get('description'):
                    warning['missing_summary'] = f'No summary or description found in operation {method} {path}.'
                
                openapi['paths'][path][method] = {
                    'operationId': operation['operationId'],
                    'summary': operation.get('summary', ''),
                    'description': operation.get('description', ''),
                    'parameters': operation.get('parameters', []),
                    'responses': operation.get('responses', {}),
                }

                if 'requestBody' in operation:
                    openapi['paths'][path][method]['requestBody'] = operation['requestBody']

        # Convert definitions
        for name, definition in swagger.get('definitions', {}).items():
            openapi['components']['schemas'][name] = definition

        return openapi

    @staticmethod
    def parse_openai_plugin_json_to_tool_bundle(json_str: str, extra_info: Optional[dict] = None, 
                                                warning: Optional[dict] = None) -> List[ApiToolBundle]:
        """
        Parse OpenAI plugin JSON to tool bundle.
        
        Args:
            json_str: The JSON string
            extra_info: Additional information to include
            warning: Warning messages dictionary
            
        Returns:
            List of ApiToolBundle objects
        """
        warning = warning or {}
        extra_info = extra_info or {}

        try:
            openai_plugin = json_loads(json_str)
            api = openai_plugin['api']
            api_url = api['url']
            api_type = api['type']
        except (KeyError, JSONDecodeError):
            raise ValueError('Invalid OpenAI plugin JSON.')
        
        if api_type != 'openapi':
            raise ValueError('Only OpenAPI format is supported.')
        
        # Get OpenAPI YAML
        response = get(api_url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        }, timeout=5)

        if response.status_code != 200:
            raise ValueError('Cannot get OpenAPI YAML from URL.')
        
        return ApiBasedToolSchemaParser.parse_openapi_yaml_to_tool_bundle(
            response.text, extra_info=extra_info, warning=warning
        )
    
    @staticmethod
    def auto_parse_to_tool_bundle(content: str, extra_info: Optional[dict] = None, 
                                  warning: Optional[dict] = None) -> Tuple[List[ApiToolBundle], str]:
        """
        Automatically parse content to tool bundle.
        
        Args:
            content: The content to parse
            extra_info: Additional information to include
            warning: Warning messages dictionary
            
        Returns:
            Tuple of (tool bundles, schema type)
        """
        warning = warning or {}
        extra_info = extra_info or {}

        content = content.strip()
        loaded_content = None
        json_error = None
        yaml_error = None
        
        try:
            loaded_content = json_loads(content)
        except JSONDecodeError as e:
            json_error = e

        if loaded_content is None:
            try:
                loaded_content = safe_load(content)
            except YAMLError as e:
                yaml_error = e
                
        if loaded_content is None:
            raise ValueError(
                f'Invalid API schema, schema is neither JSON nor YAML. '
                f'JSON error: {str(json_error)}, YAML error: {str(yaml_error)}'
            )

        # Try parsing as OpenAPI
        try:
            openapi = ApiBasedToolSchemaParser.parse_openapi_to_tool_bundle(
                loaded_content, extra_info=extra_info, warning=warning
            )
            schema_type = "openapi"
            return openapi, schema_type
        except Exception as e:
            # Store the error for potential debugging
            openapi_error = e

        # Try parsing as Swagger
        try:
            converted_swagger = ApiBasedToolSchemaParser.parse_swagger_to_openapi(
                loaded_content, extra_info=extra_info, warning=warning
            )
            schema_type = "swagger"  # Using string instead of undefined ApiProviderSchemaType.SWAGGER.value
            return ApiBasedToolSchemaParser.parse_openapi_to_tool_bundle(
                converted_swagger, extra_info=extra_info, warning=warning
            ), schema_type
        except Exception as e:
            swagger_error = e

        # Try parsing as OpenAI plugin
        try:
            openapi_plugin = ApiBasedToolSchemaParser.parse_openai_plugin_json_to_tool_bundle(
                json_dumps(loaded_content), extra_info=extra_info, warning=warning
            )
            schema_type = "openai_plugin"  # Using string instead of undefined ApiProviderSchemaType.OPENAI_PLUGIN.value
            return openapi_plugin, schema_type
        except Exception as e:
            openapi_plugin_error = e

        raise ValueError(
            f'Invalid API schema. '
            f'OpenAPI error: {str(openapi_error)}, '
            f'Swagger error: {str(swagger_error)}, '
            f'OpenAI plugin error: {str(openapi_plugin_error)}'
        )


def parser_tool_from_path(tool_path: str, file_reader=None) -> Tuple[List[ApiToolBundle], str]:
    """
    Parse tool from file path.
    
    Args:
        tool_path: Path to the tool file
        file_reader: File reader function (defaults to file_db.read_json)
        
    Returns:
        Tuple of (tool bundles, schema type)
    """
    if file_reader is None:
        from swiftmcp.utils.file_db import AgentFileDB
        file_db = AgentFileDB(db_path="tmp/test.db")
        file_reader = file_db

    content_json = file_reader.read_json(tool_path)
    content = json.dumps(content_json)
    return ApiBasedToolSchemaParser.auto_parse_to_tool_bundle(content)


if __name__ == "__main__":
    tool_bundles, schema_type = parser_tool_from_path("data/tools/SampleTool.json")
    server_url: str = tool_bundles[0].server_url
    request_method: str = tool_bundles[0].method
    summary: str = tool_bundles[0].summary
    parameters: list = tool_bundles[0].parameters
    returns: list = tool_bundles[0].returns
    operation_id = tool_bundles[0].operation_id