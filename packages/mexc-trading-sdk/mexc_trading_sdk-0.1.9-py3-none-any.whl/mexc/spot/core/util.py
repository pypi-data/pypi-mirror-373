from typing_extensions import TypedDict
from dataclasses import dataclass, field
from mexc.core import HttpMixin, ValidationMixin
from .auth import AuthHttpMixin

MEXC_SPOT_API_BASE = 'https://api.mexc.com'

@dataclass
class SpotMixin(HttpMixin, ValidationMixin):
  base_url: str = field(default=MEXC_SPOT_API_BASE, kw_only=True)

@dataclass
class AuthSpotMixin(AuthHttpMixin, ValidationMixin):
  base_url: str = field(default=MEXC_SPOT_API_BASE, kw_only=True)

  @classmethod
  def env(cls):
    import os
    return cls.new(
      api_key=os.environ['MEXC_ACCESS_KEY'],
      api_secret=os.environ['MEXC_SECRET_KEY'],
      base_url=MEXC_SPOT_API_BASE,
    )
  
class ApiError(TypedDict):
  msg: str
  code: int