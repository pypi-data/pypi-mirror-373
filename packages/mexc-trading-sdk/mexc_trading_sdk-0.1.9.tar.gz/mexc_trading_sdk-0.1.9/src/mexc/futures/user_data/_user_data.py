from dataclasses import dataclass
from .funding_rate_history import FundingRateHistory
from .my_trades import MyTrades

@dataclass
class UserData(FundingRateHistory, MyTrades):
  ...