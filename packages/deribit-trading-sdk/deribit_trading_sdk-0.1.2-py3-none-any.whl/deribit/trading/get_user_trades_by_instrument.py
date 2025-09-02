from typing_extensions import Literal, AsyncIterable
from dataclasses import dataclass
from datetime import datetime

from deribit.core import AuthedClientMixin, ApiResponse, timestamp as ts, ApiError
from .get_user_trades_by_currency import TradesResponse, validate_response, Trade

@dataclass(frozen=True)
class GetUserTradesByInstrument(AuthedClientMixin):
  async def get_user_trades_by_instrument(
    self, instrument_name: str, *,
    start_seq: int | None = None,
    end_seq: int | None = None,
    count: int | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    historical: bool | None = None,
    sorting: Literal['asc', 'desc', 'default'] | None = None,
    validate: bool = True
  ) -> ApiResponse[TradesResponse]:
    """Query all your trades in a given instrument.
    
    - `instrument_name`: Instrument name
    - `start_seq`: The sequence number of the first trade to be returned
    - `end_seq`: The sequence number of the last trade to be returned
    - `count`: Number of items requested (default: 10, max: 1000)
    - `start`: The earliest timestamp to return result from
    - `end`: The most recent timestamp to return result from. Only one of start/end is truly required
    - `historical`: If true, fetches historical records (available after delay). If false (default), returns recent records only (orders for 30min, trades for 24h)
    - `sorting`: Direction of results sorting ('asc', 'desc', or 'default' for database order)
    - `validate`: Whether to validate the response against the expected schema.
    
    > [Deribit API docs](https://docs.deribit.com/#private-get_user_trades_by_instrument)
    """
    params: dict = {'instrument_name': instrument_name}
    if start_seq is not None:
      params['start_seq'] = start_seq
    if end_seq is not None:
      params['end_seq'] = end_seq
    if count is not None:
      params['count'] = count
    if start is not None:
      params['start_timestamp'] = ts.dump(start)
    if end is not None:
      params['end_timestamp'] = ts.dump(end)
    if sorting is not None:
      params['sorting'] = sorting
    if historical is not None:
      params['historical'] = historical
    r = await self.authed_request('/private/get_user_trades_by_instrument', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
  
  async def get_user_trades_by_instrument_paged(
    self, instrument_name: str, *,
    start_seq: int | None = None,
    end_seq: int | None = None,
    count: int | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    historical: bool | None = None,
    validate: bool = True
  ) -> AsyncIterable[list[Trade]]:
    """Query all your trades in a given instrument, automatically paginating the results.
    
    - `instrument_name`: Instrument name
    - `start_seq`: The sequence number of the first trade to be returned
    - `end_seq`: The sequence number of the last trade to be returned
    - `count`: Number of items per request (default: 10, max: 1000)
    - `start`: The earliest timestamp to return result from
    - `end`: The most recent timestamp to return result from. Only one of start/end is truly required
    - `historical`: If true, fetches historical records (available after delay). If false (default), returns recent records only (orders for 30min, trades for 24h)
    - `validate`: Whether to validate the response against the expected schema.
    
    > [Deribit API docs](https://docs.deribit.com/#private-get_user_trades_by_instrument)
    """
    last_seq = None
    if count is not None:
      count = max(count, 2) # required for pagination
    while True:
      r = await self.get_user_trades_by_instrument(
        instrument_name, sorting='desc',
        start_seq=start_seq, end_seq=end_seq, count=count,
        start=start, end=end, historical=historical, validate=validate
      )
      if not 'result' in r:
        raise ApiError(r['error'])
      else:
        trades = r['result']['trades']
        yield [t for t in trades if t['trade_seq'] != last_seq]
        if not r['result']['has_more']:
          break
        last_seq = end_seq = r['result']['trades'][-1]['trade_seq']
    

