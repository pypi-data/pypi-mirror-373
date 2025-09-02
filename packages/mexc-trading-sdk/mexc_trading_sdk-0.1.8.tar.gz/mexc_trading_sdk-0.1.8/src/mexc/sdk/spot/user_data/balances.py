from dataclasses import dataclass
from decimal import Decimal
from trading_sdk.types import ApiError
from trading_sdk.spot.user_data.balances import Balances as BalancesTDK, Balance
from mexc.sdk.util import SdkMixin, wrap_exceptions

@dataclass
class Balances(BalancesTDK, SdkMixin):
  @wrap_exceptions
  async def balances(self, *currencies: str) -> dict[str, Balance]:
    r = await self.client.spot.account()
    if 'code' in r:
      raise ApiError(r)
    else:
      return {
        b['asset']: Balance(
          free=Decimal(b['free']),
          locked=Decimal(b['locked'])
        )
        for b in r['balances']
      }
    
  async def balance(self, currency: str) -> Balance:
    return await super().balance(currency)
