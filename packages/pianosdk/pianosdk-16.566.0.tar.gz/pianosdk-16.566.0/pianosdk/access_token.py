import gzip
import json
import re
import urllib.parse
from datetime import datetime
from http.cookies import SimpleCookie
from typing import List, Dict, Callable, Tuple, Optional

from pydantic import Field, BaseModel

from pianosdk.configuration import Configuration
from pianosdk.utils import _decrypt, _unbox_object

_token_pattern = re.compile(r'{(j[azo]x)}([\w-]+)')


class AccessToken(BaseModel):
    rid: str
    expiration_seconds: int = Field(0, alias='ex')
    early_expiration_seconds: int = Field(0, alias='eex')
    access_id: Optional[str] = Field(None, alias='id')
    build_time: int = Field(0, alias='bt')
    created_time: int = Field(0, alias='ct')
    ips: Optional[str]
    uid: Optional[str]

    @property
    def is_expired(self) -> bool:
        seconds = self.early_expiration_seconds or self.expiration_seconds
        return 0 < seconds < datetime.utcnow().timestamp()

    @property
    def is_access_granted(self) -> bool:
        return self.expiration_seconds >= 0 and not self.is_expired


class AccessTokenStorage:
    _tokens: Dict[str, AccessToken] = {}

    def __init__(self, config: Configuration) -> None:
        self.config = config
        self._decoders: Dict[str, Callable[[str], str]] = {
            'a': lambda x: _decrypt(self.config.private_key, x),
            'o': lambda x: x,
            'z': lambda x: gzip.decompress(_decrypt(self.config.private_key, x).encode()).decode(),
        }

    def get_access_token(self, rid: str) -> Optional[AccessToken]:
        return self._tokens.get(rid, AccessToken(rid=rid, ex=-1))

    def parse_access_tokens(self, cookie: str) -> None:
        tokens = _token_pattern.findall(urllib.parse.unquote(cookie))
        self._tokens = {item.rid: item for enc_token in tokens for item in self._decode_token(enc_token)}

    def parse_access_tokens_from_cookies_string(self, cookies: str, cookie_name: str = '__tac') -> None:
        parsed_cookies = SimpleCookie()
        parsed_cookies.load(cookies)
        if cookie_name in parsed_cookies:
            self.parse_access_tokens(parsed_cookies.get(cookie_name).value or '')

    def _decode_token(self, groups: Tuple[str, str]) -> List[AccessToken]:
        encoding, encoded_value = groups
        decode = self._decoders.get(encoding[1])
        if not decode:
            raise ValueError(f'Unknown format {encoding}')
        json_data = json.loads(decode(encoded_value))
        return [item for sublist in [_unbox_object(json_data, AccessToken)] for item in sublist]
