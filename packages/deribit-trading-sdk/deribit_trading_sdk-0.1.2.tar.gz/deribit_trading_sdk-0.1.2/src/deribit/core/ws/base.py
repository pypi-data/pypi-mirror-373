from typing_extensions import Mapping, TypeVar, Generic
from abc import ABC, abstractmethod
import asyncio
from functools import wraps
from dataclasses import dataclass, field
from datetime import timedelta
import logging
import websockets

from deribit.core import NetworkError, DERIBIT_MAINNET, path_join

T = TypeVar('T')

logger = logging.getLogger('deribit.core.ws')

@dataclass
class Context:
  ws: websockets.ClientConnection
  listener: asyncio.Task

@dataclass(kw_only=True)
class BaseSocketClient(ABC):
  """Base socket client class, including:
  - Connection management
  - Keep alive (ping) loop
  - Restart loop
  - Message handling loop
  """
  domain: str = DERIBIT_MAINNET
  path: str = '/ws/api/v2'
  timeout: timedelta = timedelta(seconds=10)
  started: asyncio.Event = field(default_factory=asyncio.Event, init=False, repr=False)

  @property
  def url(self) -> str:
    return path_join(f'wss://{self.domain}', self.path)

  @property
  async def ctx(self) -> Context:
    if (ctx := getattr(self, '_ctx', None)) is None:
      ctx = await self.open()
    return ctx
  
  @property
  async def ws(self) -> websockets.ClientConnection:
    return (await self.ctx).ws
  
  @staticmethod
  def with_client(fn):
    @wraps(fn)
    async def wrapper(self, *args, **kwargs):
      if getattr(self, '_client', None) is None:
        async with self:
          return await fn(self, *args, **kwargs)
      else:
        return await fn(self, *args, **kwargs)
      
    return wrapper
  
  async def __aenter__(self):
    await self.open()
    return self
  
  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.close(await self.ctx, exc_type, exc_value, traceback)
  
  async def open(self):
    logger.info('Opening...')
    async def connect():
      try:
        return await websockets.connect(self.url, open_timeout=self.timeout.total_seconds())
      except websockets.exceptions.WebSocketException as e:
        raise NetworkError(f'Failed to connect to {self.url}') from e
    
    ws = await connect()
    logger.info('Connected!')
    self._ctx = Context(
      ws=ws,
      listener=asyncio.create_task(self.listener(ws)),
    )
    self.started.set()
    return self._ctx

  async def close(self, ctx: Context, exc_type=None, exc_value=None, traceback=None):
    ctx.listener.cancel()
    await ctx.ws.__aexit__(exc_type, exc_value, traceback)
    self._ctx = None

  async def listener(self, ws: websockets.ClientConnection, /):
    while True:
      msg = await ws.recv()
      logger.debug('Received: %s', msg)
      self.on_msg(msg)

  @abstractmethod
  def on_msg(self, msg: str | bytes):
    ...

class RpcSocketClient(BaseSocketClient, Generic[T]):
  """Base request/response socket client."""
  @abstractmethod
  async def req(self, msg: Mapping) -> T:
    ...
