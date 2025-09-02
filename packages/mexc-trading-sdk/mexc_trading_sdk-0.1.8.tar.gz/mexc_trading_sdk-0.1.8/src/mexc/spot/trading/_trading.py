from dataclasses import dataclass
from .place_order import PlaceOrder
from .cancel_order import CancelOrder
from .cancel_all_orders import CancelAllOrders

@dataclass
class Trading(
  PlaceOrder,
  CancelOrder,
  CancelAllOrders,
):
  ...