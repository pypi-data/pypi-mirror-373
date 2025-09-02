from typing_extensions import TypedDict
from dataclasses import dataclass

from deribit.core import AuthedClientMixin, ApiResponse, validator
from .get_account_summary import AccountSummary

class SummariesResponse(TypedDict):
  summaries: list[AccountSummary]

validate_response = validator(SummariesResponse)

@dataclass(frozen=True)
class GetAccountSummaries(AuthedClientMixin):
  async def get_account_summaries(
    self, *,
    subaccount_id: str | None = None,
    validate: bool = True
  ) -> ApiResponse[SummariesResponse]:
    """Places a buy order for an instrument.
    
    - `instrument_name`: The name of the instrument to get the order book for.
    - `order`: The order to place.
    - `validate`: Whether to validate the response against the expected schema.
    
    > [Deribit API docs](https://docs.deribit.com/#private-get_account_summaries)
    """
    params = {'subaccount_id': subaccount_id} if subaccount_id is not None else None
    r = await self.authed_request('/private/get_account_summaries', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
    