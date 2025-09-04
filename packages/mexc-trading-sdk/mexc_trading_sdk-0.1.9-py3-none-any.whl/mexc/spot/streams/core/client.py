from typing_extensions import Any, TypedDict
from dataclasses import dataclass, field
from mexc.core import json, validator, ValidationError
from mexc.core.ws.streams_rpc import StreamsRPCSocketClient
from .proto import parse_proto

MEXC_SPOT_SOCKET_URL = 'wss://wbs-api.mexc.com/ws'

class Response(TypedDict):
  id: int
  code: int
  msg: str

validate_response = validator(Response)

@dataclass
class StreamsClient(StreamsRPCSocketClient):
  url: str = field(default=MEXC_SPOT_SOCKET_URL, kw_only=True)

  async def send(self, msg):
    await (await self.ws).send(json().dumps(msg), text=True)

  async def send_request(self, method: str, params=None):
    msg = {'method': method}
    if params is not None:
      msg['params'] = params
    await self.send(msg)

  async def ping(self):
    await self.send('PING')

  async def request_subscription(self, channel: str, params=None):
    await self.send_request('SUBSCRIPTION', [channel])

  async def request_unsubscription(self, channel: str):
    await self.send_request('UNSUBSCRIPTION', [channel])

  def parse_msg(self, msg: str | bytes) -> tuple[str|None, Any]:
    try:
      data = validate_response(msg)
      return None, data
    except ValidationError:
      proto = parse_proto(msg)
      channel: str = proto.channel # type: ignore
      return channel, proto
    
  async def open(self):
    return await super().open()

@dataclass
class StreamsMixin:
  ws: StreamsClient = field(default_factory=StreamsClient, kw_only=True)

  async def __aenter__(self):
    await self.ws.__aenter__()
    return self
  
  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.ws.__aexit__(exc_type, exc_value, traceback)

  async def subscribe(self, channel: str):
    async for msg in self.ws.subscribe(channel):
      yield msg