from typing_extensions import TypedDict, Literal
from datetime import datetime
from mexc.core import timestamp as ts, validator
from mexc.futures.core import FuturesMixin, FuturesResponse

class CandleData(TypedDict):
  time: list[int]
  open: list[float]
  close: list[float]
  high: list[float]
  low: list[float]
  vol: list[float]
  amount: list[float]
  realOpen: list[float]
  realClose: list[float]
  realHigh: list[float]
  realLow: list[float]

Response: type[FuturesResponse[CandleData]] = FuturesResponse[CandleData] # type: ignore
validate_response = validator(Response)

Interval = Literal['Min1', 'Min5', 'Min15', 'Min30', 'Min60', 'Hour4', 'Day1', 'Week1']

class Candles(FuturesMixin):
  async def candles(
    self, symbol: str, *,
    interval: Interval | None = None,
    start: datetime | None = None, end: datetime | None = None,
    validate: bool | None = None,
  ) -> FuturesResponse[CandleData]:
    """Get klines (candles) for a given symbol. Returns at most 2000 candles.
    
    - `symbol`: The symbol being traded, e.g. `BTC_USDT`.
    - `interval`: The interval of the klines (default: 1m).
    - `start`: The start time to query. If given, only klines after this time will be returned.
    - `end`: The end time to query. If given, only klines before this time will be returned.
    - `validate`: Whether to validate the response against the expected schema (default: True).

    > [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#k-line-data)
    """
    params = {}
    if interval is not None:
      params['interval'] = interval
    if start is not None:
      params['start'] = ts.dump(start)
    if end is not None:
      params['end'] = ts.dump(end)
    r = await self.request('GET', f'/api/v1/contract/kline/{symbol}', params=params)
    return validate_response(r.text) if self.validate(validate) else r.json()