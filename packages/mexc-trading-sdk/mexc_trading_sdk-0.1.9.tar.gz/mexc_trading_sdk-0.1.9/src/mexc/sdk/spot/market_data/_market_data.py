from dataclasses import dataclass
from .depth import Depth
from .exchange_info import ExchangeInfo

@dataclass
class MarketData(Depth, ExchangeInfo):
  ...