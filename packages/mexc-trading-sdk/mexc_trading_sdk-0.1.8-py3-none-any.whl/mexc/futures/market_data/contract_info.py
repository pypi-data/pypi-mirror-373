from typing_extensions import TypedDict
from decimal import Decimal
from enum import Enum
from mexc.core import validator
from mexc.futures.core import FuturesMixin, FuturesResponse

class OpenType(Enum):
  isolated = 1
  cross = 2
  both = 3

class Info(TypedDict):
  symbol: str
  displayNameEn: str
  positionOpenType: OpenType
  baseCoin: str
  quoteCoin: str
  settleCoin: str
  contractSize: Decimal
  minLeverage: int
  maxLeverage: int
  priceScale: int
  volScale: int
  amountScale: int
  priceUnit: Decimal
  volUnit: Decimal
  minVol: Decimal
  maxVol: Decimal
  bidLimitPriceRate: Decimal
  askLimitPriceRate: Decimal
  takerFeeRate: Decimal
  makerFeeRate: Decimal
  maintenanceMarginRate: Decimal
  initialMarginRate: Decimal

Response: type[FuturesResponse[Info]] = FuturesResponse[Info] # type: ignore
validate_response = validator(Response)

class ContractInfo(FuturesMixin):
  async def contract_info(self, symbol: str, *, validate: bool | None = None) -> FuturesResponse[Info]:
    """Get information about a futures contract.
    
    - `symbol`: The symbol to retrieve information for, e.g. `BTC_USDT`.
    - `validate`: Whether to validate the response against the expected schema (default: True).

    > [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#get-the-contract-information)
    """
    r = await self.request('GET', '/api/v1/contract/detail', params={'symbol': symbol})
    return validate_response(r.text) if self.validate(validate) else r.json()