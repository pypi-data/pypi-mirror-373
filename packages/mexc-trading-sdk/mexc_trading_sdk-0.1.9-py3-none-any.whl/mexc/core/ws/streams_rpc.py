from typing_extensions import Any
from abc import abstractmethod
from dataclasses import dataclass, field
import asyncio
from .base import SocketClient, Restart

@dataclass
class StreamsRPCSocketClient(SocketClient):
  """Multiplexed streams socket client, allowing subscription to multiple channels. Also supports serial request/response communication, using a lock to serialize requests"""
  lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)
  replies: asyncio.Queue = field(default_factory=asyncio.Queue, init=False)
  subscribers: dict[str, asyncio.Queue] = field(default_factory=dict, init=False)

  @abstractmethod
  async def request_subscription(self, channel: str, params=None):
    ...

  @abstractmethod
  async def request_unsubscription(self, channel: str):
    ...

  @abstractmethod
  def parse_msg(self, msg: str | bytes) -> tuple[str|None, Any]:
    """Returns `(channel, data)` in case of a subscription push message, or `(None, data)` in case of a reply"""

  def on_msg(self, msg: str | bytes | Restart):
    if isinstance(msg, Restart):
      for queue in self.subscribers.values():
        queue.put_nowait(Restart())
    else:
      channel, data = self.parse_msg(msg)
      if channel is None:
        self.replies.put_nowait(data)
      elif channel in self.subscribers:
        self.subscribers[channel].put_nowait(data)

  @abstractmethod
  async def send(self, msg):
    ...

  async def request(self, msg):
    while True:
      async with self.lock:
        await self.send(msg)
        res = await self.replies.get()
        if isinstance(res, Restart):
          continue
        return res

  async def subscribe(self, channel: str, params=None):
    self.subscribers[channel] = asyncio.Queue()
    while True:
      await self.request_subscription(channel, params)
      while True:
        if (queue := self.subscribers.get(channel)) is None:
          return # unsubscribed
        val = await queue.get()
        if isinstance(val, Restart):
          await self.started.wait()
          break
        else:
          yield val

  async def unsubscribe(self, channel: str):
    del self.subscribers[channel]
    await self.request_unsubscription(channel)
    