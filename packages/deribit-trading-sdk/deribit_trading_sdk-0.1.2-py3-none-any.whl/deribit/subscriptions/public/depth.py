from typing_extensions import Literal, TypedDict, AsyncIterable
from dataclasses import dataclass

from deribit.core import SocketMixin, ApiResponse, validator
from deribit.core.ws.client import SubscribeResponse
from deribit.market_data.get_order_book import BookEntry

class OrderBook(TypedDict):
  asks: list[BookEntry]
  bids: list[BookEntry]
  change_id: int
  instrument_name: str
  timestamp: int

validate_message = validator(OrderBook)

@dataclass(frozen=True)
class Depth(SocketMixin):
  async def depth(
    self, instrument_name: str, *,
    group: int | Literal['none'] = 'none',
    depth: int = 20,
    interval: Literal['100ms', 'agg2'] = '100ms',
    validate: bool = True,
  ) -> tuple[SubscribeResponse, AsyncIterable[OrderBook]]:
    """Subscribes to the order book for a certain instrument.
    
    - `instrument_name`: The instrument name to subscribe to.
    - `group`: Price grouping by rounding. See the [docs](https://docs.deribit.com/#book-instrument_name-group-depth-interval) for details.
    - `depth`: Number of price levels to include (1, 10, or 20).
    - `interval`: Frequency of notifications.
    - `validate`: Whether to validate the response against the expected schema.

    > [Deribit API docs](https://docs.deribit.com/#book-instrument_name-group-depth-interval)
    """
    resp, raw_gen = await self.subscribe(f'book.{instrument_name}.{group}.{depth}.{interval}')

    if self.validate(validate):
      async def gen():
        async for msg in raw_gen:
          yield validate_message(msg)
      return resp, gen()
    
    else:
      return resp, raw_gen
  