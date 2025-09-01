from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class PageInfo(BaseModel):
    offset: Optional[int] = None
    limit: Optional[int] = None
    total: Optional[int] = None
    limited: Optional[bool] = None
    end_page: Optional[int] = None
    begin_page: Optional[int] = None
    total_pages: Optional[int] = None
    has_next_page: Optional[bool] = None
    has_prev_page: Optional[bool] = None
    total_count_known: Optional[bool] = None


PageInfo.model_rebuild()
