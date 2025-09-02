from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional
from .common_schema import BaseFieldSchema, ValidationRules, FieldType

class Validation(ValidationRules):
    unique: Optional[bool] = Field(default=False)
    index: Optional[bool] = Field(default=False)

    
class FieldSchema(BaseFieldSchema):
    is_protected: bool = Field(default=False)
    entity_id: str
    description: Optional[str] = None
    validations: Optional[Validation] = None

    @model_validator(mode='after')
    def validate_options_sources(self) -> 'FieldSchema':
        if self.type in [FieldType.DROPDOWN, FieldType.CHECKBOX, FieldType.RADIO]:
            if not self.options:
                self.options = []
        return self
    
    model_config = ConfigDict(extra="ignore")
        
