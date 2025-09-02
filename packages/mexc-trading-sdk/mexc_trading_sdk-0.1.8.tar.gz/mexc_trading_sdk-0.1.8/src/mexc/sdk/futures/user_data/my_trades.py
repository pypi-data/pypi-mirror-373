from typing_extensions import Sequence, AsyncIterable
from dataclasses import dataclass
from functools import cache
from datetime import datetime
from decimal import Decimal
from trading_sdk.types import ApiError
from trading_sdk.spot.user_data.my_trades import MyTrades as MyTradesTDK, Trade, Side as SideTDK

from mexc.core import timestamp
from mexc.futures.user_data.my_trades import Side
from mexc.sdk.util import SdkMixin, wrap_exceptions

def parse_side(side: Side) -> SideTDK:
  match side:
    case Side.open_long | Side.close_short:
      return 'BUY'
    case Side.open_short | Side.close_long:
      return 'SELL'

@dataclass
class MyTrades(MyTradesTDK, SdkMixin):
  @wrap_exceptions
  async def my_trades(
    self, base: str, quote: str, *,
    start: datetime | None = None, end: datetime | None = None
  ) -> AsyncIterable[Sequence[Trade]]:
    symbol = f'{base}_{quote}'
    page_size = 100
    page_num = 1

    r = await self.client.futures.contract_info(symbol)
    if not 'data' in r:
      raise ApiError(r)
    else:
      contract_size = r['data']['contractSize']

    while True:
      r = await self.client.futures.my_trades(symbol, start=start, end=end, page_size=page_size, page_num=page_num)
      if not 'data' in r:
        raise ApiError(r)
      else:
        trades = r['data']
        yield [
          Trade(
            id=str(t['id']),
            price=t['price'],
            qty=t['vol'] * contract_size,
            time=timestamp.parse(t['timestamp']),
            side=parse_side(t['side']),
            maker=not t['taker'],
            fee=Trade.Fee(
              asset=t['feeCurrency'],
              amount=t['fee'],
            ) if t['feeCurrency'] and t['fee'] else None,
          )
          for t in trades
        ]
        if len(trades) < page_size:
          break
        page_num += 1
    
