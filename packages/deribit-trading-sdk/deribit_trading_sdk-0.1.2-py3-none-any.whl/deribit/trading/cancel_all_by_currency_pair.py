from dataclasses import dataclass

from deribit.core import AuthedClientMixin, ApiResponse, validator
from .cancel_all_by_currency import InstrumentKind, OrderType

validate_response = validator(int)

@dataclass(frozen=True)
class CancelAllByCurrencyPair(AuthedClientMixin):
  async def cancel_all_by_currency_pair(
    self, currency_pair: str, /, *,
    kind: InstrumentKind | None = None,
    type: OrderType | None = None,
    validate: bool = True,
    **kwargs,
  ) -> ApiResponse[int]:
    """Cancel all existing orders by currency pair, optionally filtered by instrument kind and/or order type.
    
    - `currency`: The currency pair symbol to cancel orders for (e.g. 'btc_usd')
    - `kind`: Optional filter by instrument kind
    - `type`: Optional filter by order type
    - `validate`: Whether to validate the response against the expected schema.
    - `**kwargs`: Additional parameters to pass to the API. Read the [docs](https://docs.deribit.com/#private-cancel_all_by_currency_pair) for full details.

    Returns the number of cancelled orders.
    
    > [Deribit API docs](https://docs.deribit.com/#private-cancel_all_by_currency_pair)
    """
    params = {'currency_pair': currency_pair, **kwargs}
    if kind is not None:
      params['kind'] = kind
    if type is not None:
      params['type'] = type
    r = await self.authed_request('/private/cancel_all_by_currency_pair', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
  