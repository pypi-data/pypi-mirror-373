from typing_extensions import TypedDict, Literal, NotRequired
from dataclasses import dataclass

from deribit.core import AuthedClientMixin, ApiResponse, validator
from .get_withdrawals import Withdrawal

validate_response = validator(Withdrawal)

Priority = Literal['insane', 'extreme_high', 'very_high', 'high', 'mid', 'low', 'very_low']

@dataclass(frozen=True)
class Withdraw(AuthedClientMixin):
  async def withdraw(
    self, *, currency: str, amount: str, address: str,
    priority: Priority | None = None,
    validate: bool = True,
  ) -> ApiResponse[Withdrawal]:
    """Submit a withdrawal request.
    
    - `currency`: The currency to withdraw.
    - `amount`: The amount to withdraw.
    - `address`: The address to withdraw to.
    - `priority`: The priority of the withdrawal (default: 'high').
    - `validate`: Whether to validate the response against the expected schema.

    > [Deribit API docs](https://docs.deribit.com/#private-withdraw)
    """
    params = {
      'currency': currency,
      'amount': amount,
      'address': address,
    }
    if priority is not None:
      params['priority'] = priority
    r = await self.authed_request('/private/withdraw', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
  