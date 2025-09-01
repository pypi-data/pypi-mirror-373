from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.import_item import ImportItem
from typing import List


class ImportSection(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    import_list_items: Optional['List[ImportItem]'] = None


ImportSection.model_rebuild()
