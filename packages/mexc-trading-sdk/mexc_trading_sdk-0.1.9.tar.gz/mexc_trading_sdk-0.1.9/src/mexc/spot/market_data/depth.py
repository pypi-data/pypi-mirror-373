from typing_extensions import TypedDict, NamedTuple 
from mexc.core import validator
from mexc.spot.core import SpotMixin, ApiError

class BookEntry(NamedTuple):
  price: str
  qty: str

class OrderBook(TypedDict):
  lastUpdateId: int
  bids: list[BookEntry]
  asks: list[BookEntry]

Response: type[OrderBook | ApiError] = OrderBook | ApiError # type: ignore
validate_response = validator(Response)

class Depth(SpotMixin):
  async def depth(self, symbol: str, *, limit: int | None = None, validate: bool | None = None) -> ApiError | OrderBook:
    """Get the order book for a given symbol.
    
    - `symbol`: The symbol being traded, e.g. `BTCUSDT`.
    - `limit`: The maximum number of bids/asks to return (default: 100, max: 5000).
    - `validate`: Whether to validate the response against the expected schema (default: True).

    > [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#order-book)
    """
    params: dict = {'symbol': symbol}
    if limit is not None:
      params['limit'] = limit
    r = await self.request('GET', f'/api/v3/depth', params=params)
    return validate_response(r.text) if self.validate(validate) else r.json()