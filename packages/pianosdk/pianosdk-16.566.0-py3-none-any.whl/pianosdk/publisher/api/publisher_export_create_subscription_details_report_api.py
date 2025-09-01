from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.export import Export


class PublisherExportCreateSubscriptionDetailsReportApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def create_subscription_detailed_report_tz(self, aid: str, export_name: str, q: str = None, search_new_subscriptions: bool = None, new_subscriptions_created_from: datetime = None, new_subscriptions_created_to: datetime = None, search_active_now_subscriptions: bool = None, active_now_subscriptions_statuses: List[str] = None, search_inactive_subscriptions: bool = None, inactive_subscriptions_statuses: List[str] = None, subscriptions_inactive_from: datetime = None, subscriptions_inactive_to: datetime = None, search_updated_subscriptions: bool = None, updated_subscriptions_statuses: List[str] = None, subscriptions_updated_from: datetime = None, subscriptions_updated_to: datetime = None, search_auto_renewing_subscriptions: bool = None, subscriptions_auto_renewing: bool = None, search_subscriptions_by_next_billing_date: bool = None, subscriptions_next_billing_date_from: datetime = None, subscriptions_next_billing_date_to: datetime = None, search_subscriptions_by_terms: bool = None, subscriptions_terms: List[str] = None, subscriptions_term_types: List[str] = None) -> ApiResponse[Export]:
        _url_path = '/api/v3/publisher/export/create/subscriptionDetailsReport/v2'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'export_name': _encode_parameter(export_name),
            'q': _encode_parameter(q),
            'search_new_subscriptions': _encode_parameter(search_new_subscriptions),
            'new_subscriptions_created_from': _encode_parameter(new_subscriptions_created_from),
            'new_subscriptions_created_to': _encode_parameter(new_subscriptions_created_to),
            'search_active_now_subscriptions': _encode_parameter(search_active_now_subscriptions),
            'active_now_subscriptions_statuses': _encode_parameter(active_now_subscriptions_statuses),
            'search_inactive_subscriptions': _encode_parameter(search_inactive_subscriptions),
            'inactive_subscriptions_statuses': _encode_parameter(inactive_subscriptions_statuses),
            'subscriptions_inactive_from': _encode_parameter(subscriptions_inactive_from),
            'subscriptions_inactive_to': _encode_parameter(subscriptions_inactive_to),
            'search_updated_subscriptions': _encode_parameter(search_updated_subscriptions),
            'updated_subscriptions_statuses': _encode_parameter(updated_subscriptions_statuses),
            'subscriptions_updated_from': _encode_parameter(subscriptions_updated_from),
            'subscriptions_updated_to': _encode_parameter(subscriptions_updated_to),
            'search_auto_renewing_subscriptions': _encode_parameter(search_auto_renewing_subscriptions),
            'subscriptions_auto_renewing': _encode_parameter(subscriptions_auto_renewing),
            'search_subscriptions_by_next_billing_date': _encode_parameter(search_subscriptions_by_next_billing_date),
            'subscriptions_next_billing_date_from': _encode_parameter(subscriptions_next_billing_date_from),
            'subscriptions_next_billing_date_to': _encode_parameter(subscriptions_next_billing_date_to),
            'search_subscriptions_by_terms': _encode_parameter(search_subscriptions_by_terms),
            'subscriptions_terms': _encode_parameter(subscriptions_terms),
            'subscriptions_term_types': _encode_parameter(subscriptions_term_types)
        }

        _body = None
        _files = None

        _request = self.config.http_client.build_request('POST',
                                                         _query_url,
                                                         headers=_headers,
                                                         query_parameters=_query_parameters,
                                                         parameters=_parameters,
                                                         json=_body,
                                                         files=_files)
        _response = self._execute_request(_request)
        _result = _json_deserialize(_response, Export)
        return _result

