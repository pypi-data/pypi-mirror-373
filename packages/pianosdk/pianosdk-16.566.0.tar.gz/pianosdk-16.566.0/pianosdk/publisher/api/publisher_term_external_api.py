from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.term import Term


class PublisherTermExternalApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def create_external_verification_term(self, aid: str, rid: str, external_api_id: str, name: str, description: str = None, evt_fixed_time_access_period: int = None, evt_grace_period: int = None, evt_verification_period: int = None, evt_itunes_bundle_id: str = None, evt_itunes_product_id: str = None, evt_google_play_product_id: str = None, shared_account_count: int = None, shared_redemption_url: str = None) -> ApiResponse[Term]:
        _url_path = '/api/v3/publisher/term/external/create'
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
            'external_api_id': _encode_parameter(external_api_id),
            'name': _encode_parameter(name),
            'description': _encode_parameter(description),
            'evt_fixed_time_access_period': _encode_parameter(evt_fixed_time_access_period),
            'evt_grace_period': _encode_parameter(evt_grace_period),
            'evt_verification_period': _encode_parameter(evt_verification_period),
            'evt_itunes_bundle_id': _encode_parameter(evt_itunes_bundle_id),
            'evt_itunes_product_id': _encode_parameter(evt_itunes_product_id),
            'evt_google_play_product_id': _encode_parameter(evt_google_play_product_id),
            'shared_account_count': _encode_parameter(shared_account_count),
            'shared_redemption_url': _encode_parameter(shared_redemption_url)
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

    def update_external_verification_term(self, term_id: str, external_api_id: str, name: str, rid: str = None, description: str = None, evt_fixed_time_access_period: int = None, evt_grace_period: int = None, evt_verification_period: int = None, evt_itunes_bundle_id: str = None, evt_itunes_product_id: str = None, evt_google_play_product_id: str = None, shared_account_count: int = None, shared_redemption_url: str = None) -> ApiResponse[Term]:
        _url_path = '/api/v3/publisher/term/external/update'
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
            'external_api_id': _encode_parameter(external_api_id),
            'name': _encode_parameter(name),
            'description': _encode_parameter(description),
            'evt_fixed_time_access_period': _encode_parameter(evt_fixed_time_access_period),
            'evt_grace_period': _encode_parameter(evt_grace_period),
            'evt_verification_period': _encode_parameter(evt_verification_period),
            'evt_itunes_bundle_id': _encode_parameter(evt_itunes_bundle_id),
            'evt_itunes_product_id': _encode_parameter(evt_itunes_product_id),
            'evt_google_play_product_id': _encode_parameter(evt_google_play_product_id),
            'shared_account_count': _encode_parameter(shared_account_count),
            'shared_redemption_url': _encode_parameter(shared_redemption_url)
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

