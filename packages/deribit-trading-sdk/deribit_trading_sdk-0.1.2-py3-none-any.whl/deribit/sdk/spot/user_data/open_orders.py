from dataclasses import dataclass
from decimal import Decimal
from trading_sdk.spot.user_data.open_orders import OpenOrders as OpenOrdersTDK, OrderState

from deribit.core import timestamp as ts, ApiError
from deribit.sdk.util import SdkMixin, wrap_exceptions, parse_side, parse_status

@dataclass
class OpenOrders(OpenOrdersTDK, SdkMixin):
  @wrap_exceptions
  async def open_orders(self, base: str, quote: str) -> list[OrderState]:
    symbol = f'{base}_{quote}'
    r = await self.client.get_open_orders_by_instrument(symbol)
    if not 'result' in r:
      raise ApiError(r['error'])
    else:
      orders = r['result']
      return [
        OrderState(
          id=o['order_id'],
          price=Decimal(o['price']),
          qty=Decimal(o['amount']),
          filled_qty=Decimal(o['filled_amount']),
          time=ts.parse(o['creation_timestamp']),
          side=parse_side(o['direction']),
          status=parse_status(o)
        )
        for o in orders
      ]
