from dataclasses import dataclass

from deribit.core import AuthedClientMixin, ApiResponse
from .get_open_orders import OrderStatus, validate_response, OrderType

@dataclass(frozen=True)
class GetOpenOrdersByInstrument(AuthedClientMixin):
  async def get_open_orders_by_instrument(
    self, instrument_name: str, *,
    type: OrderType | None = None,
    validate: bool = True
  ) -> ApiResponse[list[OrderStatus]]:
    """Query all your open orders in a given instrument.
    
    - `instrument_name`: The instrument to get the open orders of.
    - `type`: Optional filter by order type.
    - `validate`: Whether to validate the response against the expected schema.
    
    > [Deribit API docs](https://docs.deribit.com/#private-get_open_orders_by_instrument)
    """
    params = {'instrument_name': instrument_name}
    if type is not None:
      params['type'] = type
    r = await self.authed_request('/private/get_open_orders_by_instrument', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
  