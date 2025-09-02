from typing_extensions import Literal, overload, AsyncIterable
from dataclasses import dataclass

from deribit.core import SocketMixin, validator
from deribit.core.ws.client import SubscribeResponse
from deribit.market_data.get_last_trades_by_instrument import Trade

validate_message = validator(list[Trade])

InstrumentKind = Literal['spot', 'future', 'option', 'future_combo', 'option_combo']

@dataclass(frozen=True)
class Trades(SocketMixin):
  @overload
  async def trades(
    self, *, instrument_name: str,
    interval: Literal['raw', '100ms', 'agg2'] = 'raw',
    validate: bool = True,
  ) -> tuple[SubscribeResponse, AsyncIterable[list[Trade]]]:
    """Subscribe to trades in a given instrument.
    
    - `instrument_name`: The instrument name to subscribe to.
    - `interval`: The interval to subscribe to.
    - `validate`: Whether to validate the response against the expected schema.

    > [Deribit API docs](https://docs.deribit.com/#trades-instrument_name-interval)
    """
    ...
  @overload
  async def trades(
    self, *, kind: InstrumentKind,
    currency: str | Literal['any'] = 'any',
    interval: Literal['raw', '100ms', 'agg2'] = 'raw',
    validate: bool = True,
  ) -> tuple[SubscribeResponse, AsyncIterable[list[Trade]]]:
    """Subscribe to trades in a given currency, optionally filtered by instrument kind.
    
    - `kind`: The instrument kind to subscribe to.
    - `currency`: The currency to subscribe to.
    - `interval`: The interval to subscribe to.
    - `validate`: Whether to validate the response against the expected schema.

    > [Deribit API docs](https://docs.deribit.com/#trades-instrument_name-interval)
    """
  async def trades(
    self, *, instrument_name: str | None = None,
    kind: InstrumentKind | None = None,
    currency: str | Literal['any'] = 'any',
    interval: Literal['raw', '100ms', 'agg2'] = 'raw',
    validate: bool = True,
  ):
    if instrument_name is not None:
      channel = f'trades.{instrument_name}.{interval}'
    elif kind is not None:
      channel = f'trades.{kind}.{currency}.{interval}'
    else:
      raise ValueError('Must provide either instrument_name or kind')
    
    resp, raw_gen = await self.subscribe(channel)

    if self.validate(validate):
      async def gen():
        async for msg in raw_gen:
          yield validate_message(msg)
      return resp, gen()
    
    else:
      return resp, raw_gen
  