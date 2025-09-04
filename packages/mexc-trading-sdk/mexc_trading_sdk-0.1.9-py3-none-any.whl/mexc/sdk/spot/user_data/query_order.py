from dataclasses import dataclass
from decimal import Decimal
from trading_sdk.types import ApiError
from trading_sdk.spot.user_data.query_order import QueryOrder as QueryOrderTDK, OrderState
from mexc.core import timestamp
from mexc.sdk.util import SdkMixin, wrap_exceptions

@dataclass
class QueryOrder(QueryOrderTDK, SdkMixin):
  @wrap_exceptions
  async def query_order(self, base: str, quote: str, *, id: str) -> OrderState:
    symbol = f'{base}{quote}'
    r = await self.client.spot.query_order(symbol, orderId=id)
    if 'code' in r:
      raise ApiError(r)
    else:
      return OrderState(
        id=r['orderId'],
        price=Decimal(r['price']),
        qty=Decimal(r['origQty']),
        filled_qty=Decimal(r['executedQty']),
        time=timestamp.parse(r['time']),
        side=r['side'],
        status=r['status']
      )
