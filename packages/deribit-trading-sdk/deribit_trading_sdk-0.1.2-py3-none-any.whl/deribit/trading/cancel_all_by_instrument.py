from dataclasses import dataclass

from deribit.core import AuthedClientMixin, ApiResponse, validator
from .cancel_all_by_currency import OrderType

validate_response = validator(int)

@dataclass(frozen=True)
class CancelAllByInstrument(AuthedClientMixin):
  async def cancel_all_by_instrument(
    self, instrument_name: str, /, *,
    type: OrderType | None = None,
    validate: bool = True,
    **kwargs,
  ) -> ApiResponse[int]:
    """Cancel all existing orders by instrument, optionally filtered by order type.
    
    - `instrument_name`: The instrument to cancel orders for (e.g. 'BTC_USDC', 'BTC-25MAR23-420-C')
    - `type`: Optional filter by order type
    - `validate`: Whether to validate the response against the expected schema.
    - `**kwargs`: Additional parameters to pass to the API. Read the [docs](https://docs.deribit.com/#private-cancel_all_by_instrument) for full details.

    Returns the number of cancelled orders.
    
    > [Deribit API docs](https://docs.deribit.com/#private-cancel_all_by_instrument)
    """
    params = {'instrument_name': instrument_name, **kwargs}
    if type is not None:
      params['type'] = type
    r = await self.authed_request('/private/cancel_all_by_instrument', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
  