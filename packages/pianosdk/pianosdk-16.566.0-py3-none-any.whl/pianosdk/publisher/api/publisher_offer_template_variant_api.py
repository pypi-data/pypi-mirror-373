from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.offer_template_variant import OfferTemplateVariant


class PublisherOfferTemplateVariantApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def archive(self, aid: str, offer_template_variant_id: str, history_comment: str = None) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/offer/template/variant/archive'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'offer_template_variant_id': _encode_parameter(offer_template_variant_id),
            'history_comment': _encode_parameter(history_comment)
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
        _result = _json_deserialize(_response)
        return _result

    def create(self, aid: str, offer_template_id: str, name: str, description: str = None, history_comment: str = None) -> ApiResponse[OfferTemplateVariant]:
        _url_path = '/api/v3/publisher/offer/template/variant/create'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'offer_template_id': _encode_parameter(offer_template_id),
            'name': _encode_parameter(name),
            'description': _encode_parameter(description),
            'history_comment': _encode_parameter(history_comment)
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
        _result = _json_deserialize(_response, OfferTemplateVariant)
        return _result

    def delete(self, aid: str, offer_template_variant_id: str, history_comment: str = None) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/offer/template/variant/delete'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'offer_template_variant_id': _encode_parameter(offer_template_variant_id),
            'history_comment': _encode_parameter(history_comment)
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

    def get(self, aid: str, offer_template_variant_id: str) -> ApiResponse[OfferTemplateVariant]:
        _url_path = '/api/v3/publisher/offer/template/variant/get'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'offer_template_variant_id': _encode_parameter(offer_template_variant_id)
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
        _result = _json_deserialize(_response, OfferTemplateVariant)
        return _result

    def get_duplicate(self, aid: str, offer_template_variant_id: str, history_comment: str = None) -> ApiResponse[OfferTemplateVariant]:
        _url_path = '/api/v3/publisher/offer/template/variant/duplicate'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'offer_template_variant_id': _encode_parameter(offer_template_variant_id),
            'history_comment': _encode_parameter(history_comment)
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
        _result = _json_deserialize(_response, OfferTemplateVariant)
        return _result

    def restore(self, aid: str, offer_template_variant_id: str, history_comment: str = None) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/offer/template/variant/restore'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'offer_template_variant_id': _encode_parameter(offer_template_variant_id),
            'history_comment': _encode_parameter(history_comment)
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
        _result = _json_deserialize(_response)
        return _result

    def update(self, aid: str, offer_template_variant_id: str, name: str, description: str = None, content_field_list: str = None, history_comment: str = None, is_validate: bool = None) -> ApiResponse[OfferTemplateVariant]:
        _url_path = '/api/v3/publisher/offer/template/variant/update'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'offer_template_variant_id': _encode_parameter(offer_template_variant_id),
            'name': _encode_parameter(name),
            'description': _encode_parameter(description),
            'content_field_list': _encode_parameter(content_field_list),
            'history_comment': _encode_parameter(history_comment),
            'is_validate': _encode_parameter(is_validate)
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
        _result = _json_deserialize(_response, OfferTemplateVariant)
        return _result

