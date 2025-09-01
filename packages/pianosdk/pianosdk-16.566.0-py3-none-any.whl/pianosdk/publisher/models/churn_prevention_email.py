from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.churn_prevention_template_version import ChurnPreventionTemplateVersion
from typing import List


class ChurnPreventionEmail(BaseModel):
    email_id: Optional[int] = None
    email_name: Optional[str] = None
    template_id: Optional[str] = None
    versions: Optional['List[ChurnPreventionTemplateVersion]'] = None


ChurnPreventionEmail.model_rebuild()
