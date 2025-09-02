from typing_extensions import Literal
from dataclasses import dataclass

from deribit.core import AuthedClientMixin, ApiResponse, validator

validate_response = validator(int)

InstrumentKind = Literal['spot', 'future', 'option', 'future_combo', 'option_combo', 'combo', 'any']
OrderType = Literal['all', 'limit', 'trigger_all', 'stop', 'take', 'trailing_stop']

@dataclass(frozen=True)
class CancelAllByCurrency(AuthedClientMixin):
  async def cancel_all_by_currency(
    self, currency: str, /, *,
    kind: InstrumentKind | None = None,
    type: OrderType | None = None,
    validate: bool = True,
    **kwargs,
  ) -> ApiResponse[int]:
    """Cancel all existing orders by currency, optionally filtered by instrument kind and/or order type.
    
    - `currency`: The currency symbol to cancel orders for (e.g. 'BTC')
    - `kind`: Optional filter by instrument kind
    - `type`: Optional filter by order type
    - `validate`: Whether to validate the response against the expected schema.
    - `**kwargs`: Additional parameters to pass to the API. Read the [docs](https://docs.deribit.com/#private-cancel_all_by_currency) for full details.

    Returns the number of cancelled orders.
    
    > [Deribit API docs](https://docs.deribit.com/#private-cancel_all_by_currency)
    """
    params = {'currency': currency, **kwargs}
    if kind is not None:
      params['kind'] = kind
    if type is not None:
      params['type'] = type
    r = await self.authed_request('/private/cancel_all_by_currency', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
  