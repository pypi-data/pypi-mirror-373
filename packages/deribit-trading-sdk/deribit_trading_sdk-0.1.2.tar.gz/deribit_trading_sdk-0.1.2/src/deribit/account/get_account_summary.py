from typing_extensions import TypedDict, NotRequired
from dataclasses import dataclass
from decimal import Decimal

from deribit.core import AuthedClientMixin, ApiResponse, validator

class AccountSummary(TypedDict):
  available_funds: Decimal
  deposit_address: NotRequired[str]
  available_withdrawal_funds: Decimal
  spot_reserve: Decimal
  additional_reserve: Decimal
  cross_collateral_enabled: bool
  options_value: Decimal
  currency: str
  balance: Decimal
  estimated_liquidation_ratio: Decimal
  equity: Decimal

validate_response = validator(AccountSummary)

@dataclass(frozen=True)
class GetAccountSummary(AuthedClientMixin):
  async def get_account_summary(
    self, currency: str, *,
    subaccount_id: str | None = None,
    validate: bool = True
  ) -> ApiResponse[AccountSummary]:
    """Places a buy order for an instrument.
    
    - `instrument_name`: The name of the instrument to get the order book for.
    - `order`: The order to place.
    - `validate`: Whether to validate the response against the expected schema.
    
    > [Deribit API docs](https://docs.deribit.com/#private-get_account_summary)
    """
    params = {'currency': currency}
    if subaccount_id is not None:
      params['subaccount_id'] = subaccount_id
    r = await self.authed_request('/private/get_account_summary', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
    