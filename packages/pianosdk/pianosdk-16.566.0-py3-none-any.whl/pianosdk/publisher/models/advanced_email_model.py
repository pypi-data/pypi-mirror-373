from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.template_version import TemplateVersion
from typing import List


class AdvancedEmailModel(BaseModel):
    email_id: Optional[int] = None
    name: Optional[str] = None
    caption: Optional[str] = None
    description: Optional[str] = None
    publisher_config: Optional[str] = None
    xdays: Optional[int] = None
    default_xdays: Optional[int] = None
    template_versions: Optional['List[TemplateVersion]'] = None
    default_template_id: Optional[str] = None
    system_template_id: Optional[str] = None
    caption_localized: Optional[str] = None
    description_localized: Optional[str] = None


AdvancedEmailModel.model_rebuild()
