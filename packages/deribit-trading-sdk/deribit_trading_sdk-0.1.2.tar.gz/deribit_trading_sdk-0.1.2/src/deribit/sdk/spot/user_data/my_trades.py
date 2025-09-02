from typing_extensions import Sequence, AsyncIterable
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from trading_sdk.types import ApiError
from trading_sdk.spot.user_data.my_trades import MyTrades as MyTradesTDK, Trade

from deribit.core import timestamp as ts
from deribit.sdk.util import SdkMixin, wrap_exceptions

@dataclass
class MyTrades(MyTradesTDK, SdkMixin):
  @wrap_exceptions
  async def my_trades(
    self, base: str, quote: str, *,
    start: datetime | None = None, end: datetime | None = None
  ) -> AsyncIterable[Sequence[Trade]]:
    symbol = f'{base}_{quote}'
    async for trades in self.client.get_user_trades_by_instrument_paged(symbol, start=start, end=end, historical=True, count=20):
      yield [
        Trade(
          id=t['trade_id'],
          price=t['price'],
          qty=t['amount'],
          time=ts.parse(t['timestamp']),
          side='SELL' if t['direction'] == 'sell' else 'BUY',
          maker=t['liquidity'] == 'M',
          fee=Trade.Fee(
            amount=t['fee'],
            asset=t['fee_currency']
          ) if ('fee' in t and 'fee_currency' in t) else None
        )
        for t in trades
      ]