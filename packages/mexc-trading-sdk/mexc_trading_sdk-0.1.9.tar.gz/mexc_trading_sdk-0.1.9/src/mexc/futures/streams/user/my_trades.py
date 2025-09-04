from typing_extensions import TypedDict, AsyncIterable
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from mexc.core import validator
from mexc.futures.streams.core import AuthedStreamsMixin

class Side(Enum):
  open_long = 1
  close_short = 2
  open_short = 3
  close_long = 4

class Deal(TypedDict):
  category: int
  externalOid: str
  fee: Decimal
  feeCurrency: str
  id: str
  isSelf: bool
  orderId: str
  positionMode: int
  price: Decimal
  profit: Decimal
  side: Side
  symbol: str
  taker: bool
  timestamp: int
  vol: Decimal
  """Base asset amount, in volume units"""

validate_response = validator(Deal)

@dataclass
class MyTrades(AuthedStreamsMixin):
  async def my_trades(self, *, validate: bool = True) -> AsyncIterable[Deal]:
    """Subscribe to your future trades.

    - `validate`: Whether to validate the response against the expected schema (default: True).

    > [MEXC API docs (not very good, they don't even mention this channel)](https://mexcdevelop.github.io/apidocs/contract_v1_en/#private-channels)
    """
    async for msg in self.auth_ws.subscribe('personal.order.deal'):
      yield validate_response(msg) if self.validate(validate) else msg