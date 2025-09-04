from dataclasses import dataclass, field
from .market_data import MarketData
from .trading import Trading
from .user_data import UserData
from .market_streams import MarketStreams
from .user_streams import UserStreams

@dataclass
class Spot(MarketData, Trading, UserData):
  market_streams: MarketStreams = field(init=False)
  user_streams: UserStreams = field(init=False)
  
  def __post_init__(self):
    self.market_streams = MarketStreams(client=self.client)
    self.user_streams = UserStreams(client=self.client)
    

