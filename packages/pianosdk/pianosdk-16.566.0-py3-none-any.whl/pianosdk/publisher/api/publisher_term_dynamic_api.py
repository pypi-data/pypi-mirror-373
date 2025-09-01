from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.create_billing_configuration_request import CreateBillingConfigurationRequest
from pianosdk.publisher.models.term import Term
from pianosdk.publisher.models.update_billing_configuration_request import UpdateBillingConfigurationRequest


class PublisherTermDynamicApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def create_dynamic_term(self, aid: str, rid: str, name: str, currency: str, description: str = None, allow_start_in_future: bool = None, maximum_days_in_advance: int = None, shared_account_count: int = None, shared_redemption_url: str = None, collect_address: bool = None, delivery_zone: List[str] = None, default_country: str = None, payment_force_auto_renew: bool = False, body: CreateBillingConfigurationRequest = None) -> ApiResponse[Term]:
        _url_path = '/api/v3/publisher/term/dynamic/create'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'rid': _encode_parameter(rid),
            'name': _encode_parameter(name),
            'currency': _encode_parameter(currency),
            'description': _encode_parameter(description),
            'allow_start_in_future': _encode_parameter(allow_start_in_future),
            'maximum_days_in_advance': _encode_parameter(maximum_days_in_advance),
            'shared_account_count': _encode_parameter(shared_account_count),
            'shared_redemption_url': _encode_parameter(shared_redemption_url),
            'collect_address': _encode_parameter(collect_address),
            'delivery_zone': _encode_parameter(delivery_zone),
            'default_country': _encode_parameter(default_country),
            'payment_force_auto_renew': _encode_parameter(payment_force_auto_renew)
        }

        _body = body and body.dict()
        _files = None

        _request = self.config.http_client.build_request('POST',
                                                         _query_url,
                                                         headers=_headers,
                                                         query_parameters=_query_parameters,
                                                         parameters=_parameters,
                                                         json=_body,
                                                         files=_files)
        _response = self._execute_request(_request)
        _result = _json_deserialize(_response, Term)
        return _result

    def update_dynamic_term(self, aid: str, term_pub_id: str, rid: str = None, name: str = None, currency: str = None, description: str = None, payment_new_customers_only: bool = None, payment_allow_promo_codes: bool = None, show_full_billing_plan: bool = None, allow_start_in_future: bool = None, maximum_days_in_advance: int = None, shared_account_count: int = None, shared_redemption_url: str = None, payment_force_auto_renew: bool = False, collect_address: bool = None, delivery_zone: List[str] = None, default_country: str = None, body: UpdateBillingConfigurationRequest = None) -> ApiResponse[Term]:
        _url_path = '/api/v3/publisher/term/dynamic/update'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'term_pub_id': _encode_parameter(term_pub_id),
            'rid': _encode_parameter(rid),
            'name': _encode_parameter(name),
            'currency': _encode_parameter(currency),
            'description': _encode_parameter(description),
            'payment_new_customers_only': _encode_parameter(payment_new_customers_only),
            'payment_allow_promo_codes': _encode_parameter(payment_allow_promo_codes),
            'show_full_billing_plan': _encode_parameter(show_full_billing_plan),
            'allow_start_in_future': _encode_parameter(allow_start_in_future),
            'maximum_days_in_advance': _encode_parameter(maximum_days_in_advance),
            'shared_account_count': _encode_parameter(shared_account_count),
            'shared_redemption_url': _encode_parameter(shared_redemption_url),
            'payment_force_auto_renew': _encode_parameter(payment_force_auto_renew),
            'collect_address': _encode_parameter(collect_address),
            'delivery_zone': _encode_parameter(delivery_zone),
            'default_country': _encode_parameter(default_country)
        }

        _body = body and body.dict()
        _files = None

        _request = self.config.http_client.build_request('POST',
                                                         _query_url,
                                                         headers=_headers,
                                                         query_parameters=_query_parameters,
                                                         parameters=_parameters,
                                                         json=_body,
                                                         files=_files)
        _response = self._execute_request(_request)
        _result = _json_deserialize(_response, Term)
        return _result

