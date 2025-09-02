from dataclasses import dataclass
from decimal import Decimal
from trading_sdk.types import ApiError
from trading_sdk.spot.trading.cancel_order import CancelOrder as CancelOrderTDK
from trading_sdk.spot.user_data.query_order import OrderState as OrderStateTDK

from deribit.core import timestamp as ts
from deribit.sdk.util import SdkMixin, wrap_exceptions, parse_side, parse_status

@dataclass
class CancelOrder(CancelOrderTDK, SdkMixin):
  @wrap_exceptions
  async def cancel_order(self, base: str, quote: str, *, id: str) -> OrderStateTDK:
    r = await self.client.cancel(id)
    if not 'result' in r:
      raise ApiError(r['error'])
    else:
      o = r['result']
      return OrderStateTDK(
        id=id,
        price=Decimal(o['price']),
        qty=Decimal(o['amount']),
        filled_qty=Decimal(o['filled_amount']),
        side=parse_side(o['direction']),
        time=ts.parse(o['last_update_timestamp']),
        status=parse_status(o)
      )