from dataclasses import dataclass

from deribit.core import AuthedClientMixin, ApiResponse
from .buy import TradeResponse, validate_response

@dataclass(frozen=True)
class Edit(AuthedClientMixin):
  async def edit(
    self, orderId: str, /, *,
    amount: str | None = None,
    price: str | None = None,
    validate: bool = True,
    **kwargs,
  ) -> ApiResponse[TradeResponse]:
    """Edits an existing order.
    
    - `orderId`: The ID of the order to edit.
    - `amount`: The new amount for the order.
    - `price`: The new price for the order.
    - `validate`: Whether to validate the response against the expected schema.
    - `**kwargs`: Additional parameters to pass to the API. Read the [docs](https://docs.deribit.com/#private-edit) for full details.
    
    > [Deribit API docs](https://docs.deribit.com/#private-edit)
    """
    params = {
      'order_id': orderId,
      **kwargs,
    }
    if amount is not None:
      params['amount'] = amount
    if price is not None:
      params['price'] = price
    r = await self.authed_request('/private/edit', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
  