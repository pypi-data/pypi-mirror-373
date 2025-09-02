from dataclasses import dataclass
from enum import Enum
from mexc.spot.streams.core import UserStreamsMixin

class TradeType(Enum):
  BUY = 1
  SELL = 2

@dataclass
class Trade:
  symbol: str
  price: str
  quantity: str
  amount: str
  tradeType: TradeType
  tradeId: str
  orderId: str
  feeAmount: str
  feeCurrency: str
  time: int

  @classmethod
  def from_proto(cls, proto):
    deals = proto.privateDeals
    return cls(
      symbol=proto.symbol,
      price=deals.price,
      quantity=deals.quantity,
      amount=deals.amount,
      tradeType=TradeType(deals.tradeType),
      tradeId=deals.tradeId,
      orderId=deals.orderId,
      feeAmount=deals.feeAmount,
      feeCurrency=deals.feeCurrency,
      time=deals.time
    )

@dataclass
class MyTrades(UserStreamsMixin):
  async def my_trades(self):
    """Subscribe to your trades.
    
    > [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#spot-account-deals)
    """
    async for msg in self.authed_subscribe('spot@private.deals.v3.api.pb'):
      yield Trade.from_proto(msg)