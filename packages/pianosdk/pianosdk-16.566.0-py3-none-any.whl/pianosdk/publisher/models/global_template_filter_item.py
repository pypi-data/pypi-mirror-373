from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.global_template_filter_sub_item import GlobalTemplateFilterSubItem
from typing import List


class GlobalTemplateFilterItem(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    counter_value: Optional[int] = None
    global_template_filter_sub_items: Optional['List[GlobalTemplateFilterSubItem]'] = None


GlobalTemplateFilterItem.model_rebuild()
