from typing_extensions import Any, TypedDict
import asyncio
from dataclasses import dataclass, field
from mexc.core import json, validator, ValidationMixin
from mexc.core.ws.streams_rpc import StreamsRPCSocketClient

MEXC_FUTURES_SOCKET_URL = 'wss://contract.mexc.com/edge'

class Response(TypedDict):
  channel: str
  data: Any
  ts: int

validate_response = validator(Response)

@dataclass
class StreamsClient(StreamsRPCSocketClient):
  url: str = field(default=MEXC_FUTURES_SOCKET_URL, kw_only=True)

  async def send(self, msg):
    await (await self.ws).send(json().dumps(msg), text=True)

  async def send_request(self, method: str, params=None):
    msg = {'method': method}
    if params is not None:
      msg['param'] = params
    await self.send(msg)

  async def ping(self):
    if not 'pong' in self.subscribers:
      self.subscribers['pong'] = asyncio.Queue()
    await self.send_request('ping')
    await self.subscribers['pong'].get()

  async def request_subscription(self, channel: str, params=None):
    await self.send_request(f'sub.{channel}', params)

  async def request_unsubscription(self, channel: str):
    await self.send_request(f'unsub.{channel}')

  def parse_msg(self, msg: str | bytes) -> tuple[str|None, Any]:
    r = validate_response(msg)
    if r['channel'].startswith('push.'):
      channel = r['channel'].removeprefix('push.')
      return channel, r['data']
    elif r['channel'] == 'pong':
      return 'pong', r
    else:
      return None, r
    
  async def open(self):
    return await super().open()

@dataclass
class StreamsMixin(ValidationMixin):
  ws: StreamsClient

  async def __aenter__(self):
    await self.ws.__aenter__()
    return self
  
  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.ws.__aexit__(exc_type, exc_value, traceback)

  async def subscribe(self, channel: str, params=None):
    async for msg in self.ws.subscribe(channel, params):
      yield msg