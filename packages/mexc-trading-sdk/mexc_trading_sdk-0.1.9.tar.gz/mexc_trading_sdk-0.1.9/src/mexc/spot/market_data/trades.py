from typing_extensions import TypedDict
from mexc.core import validator
from mexc.spot.core import SpotMixin, ApiError

class Trade(TypedDict):
  id: str | None
  price: str
  qty: str
  quoteQty: str
  time: int
  isBuyerMaker: bool
  isBestMatch: bool

Response: type[list[Trade] | ApiError] = list[Trade] | ApiError # type: ignore
validate_response = validator(Response)

class Trades(SpotMixin):
  async def trades(
    self, symbol: str, *,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> ApiError | list[Trade]:
    """Get recent trades for a given symbol.
    
    - `symbol`: The symbol being traded, e.g. `BTCUSDT`.
    - `limit`: The maximum number of trades to return (default: 500, max: 1000).
    - `validate`: Whether to validate the response against the expected schema (default: True).

    > [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#recent-trades-list)
    """
    params: dict = {'symbol': symbol}
    if limit is not None:
      params['limit'] = limit
    r = await self.request('GET', '/api/v3/trades', params=params)
    return validate_response(r.text) if self.validate(validate) else r.json()