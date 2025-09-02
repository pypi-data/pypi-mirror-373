from typing_extensions import AsyncIterable, Sequence
from dataclasses import dataclass
from datetime import datetime
from trading_sdk.types import ApiError
from trading_sdk.wallet.withdrawal_history import Withdrawal, WithdrawalHistory as WithdrawalHistoryTDK

from deribit.core import timestamp as ts
from deribit.account.get_transaction_log import GetTransactionLog
from deribit.market_data.get_currencies import GetCurrencies
from deribit.sdk.util import SdkMixin, wrap_exceptions

async def _transaction_log(client: GetTransactionLog, *, asset: str, start: datetime, end: datetime) -> AsyncIterable[Sequence[Withdrawal]]:
  async for txs in client.get_transaction_log_paged(asset, start=start, end=end, query='withdrawal'):
    yield [
      Withdrawal(
        id=str(tx['id']),
        amount=abs(tx['change']),
        asset=tx['currency'],
        address=tx['info']['addr'],
        time=ts.parse(tx['timestamp']),
        fee=Withdrawal.Fee(
          asset=tx['currency'],
          amount=tx['commission'],
        ),
      )
      for tx in txs if tx['type'] == 'withdrawal'
    ]

async def _currencies(client: GetCurrencies) -> list[str]:
  r = await client.get_currencies()
  if not 'result' in r:
    raise ApiError(r['error'])
  return [c['currency'] for c in r['result']]

@dataclass
class WithdrawalHistory(WithdrawalHistoryTDK, SdkMixin):
  @wrap_exceptions
  async def withdrawal_history(
    self, *, asset: str | None = None,
    start: datetime,
    end: datetime,
  ) -> AsyncIterable[Sequence[Withdrawal]]:
    if asset is not None:
      async for deposits in _transaction_log(self.client, asset=asset, start=start, end=end):
        yield deposits
    else:
      for asset in await _currencies(self.client):
        async for deposits in _transaction_log(self.client, asset=asset, start=start, end=end):
          yield deposits