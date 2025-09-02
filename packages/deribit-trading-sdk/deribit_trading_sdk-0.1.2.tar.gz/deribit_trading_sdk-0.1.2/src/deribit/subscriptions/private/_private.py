from dataclasses import dataclass

from .user_orders import UserOrders
from .user_trades import UserTrades

@dataclass(frozen=True)
class PrivateSubscriptions(
  UserOrders,
  UserTrades,
):
  ...