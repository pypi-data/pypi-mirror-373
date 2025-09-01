from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class Resource(BaseModel):
    rid: Optional[str] = None
    aid: Optional[str] = None
    deleted: Optional[bool] = None
    disabled: Optional[bool] = None
    create_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    publish_date: Optional[datetime] = None
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    type: Optional[str] = None
    type_label: Optional[str] = None
    bundle_type: Optional[str] = None
    bundle_type_label: Optional[str] = None
    purchase_url: Optional[str] = None
    resource_url: Optional[str] = None
    external_id: Optional[str] = None
    is_fbia_resource: Optional[bool] = None


Resource.model_rebuild()
