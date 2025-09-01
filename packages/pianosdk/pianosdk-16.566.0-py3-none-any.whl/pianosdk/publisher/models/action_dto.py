from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.action_step_dto import ActionStepDTO


class ActionDTO(BaseModel):
    action_id: Optional[str] = None
    type: Optional[str] = None
    number_of_items: Optional[int] = None
    status: Optional[str] = None
    schedule_time: Optional[datetime] = None
    create_date: Optional[datetime] = None
    change_subscription_term_step: Optional['ActionStepDTO'] = None
    upgrade_subscription_step: Optional['ActionStepDTO'] = None
    readonly: Optional[bool] = None
    send_email_step: Optional['ActionStepDTO'] = None
    progress: Optional[int] = None


ActionDTO.model_rebuild()
