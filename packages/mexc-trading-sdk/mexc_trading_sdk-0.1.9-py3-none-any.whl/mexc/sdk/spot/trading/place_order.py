from dataclasses import dataclass
from trading_sdk.types import fmt_num, ApiError
from trading_sdk.spot.trading.place_order import PlaceOrder as PlaceOrderTDK, Order as OrderTDK
from mexc.spot.trading.place_order import Order, LimitOrder, MarketOrder
from mexc.sdk.util import SdkMixin, wrap_exceptions

def parse_order(order: OrderTDK) -> Order:
  if order['type'] == 'LIMIT':
    return LimitOrder(
      type='LIMIT',
      side=order['side'],
      price=fmt_num(order['price']),
      quantity=fmt_num(order['qty'])
    )
  elif order['type'] == 'MARKET':
    return MarketOrder(
      type='MARKET',
      side=order['side'],
      quantity=fmt_num(order['qty'])
    )

@dataclass
class PlaceOrder(PlaceOrderTDK, SdkMixin):
  @wrap_exceptions
  async def place_order(self, base: str, quote: str, order: OrderTDK) -> str:
    symbol = f'{base}{quote}'
    r = await self.client.spot.place_order(symbol, parse_order(order))
    if 'code' in r:
      raise ApiError(r)
    else:
      return r['orderId']