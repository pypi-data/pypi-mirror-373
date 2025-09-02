from dataclasses import dataclass

from deribit.core import AuthedClientMixin, ApiResponse, validator
from .get_order_state import OrderStatus

validate_response = validator(list[OrderStatus])

@dataclass(frozen=True)
class GetOrderStateByLabel(AuthedClientMixin):
  async def get_order_state_by_label(
    self, *, currency: str, label: str,
    validate: bool = True
  ) -> ApiResponse[list[OrderStatus]]:
    """Get the state of existing orders in a given currency, optionally filtered by label.
    
    - `currency`: The currency to get the order states of.
    - `label`: The label to filter the orders by.
    - `validate`: Whether to validate the response against the expected schema.
    
    > [Deribit API docs](https://docs.deribit.com/#private-get_order_state_by_label)
    """
    params = {'currency': currency, 'label': label}
    r = await self.authed_request('/private/get_order_state_by_label', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
  