from datetime import datetime
from typing_extensions import AsyncIterable, Sequence
from dataclasses import dataclass
from decimal import Decimal
from trading_sdk.types import ApiError
from trading_sdk.futures.user_data.funding_rate_history import FundingRateHistory as FundingRateHistoryTDK, Funding

from mexc.core import timestamp
from mexc.sdk.util import SdkMixin, wrap_exceptions
from mexc.futures.user_data.funding_rate_history import PositionType

@dataclass
class FundingRateHistory(FundingRateHistoryTDK, SdkMixin):
  @wrap_exceptions
  async def funding_rate_history(
    self, base: str, quote: str, *, start: datetime | None = None, end: datetime | None = None
  ) -> AsyncIterable[Sequence[Funding]]:
    symbol = f'{base}_{quote}'
    page_num = 1
    num_pages = None
    while num_pages is None or page_num <= num_pages:
      r = await self.client.futures.funding_rate_history(symbol)
      if not 'data' in r:
        raise ApiError(r)
      else:
        yield [
          Funding(
            rate=Decimal(f['rate']),
            funding=Decimal(f['funding']),
            time=timestamp.parse(f['settleTime']),
            position_type='LONG' if f['positionType'] == PositionType.long else 'SHORT',
          )
          for f in r['data']['resultList']
        ]
        num_pages = r['data']['totalPage']
        page_num += 1
