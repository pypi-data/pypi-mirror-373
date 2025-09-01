from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from typing import List


class ConfigurationPropertyMetadata(BaseModel):
    name: Optional[str] = None
    attributes: Optional[str] = None
    validation_rules: Optional[str] = None
    properties: Optional['List[ConfigurationPropertyMetadata]'] = None


ConfigurationPropertyMetadata.model_rebuild()
