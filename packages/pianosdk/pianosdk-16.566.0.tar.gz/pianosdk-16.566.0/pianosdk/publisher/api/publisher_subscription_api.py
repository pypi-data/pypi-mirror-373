from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.subscription_log_item import SubscriptionLogItem
from pianosdk.publisher.models.user_subscription import UserSubscription
from pianosdk.publisher.models.user_subscription_dto import UserSubscriptionDto
from pianosdk.publisher.models.user_subscription_list_item import UserSubscriptionListItem


class PublisherSubscriptionApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def cancel_subscription(self, aid: str, subscription_id: str, refund_last_payment: bool = False) -> ApiResponse[bool]:
        _url_path = '/api/v3/publisher/subscription/cancel'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'subscription_id': _encode_parameter(subscription_id),
            'refund_last_payment': _encode_parameter(refund_last_payment)
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
        _result = _json_deserialize(_response, bool)
        return _result

    def count(self, aid: str) -> ApiResponse[int]:
        _url_path = '/api/v3/publisher/subscription/count'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid)
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
        _result = _json_deserialize(_response, int)
        return _result

    def get(self, aid: str, subscription_id: str) -> ApiResponse[UserSubscription]:
        _url_path = '/api/v3/publisher/subscription/get'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'subscription_id': _encode_parameter(subscription_id)
        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {

        }

        _body = None
        _files = None

        _request = self.config.http_client.build_request('GET',
                                                         _query_url,
                                                         headers=_headers,
                                                         query_parameters=_query_parameters,
                                                         parameters=_parameters,
                                                         json=_body,
                                                         files=_files)
        _response = self._execute_request(_request)
        _result = _json_deserialize(_response, UserSubscription)
        return _result

    def is_partially_refundable(self, aid: str, subscription_id: str) -> ApiResponse[bool]:
        _url_path = '/api/v3/publisher/subscription/isPartiallyRefundable'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'subscription_id': _encode_parameter(subscription_id)
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
        _result = _json_deserialize(_response, bool)
        return _result

    def list(self, aid: str, offset: int = 0, limit: int = 100, uid: str = None, type: str = None, start_date: datetime = None, end_date: datetime = None, q: str = None, select_by: str = None, status: str = None) -> ApiResponse[List[UserSubscriptionListItem]]:
        _url_path = '/api/v3/publisher/subscription/list'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'uid': _encode_parameter(uid),
            'type': _encode_parameter(type),
            'start_date': _encode_parameter(start_date),
            'end_date': _encode_parameter(end_date),
            'q': _encode_parameter(q),
            'offset': _encode_parameter(offset),
            'limit': _encode_parameter(limit),
            'select_by': _encode_parameter(select_by),
            'status': _encode_parameter(status)
        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {

        }

        _body = None
        _files = None

        _request = self.config.http_client.build_request('GET',
                                                         _query_url,
                                                         headers=_headers,
                                                         query_parameters=_query_parameters,
                                                         parameters=_parameters,
                                                         json=_body,
                                                         files=_files)
        _response = self._execute_request(_request)
        _result = _json_deserialize(_response, UserSubscriptionListItem)
        return _result

    def resume_subscription(self, aid: str, subscription_id: str) -> ApiResponse[bool]:
        _url_path = '/api/v3/publisher/subscription/resume'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'subscription_id': _encode_parameter(subscription_id)
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
        _result = _json_deserialize(_response, bool)
        return _result

    def search(self, aid: str, offset: int = 0, limit: int = 100, q: str = None, order_by: str = None, order_direction: str = None, search_new_subscriptions: bool = None, new_subscriptions_created_from: datetime = None, new_subscriptions_created_to: datetime = None, search_active_now_subscriptions: bool = None, active_now_subscriptions_statuses: List[str] = None, search_inactive_subscriptions: bool = None, inactive_subscriptions_statuses: List[str] = None, subscriptions_inactive_from: datetime = None, subscriptions_inactive_to: datetime = None, search_updated_subscriptions: bool = None, updated_subscriptions_statuses: List[str] = None, subscriptions_updated_from: datetime = None, subscriptions_updated_to: datetime = None, search_auto_renewing_subscriptions: bool = None, subscriptions_auto_renewing: bool = None, search_subscriptions_by_next_billing_date: bool = None, subscriptions_next_billing_date_from: datetime = None, subscriptions_next_billing_date_to: datetime = None, search_subscriptions_by_terms: bool = None, subscriptions_terms: List[str] = None, subscriptions_term_types: List[str] = None) -> ApiResponse[List[SubscriptionLogItem]]:
        _url_path = '/api/v3/publisher/subscription/search'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'q': _encode_parameter(q),
            'offset': _encode_parameter(offset),
            'limit': _encode_parameter(limit),
            'order_by': _encode_parameter(order_by),
            'order_direction': _encode_parameter(order_direction),
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

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {

        }

        _body = None
        _files = None

        _request = self.config.http_client.build_request('GET',
                                                         _query_url,
                                                         headers=_headers,
                                                         query_parameters=_query_parameters,
                                                         parameters=_parameters,
                                                         json=_body,
                                                         files=_files)
        _response = self._execute_request(_request)
        _result = _json_deserialize(_response, SubscriptionLogItem)
        return _result

    def stats(self, aid: str, uid: str, offset: int = 0, limit: int = 100) -> ApiResponse[List[UserSubscriptionDto]]:
        _url_path = '/api/v3/publisher/subscription/stats'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'uid': _encode_parameter(uid),
            'offset': _encode_parameter(offset),
            'limit': _encode_parameter(limit)
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
        _result = _json_deserialize(_response, UserSubscriptionDto)
        return _result

    def update(self, aid: str, subscription_id: str, next_bill_date: datetime = None, auto_renew: bool = None, payment_method_id: str = None, user_address_id: str = None, scheduled_access_period_id: str = None) -> ApiResponse[bool]:
        _url_path = '/api/v3/publisher/subscription/update'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'subscription_id': _encode_parameter(subscription_id),
            'next_bill_date': _encode_parameter(next_bill_date),
            'auto_renew': _encode_parameter(auto_renew),
            'payment_method_id': _encode_parameter(payment_method_id),
            'user_address_id': _encode_parameter(user_address_id),
            'scheduled_access_period_id': _encode_parameter(scheduled_access_period_id)
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
        _result = _json_deserialize(_response, bool)
        return _result

