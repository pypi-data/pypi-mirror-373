from dataclasses import dataclass

from .buy import Buy
from .sell import Sell
from .edit import Edit
from .edit_by_label import EditByLabel
from .cancel import Cancel
from .cancel_all import CancelAll
from .cancel_all_by_currency import CancelAllByCurrency
from .cancel_all_by_currency_pair import CancelAllByCurrencyPair
from .cancel_all_by_instrument import CancelAllByInstrument
from .cancel_by_label import CancelByLabel
from .get_order_state import GetOrderState
from .get_order_state_by_label import GetOrderStateByLabel
from .get_open_orders import GetOpenOrders
from .get_open_orders_by_currency import GetOpenOrdersByCurrency
from .get_open_orders_by_instrument import GetOpenOrdersByInstrument
from .get_open_orders_by_label import GetOpenOrdersByLabel
from .get_user_trades_by_currency import GetUserTradesByCurrency
from .get_user_trades_by_instrument import GetUserTradesByInstrument
from .get_user_trades_by_order import GetUserTradesByOrder

@dataclass(frozen=True)
class Trading(
  Buy,
  Sell,
  Edit,
  EditByLabel,
  Cancel,
  CancelAll,
  CancelAllByCurrency,
  CancelAllByCurrencyPair,
  CancelAllByInstrument,
  CancelByLabel,
  GetOrderState,
  GetOrderStateByLabel,
  GetOpenOrders,
  GetOpenOrdersByCurrency,
  GetOpenOrdersByInstrument,
  GetOpenOrdersByLabel,
  GetUserTradesByCurrency,
  GetUserTradesByInstrument,
  GetUserTradesByOrder,
):
  ...