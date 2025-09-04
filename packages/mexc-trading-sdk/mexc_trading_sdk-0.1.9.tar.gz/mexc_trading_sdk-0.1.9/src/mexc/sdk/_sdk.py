from dataclasses import dataclass, field
from mexc import MEXC as Client
from .spot import Spot
from .wallet import Wallet
from .futures import Futures

@dataclass
class MEXC:
  spot: Spot
  wallet: Wallet
  futures: Futures
  client: Client = field(kw_only=True)

  @classmethod
  def new(
    cls, api_key: str, api_secret: str, *,
    validate: bool = True, recvWindow: int | None = None,
  ):
    client = Client.new(api_key, api_secret, validate=validate)
    return cls(
      spot=Spot(client=client, validate=validate, recvWindow=recvWindow),
      wallet=Wallet(client=client, validate=validate, recvWindow=recvWindow),
      futures=Futures(client=client, validate=validate, recvWindow=recvWindow),
      client=client,
    )
  
  @classmethod
  def env(cls, *, validate: bool = True, recvWindow: int | None = None):
    import os
    return cls.new(
      api_key=os.environ['MEXC_ACCESS_KEY'],
      api_secret=os.environ['MEXC_SECRET_KEY'],
      validate=validate,
      recvWindow=recvWindow,
    )
  
  async def __aenter__(self):
    await self.client.__aenter__()
    return self
  
  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)