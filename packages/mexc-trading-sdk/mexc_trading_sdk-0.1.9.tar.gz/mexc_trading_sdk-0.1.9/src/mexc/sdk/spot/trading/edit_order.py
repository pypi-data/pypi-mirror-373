from dataclasses import dataclass
from trading_sdk.spot.trading.edit_order import EditOrder as EditOrderTDK
from trading_sdk.types import Num, fmt_num, ApiError
from mexc.spot.trading.place_order import LimitOrder
from mexc.sdk.util import SdkMixin, wrap_exceptions

@dataclass
class EditOrder(EditOrderTDK, SdkMixin):
  @wrap_exceptions
  async def edit_order(self, base: str, quote: str, *, id: str, qty: Num) -> str:
    symbol = f'{base}{quote}'
    state = await self.client.spot.cancel_order(symbol, orderId=id)
    if 'code' in state:
      raise ApiError(state)
    r = await self.client.spot.place_order(symbol, LimitOrder(
      type='LIMIT',
      side=state['side'],
      price=state['price'],
      quantity=fmt_num(qty)
    ))
    if 'code' in r:
      raise ApiError(r)
    else:
      return r['orderId']