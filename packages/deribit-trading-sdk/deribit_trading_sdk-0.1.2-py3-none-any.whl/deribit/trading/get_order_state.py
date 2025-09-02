from typing_extensions import TypedDict, NotRequired, Literal
from dataclasses import dataclass
from decimal import Decimal

from deribit.core import AuthedClientMixin, ApiResponse, validator
from .buy import OrderState

Direction = Literal['buy', 'sell']

class OrderStatus(TypedDict):
  order_id: str
  filled_amount: Decimal
  oto_order_ids: NotRequired[list[str]]
  api: NotRequired[bool]
  web: NotRequired[bool]
  average_price: NotRequired[Decimal]
  post_only: NotRequired[bool]
  direction: Direction
  replaced: NotRequired[bool]
  last_update_timestamp: int
  creation_timestamp: int
  order_state: OrderState
  price: Decimal
  amount: Decimal

validate_response = validator(OrderStatus)

@dataclass(frozen=True)
class GetOrderState(AuthedClientMixin):
  async def get_order_state(
    self, orderId: str, /, *,
    validate: bool = True
  ) -> ApiResponse[OrderStatus]:
    """Get the state of an existing order.
    
    - `orderId`: The ID of the order to get the state of.
    - `validate`: Whether to validate the response against the expected schema.
    
    > [Deribit API docs](https://docs.deribit.com/#private-get_order_state)
    """
    params = {'order_id': orderId}
    r = await self.authed_request('/private/get_order_state', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
  