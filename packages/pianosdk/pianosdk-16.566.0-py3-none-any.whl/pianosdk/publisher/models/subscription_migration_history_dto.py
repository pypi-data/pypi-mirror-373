from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class SubscriptionMigrationHistoryDTO(BaseModel):
    subscription_id: Optional[str] = None
    schedule_time: Optional[datetime] = None
    from_term_name: Optional[str] = None
    is_migrated: Optional[bool] = None


SubscriptionMigrationHistoryDTO.model_rebuild()
