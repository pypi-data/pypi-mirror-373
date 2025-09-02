from dataclasses import dataclass

from deribit.core import AuthedClientMixin, ApiResponse
from .buy import Order, TradeResponse, validate_response

@dataclass(frozen=True)
class Sell(AuthedClientMixin):
  async def sell(
    self, instrument_name: str, order: Order, *,
    validate: bool = True
  ) -> ApiResponse[TradeResponse]:
    """Places a sell order for an instrument.
    
    - `instrument_name`: The name of the instrument to get the order book for.
    - `order`: The order to place.
    - `validate`: Whether to validate the response against the expected schema.
    
    > [Deribit API docs](https://docs.deribit.com/#private-sell)
    """
    params = {**order, 'instrument_name': instrument_name}
    r = await self.authed_request('/private/sell', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
    