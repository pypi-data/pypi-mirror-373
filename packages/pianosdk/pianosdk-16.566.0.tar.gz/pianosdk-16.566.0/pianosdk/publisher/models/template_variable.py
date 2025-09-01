from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class TemplateVariable(BaseModel):
    template_variable_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    test_value: Optional[str] = None
    parent_id: Optional[str] = None


TemplateVariable.model_rebuild()
