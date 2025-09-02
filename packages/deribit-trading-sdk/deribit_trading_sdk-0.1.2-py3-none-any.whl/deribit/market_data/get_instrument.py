from typing_extensions import TypedDict, Literal, NotRequired
from dataclasses import dataclass
from decimal import Decimal

from deribit.core import ClientMixin, ApiResponse, validator

InstrumentType = Literal['linear', 'reversed']
InstrumentKind = Literal['future', 'option', 'spot', 'future_combo', 'option_combo']

class BaseInstrument(TypedDict):
  base_currency: str
  block_trade_commission: NotRequired[Decimal]
  block_trade_min_trade_amount: NotRequired[Decimal]
  block_trade_tick_size: NotRequired[Decimal]
  contract_size: Decimal
  counter_currency: str
  creation_timestamp: int
  expiration_timestamp: int
  instrument_id: int
  instrument_name: str
  instrument_type: InstrumentType
  is_active: bool
  maker_commission: Decimal
  min_trade_amount: Decimal
  price_index: str
  quote_currency: str
  rfq: bool
  taker_commission: Decimal
  tick_size: Decimal

class Derivative(BaseInstrument):
  settlement_currency: str
  settlement_period: str

class Future(Derivative):
  kind: Literal['future']
  max_leverage: int
  max_liquidation_commission: Decimal

OptionType = Literal['oops']

class Option(Derivative):
  kind: Literal['option']
  option_type: OptionType
  strike: Decimal

Instrument = Future | Option | BaseInstrument

InstrumentT: type[Instrument] = Instrument # type: ignore
validate_response = validator(InstrumentT)

@dataclass(frozen=True)
class GetInstrument(ClientMixin):
  async def get_instrument(
    self, instrument_name: str, *,
    validate: bool = True
  ) -> ApiResponse[Instrument]:
    """Get information about an instrument.
    
    - `instrument_name`: The name of the instrument to get information for.
    - `validate`: Whether to validate the response against the expected schema.
    
    > [Deribit API docs](https://docs.deribit.com/#public-get_instrument)
    """
    r = await self.get('/public/get_instrument', {
      'instrument_name': instrument_name,
    })
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
    