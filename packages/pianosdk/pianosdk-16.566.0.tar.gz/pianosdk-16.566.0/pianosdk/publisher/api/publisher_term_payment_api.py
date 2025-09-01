from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.term import Term


class PublisherTermPaymentApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def create_payment_term(self, aid: str, rid: str, name: str, payment_billing_plan: str = None, payment_allow_renew_days: int = None, payment_force_auto_renew: bool = False, payment_new_customers_only: bool = True, payment_trial_new_customers_only: bool = True, payment_allow_promo_codes: bool = True, payment_renew_grace_period: int = None, payment_allow_gift: bool = False, description: str = None, product_category: str = None, verify_on_renewal: bool = False, evt_verification_period: int = None, schedule_id: str = None, schedule_billing_model: str = None, term_billing_descriptor: str = None, shared_account_count: int = None, shared_redemption_url: str = None, churn_prevention_logic_id: str = None, allow_start_in_future: bool = None, maximum_days_in_advance: int = None, collect_address: bool = None, delivery_zone: List[str] = None, default_country: str = None) -> ApiResponse[Term]:
        _url_path = '/api/v3/publisher/term/payment/create'
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
            'payment_billing_plan': _encode_parameter(payment_billing_plan),
            'payment_allow_renew_days': _encode_parameter(payment_allow_renew_days),
            'payment_force_auto_renew': _encode_parameter(payment_force_auto_renew),
            'payment_new_customers_only': _encode_parameter(payment_new_customers_only),
            'payment_trial_new_customers_only': _encode_parameter(payment_trial_new_customers_only),
            'payment_allow_promo_codes': _encode_parameter(payment_allow_promo_codes),
            'payment_renew_grace_period': _encode_parameter(payment_renew_grace_period),
            'payment_allow_gift': _encode_parameter(payment_allow_gift),
            'description': _encode_parameter(description),
            'product_category': _encode_parameter(product_category),
            'verify_on_renewal': _encode_parameter(verify_on_renewal),
            'evt_verification_period': _encode_parameter(evt_verification_period),
            'schedule_id': _encode_parameter(schedule_id),
            'schedule_billing_model': _encode_parameter(schedule_billing_model),
            'term_billing_descriptor': _encode_parameter(term_billing_descriptor),
            'shared_account_count': _encode_parameter(shared_account_count),
            'shared_redemption_url': _encode_parameter(shared_redemption_url),
            'churn_prevention_logic_id': _encode_parameter(churn_prevention_logic_id),
            'allow_start_in_future': _encode_parameter(allow_start_in_future),
            'maximum_days_in_advance': _encode_parameter(maximum_days_in_advance),
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

    def update_payment_term(self, term_id: str, rid: str = None, name: str = None, payment_billing_plan: str = None, payment_allow_renew_days: int = None, payment_force_auto_renew: bool = None, payment_new_customers_only: bool = None, payment_trial_new_customers_only: bool = None, payment_allow_promo_codes: bool = None, payment_renew_grace_period: int = None, payment_allow_gift: bool = None, description: str = None, product_category: str = None, verify_on_renewal: bool = None, evt_verification_period: int = None, schedule_id: str = None, schedule_billing_model: str = None, change_options: List[str] = None, term_billing_descriptor: str = None, external_api_id: str = None, shared_account_count: int = None, shared_redemption_url: str = None, churn_prevention_logic_id: str = None, allow_start_in_future: bool = None, maximum_days_in_advance: int = None, collect_address: bool = None, delivery_zone: List[str] = None, default_country: str = None) -> ApiResponse[Term]:
        _url_path = '/api/v3/publisher/term/payment/update'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'term_id': _encode_parameter(term_id),
            'rid': _encode_parameter(rid),
            'name': _encode_parameter(name),
            'payment_billing_plan': _encode_parameter(payment_billing_plan),
            'payment_allow_renew_days': _encode_parameter(payment_allow_renew_days),
            'payment_force_auto_renew': _encode_parameter(payment_force_auto_renew),
            'payment_new_customers_only': _encode_parameter(payment_new_customers_only),
            'payment_trial_new_customers_only': _encode_parameter(payment_trial_new_customers_only),
            'payment_allow_promo_codes': _encode_parameter(payment_allow_promo_codes),
            'payment_renew_grace_period': _encode_parameter(payment_renew_grace_period),
            'payment_allow_gift': _encode_parameter(payment_allow_gift),
            'description': _encode_parameter(description),
            'product_category': _encode_parameter(product_category),
            'verify_on_renewal': _encode_parameter(verify_on_renewal),
            'evt_verification_period': _encode_parameter(evt_verification_period),
            'schedule_id': _encode_parameter(schedule_id),
            'schedule_billing_model': _encode_parameter(schedule_billing_model),
            'change_options': _encode_parameter(change_options),
            'term_billing_descriptor': _encode_parameter(term_billing_descriptor),
            'external_api_id': _encode_parameter(external_api_id),
            'shared_account_count': _encode_parameter(shared_account_count),
            'shared_redemption_url': _encode_parameter(shared_redemption_url),
            'churn_prevention_logic_id': _encode_parameter(churn_prevention_logic_id),
            'allow_start_in_future': _encode_parameter(allow_start_in_future),
            'maximum_days_in_advance': _encode_parameter(maximum_days_in_advance),
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

