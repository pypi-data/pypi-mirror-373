from typing_extensions import Literal
from dataclasses import dataclass
from trading_sdk.types import NetworkError, ValidationError, ApiError, Network, is_network

from deribit import Deribit, core

def wrap_exceptions(fn):
  import inspect
  from functools import wraps

  if inspect.iscoroutinefunction(fn):
    @wraps(fn)
    async def wrapper(*args, **kwargs): # type: ignore
      try:
        return await fn(*args, **kwargs)
      except core.NetworkError as e:
        raise NetworkError from e
      except core.ValidationError as e:
        raise ValidationError from e
      
  elif inspect.isgeneratorfunction(fn):
    @wraps(fn)
    async def wrapper(*args, **kwargs): # type: ignore
      try:
        return await fn(*args, **kwargs)
      except core.NetworkError as e:
        raise NetworkError from e
      except core.ValidationError as e:
        raise ValidationError from e
      
  else:
    @wraps(fn)
    def wrapper(*args, **kwargs):
      try:
        return fn(*args, **kwargs)
      except core.NetworkError as e:
        raise NetworkError from e
      except core.ValidationError as e:
        raise ValidationError from e
  return wrapper

@dataclass
class SdkMixin:
  client: Deribit
  subaccount_id: str | None = None
  validate: bool = True

  @classmethod
  def new(
    cls, client_id: str | None = None, client_secret: str | None = None, *,
    mainnet: bool = True, protocol: Literal['ws', 'http'] = 'ws',
    subaccount_id: str | None = None, validate: bool = True
  ):
    client = Deribit.new(client_id=client_id, client_secret=client_secret, mainnet=mainnet, protocol=protocol)
    return cls(client=client, subaccount_id=subaccount_id, validate=validate)

  async def __aenter__(self):
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)

def parse_network(network: str) -> Network:
  if is_network(network):
    return network
  else:
    raise ApiError(f'Invalid network: {network}')
  
from trading_sdk.spot.user_data.query_order import Side as SideTDK, OrderStatus as OrderStatusTDK
from deribit.trading.get_order_state import OrderStatus, Direction

def parse_side(side: Direction) -> SideTDK:
  return 'BUY' if side == 'buy' else 'SELL'

def parse_status(order: OrderStatus) -> OrderStatusTDK:
  match order['order_state']:
    case 'open' if order['filled_amount'] > 0:
      return 'PARTIALLY_FILLED'
    case 'open':
      return 'NEW'
    case 'rejected':
      return 'CANCELED'
    case 'cancelled' if order['filled_amount'] > 0:
      return 'PARTIALLY_CANCELED'
    case 'cancelled':
      return 'CANCELED'
    case 'filled':
      return 'FILLED'
    case 'untriggered':
      return 'UNTRIGGERED'