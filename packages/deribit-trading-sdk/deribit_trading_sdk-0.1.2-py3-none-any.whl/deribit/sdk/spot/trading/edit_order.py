from dataclasses import dataclass
from trading_sdk.spot.trading.edit_order import EditOrder as EditOrderTDK
from trading_sdk.types import Num, fmt_num, ApiError

from deribit.sdk.util import SdkMixin, wrap_exceptions

@dataclass
class EditOrder(EditOrderTDK, SdkMixin):
  @wrap_exceptions
  async def edit_order(self, base: str, quote: str, *, id: str, qty: Num) -> str:
    r = await self.client.edit(id, amount=fmt_num(qty))
    if not 'result' in r:
      raise ApiError(r['error'])
    else:
      return r['result']['order']['order_id']