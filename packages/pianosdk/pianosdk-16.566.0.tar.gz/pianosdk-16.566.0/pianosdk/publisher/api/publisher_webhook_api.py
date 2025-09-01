from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.webhook_event import WebhookEvent
from pianosdk.publisher.models.webhook_settings import WebhookSettings
from pianosdk.publisher.models.webhook_status import WebhookStatus


class PublisherWebhookApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def events(self, aid: str, skip_deprecated_webhooks: bool = None) -> ApiResponse[List[str]]:
        _url_path = '/api/v3/publisher/webhook/events'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'skip_deprecated_webhooks': _encode_parameter(skip_deprecated_webhooks)
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
        _result = _json_deserialize(_response, str)
        return _result

    def get_event(self, webhook_id: str) -> ApiResponse[WebhookEvent]:
        _url_path = '/api/v3/publisher/webhook/get'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'webhook_id': _encode_parameter(webhook_id)
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
        _result = _json_deserialize(_response, WebhookEvent)
        return _result

    def get_settings(self, aid: str = None) -> ApiResponse[WebhookSettings]:
        _url_path = '/api/v3/publisher/webhook/settings'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid)
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
        _result = _json_deserialize(_response, WebhookSettings)
        return _result

    def list(self, aid: str, offset: int = 0, limit: int = 100, order_by: str = 'create_date', order_direction: str = 'desc', status: str = None, keyword: str = None, event_type: List[str] = None, type: List[str] = None) -> ApiResponse[List[WebhookEvent]]:
        _url_path = '/api/v3/publisher/webhook/list'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'status': _encode_parameter(status),
            'keyword': _encode_parameter(keyword),
            'limit': _encode_parameter(limit),
            'offset': _encode_parameter(offset),
            'order_by': _encode_parameter(order_by),
            'order_direction': _encode_parameter(order_direction),
            'event_type': _encode_parameter(event_type),
            'type': _encode_parameter(type)
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
        _result = _json_deserialize(_response, WebhookEvent)
        return _result

    def skip(self, webhook_id: str) -> ApiResponse[WebhookEvent]:
        _url_path = '/api/v3/publisher/webhook/skip'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'webhook_id': _encode_parameter(webhook_id)
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
        _result = _json_deserialize(_response, WebhookEvent)
        return _result

    def status(self, aid: str) -> ApiResponse[WebhookStatus]:
        _url_path = '/api/v3/publisher/webhook/status'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid)
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
        _result = _json_deserialize(_response, WebhookStatus)
        return _result

