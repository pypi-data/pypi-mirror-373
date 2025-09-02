from typing_extensions import Literal
from dataclasses import dataclass

from deribit.core import ClientMixin, ApiResponse, validator
from .get_instrument import InstrumentKind, Instrument

Currency = Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR', 'any']

validate_response = validator(list[Instrument])

@dataclass(frozen=True)
class GetInstruments(ClientMixin):
  async def get_instruments(
    self, currency: Currency, *,
    kind: InstrumentKind | None = None,
    expired: bool | None = None,
    validate: bool = True
  ) -> ApiResponse[list[Instrument]]:
    """Retrieves available trading instruments. This method can be used to see which instruments are available for trading, or which instruments have recently expired.
    
    - `instrument_name`: The name of the instrument to get information for.
    - `validate`: Whether to validate the response against the expected schema.
    
    > [Deribit API docs](https://docs.deribit.com/#public-get_instrument)
    """
    params: dict = {'currency': currency}
    if kind is not None:
      params['kind'] = kind
    if expired is not None:
      params['expired'] = expired
    r = await self.get('/public/get_instruments', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
    