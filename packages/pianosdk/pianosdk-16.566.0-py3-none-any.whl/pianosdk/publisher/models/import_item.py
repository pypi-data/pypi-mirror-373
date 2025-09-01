from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.variant_item import VariantItem
from pianosdk.publisher.models.version_item import VersionItem
from typing import List


class ImportItem(BaseModel):
    item_id: Optional[str] = None
    name: Optional[str] = None
    action: Optional[str] = None
    import_result: Optional[str] = None
    update_date: Optional[int] = None
    count_variants: Optional[int] = None
    variant_list: Optional['List[VariantItem]'] = None
    version: Optional[int] = None
    version_list: Optional['List[VersionItem]'] = None


ImportItem.model_rebuild()
