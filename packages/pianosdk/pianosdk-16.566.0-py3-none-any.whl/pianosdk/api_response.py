from dataclasses import dataclass
from typing import TypeVar, Generic, Optional

T = TypeVar('T')


@dataclass
class ApiResponse(Generic[T]):
    request_id: str
    code: int
    ts: int
    data: T
    count: Optional[int] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    total: Optional[int] = None
