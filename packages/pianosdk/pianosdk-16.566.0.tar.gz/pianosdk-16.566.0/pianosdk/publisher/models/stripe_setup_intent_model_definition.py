from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class StripeSetupIntentModelDefinition(BaseModel):
    setup_intent_client_secret: Optional[str] = None
    tracking_id: Optional[str] = None


StripeSetupIntentModelDefinition.model_rebuild()
