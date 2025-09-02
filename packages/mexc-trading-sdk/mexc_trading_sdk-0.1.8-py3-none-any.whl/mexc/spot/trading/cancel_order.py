from typing_extensions import TypedDict, NotRequired
from mexc.core import timestamp as ts, validator, OrderSide, OrderType, OrderStatus, TimeInForce
from mexc.spot.core import AuthSpotMixin, ApiError

class CanceledOrder(TypedDict):
  symbol: str
  origClientOrderId: NotRequired[str|None]
  orderId: str
  clientOrderId: NotRequired[str|None]
  orderListId: NotRequired[int|None]
  price: str
  origQty: str
  executedQty: str
  cummulativeQuoteQty: str
  status: OrderStatus
  timeInForce: NotRequired[TimeInForce|None]
  type: OrderType
  side: OrderSide

Response: type[CanceledOrder | ApiError] = CanceledOrder | ApiError # type: ignore
validate_response = validator(Response)
  
class CancelOrder(AuthSpotMixin):
  async def cancel_order(
    self, symbol: str, *, orderId: str,
    recvWindow: int | None = None,
    timestamp: int | None = None,
    validate: bool | None = None,
  ) -> ApiError | CanceledOrder:
    """Cancel an open order (of your account) by ID.
    
    - `symbol`: The symbol being traded, e.g. `BTCUSDT`
    - `orderId`: The order ID to cancel.
    - `recvWindow`: If the server receives the request after `timestamp + recvWindow`, it will be rejected (default: 5000).
    - `timestamp`: The timestamp for the request, in milliseconds (default: now).
    - `validate`: Whether to validate the response against the expected schema (default: True).
    
    > [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#cancel-order)
    """
    params: dict = {
      'symbol': symbol, 'orderId': orderId,
      'timestamp': timestamp or ts.now(),
    }
    if recvWindow is not None:
      params['recvWindow'] = recvWindow
    r = await self.signed_request('DELETE', '/api/v3/order', params=params)
    return validate_response(r.text) if self.validate(validate) else r.json()