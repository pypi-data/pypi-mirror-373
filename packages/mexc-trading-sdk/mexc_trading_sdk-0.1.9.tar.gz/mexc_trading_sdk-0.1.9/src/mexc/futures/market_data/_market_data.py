from dataclasses import dataclass
from .candles import Candles
from .funding_rate import FundingRate
from .contract_info import ContractInfo

@dataclass
class MarketData(
  FundingRate,
  Candles,
  ContractInfo,
):
  ...