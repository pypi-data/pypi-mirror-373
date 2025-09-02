from typing_extensions import TypedDict
from dataclasses import dataclass
from decimal import Decimal

from deribit.core import ClientMixin, ApiResponse, validator

class ContractSize(TypedDict):
  contract_size: Decimal

validate_response = validator(ContractSize)

@dataclass(frozen=True)
class GetContractSize(ClientMixin):
  async def get_contract_size(
    self, instrument_name: str, *,
    validate: bool = True
  ) -> ApiResponse[ContractSize]:
    """Get the contract size for a given instrument.
    
    - `instrument_name`: The name of the instrument to get the contract size for.
    - `validate`: Whether to validate the response against the expected schema.
    
    > [Deribit API docs](https://docs.deribit.com/#public-get_contract_size)
    """
    r = await self.get('/public/get_contract_size', {
      'instrument_name': instrument_name,
    })
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
    