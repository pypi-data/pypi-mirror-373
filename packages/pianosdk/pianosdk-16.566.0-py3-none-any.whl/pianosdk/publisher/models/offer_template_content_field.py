from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class OfferTemplateContentField(BaseModel):
    content_field_id: Optional[str] = None
    offer_template_variant_id: Optional[str] = None
    offer_template_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    deleted: Optional[bool] = None
    value: Optional[str] = None


OfferTemplateContentField.model_rebuild()
