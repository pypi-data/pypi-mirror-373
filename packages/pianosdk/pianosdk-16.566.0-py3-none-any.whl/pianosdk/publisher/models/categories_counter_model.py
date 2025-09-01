from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.template_counter_model import TemplateCounterModel
from typing import List


class CategoriesCounterModel(BaseModel):
    section: Optional[str] = None
    template_count: Optional[str] = None
    categories: Optional['List[TemplateCounterModel]'] = None


CategoriesCounterModel.model_rebuild()
