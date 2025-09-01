from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.term import Term
from typing import List


class PeriodSettings(BaseModel):
    period_id: Optional[str] = None
    title_editable: Optional[bool] = None
    sell_date_editable: Optional[bool] = None
    begin_date_editable: Optional[bool] = None
    end_date_editable: Optional[bool] = None
    period_deletable: Optional[bool] = None
    dependent_terms: Optional['List[Term]'] = None


PeriodSettings.model_rebuild()
