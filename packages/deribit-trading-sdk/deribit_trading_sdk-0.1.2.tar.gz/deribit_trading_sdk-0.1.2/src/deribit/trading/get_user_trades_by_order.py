from typing_extensions import Literal
from dataclasses import dataclass

from deribit.core import AuthedClientMixin, ApiResponse
from .get_user_trades_by_currency import TradesResponse, validate_response

@dataclass(frozen=True)
class GetUserTradesByOrder(AuthedClientMixin):
  async def get_user_trades_by_order(
    self, order_id: str, *,
    historical: bool | None = None,
    sorting: Literal['asc', 'desc', 'default'] | None = None,
    validate: bool = True
  ) -> ApiResponse[TradesResponse]:
    """Query all your trades in a given order.
    
    - `order_id`: Order ID
    - `historical`: If true, fetches historical records (available after delay). If false (default), returns recent records only (orders for 30min, trades for 24h)
    - `sorting`: Direction of results sorting ('asc', 'desc', or 'default' for database order)
    - `validate`: Whether to validate the response against the expected schema.
    
    > [Deribit API docs](https://docs.deribit.com/#private-get_user_trades_by_order)
    """
    params: dict = {'order_id': order_id}
    if sorting is not None:
      params['sorting'] = sorting
    if historical is not None:
      params['historical'] = historical
    r = await self.authed_request('/private/get_user_trades_by_order', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
  