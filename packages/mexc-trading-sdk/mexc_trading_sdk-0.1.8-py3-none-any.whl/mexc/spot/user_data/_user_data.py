from dataclasses import dataclass
from .my_trades import MyTrades
from .account import Account
from .query_order import QueryOrder
from .open_orders import OpenOrders
from .my_orders import MyOrders

@dataclass
class UserData(
  MyTrades,
  Account,
  QueryOrder,
  OpenOrders,
  MyOrders,
):
  ...