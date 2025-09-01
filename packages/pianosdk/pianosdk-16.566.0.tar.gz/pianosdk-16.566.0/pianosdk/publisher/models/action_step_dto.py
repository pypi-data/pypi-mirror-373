from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.mail import Mail
from pianosdk.publisher.models.term_short import TermShort


class ActionStepDTO(BaseModel):
    action_id: Optional[str] = None
    type: Optional[str] = None
    from_term: Optional['TermShort'] = None
    to_term: Optional['TermShort'] = None
    optional: Optional[bool] = None
    enabled: Optional[bool] = None
    email: Optional['Mail'] = None


ActionStepDTO.model_rebuild()
