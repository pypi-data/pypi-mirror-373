from typing_extensions import TypedDict, TypeVar, Generic, Any, Literal
from dataclasses import dataclass, field
from mexc.core import HttpMixin, ValidationMixin
from .auth import AuthHttpMixin

T = TypeVar('T', default=Any)

class OkResponse(TypedDict, Generic[T]):
  code: int
  success: Literal[True]
  data: T

class ErrResponse(TypedDict):
  code: int
  success: Literal[False]
  message: str

FuturesResponse = OkResponse[T] | ErrResponse

MEXC_FUTURES_API_BASE = 'https://contract.mexc.com'

@dataclass
class FuturesMixin(HttpMixin, ValidationMixin):
  base_url: str = field(default=MEXC_FUTURES_API_BASE, kw_only=True)

@dataclass
class AuthFuturesMixin(AuthHttpMixin, ValidationMixin):
  base_url: str = field(default=MEXC_FUTURES_API_BASE, kw_only=True)

  @classmethod
  def env(cls):
    import os
    return cls.new(
      api_key=os.environ['MEXC_ACCESS_KEY'],
      api_secret=os.environ['MEXC_SECRET_KEY'],
      base_url=MEXC_FUTURES_API_BASE,
    )
