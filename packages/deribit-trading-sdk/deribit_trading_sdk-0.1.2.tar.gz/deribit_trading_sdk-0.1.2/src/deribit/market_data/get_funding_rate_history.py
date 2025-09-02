from typing_extensions import TypedDict
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime

from deribit.core import ClientMixin, ApiResponse, validator, timestamp as ts

class FundingResponse(TypedDict):
  index_price: Decimal
  interest_1h: Decimal
  interest_8h: Decimal
  prev_index_price: Decimal
  timestamp: int

validate_response = validator(list[FundingResponse])

@dataclass(frozen=True)
class GetFundingRateHistory(ClientMixin):
  async def get_funding_rate_history(
    self, instrument_name: str, *,
    start: datetime, end: datetime,
    validate: bool = True
  ) -> ApiResponse[list[FundingResponse]]:
    """Retrieves hourly historical interest rate for a perpetual instrument.
    
    - `instrument_name`: The name of the instrument to get the funding rate history for.
    - `start`: The start timestamp to get the funding rate history for.
    - `end`: The end timestamp to get the funding rate history for.
    - `validate`: Whether to validate the response against the expected schema.
    
    > [Deribit API docs](https://docs.deribit.com/#public-get_funding_rate_history)
    """
    params: dict = {
      'instrument_name': instrument_name,
      'start_timestamp': ts.dump(start),
      'end_timestamp': ts.dump(end),
    }
    r = await self.get('/public/get_funding_rate_history', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
    