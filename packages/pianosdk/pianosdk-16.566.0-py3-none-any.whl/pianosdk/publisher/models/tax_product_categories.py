from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.tax_product_category import TaxProductCategory
from typing import List


class TaxProductCategories(BaseModel):
    term_level_categories: Optional['List[TaxProductCategory]'] = None
    categories: Optional['List[TaxProductCategory]'] = None


TaxProductCategories.model_rebuild()
