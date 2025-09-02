from typing_extensions import Literal, overload, AsyncIterable
from dataclasses import dataclass

from deribit.core import AuthedSocketMixin, validator
from deribit.core.ws.client import SubscribeResponse
from deribit.trading.get_user_trades_by_currency import Trade

validate_message = validator(list[Trade])

InstrumentKind = Literal['spot', 'future', 'option', 'future_combo', 'option_combo', 'combo', 'any']

@dataclass(frozen=True)
class UserTrades(AuthedSocketMixin):
  @overload
  async def user_trades(
    self, *, instrument_name: str,
    interval: Literal['raw', '100ms', 'agg2'] = 'raw',
    validate: bool = True,
  ) -> tuple[SubscribeResponse, AsyncIterable[list[Trade]]]:
    """Subscribe to user trades in a given instrument.
    
    - `instrument_name`: The instrument name to subscribe to.
    - `interval`: The interval to subscribe to.
    - `validate`: Whether to validate the response against the expected schema.

    > [Deribit API docs](https://docs.deribit.com/#user-trades-instrument_name-interval)
    """
    ...
  @overload
  async def user_trades(
    self, *, kind: InstrumentKind = 'any',
    currency: str | Literal['any'] = 'any',
    interval: Literal['raw', '100ms', 'agg2'] = 'raw',
    validate: bool = True,
  ) -> tuple[SubscribeResponse, AsyncIterable[list[Trade]]]:
    """Subscribe to user trades in a given currency, optionally filtered by instrument kind.
    
    - `kind`: The instrument kind to subscribe to.
    - `currency`: The currency to subscribe to.
    - `interval`: The interval to subscribe to.
    - `validate`: Whether to validate the response against the expected schema.

    > [Deribit API docs](https://docs.deribit.com/#user-trades-kind-currency-interval)
    """
  async def user_trades(
    self, *, instrument_name: str | None = None,
    kind: InstrumentKind = 'any',
    currency: str | Literal['any'] = 'any',
    interval: Literal['raw', '100ms', 'agg2'] = 'raw',
    validate: bool = True,
  ):
    if instrument_name is not None:
      channel = f'user.trades.{instrument_name}.{interval}'
    else:
      channel = f'user.trades.{kind}.{currency}.{interval}'
    
    resp, raw_gen = await self.subscribe(channel)

    if self.validate(validate):
      async def gen():
        async for msg in raw_gen:
          yield validate_message(msg)
      return resp, gen()
    
    else:
      return resp, raw_gen
  