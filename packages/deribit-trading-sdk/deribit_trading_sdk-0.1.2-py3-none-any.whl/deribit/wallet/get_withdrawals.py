from typing_extensions import TypedDict, Literal, NotRequired, AsyncIterable
from dataclasses import dataclass
from decimal import Decimal

from deribit.core import AuthedClientMixin, ApiResponse, validator, ApiError

WithdrawalState = Literal['unconfirmed', 'confirmed', 'cancelled', 'completed', 'interrupted', 'rejected']

class Withdrawal(TypedDict):
  address: str
  amount: Decimal
  confirmed_timestamp: NotRequired[int]
  created_timestamp: int
  currency: str
  fee: Decimal
  """Fee amount in the withdrawn currency."""
  id: int
  priority: int
  state: WithdrawalState
  transaction_id: NotRequired[str]
  updated_timestamp: NotRequired[int]

class WithdrawalsResponse(TypedDict):
  count: int
  data: list[Withdrawal]

validate_response = validator(WithdrawalsResponse)

@dataclass(frozen=True)
class GetWithdrawals(AuthedClientMixin):
  async def get_withdrawals(
    self, currency: str, *,
    count: int | None = None,
    offset: int | None = None,
    validate: bool = True,
  ) -> ApiResponse[WithdrawalsResponse]:
    """Get your withdrawal history.
    
    - `currency`: The currency to get the withdrawals of.
    - `count`: Number of requested items (default: 10, max: 1000)
    - `offset`: The offset for pagination (default: 0)
    - `validate`: Whether to validate the response against the expected schema.

    > [Deribit API docs](https://docs.deribit.com/#private-get_withdrawals)
    """
    params: dict = {'currency': currency}
    if count is not None:
      params['count'] = count
    if offset is not None:
      params['offset'] = offset
    r = await self.authed_request('/private/get_withdrawals', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
  
  async def get_withdrawals_paged(
    self, currency: str, *,
    count: int | None = None,
    validate: bool = True,
  ) -> AsyncIterable[list[Withdrawal]]:
    """Get your withdrawal history, automatically paginating the results.
    
    - `currency`: The currency to get the withdrawals of.
    - `count`: Number of items per request (default: 10, max: 1000)
    - `validate`: Whether to validate the response against the expected schema.

    > [Deribit API docs](https://docs.deribit.com/#private-get_withdrawals)
    """
    offset = 0
    while True:
      r = await self.get_withdrawals(currency, count=count, offset=offset, validate=validate)
      if not 'result' in r:
        raise ApiError(r['error'])
      withdrawals = r['result']['data']
      yield withdrawals
      offset += len(withdrawals)
      if offset >= r['result']['count']:
        break