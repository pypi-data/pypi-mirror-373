from typing_extensions import Literal
from dataclasses import dataclass

from deribit.core import AuthedClientMixin, ApiResponse, validator
from .get_order_state import OrderStatus

validate_response = validator(list[OrderStatus])

InstrumentKind = Literal['spot', 'future', 'option', 'future_combo', 'option_combo']
OrderType = Literal['all', 'limit', 'trigger_all', 'stop_all', 'stop_limit', 'stop_market', 'take_all', 'take_limit', 'take_market', 'trailing_all', 'trailing_stop']

@dataclass(frozen=True)
class GetOpenOrders(AuthedClientMixin):
  async def get_open_orders(
    self, *, kind: InstrumentKind | None = None,
    type: OrderType | None = None,
    validate: bool = True
  ) -> ApiResponse[list[OrderStatus]]:
    """Query all your open orders.
    
    - `kind`: Optional filter by instrument kind.
    - `type`: Optional filter by order type.
    - `validate`: Whether to validate the response against the expected schema.
    
    > [Deribit API docs](https://docs.deribit.com/#private-get_open_orders)
    """
    params = {}
    if kind is not None:
      params['kind'] = kind
    if type is not None:
      params['type'] = type
    r = await self.authed_request('/private/get_open_orders', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
  