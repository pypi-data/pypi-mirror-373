from dataclasses import dataclass
from decimal import Decimal
from trading_sdk.types import ApiError
from trading_sdk.spot.market_data.exchange_info import ExchangeInfo as ExchangeInfoTDK, Info
from mexc.sdk.util import SdkMixin, wrap_exceptions

@dataclass
class ExchangeInfo(ExchangeInfoTDK, SdkMixin):
  @wrap_exceptions
  async def exchange_info(self, base: str, quote: str) -> Info:
    symbol = f'{base}{quote}'
    r = await self.client.spot.exchange_info(symbol)
    if 'code' in r:
      raise ApiError(r)
    else:
      info = r[symbol]
      return Info(
        tick_size=Decimal(1) / Decimal(10 ** info['quotePrecision']),
        step_size=Decimal(info['baseSizePrecision']),
      )
