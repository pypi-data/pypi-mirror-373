from typing_extensions import TypedDict
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from enum import Enum
from mexc.core import validator, timestamp as ts
from mexc.futures.core import AuthFuturesMixin, FuturesResponse

class Side(Enum):
  open_long = 1
  close_short = 2
  open_short = 3
  close_long = 4

class Category(Enum):
  limit_order = 1
  system_takeover_delegate = 2
  close_delegate = 3
  adl_reduction = 4

class Trade(TypedDict):
  id: int | str
  symbol: str
  side: Side
  vol: Decimal
  """Volume of the trade in contract units."""
  price: Decimal
  fee: Decimal
  feeCurrency: str
  profit: Decimal
  taker: bool
  category: Category
  orderId: int | str
  timestamp: int

Response: type[FuturesResponse[list[Trade]]] = FuturesResponse[list[Trade]] # type: ignore
validate_response = validator(Response)

@dataclass
class MyTrades(AuthFuturesMixin):
  async def my_trades(
    self, symbol: str | None = None, *,
    start: datetime | None = None,
    end: datetime | None = None,
    page_num: int | None = None,
    page_size: int | None = None,
    validate: bool | None = None,
  ) -> FuturesResponse[list[Trade]]:
    """Get futures trades of your account.

    - `symbol`: The symbol being traded, e.g. `BTCUSDT`. If not provided, all symbols will be returned.
    - `start`: The start time to query. If given, only trades after this time will be returned.
    - `end`: The end time to query. If given, only trades before this time will be returned.
    - `page_num`: The page number (default: 1).
    - `page_size`: The page size (default: 20, max: 100).
    - `validate`: Whether to validate the response against the expected schema (default: True).

    > [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#get-all-transaction-details-of-the-user-s-order)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    if start is not None:
      params['start_time'] = ts.dump(start)
    if end is not None:
      params['end_time'] = ts.dump(end)
    if page_num is not None:
      params['page_num'] = page_num
    if page_size is not None:
      params['page_size'] = page_size
    r = await self.signed_request('GET', '/api/v1/private/order/list/order_deals', params=params)
    return validate_response(r.text) if self.validate(validate) else r.json()