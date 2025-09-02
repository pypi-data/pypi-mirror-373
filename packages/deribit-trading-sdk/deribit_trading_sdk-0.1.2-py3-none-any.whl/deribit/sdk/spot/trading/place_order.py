from dataclasses import dataclass
from trading_sdk.types import fmt_num, ApiError
from trading_sdk.spot.trading.place_order import PlaceOrder as PlaceOrderTDK, Order as OrderTDK

from deribit.trading.buy import Order, LimitOrder, MarketOrder
from deribit.sdk.util import SdkMixin, wrap_exceptions

def parse_order(order: OrderTDK) -> Order:
  if order['type'] == 'LIMIT':
    return LimitOrder(
      type='limit',
      price=fmt_num(order['price']),
      amount=fmt_num(order['qty'])
    )
  elif order['type'] == 'MARKET':
    return MarketOrder(
      type='market',
      amount=fmt_num(order['qty'])
    )

@dataclass
class PlaceOrder(PlaceOrderTDK, SdkMixin):
  @wrap_exceptions
  async def place_order(self, base: str, quote: str, order: OrderTDK) -> str:
    symbol = f'{base}_{quote}'
    fn = self.client.buy if order['side'] == 'BUY' else self.client.sell
    r = await fn(symbol, parse_order(order))
    if not 'result' in r:
      raise ApiError(r['error'])
    else:
      return r['result']['order']['order_id']