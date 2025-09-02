from typing_extensions import Literal
from dataclasses import dataclass
from functools import cached_property

from . import MarketData, Trading, Account, Wallet, Subscriptions

@dataclass(frozen=True)
class Deribit(
  MarketData,
  Trading,
  Account,
  Wallet,
):
  @cached_property
  def subscriptions(self) -> Subscriptions:
    from deribit.core import AuthedSocketClient, UserError
    if isinstance(self.client, AuthedSocketClient):
      return Subscriptions(self.client)
    else:
      raise UserError('Use WebSockets to access subscriptions')

  