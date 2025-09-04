from datetime import datetime
from mexc.core import timestamp as ts, validator
from mexc.spot.core import AuthSpotMixin, ApiError
from .query_order import OrderState

Response: type[list[OrderState] | ApiError] = list[OrderState] | ApiError # type: ignore
validate_response = validator(Response)

class MyOrders(AuthSpotMixin):
  async def my_orders(
    self, symbol: str, *,
    limit: int | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    recvWindow: int | None = None,
    timestamp: int | None = None,
    validate: bool | None = None,
  ) -> ApiError | list[OrderState]:
    """Query orders (open or not, of your account) for a given symbol.
    
    - `symbol`: The symbol being traded, e.g. `BTCUSDT`
    - `limit`: The maximum number of orders to return (default: 500, max: 1000)
    - `start`: The start time to query. If given, only orders after this time will be returned.
    - `end`: The end time to query. If given, only orders before this time will be returned.
    - `recvWindow`: If the server receives the request after `timestamp + recvWindow`, it will be rejected (default: 5000).
    - `timestamp`: The timestamp for the request, in milliseconds (default: now).
    - `validate`: Whether to validate the response against the expected schema (default: True).

    > [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#all-orders)
    """
    params = {
      'symbol': symbol,
      'timestamp': timestamp or ts.now(),
    }
    if limit is not None:
      params['limit'] = limit
    if start is not None:
      params['startTime'] = ts.dump(start)
    if end is not None:
      params['endTime'] = ts.dump(end)
    if recvWindow is not None:
      params['recvWindow'] = recvWindow
    r = await self.signed_request('GET', '/api/v3/allOrders', params=params)
    return validate_response(r.text) if self.validate(validate) else r.json()