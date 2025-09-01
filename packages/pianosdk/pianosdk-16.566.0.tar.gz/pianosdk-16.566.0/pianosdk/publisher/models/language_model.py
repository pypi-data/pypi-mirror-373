from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.locale_model import LocaleModel
from typing import List


class LanguageModel(BaseModel):
    language_name: Optional[str] = None
    label: Optional[str] = None
    localized_label: Optional[str] = None
    locales: Optional['List[LocaleModel]'] = None


LanguageModel.model_rebuild()
