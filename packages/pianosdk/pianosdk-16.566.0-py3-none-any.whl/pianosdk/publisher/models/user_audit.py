from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.audit_changed_field_dto import AuditChangedFieldDto
from typing import List


class UserAudit(BaseModel):
    user_audit_id: Optional[str] = None
    uid: Optional[str] = None
    session_id: Optional[str] = None
    country_name: Optional[str] = None
    city: Optional[str] = None
    user_agent: Optional[str] = None
    visited: Optional[datetime] = None
    action_type: Optional[str] = None
    aid: Optional[str] = None
    changed_fields: Optional['List[AuditChangedFieldDto]'] = None


UserAudit.model_rebuild()
