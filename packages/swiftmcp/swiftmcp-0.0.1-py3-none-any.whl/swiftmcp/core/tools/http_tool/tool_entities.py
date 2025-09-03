from enum import Enum
from typing import Any, Optional, Union, List

from pydantic import BaseModel, Field, field_validator


class MultilingualText(BaseModel):
    """
    Supports multiple languages with fallback to English.
    """
    zh_Hans: Optional[str] = None
    en_US: str

    def __init__(self, **data):
        super().__init__(**data)
        if not self.zh_Hans:
            self.zh_Hans = self.en_US
            
    def to_dict(self) -> dict:
        return {
            'zh_Hans': self.zh_Hans,
            'en_US': self.en_US,
        }


class ToolParameterOption(BaseModel):
    """Option for SELECT type parameters"""
    value: str = Field(..., description="The value of the option")
    label: MultilingualText = Field(..., description="The label of the option")

    @field_validator('value', mode='before')
    @classmethod
    def transform_id_to_str(cls, value) -> str:
        """Convert value to string if needed"""
        if not isinstance(value, str):
            return str(value)
        else:
            return value


class ToolParameter(BaseModel):
    """Defines a parameter for a tool"""
    
    class ToolParameterType(str, Enum):
        """Supported parameter types"""
        STRING = "string"
        NUMBER = "number"
        BOOLEAN = "boolean"
        SELECT = "select"
        SECRET_INPUT = "secret-input"
        FILE = "file"
        INT = "int"
        BOOL = "bool"
        FLOAT = "float"

    class ToolParameterForm(Enum):
        """When the parameter value should be provided"""
        SCHEMA = "schema"  # Set while adding tool
        FORM = "form"      # Set before invoking tool
        LLM = "llm"        # Set by LLM

    # Parameter name
    name: str = Field(..., description="The name of the parameter")
    # Label presented to the user
    label: MultilingualText = Field(..., description="The label presented to the user")
    # Description presented to the user
    human_description: Optional[MultilingualText] = Field(None, description="The description presented to the user")
    # Placeholder text for input fields
    placeholder: Optional[MultilingualText] = Field(None, description="The placeholder presented to the user")
    # Parameter type
    type: ToolParameterType = Field(..., description="The type of the parameter")
    # When the parameter should be set
    form: ToolParameterForm = Field(..., description="The form of the parameter, schema/form/llm")
    # Description for LLM
    llm_description: Optional[str] = None
    # Whether the parameter is required
    required: bool = False
    # Default value
    default: Optional[Union[float, int, str]] = None
    # Minimum allowed value (for numeric types)
    min: Optional[Union[float, int]] = None
    # Maximum allowed value (for numeric types)
    max: Optional[Union[float, int]] = None
    # Options for SELECT type parameters
    options: Optional[List[ToolParameterOption]] = None

    @classmethod
    def get_simple_instance(cls, name: str, llm_description: str, param_type: ToolParameterType,
                            required: bool, options: Optional[List[str]] = None) -> 'ToolParameter':
        """
        Create a simple tool parameter.
        
        Args:
            name: The name of the parameter
            llm_description: The description presented to the LLM
            param_type: The type of the parameter
            required: If the parameter is required
            options: The options of the parameter (for SELECT type)
            
        Returns:
            A new ToolParameter instance
        """
        # Convert options to ToolParameterOption objects
        param_options = None
        if options:
            param_options = [
                ToolParameterOption(
                    value=option, 
                    label=MultilingualText(en_US=option, zh_Hans=option)
                ) for option in options
            ]
            
        return cls(
            name=name,
            label=MultilingualText(en_US='', zh_Hans=''),
            human_description=MultilingualText(en_US='', zh_Hans=''),
            type=param_type,
            form=cls.ToolParameterForm.LLM,
            llm_description=llm_description,
            required=required,
            options=param_options,
        )