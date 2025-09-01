from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from typing import Any
from typing import Dict
from typing import List


class UpdateLinkedTermRequest(BaseModel):
    aid: Optional[str] = None
    term_pub_id: Optional[str] = None
    external_term_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    subscription_management_url: Optional[str] = None
    external_product_ids: Optional[str] = None
    custom_data: Optional['Dict[str, Any]'] = None


UpdateLinkedTermRequest.model_rebuild()
