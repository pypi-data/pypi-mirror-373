from dataclasses import dataclass
from decimal import Decimal
from trading_sdk.types import ApiError
from trading_sdk.spot.market_data.depth import Depth as DepthTDK, Book
from deribit.sdk.util import SdkMixin, wrap_exceptions

@dataclass
class Depth(DepthTDK, SdkMixin):
  @wrap_exceptions
  async def depth(self, base: str, quote: str, *, limit: int | None = None) -> Book:
    symbol = f'{base}_{quote}'
    r = await self.client.get_order_book(symbol, depth=limit)
    if not 'result' in r:
      raise ApiError(r['error'])
    else:
      return Book(
        asks=[Book.Entry(
          price=Decimal(p.price),
          qty=Decimal(p.amount)
        ) for p in r['result']['asks']],
        bids=[Book.Entry(
          price=Decimal(p.price),
          qty=Decimal(p.amount)
        ) for p in r['result']['bids']],
      )
