from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.address_config import AddressConfig
from pianosdk.publisher.models.avalara_origin_address import AvalaraOriginAddress
from typing import List


class AvalaraConfiguration(BaseModel):
    avalara_account_id: Optional[str] = None
    avalara_license_key: Optional[str] = None
    avalara_company_code: Optional[str] = None
    avalara_sales_invoice_enabled: Optional[bool] = None
    avalara_return_invoice_enabled: Optional[bool] = None
    avalara_collect_address_enabled: Optional[bool] = None
    avalara_address_config_us: Optional['List[AddressConfig]'] = None
    avalara_address_config_ca: Optional['List[AddressConfig]'] = None
    avalara_origin_address: Optional['AvalaraOriginAddress'] = None


AvalaraConfiguration.model_rebuild()
