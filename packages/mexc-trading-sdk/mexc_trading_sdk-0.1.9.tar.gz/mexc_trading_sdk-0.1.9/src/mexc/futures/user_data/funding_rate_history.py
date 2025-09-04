from typing_extensions import TypedDict
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from mexc.core import validator
from mexc.futures.core import AuthFuturesMixin, FuturesResponse

class PositionType(Enum):
  long = 1
  short = 2

class Result(TypedDict):
  id: int
  symbol: str
  positionType: PositionType
  positionValue: Decimal
  funding: Decimal
  rate: Decimal
  settleTime: int

class Data(TypedDict):
  pageSize: int
  totalCount: int
  totalPage: int
  currentPage: int
  resultList: list[Result]

Response: type[FuturesResponse[Data]] = FuturesResponse[Data] # type: ignore
validate_response = validator(Response)

@dataclass
class FundingRateHistory(AuthFuturesMixin):
  async def funding_rate_history(
    self, symbol: str | None = None, *,
    position_id: int | None = None,
    page_num: int | None = None,
    page_size: int | None = None,
    validate: bool | None = None,
  ) -> FuturesResponse[Data]:
    """Fetch the funding rate history.

    - `symbol`: The symbol being traded, e.g. `BTCUSDT`. If not provided, all symbols will be returned.
    - `position_id`: The position ID.
    - `page_num`: The page number (default: 1).
    - `page_size`: The page size (default: 20, max: 100).
    - `validate`: Whether to validate the response against the expected schema (default: True).

    > [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#get-details-of-user-s-funding-rate)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    if position_id is not None:
      params['positionId'] = position_id
    if page_num is not None:
      params['pageNum'] = page_num
    if page_size is not None:
      params['pageSize'] = page_size
    r = await self.signed_request('GET', '/api/v1/private/position/funding_records', params=params)
    return validate_response(r.text) if self.validate(validate) else r.json()