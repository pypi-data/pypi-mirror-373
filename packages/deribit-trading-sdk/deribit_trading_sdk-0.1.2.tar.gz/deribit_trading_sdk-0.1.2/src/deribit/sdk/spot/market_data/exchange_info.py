from dataclasses import dataclass
from trading_sdk.types import ApiError
from trading_sdk.spot.market_data.exchange_info import ExchangeInfo as ExchangeInfoTDK, Info
from deribit.sdk.util import SdkMixin, wrap_exceptions

@dataclass
class ExchangeInfo(ExchangeInfoTDK, SdkMixin):
  @wrap_exceptions
  async def exchange_info(self, base: str, quote: str) -> Info:
    symbol = f'{base}_{quote}'
    r = await self.client.get_instrument(symbol)
    if not 'result' in r:
      raise ApiError(r['error'])
    else:
      info = r['result']
      return Info(
        tick_size=info['tick_size'],
        step_size=info['contract_size'],
        min_qty_=info['min_trade_amount']
      )
