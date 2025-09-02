from typing_extensions import TypedDict
from dataclasses import dataclass
from datetime import timedelta
import asyncio
from mexc.core import timestamp as ts, validator
from mexc.spot.core import MEXC_SPOT_API_BASE, AuthHttpClient
from .client import StreamsClient, MEXC_SPOT_SOCKET_URL

class ListenResponse(TypedDict):
  listenKey: str

validate_listen_response = validator(ListenResponse)

@dataclass
class Context:
  ws: StreamsClient
  listen_key: str
  pinger: asyncio.Task

@dataclass
class UserStreamsClient:
  auth_http: AuthHttpClient
  api_url: str = MEXC_SPOT_API_BASE
  ws_url: str = MEXC_SPOT_SOCKET_URL
  keep_alive_every: timedelta = timedelta(minutes=30)
  ctx: Context | None = None

  class Config(TypedDict, total=False):
    keep_alive_every: timedelta

  @classmethod
  def new(
    cls, api_key: str, api_secret: str, *,
    api_url: str = MEXC_SPOT_API_BASE,
    ws_url: str = MEXC_SPOT_SOCKET_URL,
    keep_alive_every: timedelta = timedelta(minutes=30),
  ):
    auth_http = AuthHttpClient(api_key=api_key, api_secret=api_secret)
    return cls(auth_http=auth_http, api_url=api_url, ws_url=ws_url, keep_alive_every=keep_alive_every)
  
  @classmethod
  def env(
    cls, *,
    api_url: str = MEXC_SPOT_API_BASE,
    ws_url: str = MEXC_SPOT_SOCKET_URL,
    keep_alive_every: timedelta = timedelta(minutes=30),
  ):
    import os
    return cls.new(
      api_key=os.environ['MEXC_ACCESS_KEY'],
      api_secret=os.environ['MEXC_SECRET_KEY'],
      api_url=api_url,
      ws_url=ws_url,
      keep_alive_every=keep_alive_every,
    )
  
  async def listen_key(self):
    r = await self.auth_http.signed_request('POST', self.api_url + '/api/v3/userDataStream', params={
      'timestamp': ts.now(),
    })
    return validate_listen_response(r.text)['listenKey']
  
  async def refresh_key(self, key: str):
    r = await self.auth_http.signed_request('PUT', self.api_url + '/api/v3/userDataStream', params={
      'listenKey': key,
      'timestamp': ts.now(),
    })
    return validate_listen_response(r.text)['listenKey']
  
  async def delete_key(self, key: str):
    r = await self.auth_http.signed_request('DELETE', self.api_url + '/api/v3/userDataStream', params={
      'listenKey': key,
      'timestamp': ts.now(),
    })
    return validate_listen_response(r.text)['listenKey']

  async def start(self):
    if self.ctx is None:
      key = await self.listen_key()
      ws = await StreamsClient(url=self.ws_url + f'?listenKey={key}').__aenter__()
      pinger = asyncio.create_task(self.pinger(key))
      self.ctx = Context(ws=ws, listen_key=key, pinger=pinger)
    return self.ctx
  
  async def __aenter__(self):
    await self.start()
    return self
  
  async def __aexit__(self, exc_type, exc_value, traceback):
    if self.ctx is not None:
      self.ctx.pinger.cancel()
      await self.ctx.ws.__aexit__(exc_type, exc_value, traceback)
      await self.delete_key(self.ctx.listen_key)
      self.ctx = None

  async def pinger(self, key: str):
    while True:
      await asyncio.sleep(self.keep_alive_every.total_seconds())
      await self.refresh_key(key)

  async def subscribe(self, channel: str):
    ctx = await self.start()
    async for msg in ctx.ws.subscribe(channel):
      yield msg

@dataclass
class UserStreamsMixin:
  auth_ws: UserStreamsClient

  async def __aenter__(self):
    await self.auth_ws.__aenter__()
    return self
  
  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.auth_ws.__aexit__(exc_type, exc_value, traceback)

  async def authed_subscribe(self, channel: str):
    async for msg in self.auth_ws.subscribe(channel):
      yield msg