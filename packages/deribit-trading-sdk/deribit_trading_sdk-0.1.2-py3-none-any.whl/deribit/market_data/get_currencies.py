from typing_extensions import Literal, TypedDict, NotRequired
from dataclasses import dataclass
from decimal import Decimal

from deribit.core import ClientMixin, ApiResponse, validator

class WithdrawalPriority(TypedDict):
  name: str
  value: Decimal

class Currency(TypedDict):
  apr: NotRequired[Decimal]
  coin_type: str
  currency: str
  currency_long: str
  fee_precision: int
  in_cross_collateral_pool: NotRequired[bool]
  min_confirmations: NotRequired[int]
  min_withdrawal_fee: NotRequired[Decimal]
  withdrawal_fee: NotRequired[Decimal]
  withdrawal_priorities: NotRequired[list[WithdrawalPriority]]

validate_response = validator(list[Currency])

@dataclass(frozen=True)
class GetCurrencies(ClientMixin):
  async def get_currencies(
    self, *, validate: bool = True
  ) -> ApiResponse[list[Currency]]:
    """Retrieves all cryptocurrencies supported by the API.
    
    - `validate`: Whether to validate the response against the expected schema.
    
    > [Deribit API docs](https://docs.deribit.com/#public-get_currencies)
    """
    r = await self.get('/public/get_currencies')
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
    