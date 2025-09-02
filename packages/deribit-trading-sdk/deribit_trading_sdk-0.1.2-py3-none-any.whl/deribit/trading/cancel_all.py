from dataclasses import dataclass

from deribit.core import AuthedClientMixin, ApiResponse, validator

validate_response = validator(int)

@dataclass(frozen=True)
class CancelAll(AuthedClientMixin):
  async def cancel_all(
    self, *, validate: bool = True,
    **kwargs,
  ) -> ApiResponse[int]:
    """Cancel all existing orders.
    
    - `validate`: Whether to validate the response against the expected schema.
    - `**kwargs`: Additional parameters to pass to the API. Read the [docs](https://docs.deribit.com/#private-cancel_all) for full details.

    Returns the number of cancelled orders.
    
    > [Deribit API docs](https://docs.deribit.com/#private-cancel_all)
    """
    params = kwargs
    r = await self.authed_request('/private/cancel_all', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
  