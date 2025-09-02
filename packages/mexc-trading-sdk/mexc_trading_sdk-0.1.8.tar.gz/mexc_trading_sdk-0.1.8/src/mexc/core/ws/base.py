from typing_extensions import TypedDict
from abc import ABC, abstractmethod
import asyncio
from functools import wraps
from dataclasses import dataclass, field
from datetime import timedelta
import logging
import websockets
from ..exc import NetworkError

logger = logging.getLogger('mexc.core.ws')

class Restart:
  ...

@dataclass
class Context:
  ws: websockets.ClientConnection
  pinger: asyncio.Task
  listener: asyncio.Task
  restarter: asyncio.Task

@dataclass(kw_only=True)
class SocketClient(ABC):
  """Base socket client class, including:
  - Connection management
  - Keep alive (ping) loop
  - Restart loop
  - Message handling loop
  """
  url: str
  timeout: timedelta = timedelta(seconds=10)
  ping_every: timedelta = timedelta(seconds=15)
  restart_every: timedelta = timedelta(hours=23)
  started: asyncio.Event = field(default_factory=asyncio.Event, init=False)

  class Config(TypedDict, total=False):
    timeout: timedelta
    ping_every: timedelta
    restart_every: timedelta

  @property
  async def ctx(self) -> Context:
    if (ctx := getattr(self, '_ctx', None)) is None:
      ctx = await self.open()
    return ctx
  
  @property
  async def ws(self) -> websockets.ClientConnection:
    return (await self.ctx).ws
  
  @staticmethod
  def with_client(fn):
    @wraps(fn)
    async def wrapper(self, *args, **kwargs):
      if getattr(self, '_client', None) is None:
        async with self:
          return await fn(self, *args, **kwargs)
      else:
        return await fn(self, *args, **kwargs)
      
    return wrapper
  
  async def __aenter__(self):
    await self.open()
    return self
  
  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.close(await self.ctx, exc_type, exc_value, traceback)
  
  @abstractmethod
  async def open(self):
    logger.info('Opening...')
    async def connect():
      try:
        return await websockets.connect(self.url, open_timeout=self.timeout.total_seconds())
      except websockets.exceptions.WebSocketException as e:
        raise NetworkError(f'Failed to connect to {self.url}') from e
    
    ws = await connect()
    logger.info('Connected!')
    self._ctx = Context(
      ws=ws,
      pinger=asyncio.create_task(self.pinger()),
      listener=asyncio.create_task(self.listener(ws)),
      restarter=asyncio.create_task(self.restarter()),
    )
    self.started.set()
    return self._ctx

  async def close(self, ctx: Context, exc_type=None, exc_value=None, traceback=None):
    ctx.pinger.cancel()
    ctx.listener.cancel()
    ctx.restarter.cancel()
    await ctx.ws.__aexit__(exc_type, exc_value, traceback)

  async def pinger(self):
    while True:
      await asyncio.sleep(self.ping_every.total_seconds())
      try:
        logger.debug('Pinging...')
        await asyncio.wait_for(self.ping(), self.timeout.total_seconds())
      except asyncio.TimeoutError:
        logger.warning('Ping timeout, restarting...')
        asyncio.create_task(self.restart())
        break

  async def listener(self, ws: websockets.ClientConnection, /):
    while True:
      msg = await ws.recv()
      logger.debug('Received: %s', msg)
      self.on_msg(msg)

  async def restarter(self):
    await asyncio.sleep(self.restart_every.total_seconds())
    asyncio.create_task(self.restart())

  async def restart(self):
    logger.info('Restarting...')
    self.started.clear()
    self.on_msg(Restart())
    await self.close(await self.ctx)
    await self.open()

  @abstractmethod
  def on_msg(self, msg: str | bytes | Restart):
    ...

  @abstractmethod
  async def ping(self):
    ...

class RpcSocketClient(SocketClient):
  """Base request/response socket client."""
  @abstractmethod
  async def request(self, msg) -> str | bytes:
    ...
