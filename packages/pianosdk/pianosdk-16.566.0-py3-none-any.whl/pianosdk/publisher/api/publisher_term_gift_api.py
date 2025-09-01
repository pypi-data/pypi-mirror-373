from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.term import Term


class PublisherTermGiftApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def create_gift_term(self, aid: str, name: str, rid: str, vouchering_policy_redemption_url: str, term_type: str = 'subscription', description: str = None, product_category: str = None, billing_plan_period: str = None, billing_plan_price: float = None, billing_plan_currency: str = None, payment_allow_promo_codes: bool = True, schedule_id: str = None, schedule_billing_model: str = None, shared_account_count: int = None, shared_redemption_url: str = None, collect_shipping_address: bool = None, collect_address: bool = None, delivery_zone: List[str] = None, default_country: str = None) -> ApiResponse[Term]:
        _url_path = '/api/v3/publisher/term/gift/create'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'name': _encode_parameter(name),
            'description': _encode_parameter(description),
            'product_category': _encode_parameter(product_category),
            'rid': _encode_parameter(rid),
            'billing_plan_period': _encode_parameter(billing_plan_period),
            'billing_plan_price': _encode_parameter(billing_plan_price),
            'billing_plan_currency': _encode_parameter(billing_plan_currency),
            'payment_allow_promo_codes': _encode_parameter(payment_allow_promo_codes),
            'vouchering_policy_redemption_url': _encode_parameter(vouchering_policy_redemption_url),
            'schedule_id': _encode_parameter(schedule_id),
            'schedule_billing_model': _encode_parameter(schedule_billing_model),
            'term_type': _encode_parameter(term_type),
            'shared_account_count': _encode_parameter(shared_account_count),
            'shared_redemption_url': _encode_parameter(shared_redemption_url),
            'collect_shipping_address': _encode_parameter(collect_shipping_address),
            'collect_address': _encode_parameter(collect_address),
            'delivery_zone': _encode_parameter(delivery_zone),
            'default_country': _encode_parameter(default_country)
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
        _result = _json_deserialize(_response, Term)
        return _result

    def update_gift_term(self, aid: str, term_id: str, name: str, rid: str, vouchering_policy_redemption_url: str, term_type: str = 'subscription', description: str = None, product_category: str = None, billing_plan_period: str = None, billing_plan_price: float = None, billing_plan_currency: str = None, payment_allow_promo_codes: bool = True, schedule_id: str = None, schedule_billing_model: str = None, shared_account_count: int = None, shared_redemption_url: str = None, collect_shipping_address: bool = None, collect_address: bool = None, delivery_zone: List[str] = None, default_country: str = None) -> ApiResponse[Term]:
        _url_path = '/api/v3/publisher/term/gift/update'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'term_id': _encode_parameter(term_id),
            'name': _encode_parameter(name),
            'description': _encode_parameter(description),
            'product_category': _encode_parameter(product_category),
            'rid': _encode_parameter(rid),
            'billing_plan_period': _encode_parameter(billing_plan_period),
            'billing_plan_price': _encode_parameter(billing_plan_price),
            'billing_plan_currency': _encode_parameter(billing_plan_currency),
            'payment_allow_promo_codes': _encode_parameter(payment_allow_promo_codes),
            'vouchering_policy_redemption_url': _encode_parameter(vouchering_policy_redemption_url),
            'schedule_id': _encode_parameter(schedule_id),
            'schedule_billing_model': _encode_parameter(schedule_billing_model),
            'term_type': _encode_parameter(term_type),
            'shared_account_count': _encode_parameter(shared_account_count),
            'shared_redemption_url': _encode_parameter(shared_redemption_url),
            'collect_shipping_address': _encode_parameter(collect_shipping_address),
            'collect_address': _encode_parameter(collect_address),
            'delivery_zone': _encode_parameter(delivery_zone),
            'default_country': _encode_parameter(default_country)
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
        _result = _json_deserialize(_response, Term)
        return _result

