from dataclasses import dataclass
from decimal import Decimal
from trading_sdk.types import ApiError
from trading_sdk.spot.market_data.depth import Depth as DepthTDK, Book
from mexc.sdk.util import SdkMixin, wrap_exceptions

@dataclass
class Depth(DepthTDK, SdkMixin):
  @wrap_exceptions
  async def depth(self, base: str, quote: str, *, limit: int | None = None) -> Book:
    symbol = f'{base}{quote}'
    r = await self.client.spot.depth(symbol, limit=limit)
    if 'code' in r:
      raise ApiError(r)
    else:
      return Book(
        asks=[Book.Entry(
          price=Decimal(p.price),
          qty=Decimal(p.qty)
        ) for p in r['asks']],
        bids=[Book.Entry(
          price=Decimal(p.price),
          qty=Decimal(p.qty)
        ) for p in r['bids']],
      )
