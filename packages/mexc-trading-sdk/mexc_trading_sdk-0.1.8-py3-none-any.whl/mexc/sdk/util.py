from dataclasses import dataclass
from trading_sdk.types import NetworkError, ValidationError, Network, is_network
from mexc import MEXC

def wrap_exceptions(fn):
  import inspect
  from functools import wraps
  import httpx
  import pydantic

  if inspect.iscoroutinefunction(fn):
    @wraps(fn)
    async def wrapper(*args, **kwargs): # type: ignore
      try:
        return await fn(*args, **kwargs)
      except httpx.HTTPError as e:
        raise NetworkError from e
      except pydantic.ValidationError as e:
        raise ValidationError from e
      
  elif inspect.isgeneratorfunction(fn):
    @wraps(fn)
    async def wrapper(*args, **kwargs): # type: ignore
      try:
        return await fn(*args, **kwargs)
      except httpx.HTTPError as e:
        raise NetworkError from e
      except pydantic.ValidationError as e:
        raise ValidationError from e
      
  else:
    @wraps(fn)
    def wrapper(*args, **kwargs):
      try:
        return fn(*args, **kwargs)
      except httpx.HTTPError as e:
        raise NetworkError from e
      except pydantic.ValidationError as e:
        raise ValidationError from e
  return wrapper

@dataclass
class SdkMixin:
  client: MEXC
  validate: bool = True
  recvWindow: int | None = None

  @classmethod
  def env(cls):
    import os
    return cls.new(api_key=os.environ['MEXC_ACCESS_KEY'], api_secret=os.environ['MEXC_SECRET_KEY'])

  @classmethod
  def new(cls, api_key: str, api_secret: str):
    client = MEXC.new(api_key=api_key, api_secret=api_secret)
    return cls(client=client)

  async def __aenter__(self):
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)

def parse_network(network: str) -> Network:
  if is_network(network):
    return network
  else:
    raise ValueError(f'Invalid network: {network}')
  
def parse_asset(asset: str) -> str:
  return asset.split('-')[0] # some assets have names like "USDT-ARB"