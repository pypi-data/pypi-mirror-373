from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class OfferTemplateSubHistory(BaseModel):
    history_content: Optional[str] = None
    offer_template_history_event: Optional[str] = None
    offer_template_id: Optional[str] = None
    offer_template_variant_id: Optional[str] = None
    offer_template_version_id: Optional[str] = None


OfferTemplateSubHistory.model_rebuild()
