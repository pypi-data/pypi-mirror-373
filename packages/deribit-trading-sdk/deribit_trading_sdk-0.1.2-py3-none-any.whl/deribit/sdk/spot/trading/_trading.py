from dataclasses import dataclass
from trading_sdk.spot.trading import PlaceOrders
from .place_order import PlaceOrder
from .edit_order import EditOrder
from .cancel_order import CancelOrder

@dataclass
class Trading(PlaceOrder, PlaceOrders, EditOrder, CancelOrder):
  ...