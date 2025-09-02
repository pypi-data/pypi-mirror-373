from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import List, Optional, Any, Union
from enum import Enum

class ValidationRules(BaseModel):
    """Validation rules for form fields."""
    required: bool = Field(default=False, description="Whether the field is required")
    min_length: Optional[int] = Field(default=None, description="Minimum length of the field")
    max_length: Optional[int] = Field(default=None, description="Maximum length of the field")
    min_value: Optional[float] = Field(default=None, description="Minimum value of the field")
    max_value: Optional[float] = Field(default=None, description="Maximum value of the field")
    pattern: Optional[str] = Field(default=None, description="Regex pattern for field validation")

    @model_validator(mode='after')
    def validate_lengths(self) -> 'ValidationRules':
        if self.min_length is not None and self.min_length < 0:
            raise ValueError("min_length cannot be negative")
        if self.max_length is not None and self.max_length < 0:
            raise ValueError("max_length cannot be negative")
        if self.min_length is not None and self.max_length is not None:
            if self.min_length > self.max_length:
                raise ValueError("min_length cannot be greater than max_length")
        return self

    @model_validator(mode='after')
    def validate_values(self) -> 'ValidationRules':
        if self.min_value is not None and self.max_value is not None:
            if self.min_value > self.max_value:
                raise ValueError("min_value cannot be greater than max_value")
        return self

class Option(BaseModel):
    """Option for select-type fields."""
    label: str = Field(description="Display label for the option")
    value: Any = Field(description="Value associated with the option")

    @model_validator(mode='after')
    def validate_option(self) -> 'Option':
        if self.label is None or self.value is None:
            raise ValueError("label and value cannot be empty")
        if self.label.strip() == "":
            raise ValueError("label cannot be empty")
        if self.value.strip() == "":
            raise ValueError("value cannot be empty")
        return self

class Reference(BaseModel):
    entity_id: str
    alias: str

    @model_validator(mode='after')
    def validate_reference(self) -> 'Reference':
        if self.entity_id is None or self.alias is None:
            raise ValueError("entity_id and alias are required")
        
        if self.entity_id.strip() == "" or self.alias.strip() == "":
            raise ValueError("entity_id and alias cannot be empty")
        
        return self
    
class UserFilter(BaseModel):
    is_active: Optional[bool] = Field(default=None, description="Whether the user is active")
    ids: Optional[List[Union[str, Any]]] = Field(default=None, description="User ids")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class FieldType(str, Enum):
    """Supported field types for form fields."""
    TEXT = "text"
    TEXTAREA = "textarea"
    EMAIL = "email"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    DROPDOWN = "dropdown"
    RADIO = "radio"
    CHECKBOX = "checkbox"
    FILE = "file"
    IMAGE = "image"
    URL = "url"
    JSON = "json"
    RICHTEXT = "richtext"
    LIST = "list"
    ASSOCIATION = "association"
    USER = "user"
    LOCATION = "location"


class BaseFieldSchema(BaseModel):
    """Base schema for field definitions."""
    name: str = Field(description="Name of the field")
    label: str = Field(description="Display label for the field")
    type: FieldType = Field(description="Type of the field")
    is_hidden: bool = Field(default=False, description="Whether the field is hidden")
    default_value: Optional[Any] = Field(default=None, description="Default value for the field")
    placeholder: Optional[str] = Field(default=None, description="Placeholder text for the field")
    validations: Optional[ValidationRules] = Field(default=None, description="Validation rules for the field")
    options: Optional[List[Option]] = Field(default=None, description="Options for select-type fields")
    multi_select: bool = Field(default=False, description="Whether multiple selections are allowed") 
    endpoint_url: Optional[str] = None
    metadata: Optional[dict] = None
    reference: Optional[Reference] = None
    user_filter: Optional[UserFilter] = None

    model_config = ConfigDict(extra="ignore")
    
    @model_validator(mode='after')
    def validate_reference(self) -> 'BaseFieldSchema':
        if self.type == FieldType.ASSOCIATION:
            if not self.reference:
                raise ValueError("For 'association' type, 'reference' must be provided.")
        return self
