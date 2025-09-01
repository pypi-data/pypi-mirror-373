from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.configuration_property_metadata import ConfigurationPropertyMetadata
from typing import Any
from typing import List


class PpcWebModel(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    source_id: Optional[str] = None
    properties: Optional['List[ConfigurationPropertyMetadata]'] = None
    configuration_attributes: Optional['Any'] = None


PpcWebModel.model_rebuild()
