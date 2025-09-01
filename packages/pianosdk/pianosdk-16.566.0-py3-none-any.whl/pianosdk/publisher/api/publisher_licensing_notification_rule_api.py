from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.licensee_notification_rule import LicenseeNotificationRule


class PublisherLicensingNotificationRuleApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def archive_licensee_notification_rule(self, aid: str, licensee_id: str, notification_rule_id: str) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/licensing/notificationRule/archive'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'licensee_id': _encode_parameter(licensee_id),
            'notification_rule_id': _encode_parameter(notification_rule_id)
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
        _result = _json_deserialize(_response)
        return _result

    def create_licensee_notification_rule(self, aid: str, licensee_id: str, is_for_all_contracts: bool, parameter: str, condition: str, contract_id_list: str = None, condition_value: int = None) -> ApiResponse[LicenseeNotificationRule]:
        _url_path = '/api/v3/publisher/licensing/notificationRule/create'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'licensee_id': _encode_parameter(licensee_id),
            'contract_id_list': _encode_parameter(contract_id_list),
            'is_for_all_contracts': _encode_parameter(is_for_all_contracts),
            'parameter': _encode_parameter(parameter),
            'condition': _encode_parameter(condition),
            'condition_value': _encode_parameter(condition_value)
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
        _result = _json_deserialize(_response, LicenseeNotificationRule)
        return _result

    def get_notification_rules_list(self, aid: str, licensee_id: str) -> ApiResponse[List[LicenseeNotificationRule]]:
        _url_path = '/api/v3/publisher/licensing/notificationRule/list'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'licensee_id': _encode_parameter(licensee_id)
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
        _result = _json_deserialize(_response, LicenseeNotificationRule)
        return _result

    def update_licensee_notification_rule(self, aid: str, licensee_id: str, notification_rule_id: str, is_for_all_contracts: bool, parameter: str, condition: str, contract_id_list: str = None, condition_value: int = None) -> ApiResponse[LicenseeNotificationRule]:
        _url_path = '/api/v3/publisher/licensing/notificationRule/update'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'licensee_id': _encode_parameter(licensee_id),
            'contract_id_list': _encode_parameter(contract_id_list),
            'notification_rule_id': _encode_parameter(notification_rule_id),
            'is_for_all_contracts': _encode_parameter(is_for_all_contracts),
            'parameter': _encode_parameter(parameter),
            'condition': _encode_parameter(condition),
            'condition_value': _encode_parameter(condition_value)
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
        _result = _json_deserialize(_response, LicenseeNotificationRule)
        return _result

