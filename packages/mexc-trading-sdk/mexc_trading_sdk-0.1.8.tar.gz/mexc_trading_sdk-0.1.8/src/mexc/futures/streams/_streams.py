from dataclasses import dataclass
from typing_extensions import Unpack
from .core import StreamsClient, AuthedStreamsClient, MEXC_FUTURES_SOCKET_URL
from .user import UserStreams

@dataclass
class Streams(
  UserStreams,
):
  @classmethod
  def new(
    cls, api_key: str, api_secret: str, *,
    url: str = MEXC_FUTURES_SOCKET_URL,
    default_validate: bool = True,
    **kwargs: Unpack[StreamsClient.Config],
  ):
    ws = AuthedStreamsClient(api_key=api_key, api_secret=api_secret, url=url, **kwargs)
    return cls(auth_ws=ws, default_validate=default_validate)
  
  @classmethod
  def env(
    cls, *,
    url: str = MEXC_FUTURES_SOCKET_URL,
    default_validate: bool = True,
    **kwargs: Unpack[StreamsClient.Config],
  ):
    import os
    return cls.new(
      api_key=os.environ['MEXC_ACCESS_KEY'],
      api_secret=os.environ['MEXC_SECRET_KEY'],
      url=url,
      default_validate=default_validate,
      **kwargs,
    )