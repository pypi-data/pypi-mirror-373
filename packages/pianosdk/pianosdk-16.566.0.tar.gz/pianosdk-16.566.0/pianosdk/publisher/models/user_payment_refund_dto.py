from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class UserPaymentRefundDTO(BaseModel):
    status: Optional[str] = None
    refund_external_tx_id: Optional[str] = None
    refund_downstream_external_tx_id: Optional[str] = None


UserPaymentRefundDTO.model_rebuild()
