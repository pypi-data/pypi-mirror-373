from typing_extensions import Literal
from dataclasses import dataclass
from mexc.spot.streams.core import StreamsMixin

Interval = Literal['Min1', 'Min5', 'Min15', 'Min30', 'Min60', 'Hour4', 'Hour8', 'Day1', 'Week1', 'Month1']

def channel_name(symbol: str, interval: Interval):
  return f'spot@public.kline.v3.api.pb@{symbol}@{interval}'

@dataclass
class Candle:
  interval: str
  windowStart: int
  openingPrice: str
  closingPrice: str
  highestPrice: str
  lowestPrice: str
  volume: str
  amount: str
  windowEnd: int

  @classmethod
  def from_proto(cls, proto):
    return cls(
      interval=proto.interval,
      windowStart=proto.windowStart,
      openingPrice=proto.openingPrice,
      closingPrice=proto.closingPrice,
      highestPrice=proto.highestPrice,
      lowestPrice=proto.lowestPrice,
      volume=proto.volume,
      amount=proto.amount,
      windowEnd=proto.windowEnd
    )
  
@dataclass
class Candles(StreamsMixin):
  async def candles(self, symbol: str, interval: Interval):
    """Subscribe to klines (candles) for a given symbol.
    
    - `symbol`: The symbol being traded, e.g. `BTCUSDT`.
    - `interval`: The interval of the klines (default: 1m).

    > [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#k-line-streams)
    """
    async for proto in self.subscribe(channel_name(symbol, interval)):
      yield Candle.from_proto(proto.publicSpotKline)
