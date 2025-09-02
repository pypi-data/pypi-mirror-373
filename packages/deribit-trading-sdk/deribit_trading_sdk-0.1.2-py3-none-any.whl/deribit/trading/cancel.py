from typing_extensions import TypedDict, NotRequired, Literal
from dataclasses import dataclass
from decimal import Decimal

from deribit.core import AuthedClientMixin, ApiResponse, validator
from .get_order_state import OrderStatus, validate_response

@dataclass(frozen=True)
class Cancel(AuthedClientMixin):
  async def cancel(
    self, orderId: str, /, *,
    validate: bool = True
  ) -> ApiResponse[OrderStatus]:
    """Cancel an existing order.
    
    - `orderId`: The ID of the order to cancel.
    - `validate`: Whether to validate the response against the expected schema.
    
    > [Deribit API docs](https://docs.deribit.com/#private-cancel)
    """
    params = {'order_id': orderId}
    r = await self.authed_request('/private/cancel', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
  