from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.global_template_filter_item import GlobalTemplateFilterItem


class GlobalTemplateFilter(BaseModel):
    template_status: Optional['GlobalTemplateFilterItem'] = None
    template_type: Optional['GlobalTemplateFilterItem'] = None
    use_case: Optional['GlobalTemplateFilterItem'] = None
    deployment_status: Optional['GlobalTemplateFilterItem'] = None


GlobalTemplateFilter.model_rebuild()
