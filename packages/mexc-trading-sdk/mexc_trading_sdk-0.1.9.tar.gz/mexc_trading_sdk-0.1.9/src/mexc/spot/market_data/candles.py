from typing_extensions import NamedTuple, Literal
from datetime import datetime
from mexc.core import timestamp as ts, validator
from mexc.spot.core import SpotMixin, ApiError

class Candle(NamedTuple):
  open_time: int
  open: str
  high: str
  low: str
  close: str
  volume: str
  close_time: int
  quote_volume: str

Response: type[list[Candle] | ApiError] = list[Candle] | ApiError # type: ignore
validate_response = validator(Response)

Interval = Literal['1m', '5m', '15m', '30m', '60m', '4h', '1d', '1W', '1M']

class Candles(SpotMixin):
  async def candles(
    self, symbol: str, *,
    interval: Interval,
    start: datetime | None = None, end: datetime | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> ApiError | list[Candle]:
    """Get klines (candles) for a given symbol.
    
    - `symbol`: The symbol being traded, e.g. `BTCUSDT`.
    - `interval`: The interval of the klines (default: 1m).
    - `start`: The start time to query. If given, only klines after this time will be returned.
    - `end`: The end time to query. If given, only klines before this time will be returned.
    - `limit`: The maximum number of klines to return (default: 500, max: 1000).
    - `validate`: Whether to validate the response against the expected schema (default: True).

    > [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#kline-candlestick-data)
    """
    params: dict = {'symbol': symbol, 'interval': interval}
    if limit is not None:
      params['limit'] = limit
    if start is not None:
      params['startTime'] = ts.dump(start)
    if end is not None:
      params['endTime'] = ts.dump(end)
    r = await self.request('GET', '/api/v3/klines', params=params)
    return validate_response(r.text) if self.validate(validate) else r.json()