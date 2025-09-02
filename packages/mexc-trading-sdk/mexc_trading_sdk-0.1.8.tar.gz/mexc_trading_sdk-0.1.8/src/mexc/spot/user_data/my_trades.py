from typing_extensions import TypedDict, NotRequired
from datetime import datetime
from mexc.core import timestamp as ts, validator
from mexc.spot.core import AuthSpotMixin, ApiError

class Trade(TypedDict):
  id: str
  orderId: str
  price: str
  qty: str
  quoteQty: str
  time: int
  commission: NotRequired[str|None]
  commissionAsset: NotRequired[str|None]
  isBuyer: bool
  isMaker: bool
  isBestMatch: bool
  isSelfTrade: bool
  clientOrderId: NotRequired[str|None]

Response: type[list[Trade] | ApiError] = list[Trade] | ApiError # type: ignore
validate_response = validator(Response)

class MyTrades(AuthSpotMixin):
  async def my_trades(
    self, symbol: str, *,
    orderId: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int | None = None,
    recvWindow: int | None = None,
    timestamp: int | None = None,
    validate: bool | None = None,
  ) -> ApiError | list[Trade]:
    """Get all trades (of your account) for a given symbol.

    Only the transaction records in the past 1 month can be queried. If you want to view more transaction records, please use the export function on the web side, which supports exporting transaction records of the past 3 years at most.
    
    - `symbol`: The symbol being traded, e.g. `BTCUSDT`
    - `orderId`: The order ID to query. If given, only trades for this order will be returned.
    - `start`: The start time to query. If given, only trades after this time will be returned.
    - `end`: The end time to query. If given, only trades before this time will be returned.
    - `limit`: The maximum number of trades to return (default: 100, max: 100)
    - `recvWindow`: If the server receives the request after `timestamp + recvWindow`, it will be rejected (default: 5000).
    - `timestamp`: The timestamp for the request, in milliseconds (default: now).
    - `validate`: Whether to validate the response against the expected schema (default: True).

    > [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#account-trade-list)
    """
    params: dict = {
      'symbol': symbol,
      'timestamp': timestamp or ts.now(),
    }
    if orderId is not None:
      params['orderId'] = orderId
    if start is not None:
      params['startTime'] = ts.dump(start)
    if end is not None:
      params['endTime'] = ts.dump(end)
    if limit is not None:
      params['limit'] = limit
    if recvWindow is not None:
      params['recvWindow'] = recvWindow
    r = await self.signed_request('GET', '/api/v3/myTrades', params=params)
    return validate_response(r.text) if self.validate(validate) else r.json()