from dataclasses import dataclass
from decimal import Decimal
from trading_sdk.spot.market_streams.depth import Depth as DepthTDK, Book

from deribit.core import ApiError
from deribit.sdk.util import SdkMixin, wrap_exceptions
@dataclass
class Depth(DepthTDK, SdkMixin):
  @wrap_exceptions
  async def depth(self, base: str, quote: str, *, limit: int | None = None):
    symbol = f'{base}_{quote}'
    r, stream = await self.client.subscriptions.depth(symbol, depth=limit or 20)
    if not 'result' in r:
      raise ApiError(r['error'])
    elif not r['result']:
      raise ApiError('Unable to subscribe to channel', r)
    
    async for book in stream:
      yield Book(
        bids=[Book.Entry(price=Decimal(e.price), qty=Decimal(e.amount)) for e in book['bids']],
        asks=[Book.Entry(price=Decimal(e.price), qty=Decimal(e.amount)) for e in book['asks']]
      )
