from dataclasses import dataclass
from decimal import Decimal
from trading_sdk.types import ApiError
from trading_sdk.spot.user_data.query_order import QueryOrder as QueryOrderTDK, OrderState

from deribit.core import timestamp as ts
from deribit.sdk.util import SdkMixin, wrap_exceptions, parse_side, parse_status

@dataclass
class QueryOrder(QueryOrderTDK, SdkMixin):
  @wrap_exceptions
  async def query_order(self, base: str, quote: str, *, id: str) -> OrderState:
    r = await self.client.get_order_state(id)
    if not 'result' in r:
      raise ApiError(r)
    else:
      o = r['result']
      return OrderState(
        id=o['order_id'],
        price=Decimal(o['price']),
        qty=Decimal(o['amount']),
        filled_qty=Decimal(o['filled_amount']),
        time=ts.parse(o['creation_timestamp']),
        side=parse_side(o['direction']),
        status=parse_status(o),
      )
