from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.app import App


class EasypayConfiguration(BaseModel):
    configuration_id: Optional[str] = None
    app: Optional['App'] = None
    source_name: Optional[str] = None
    source_id: Optional[int] = None
    title: Optional[str] = None
    is_editable: Optional[bool] = None
    is_disabled: Optional[bool] = None
    properties: Optional[str] = None
    is_visible: Optional[bool] = None


EasypayConfiguration.model_rebuild()
