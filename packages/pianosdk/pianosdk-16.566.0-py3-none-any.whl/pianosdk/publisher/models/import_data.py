from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.import_section import ImportSection
from typing import List


class ImportData(BaseModel):
    import_data_id: Optional[str] = None
    import_data_status: Optional[str] = None
    sections: Optional['List[ImportSection]'] = None


ImportData.model_rebuild()
