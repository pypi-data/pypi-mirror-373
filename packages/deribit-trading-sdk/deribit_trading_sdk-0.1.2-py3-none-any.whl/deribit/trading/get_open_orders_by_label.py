from dataclasses import dataclass

from deribit.core import AuthedClientMixin, ApiResponse
from .get_open_orders import OrderStatus, validate_response

@dataclass(frozen=True)
class GetOpenOrdersByLabel(AuthedClientMixin):
  async def get_open_orders_by_label(
    self, *, currency: str, label: str,
    validate: bool = True
  ) -> ApiResponse[list[OrderStatus]]:
    """Query all your open orders in a given currency, optionally filtered by label.
    
    - `currency`: The currency to get the open orders of.
    - `label`: The label to filter the orders by.
    - `validate`: Whether to validate the response against the expected schema.
    
    > [Deribit API docs](https://docs.deribit.com/#private-get_open_orders_by_label)
    """
    params = {'currency': currency, 'label': label}
    r = await self.authed_request('/private/get_open_orders_by_label', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
  