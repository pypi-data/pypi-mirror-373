from typing_extensions import TypedDict, NotRequired
from enum import Enum
from datetime import datetime
from mexc.core import timestamp as ts, validator
from mexc.spot.core import AuthSpotMixin, ApiError

class TransferType(Enum):
  outside = 0
  inside = 1

class Status(Enum):
  small = 1
  time_delay = 2
  large_delay = 3
  pending = 4
  success = 5
  auditing = 6
  rejected = 7
  refund = 8
  pre_success = 9
  invalid = 10
  restricted = 11
  completed = 12

class Deposit(TypedDict):
  txId: str
  amount: str
  coin: str
  network: str
  netWork: str
  status: Status
  address: str
  insertTime: int
  confirmTimes: str
  memo: NotRequired[str|None]

Response: type[list[Deposit] | ApiError] = list[Deposit] | ApiError # type: ignore
validate_response = validator(Response)

class DepositHistory(AuthSpotMixin):
  async def deposit_history(
    self, *, coin: str | None = None,
    status: Status | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int | None = None,
    timestamp: int | None = None,
    validate: bool | None = None,
  ) -> ApiError | list[Deposit]:
    """Query deposit history.
    
    - `coin`: The coin to query the deposit history for, e.g. `USDT`. (if not given, returns all coins)
    - `status`: The status of the deposit to query. (if not given, returns all statuses)
    - `start`: The start time to query. If given, only deposits after this time will be returned.
    - `end`: The end time to query. If given, only deposits before this time will be returned.
    - `limit`: The maximum number of deposits to return (default: 1000, max: 1000).
    - `timestamp`: The timestamp for the request, in milliseconds (default: now).
    - `validate`: Whether to validate the response against the expected schema (default: True).

    > [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#deposit-history-supporting-network)
    """
    params: dict = {'timestamp': timestamp or ts.now()}
    if coin is not None:
      params['coin'] = coin
    if status is not None:
      params['status'] = status.value
    if start is not None:
      params['startTime'] = ts.dump(start)
    if end is not None:
      params['endTime'] = ts.dump(end)
    if limit is not None:
      params['limit'] = limit
    r = await self.signed_request('GET', '/api/v3/capital/deposit/hisrec', params=params)
    return validate_response(r.text) if self.validate(validate) else r.json()