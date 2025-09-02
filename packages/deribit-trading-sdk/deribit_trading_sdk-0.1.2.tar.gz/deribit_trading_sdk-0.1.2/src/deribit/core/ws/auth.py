from typing_extensions import TypedDict, AsyncIterable
from dataclasses import dataclass, field
import asyncio
from uuid import uuid4
import hmac
import hashlib

from deribit.core import timestamp, AuthedClient, AuthedClientMixin, ApiResponse, validator, AuthError, DERIBIT_MAINNET, DERIBIT_TESTNET
from .client import SocketClient, SocketMixin, SubscribeResponse, validate_subscribe_response
from .base import Context, logger

def sign(data: bytes, *, secret: str):
  return hmac.new(secret.encode(), data, hashlib.sha256).hexdigest()

def signature_data(*, ts: int, nonce: str):
  return f'{ts}\n{nonce}\n'.encode()

class AuthData(TypedDict):
  access_token: str
  expires_in: int
  refresh_token: str
  scope: str

@dataclass
class AuthContext(Context):
  auth_data: AuthData
  refresher: asyncio.Task

AuthResponseT: type[AuthData] = AuthData # type: ignore
validate_auth_response = validator(AuthResponseT)

@dataclass
class AuthedSocketClient(SocketClient, AuthedClient):
  client_id: str
  client_secret: str = field(repr=False)

  @classmethod
  def new(cls, *, mainnet: bool = True, validate: bool = True):
    import os
    client_id = os.environ['DERIBIT_CLIENT_ID'] if mainnet else os.environ['TEST_DERIBIT_CLIENT_ID']
    client_secret = os.environ['DERIBIT_CLIENT_SECRET'] if mainnet else os.environ['TEST_DERIBIT_CLIENT_SECRET']
    return cls(
      client_id=client_id,
      client_secret=client_secret,
      validate=validate,
      domain=DERIBIT_MAINNET if mainnet else DERIBIT_TESTNET,
    )

  @property
  async def ctx(self) -> AuthContext:
    if (ctx := getattr(self, '_ctx', None)) is None:
      ctx = await self.open()
      self._ctx = ctx
    return ctx

  async def login(self):
    ts = timestamp.now()
    nonce = uuid4().hex
    signature = sign(signature_data(ts=ts, nonce=nonce), secret=self.client_secret)
    r = await self.request('/public/auth', {
      'grant_type': 'client_signature',
      'signature': signature,
      'timestamp': ts,
      'nonce': nonce,
      'client_id': self.client_id,
    })
    if 'error' in r:
      raise AuthError(r)
    else:
      resp: AuthData = validate_auth_response(r['result']) if self.validate else r['result']
      return resp

  async def open(self):
    ctx = await super().open()
    auth_data = await self.login()
    logger.info('Loging successful, token expires in %s seconds', auth_data['expires_in'])

    async def refresher(auth_data: AuthData):
      while True:
        await asyncio.sleep(auth_data['expires_in'] - 60)
        logger.info('Refreshing token')
        self._ctx.auth_data = auth_data = await self.login()
        logger.info('Token refreshed successfully. New token expires in %s seconds', auth_data['expires_in'])

    self._ctx = AuthContext(
      auth_data=auth_data,
      refresher=asyncio.create_task(refresher(auth_data)),
      ws=ctx.ws,
      listener=ctx.listener,
    )
    return self._ctx
  
  async def authed_request(self, path: str, params=None) -> ApiResponse:
    ctx = await self.ctx
    r = await self.req({
      'jsonrpc': '2.0',
      'method': path,
      'params': params,
      'access_token': ctx.auth_data['access_token'],
    })
    if 'error' in r and r['error']['code'] == 10028: # too many requests
      await asyncio.sleep(0.2)
      return await self.authed_request(path, params)
    else:
      return r
  
  async def req_subscription(self, channel: str) -> SubscribeResponse:
    r = await self.request('/private/subscribe', {
      'channels': [channel],
    })
    return validate_subscribe_response(r) if self.validate else r
  
  async def req_unsubscription(self, channel: str):
    return await self.request('/private/unsubscribe', {
      'channels': [channel],
    })


@dataclass(frozen=True)
class AuthedSocketMixin(SocketMixin, AuthedClientMixin):
  client: AuthedSocketClient

  async def subscribe(self, channel: str) -> tuple[SubscribeResponse, AsyncIterable]:
    return await self.client.subscribe(channel)
