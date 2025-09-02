from typing_extensions import Literal
from dataclasses import dataclass, field
from deribit import Deribit as Client
from .spot import Spot
from .wallet import Wallet
from .futures import Futures

@dataclass
class Deribit:
  spot: Spot
  wallet: Wallet
  futures: Futures
  client: Client = field(kw_only=True)

  @classmethod
  def of(cls, client: Client, *, validate: bool = True, subaccount_id: str | None = None):
    return cls(
      spot=Spot(client=client, validate=validate, subaccount_id=subaccount_id),
      wallet=Wallet(client=client, validate=validate, subaccount_id=subaccount_id),
      futures=Futures(client=client, validate=validate, subaccount_id=subaccount_id),
      client=client,
    )

  @classmethod
  def new(
    cls, client_id: str | None = None, client_secret: str | None = None, *,
    mainnet: bool = True, protocol: Literal['http', 'ws'] = 'ws',
    validate: bool = True, subaccount_id: str | None = None,
  ):
    client = Client.new(client_id, client_secret, validate=validate, mainnet=mainnet, protocol=protocol)
    return cls.of(client, validate=validate, subaccount_id=subaccount_id)
  
  async def __aenter__(self):
    await self.client.__aenter__()
    return self
  
  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)