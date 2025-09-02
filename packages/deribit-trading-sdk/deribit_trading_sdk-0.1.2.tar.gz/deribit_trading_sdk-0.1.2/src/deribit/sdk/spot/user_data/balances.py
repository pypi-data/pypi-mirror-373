from dataclasses import dataclass
from decimal import Decimal
from trading_sdk.types import ApiError
from trading_sdk.spot.user_data.balances import Balances as BalancesTDK, Balance

from deribit.account.get_account_summary import AccountSummary
from deribit.sdk.util import SdkMixin, wrap_exceptions

def parse_summary(summary: AccountSummary) -> Balance:
  free = summary['available_funds']
  locked = summary['equity'] - free
  return Balance(free=Decimal(free), locked=locked)

@dataclass
class Balances(BalancesTDK, SdkMixin):
  @wrap_exceptions
  async def balances(self, *currencies: str) -> dict[str, Balance]:
    r = await self.client.get_account_summaries()
    if not 'result' in r:
      raise ApiError(r['error'])
    else:
      return {
        s['currency']: parse_summary(s)	
        for s in r['result']['summaries']
      }
    
  async def balance(self, currency: str) -> Balance:
    r = await self.client.get_account_summary(currency, subaccount_id=self.subaccount_id)
    if not 'result' in r:
      raise ApiError(r['error'])
    else:
      return parse_summary(r['result'])
