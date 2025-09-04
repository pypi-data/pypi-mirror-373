from dataclasses import dataclass
from decimal import Decimal
from trading_sdk.spot.user_data.open_orders import OpenOrders as OpenOrdersTDK, OrderState
from mexc.core import timestamp
from mexc.sdk.util import SdkMixin, wrap_exceptions

@dataclass
class OpenOrders(OpenOrdersTDK, SdkMixin):
  @wrap_exceptions
  async def open_orders(self, base: str, quote: str) -> list[OrderState]:
    symbol = f'{base}{quote}'
    r = await self.client.spot.open_orders(symbol)
    match r:
      case list(orders):
        return [
          OrderState(
            id=o['orderId'],
            price=Decimal(o['price']),
            qty=Decimal(o['origQty']),
            filled_qty=Decimal(o['executedQty']),
            time=timestamp.parse(o['time']),
            side=o['side'],
            status=o['status']
          )
          for o in orders
        ]
      case err:
        raise RuntimeError(err)
