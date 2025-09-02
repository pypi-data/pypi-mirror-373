from typing_extensions import TypedDict
from dataclasses import dataclass

from deribit.core import AuthedClientMixin, ApiResponse, validator

class AddressResponse(TypedDict):
  address: str
  creation_timestamp: int
  currency: str

validate_response = validator(AddressResponse)

@dataclass(frozen=True)
class GetCurrentDepositAddress(AuthedClientMixin):
  async def get_current_deposit_address(
    self, currency: str, *,
    validate: bool = True,
  ) -> ApiResponse[AddressResponse]:
    """Retrieve the current deposit address for the given currency.
    
    - `currency`: The currency to get the current deposit address of.
    - `validate`: Whether to validate the response against the expected schema.

    > [Deribit API docs](https://docs.deribit.com/#private-get_current_deposit_address)
    """
    params = {'currency': currency}
    r = await self.authed_request('/private/get_current_deposit_address', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
  