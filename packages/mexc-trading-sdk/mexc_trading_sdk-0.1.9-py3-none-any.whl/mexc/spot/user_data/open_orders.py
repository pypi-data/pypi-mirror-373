from mexc.core import timestamp as ts, validator
from mexc.spot.core import AuthSpotMixin, ApiError
from .query_order import OrderState

Response: type[list[OrderState] | ApiError] = list[OrderState] | ApiError # type: ignore
validate_response = validator(Response)

class OpenOrders(AuthSpotMixin):
  async def open_orders(
    self, symbol: str, *,
    recvWindow: int | None = None,
    timestamp: int | None = None,
    validate: bool | None = None,
  ) -> ApiError | list[OrderState]:
    """Query open orders (of your account) for a given symbol.
    
    - `symbol`: The symbol being traded, e.g. `BTCUSDT`
    - `recvWindow`: If the server receives the request after `timestamp + recvWindow`, it will be rejected (default: 5000).
    - `timestamp`: The timestamp for the request, in milliseconds (default: now).
    - `validate`: Whether to validate the response against the expected schema (default: True).

    > [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#open-orders)
    """
    params = {
      'symbol': symbol,
      'timestamp': timestamp or ts.now(),
    }
    if recvWindow is not None:
      params['recvWindow'] = recvWindow
    r = await self.signed_request('GET', '/api/v3/openOrders', params=params)
    return validate_response(r.text) if self.validate(validate) else r.json()