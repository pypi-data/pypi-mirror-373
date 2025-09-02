from typing_extensions import TypedDict, Literal, NotRequired, AsyncIterable
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime

from deribit.core import AuthedClientMixin, ApiResponse, validator, timestamp as ts, ApiError

class TransferInfo(TypedDict):
  transaction: str
  addr: str

class BaseTransfer(TypedDict):
  timestamp: int
  id: int
  currency: str
  commission: Decimal
  info: TransferInfo
  change: Decimal

class Withdrawal(BaseTransfer):
  type: Literal['withdrawal']

class Deposit(BaseTransfer):
  type: Literal['deposit']

class Other(BaseTransfer):
  type: Literal['trade', 'maker', 'taker', 'open', 'close', 'liquidation', 'buy', 'sell', 'delivery', 'settlement', 'transfer', 'option', 'future', 'correction', 'block_trade', 'swap']


Transaction = Deposit | Withdrawal | Other

class TransactionLog(TypedDict):
  continuation: NotRequired[int|None]
  logs: list[Transaction]

validate_response = validator(TransactionLog)

Query = Literal['deposit', 'withdrawal']

@dataclass(frozen=True)
class GetTransactionLog(AuthedClientMixin):
  async def get_transaction_log(
    self, currency: str, *,
    start: datetime, end: datetime,
    query: Query | str | None = None,
    subaccount_id: str | None = None,
    count: int | None = None,
    continuation: int | None = None,
    validate: bool = True
  ) -> ApiResponse[TransactionLog]:
    """Retrieve user transactions by currency.
    
    - `currency`: The currency to get the transaction log for.
    - `start`: The start timestamp to get the transaction log for.
    - `end`: The end timestamp to get the transaction log for.
    - `query`: Query to filter results. See the [docs](https://docs.deribit.com/#private-get_transaction_log) for details.
    - `subaccount_id`: The subaccount id to get the transaction log for.
    - `count`: Number of requested items (default: 100, max: 250).
    - `continuation`: The continuation token to get the next page of results.
    - `validate`: Whether to validate the response against the expected schema.

    > [Deribit API docs](https://docs.deribit.com/#private-get_transaction_log)
    """
    params: dict = {'currency': currency}
    if subaccount_id is not None:
      params['subaccount_id'] = subaccount_id
    if query is not None:
      params['query'] = query
    if start is not None:
      params['start_timestamp'] = ts.dump(start)
    if end is not None:
      params['end_timestamp'] = ts.dump(end)
    if count is not None:
      params['count'] = count
    if continuation is not None:
      params['continuation'] = continuation
    r = await self.authed_request('/private/get_transaction_log', params)
    if self.validate(validate) and 'result' in r:
      r['result'] = validate_response(r['result'])
    return r
    
  async def get_transaction_log_paged(
    self, currency: str, *,
    start: datetime, end: datetime,
    query: Query | str | None = None,
    subaccount_id: str | None = None,
    count: int | None = None,
    continuation: int | None = None,
    validate: bool = True
  ) -> AsyncIterable[list[Transaction]]:
    """Retrieve user transactions by currency, automatically paginating the results.
    
    - `currency`: The currency to get the transaction log for.
    - `start`: The start timestamp to get the transaction log for.
    - `end`: The end timestamp to get the transaction log for.
    - `query`: Query to filter results. See the [docs](https://docs.deribit.com/#private-get_transaction_log) for details.
    - `subaccount_id`: The subaccount id to get the transaction log for.
    - `count`: Number of requested items per request (default: 100, max: 250).
    - `validate`: Whether to validate the response against the expected schema.

    **Raises `ApiError` if receiving an error response.**

    > [Deribit API docs](https://docs.deribit.com/#private-get_transaction_log)
    """
    continuation = None
    while True:
      r = await self.get_transaction_log(currency, start=start, end=end, query=query, subaccount_id=subaccount_id, count=count, continuation=continuation, validate=validate)
      if not 'result' in r:
        raise ApiError(r['error'])
      yield r['result']['logs']
      continuation = r['result'].get('continuation')
      if continuation is None:
        break