from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.language_stats import LanguageStats
from typing import List


class TranslationStats(BaseModel):
    keys_count: Optional[int] = None
    languages_count: Optional[int] = None
    languages_stats: Optional['List[LanguageStats]'] = None


TranslationStats.model_rebuild()
