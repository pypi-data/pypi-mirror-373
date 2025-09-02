from typing_extensions import Literal
from dataclasses import dataclass

from deribit.core import AuthedClientMixin, ApiResponse, validator

validate_response = validator(int)

InstrumentKind = Literal['spot', 'future', 'option', 'future_combo', 'option_combo', 'combo', 'any']
OrderType = Literal['all', 'limit', 'trigger_all', 'stop', 'take', 'trailing_stop']

@dataclass(frozen=True)
class CancelAllByKindOrType(AuthedClientMixin):
  async def cancel_all_by_kind_or_type(
    self, currency: str | Literal['any'] | list[str], /, *,
    kind: InstrumentKind | None = None,
    type: OrderType | None = None,
    validate: bool = True,
    **kwargs,
  ) -> ApiResponse[int]:
    """Cancels all orders in currency(currencies), optionally filtered by instrument kind and/or order type.
    
    - `currency`: The currency symbol, list of currency symbols or 'any' for all
    - `kind`: Optional filter by instrument kind
    - `type`: Optional filter by order type
    - `validate`: Whether to validate the response against the expected schema.
    - `**kwargs`: Additional parameters to pass to the API. Read the [docs](https://docs.deribit.com/#private-cancel_all_by_kind_or_type) for full details.

    Returns the number of cancelled orders.
    
    > [Deribit API docs](https://docs.deribit.com/#private-cancel_all_by_kind_or_type)
    """
    params = {'currency': currency, **kwargs}
    if kind is not None:
      params['kind'] = kind
    if type is not None:
      params['type'] = type
    r = await self.authed_request('/private/cancel_all_by_kind_or_type', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
  