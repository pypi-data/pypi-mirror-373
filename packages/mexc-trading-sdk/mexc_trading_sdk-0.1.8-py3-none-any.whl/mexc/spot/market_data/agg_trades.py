from typing_extensions import TypedDict
from datetime import datetime
from mexc.core import timestamp as ts, validator
from mexc.spot.core import SpotMixin, ApiError

class AggTrade(TypedDict):
  """Aggregate tradeId"""
  a: str | None
  """First tradeId"""
  f: str | None
  """Last tradeId"""
  l: str | None
  """Price"""
  p: str
  """Quantity"""
  q: str
  """Timestamp"""
  T: int
  """Is buyer maker"""
  m: bool
  """Is best match"""
  M: bool


Response: type[list[AggTrade] | ApiError] = list[AggTrade] | ApiError # type: ignore
validate_response = validator(Response)

class AggTrades(SpotMixin):
  async def agg_trades(
    self, symbol: str, *, limit: int | None = None,
    start: datetime | None = None, end: datetime | None = None,
    validate: bool | None = None,
  ) -> ApiError | list[AggTrade]:
    """Get aggregate trades for a given symbol, between two timestamps. There must be at most 1h between `start` and `end`.
    
    - `symbol`: The symbol being traded, e.g. `BTCUSDT`.
    - `limit`: The maximum number of trades to return (default: 500, max: 1000).
    - `start`: The start time to query. If given, only trades after this time will be returned (inclusive).
    - `end`: The end time to query. If given, only trades before this time will be returned (inclusive).
    - `validate`: Whether to validate the response against the expected schema (default: True).

    > [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#compressed-aggregate-trades-list)
    """
    params: dict = {'symbol': symbol}
    if limit is not None:
      params['limit'] = limit
    if start is not None:
      params['startTime'] = ts.dump(start)
    if end is not None:
      params['endTime'] = ts.dump(end)
    r = await self.request('GET', '/api/v3/aggTrades', params=params)
    return validate_response(r.text) if self.validate(validate) else r.json()