from typing_extensions import Unpack
from dataclasses import dataclass
from mexc.core import filter_kwargs
from mexc.spot.core import MEXC_SPOT_API_BASE, AuthHttpClient
from .core import StreamsClient, UserStreamsClient, MEXC_SPOT_SOCKET_URL
from .market import MarketStreams
from .user import UserStreams

@dataclass
class Streams(MarketStreams, UserStreams):

  class Config(StreamsClient.Config, UserStreamsClient.Config, total=False):
    ...

  def __init__(
    self, *,
    api_url: str = MEXC_SPOT_API_BASE,
    ws_url: str = MEXC_SPOT_SOCKET_URL,
    auth_http: AuthHttpClient,
    **kwargs: Unpack[Config],
  ):
    kw1 = filter_kwargs(StreamsClient.Config, kwargs)
    self.ws = StreamsClient(url=ws_url, **kw1)
    kw2 = filter_kwargs(UserStreamsClient.Config, kwargs)
    self.auth_ws = UserStreamsClient(auth_http=auth_http, api_url=api_url, ws_url=ws_url, **kw2)

  @classmethod
  def new(
    cls, api_key: str, api_secret: str, *,
    api_url: str = MEXC_SPOT_API_BASE,
    ws_url: str = MEXC_SPOT_SOCKET_URL,
    **kwargs: Unpack[Config],
  ):
    auth_http = AuthHttpClient(api_key=api_key, api_secret=api_secret)
    return cls(api_url=api_url, ws_url=ws_url, auth_http=auth_http, **kwargs)
  
  @classmethod
  def env(
    cls, *,
    api_url: str = MEXC_SPOT_API_BASE,
    ws_url: str = MEXC_SPOT_SOCKET_URL,
    **kwargs: Unpack[Config],
  ):
    import os
    return cls.new(
      api_key=os.environ['MEXC_ACCESS_KEY'],
      api_secret=os.environ['MEXC_SECRET_KEY'],
      api_url=api_url,
      ws_url=ws_url,
      **kwargs,
    )