from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class CreditGuardStoredFields(BaseModel):
    terminal_number: Optional[str] = None
    card_id: Optional[str] = None
    card_mask: Optional[str] = None
    card_expiration: Optional[str] = None
    card_acquirer: Optional[str] = None
    auth_number: Optional[str] = None
    slave_terminal_number: Optional[str] = None
    slave_terminal_sequence: Optional[str] = None
    shovar: Optional[str] = None
    cg_uid: Optional[str] = None
    user_data_1: Optional[str] = None
    user_data_2: Optional[str] = None
    user_data_3: Optional[str] = None
    user_data_4: Optional[str] = None
    user_data_5: Optional[str] = None
    user_data_6: Optional[str] = None
    user_data_7: Optional[str] = None
    user_data_8: Optional[str] = None
    user_data_9: Optional[str] = None
    user_data_10: Optional[str] = None


CreditGuardStoredFields.model_rebuild()
