from typing_extensions import Literal, TypedDict, NamedTuple
from decimal import Decimal
from dataclasses import dataclass

from deribit.core import ClientMixin, ApiResponse, validator

class BookEntry(NamedTuple):
  price: Decimal
  amount: Decimal

State = Literal['open', 'closed']

class OrderBook(TypedDict):
  asks: list[BookEntry]
  bids: list[BookEntry]
  index_price: Decimal
  state: State

validate_response = validator(OrderBook)

@dataclass(frozen=True)
class GetOrderBook(ClientMixin):
  async def get_order_book(
    self, instrument_name: str, *,
    depth: int | None = None,
    validate: bool = True
  ) -> ApiResponse[OrderBook]:
    """Retrieves the order book for a given instrument.
    
    - `instrument_name`: The name of the instrument to get the order book for.
    - `depth`: The depth of the order book.
    - `validate`: Whether to validate the response against the expected schema.
    
    > [Deribit API docs](https://docs.deribit.com/#public-get_order_book)
    """
    params: dict = {'instrument_name': instrument_name}
    if depth is not None:
      params['depth'] = depth
    r = await self.get('/public/get_order_book', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
    