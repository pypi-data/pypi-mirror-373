from typing_extensions import Literal, TypedDict, NotRequired, Sequence
from dataclasses import dataclass
from decimal import Decimal

from deribit.core import AuthedClientMixin, ApiResponse, validator

TimeInForce = Literal['good_til_cancelled', 'good_til_day', 'fill_or_kill', 'immediate_or_cancel']

class BaseOrder(TypedDict):
  amount: str | int | Decimal
  time_in_force: NotRequired[TimeInForce]
  """
  - `good_til_cancelled` - unfilled order remains in order book until cancelled
  - `good_til_day` -  unfilled order remains in order book till the end of the trading session
  - `fill_or_kill` -  execute a transaction immediately and completely or not at all
  - `immediate_or_cancel` - execute a transaction immediately, and any portion of the order that cannot be immediately filled is cancelled
  """
  post_only: NotRequired[bool]
  """If true, the order is considered post-only. If the new price would cause the order to be filled immediately (as taker), the price will be changed to be just below the spread.

  Only valid in combination with `time_in_force='good_til_cancelled'`
  """
  reject_post_only: NotRequired[bool]
  """	If an order is considered post-only and this field is set to true then the order is put to the order book unmodified or the request is rejected.

  Only valid in combination with `post_only` set to true
  """
  reduce_only: NotRequired[bool]
  """If true, the order is considered reduce-only which is intended to only reduce a current position"""
  otoco_config: NotRequired[Sequence['Order']]
  label: NotRequired[str]
  """User-defined label for the order (maximum 64 characters)"""
  display_amount: NotRequired[str|Decimal]
  """	Initial display amount for iceberg order. Has to be at least 100 times minimum amount for instrument and ratio of hidden part vs visible part has to be less than 100 as well."""

class LimitOrder(BaseOrder):
  type: Literal['limit']
  price: str | int | Decimal

class MarketOrder(BaseOrder):
  type: Literal['market', 'market_limit']

class BaseTriggerOrder(BaseOrder):
  trigger: Literal['index_price', 'mark_price', 'last_price']

class ConditionalOrder(BaseTriggerOrder):
  type: Literal['stop_limit', 'take_limit', 'spot_market', 'take_market']
  trigger_price: str | int | Decimal

class TrailingStopOrder(BaseTriggerOrder):
  type: Literal['trailing_stop']
  trigger_offset: str | int | Decimal
  """The maximum deviation from the price peak beyond which the order will be triggered"""

Order = LimitOrder | MarketOrder | ConditionalOrder | TrailingStopOrder

OrderState = Literal['open', 'filled', 'cancelled', 'rejected', 'untriggered']

class OrderResponse(TypedDict):
  order_id: str
  filled_amount: Decimal
  order_state: OrderState

class Trade(TypedDict):
  trade_id: str
  fee_currency: str
  fee: Decimal
  timestamp: int
  amount: Decimal
  trade_seq: int

class TradeResponse(TypedDict):
  order: OrderResponse
  trades: list[Trade]

validate_response = validator(TradeResponse)

@dataclass(frozen=True)
class Buy(AuthedClientMixin):
  async def buy(
    self, instrument_name: str, order: Order, *,
    validate: bool = True
  ) -> ApiResponse[TradeResponse]:
    """Places a buy order for an instrument.
    
    - `instrument_name`: The name of the instrument to get the order book for.
    - `order`: The order to place.
    - `validate`: Whether to validate the response against the expected schema.
    
    > [Deribit API docs](https://docs.deribit.com/#private-buy)
    """
    params = {**order, 'instrument_name': instrument_name}
    r = await self.authed_request('/private/buy', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
  