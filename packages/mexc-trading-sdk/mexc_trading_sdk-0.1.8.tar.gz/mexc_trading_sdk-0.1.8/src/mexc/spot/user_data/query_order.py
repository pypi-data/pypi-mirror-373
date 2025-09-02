from typing_extensions import TypedDict
from mexc.core import timestamp as ts, validator, OrderSide, OrderType, OrderStatus, TimeInForce
from mexc.spot.core import AuthSpotMixin, ApiError

class OrderState(TypedDict):
  symbol: str
  orderId: str
  orderListId: int
  price: str
  origQty: str
  executedQty: str
  cummulativeQuoteQty: str
  status: OrderStatus
  timeInForce: TimeInForce | None
  type: OrderType
  side: OrderSide
  stopPrice: str | None
  time: int
  updateTime: int | None
  isWorking: bool

Response: type[OrderState | ApiError] = OrderState | ApiError # type: ignore
validate_response = validator(Response)

class QueryOrder(AuthSpotMixin):
  async def query_order(
    self, symbol: str, *, orderId: str,
    recvWindow: int | None = None,
    timestamp: int | None = None,
    validate: bool | None = None,
  ) -> ApiError | OrderState:
    """Query an order (of your account) by ID.
    
    - `symbol`: The symbol being traded, e.g. `BTCUSDT`
    - `orderId`: The order ID to query.
    - `recvWindow`: If the server receives the request after `timestamp + recvWindow`, it will be rejected (default: 5000).
    - `timestamp`: The timestamp for the request, in milliseconds (default: now).
    - `validate`: Whether to validate the response against the expected schema (default: True).
    
    > [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-order)
    """
    params = {
      'symbol': symbol,
      'timestamp': timestamp or ts.now(),
    }
    if recvWindow is not None:
      params['recvWindow'] = recvWindow
    if orderId is not None:
      params['orderId'] = orderId
    r = await self.signed_request('GET', '/api/v3/order', params=params)
    return validate_response(r.text) if self.validate(validate) else r.json()