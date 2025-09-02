from dataclasses import dataclass, field
from decimal import Decimal
from collections import defaultdict
import asyncio
from trading_sdk.spot.user_streams.my_trades import MyTrades as MyTradesTDK, Trade

from deribit.core import timestamp as ts, ApiError
from deribit.sdk.util import SdkMixin, wrap_exceptions

@dataclass
class MyTrades(MyTradesTDK, SdkMixin):
  _queues: defaultdict[str, asyncio.Queue[Trade]] = field(default_factory=lambda: defaultdict(asyncio.Queue))
  _listener: asyncio.Task | None = None

  async def __aexit__(self, exc_type, exc_value, traceback):
    if self._listener is not None:
      self._listener.cancel()
      self._listener = None
    await super().__aexit__(exc_type, exc_value, traceback)

  @wrap_exceptions
  async def my_trades(self, base: str, quote: str):
    symbol = f'{base}_{quote}'
    if self._listener is None:
      async def listener():
        r, stream = await self.client.subscriptions.user_trades()
        if not 'result' in r:
          raise ApiError(r['error'])
        elif not r['result']:
          raise ApiError('Unable to subscribe to channel', r)
        async for trades in stream:
          for trade in trades:
            print('Trade:', trade)
            t = Trade(
              id=trade['trade_id'],
              price=Decimal(trade['price']),
              qty=Decimal(trade['amount']),
              time=ts.parse(trade['timestamp']),
              side='BUY' if trade['direction'] == 'buy' else 'SELL',
              fee=Trade.Fee(
                amount=Decimal(trade['fee']),
                asset=trade['fee_currency'],
              ) if ('fee' in trade and 'fee_currency' in trade) else None
            )
            self._queues[trade['instrument_name']].put_nowait(t)
      self._listener = asyncio.create_task(listener())

    while True:
      # propagate exceptions raised in the listener
      t = asyncio.create_task(self._queues[symbol].get())
      await asyncio.wait([t, self._listener], return_when='FIRST_COMPLETED')
      if self._listener.done() and (exc := self._listener.exception()) is not None:
        raise exc
      yield await t