import base64
import hashlib
import hmac
import json
from datetime import datetime, timezone
from typing import TypeVar, Dict, List, Union, Type, Callable, Generic, Any, Optional, overload

from Crypto.Cipher import AES
from pydantic import BaseModel

from pianosdk.api_response import ApiResponse
from pianosdk.exceptions import ApiException
from pianosdk.httpwrap import HttpResponse

_T = TypeVar('_T')
_S = TypeVar('_S')
_ObjOrList = Union[_T, List[_T]]
_DELIMITER = '~~~'


def _encrypt(key: str, value: str) -> str:
    value_bytes = value.encode()
    padding_length = (16 - len(value_bytes)) % 16
    value_bytes += bytes([padding_length]) * padding_length
    aes = _get_aes_for_key(key)
    out = aes.encrypt(value_bytes)
    safe = _urlsafe_encode_with_strip(out)
    return safe + _DELIMITER + _urlsafe_encode_with_strip(
        hmac.new(key.encode(), safe.encode(), digestmod=hashlib.sha256).digest())


def _decrypt(key: str, value: str) -> str:
    data, *hmac_value = value.split(_DELIMITER)
    if len(hmac_value) > 1:
        raise ValueError("Invalid message. We've found data after HMAC")
    if hmac_value:
        test_hmac = _urlsafe_encode_with_strip(hmac.new(key.encode(), data.encode(), digestmod=hashlib.sha256).digest())
        if test_hmac != hmac_value[0]:
            raise ValueError('Could not parse message: invalid HMAC')
    return _decrypt_to_bytes(key, data)


def _decrypt_to_bytes(key: str, value: str) -> str:
    data = _urlsafe_decode_stripped(value)
    aes = _get_aes_for_key(key)
    out = aes.decrypt(data)
    return _unpad(out).decode()


def _unpad(data: bytes) -> bytes:
    padding = data[-1]
    return data[:-padding] if 0 < padding <= 16 else data


def _get_aes_for_key(key: str):
    cipher_key = key[:32] if len(key) > 32 else key.ljust(32, 'X')
    return AES.new(key=cipher_key.encode(), mode=AES.MODE_ECB)


def _urlsafe_encode_with_strip(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip('=')


def _urlsafe_decode_stripped(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + '=' * ((4 - len(data)) % 4))


def _json_deserialize(response: HttpResponse, cls: Type[_T] = None) -> ApiResponse[_ObjOrList[_T]]:
    if response.status_code >= 300:
        raise ApiException(
            response.request_id,
            f'HTTP Error: {response.status_code} {response.reason_phrase}',
            response.status_code,
            {},
            True
        )
    request_id = response.request_id or ''
    json_data = json.loads(response.text)
    code = json_data.get('code', response.status_code)
    if code != 0:
        raise ApiException(
            request_id,
            json_data.get('message') or response.reason_phrase,
            code,
            json_data.get('validation_errors') or json_data.get('error_code_list', {})
        )

    const_keys = {'code', 'count', 'limit', 'offset', 'total', 'ts'}
    data = {k: v for k, v in json_data.items() if k in const_keys}
    data_keys = json_data.keys() - const_keys
    if len(data_keys) > 1:
        raise ApiException(request_id, f"SDK doesn't support this endpoint because it has different format [{data_keys}]")
    obj_data = json_data.get(next(iter(data_keys), None))
    if obj_data is None:
        obj_data = {}
    if cls is not None and cls == Any:
        cls = None
    data['data'] = obj_data if cls is None or not issubclass(cls, BaseModel) else _unbox_object(obj_data, cls)
    return ApiResponse(request_id, **data)


def _unbox_object(data: Union[Dict, List], cls: Type[_T]) -> _ObjOrList[_T]:
    many = type(data) == list
    return cls(**data) if not many else [cls(**x) for x in data]


def _encode_parameter(value: Optional[Any]) -> Optional[Any]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return int(value.replace(tzinfo=timezone.utc).timestamp())
    return value


class cached_property(Generic[_T]):
    func: Callable[[Any], _T]

    def __init__(self, func: Callable[[Any], _T]) -> None:
        self.__annotations__ = getattr(func, '__annotations__')
        self.__doc__ = getattr(func, '__doc__')
        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)
        self.func = func

    @overload
    def __get__(self, instance: None, owner: Optional[Type[Any]] = ...) -> 'cached_property[_T]': ...

    @overload
    def __get__(self, instance: _S, owner: Optional[Type[Any]] = ...) -> _T: ...

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = instance.__dict__[self.func.__name__] = self.func(instance)
        return value

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} func={self.func}>'
