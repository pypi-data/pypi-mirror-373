from typing_extensions import Literal
from dataclasses import dataclass

from deribit.core import AuthedClientMixin, ApiResponse, validator

validate_response = validator(int)

@dataclass(frozen=True)
class CancelByLabel(AuthedClientMixin):
  async def cancel_by_label(
    self, label: str, /, *,
    currency: str | None = None,
    validate: bool = True,
    **kwargs,
  ) -> ApiResponse[int]:
    """Cancel all existing orders by label.
    
    - `label`: The label to cancel orders for.
    - `currency`: Optional filter by currency (e.g. 'BTC').
    - `validate`: Whether to validate the response against the expected schema.
    - `**kwargs`: Additional parameters to pass to the API. Read the [docs](https://docs.deribit.com/#private-cancel_by_label) for full details.

    Returns the number of cancelled orders.
    
    > [Deribit API docs](https://docs.deribit.com/#private-cancel_by_label)
    """
    params = {'label': label, **kwargs}
    if currency is not None:
      params['currency'] = currency
    r = await self.authed_request('/private/cancel_by_label', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
  