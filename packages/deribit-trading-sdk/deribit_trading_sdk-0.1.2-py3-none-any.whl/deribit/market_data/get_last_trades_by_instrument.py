from typing_extensions import Literal, TypedDict
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from deribit.core import ClientMixin, ApiResponse, validator, timestamp

class Trade(TypedDict):
  amount: Decimal
  direction: Literal['buy', 'sell']
  instrument_name: str
  price: Decimal
  timestamp: int
  trade_id: str
  trade_seq: int

class Response(TypedDict):
  has_more: bool
  trades: list[Trade]

validate_response = validator(Response)

@dataclass(frozen=True)
class GetLastTradesByInstrument(ClientMixin):
  async def get_last_trades_by_instrument(
    self, instrument_name: str, *,
    start_seq: int | None = None,
    end_seq: int | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    count: int | None = None,
    sorting: Literal['asc', 'desc', 'default'] | None = None,
    validate: bool = True
  ) -> ApiResponse[Response]:
    """Retrieves the order book for a given instrument.
    
    - `instrument_name`: The name of the instrument to get the order book for.
    - `depth`: The depth of the order book.
    - `validate`: Whether to validate the response against the expected schema.
    
    > [Deribit API docs](https://docs.deribit.com/#public-get_order_book)
    """
    params: dict = {'instrument_name': instrument_name}
    if start_seq is not None:
      params['start_seq'] = start_seq
    if end_seq is not None:
      params['end_seq'] = end_seq
    if start is not None:
      params['start_timestamp'] = timestamp.dump(start)
    if end is not None:
      params['end_timestamp'] = timestamp.dump(end)
    if count is not None:
      params['count'] = count
    if sorting is not None:
      params['sorting'] = sorting
    r = await self.get('/public/get_last_trades_by_instrument', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
    