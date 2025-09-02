from dataclasses import dataclass

from deribit.core import AuthedClientMixin, ApiResponse
from .get_open_orders import OrderStatus, validate_response, InstrumentKind, OrderType

@dataclass(frozen=True)
class GetOpenOrdersByCurrency(AuthedClientMixin):
  async def get_open_orders_by_currency(
    self, currency: str, *,
    kind: InstrumentKind | None = None,
    type: OrderType | None = None,
    validate: bool = True
  ) -> ApiResponse[list[OrderStatus]]:
    """Query all your open orders in a given currency.
    
    - `currency`: The currency to get the open orders of.
    - `kind`: Optional filter by instrument kind.
    - `type`: Optional filter by order type.
    - `validate`: Whether to validate the response against the expected schema.
    
    > [Deribit API docs](https://docs.deribit.com/#private-get_open_orders_by_currency)
    """
    params = {'currency': currency}
    if kind is not None:
      params['kind'] = kind
    if type is not None:
      params['type'] = type
    r = await self.authed_request('/private/get_open_orders_by_currency', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
  