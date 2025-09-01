from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.change_subscription_term_step import ChangeSubscriptionTermStep
from pianosdk.publisher.models.send_email_step import SendEmailStep
from pianosdk.publisher.models.upgrade_subscription_step import UpgradeSubscriptionStep


class Action(BaseModel):
    action_id: Optional[str] = None
    type: Optional[str] = None
    number_of_items: Optional[int] = None
    status: Optional[str] = None
    schedule_time: Optional[datetime] = None
    progress: Optional[datetime] = None
    change_subscription_term_step: Optional['ChangeSubscriptionTermStep'] = None
    readonly: Optional[bool] = None
    send_email_step: Optional['SendEmailStep'] = None
    upgrade_subscription_step: Optional['UpgradeSubscriptionStep'] = None


Action.model_rebuild()
