from dataclasses import dataclass

from deribit.core import AuthedClientMixin, ApiResponse
from .buy import TradeResponse, validate_response

@dataclass(frozen=True)
class EditByLabel(AuthedClientMixin):
  async def edit_by_label(
    self, instrument_name: str, *,
    label: str,
    amount: str | None = None,
    price: str | None = None,
    validate: bool = True,
    **kwargs,
  ) -> ApiResponse[TradeResponse]:
    """Edits an existing order by label. It works only when there is one open order with this label.
    
    - `instrument_name`: The name of the instrument being traded.
    - `label`: The label of the order to edit.
    - `amount`: The new amount for the order.
    - `price`: The new price for the order.
    - `validate`: Whether to validate the response against the expected schema.
    - `**kwargs`: Additional parameters to pass to the API. Read the [docs](https://docs.deribit.com/#private-edit) for full details.
    
    > [Deribit API docs](https://docs.deribit.com/#private-edit_by_label)
    """
    params = {
      'instrument_name': instrument_name,
      'label': label,
      **kwargs,
    }
    if amount is not None:
      params['amount'] = amount
    if price is not None:
      params['price'] = price
    r = await self.authed_request('/private/edit_by_label', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
  