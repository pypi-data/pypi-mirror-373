from typing_extensions import TypedDict, NotRequired
from enum import Enum
from datetime import datetime
from mexc.core import timestamp as ts, validator
from mexc.spot.core import AuthSpotMixin, ApiError

class TransferType(Enum):
  outside = 0
  inside = 1

class Status(Enum):
  apply = 1
  auditing = 2
  wait = 3
  processing = 4
  wait_packaging = 5
  wait_confirm = 6
  success = 7
  failed = 8
  cancel = 9
  manual = 10

class Withdrawal(TypedDict):
  address: str
  amount: str
  applyTime: int
  coin: str
  id: str
  network: str
  netWork: str
  transferType: TransferType
  status: Status
  transactionFee: str
  remark: NotRequired[str|None]
  memo: NotRequired[str|None]
  coinId: NotRequired[str|None]
  vcoinId: NotRequired[str|None]

Response: type[list[Withdrawal] | ApiError] = list[Withdrawal] | ApiError # type: ignore
validate_response = validator(Response)

class WithdrawalHistory(AuthSpotMixin):
  async def withdrawal_history(
    self, *, coin: str | None = None,
    status: Status | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int | None = None,
    timestamp: int | None = None,
    validate: bool | None = None,
  ) -> ApiError | list[Withdrawal]:
    """Query withdrawal history.
    
    - `coin`: The coin to query the withdrawal history for, e.g. `USDT`. (if not given, returns all coins)
    - `status`: The status of the withdrawal to query. (if not given, returns all statuses)
    - `start`: The start time to query. If given, only withdrawals after this time will be returned.
    - `end`: The end time to query. If given, only withdrawals before this time will be returned.
    - `limit`: The maximum number of withdrawals to return (default: 1000, max: 1000).
    - `timestamp`: The timestamp for the request, in milliseconds (default: now).
    - `validate`: Whether to validate the response against the expected schema (default: True).

    > [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#withdraw-history-supporting-network)
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
    r = await self.signed_request('GET', '/api/v3/capital/withdraw/history', params=params)
    return validate_response(r.text) if self.validate(validate) else r.json()