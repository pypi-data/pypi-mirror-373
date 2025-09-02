from typing_extensions import Literal, TypedDict, NotRequired
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from deribit.core import AuthedClientMixin, ApiResponse, validator, timestamp as ts

InstrumentKind = Literal['spot', 'future', 'option', 'future_combo', 'option_combo', 'combo', 'any']

class Trade(TypedDict):
  trade_id: str
  fee: NotRequired[Decimal]
  fee_currency: NotRequired[str]
  api: NotRequired[bool]
  order_id: str
  liquidity: Literal['M', 'T']
  post_only: NotRequired[bool]
  direction: Literal['buy', 'sell']
  mmp: NotRequired[bool]
  index_price: NotRequired[Decimal]
  label: NotRequired[str]
  price: Decimal
  order_type: Literal['limit', 'market', 'liquidation']
  timestamp: int
  amount: Decimal
  trade_seq: int
  instrument_name: str

class TradesResponse(TypedDict):
  has_more: bool
  trades: list[Trade]

validate_response = validator(TradesResponse)

@dataclass(frozen=True)
class GetUserTradesByCurrency(AuthedClientMixin):
  async def get_user_trades_by_currency(
    self, currency: str, *,
    kind: InstrumentKind | None = None,
    start_id: str | None = None,
    end_id: str | None = None,
    count: int | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    sorting: Literal['asc', 'desc', 'default'] | None = None,
    historical: bool | None = None,
    subaccount_id: int | None = None,
    validate: bool = True
  ) -> ApiResponse[TradesResponse]:
    """Query all your trades in a given currency.
    
    - `currency`: The currency to get the trades of.
    - `kind`: Optional filter by instrument kind.
    - `start_id`: The ID of the first trade to be returned. Number for BTC trades, or hyphen name in ex. "ETH-15" # "ETH_USDC-16"
    - `end_id`: The ID of the last trade to be returned. Number for BTC trades, or hyphen name in ex. "ETH-15" # "ETH_USDC-16" 
    - `count`: Number of requested items, default - 10, maximum - 1000
    - `start`: The earliest timestamp to return result from
    - `end`: The most recent timestamp to return result from. Only one of start/end is truly required
    - `sorting`: Direction of results sorting ('asc', 'desc', or 'default' for database order)
    - `historical`: If true, fetches historical records (available after delay). If false (default), returns recent records only (orders for 30min, trades for 24h)
    - `subaccount_id`: The user id for the subaccount
    - `validate`: Whether to validate the response against the expected schema.
    
    > [Deribit API docs](https://docs.deribit.com/#private-get_user_trades_by_currency)
    """
    params: dict = {'currency': currency}
    if kind is not None:
      params['kind'] = kind
    if start_id is not None:
      params['start_id'] = start_id
    if end_id is not None:
      params['end_id'] = end_id
    if count is not None:
      params['count'] = count
    if start is not None:
      params['start_timestampt'] = ts.dump(start)
    if end is not None:
      params['end_timestamp'] = ts.dump(end)
    if sorting is not None:
      params['sorting'] = sorting
    if historical is not None:
      params['historical'] = historical
    if subaccount_id is not None:
      params['subaccount_id'] = subaccount_id
    r = await self.authed_request('/private/get_user_trades_by_currency', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
  