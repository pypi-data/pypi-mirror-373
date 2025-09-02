from typing_extensions import Any, TypedDict, Literal, Mapping, TypeVar, Generic, AsyncIterable
from abc import abstractmethod
from dataclasses import dataclass, field
import asyncio
from .base import RpcSocketClient

T = TypeVar('T')
U = TypeVar('U')

class Response(TypedDict, Generic[T]):
  kind: Literal['response']
  id: int
  response: T

class Subscription(TypedDict, Generic[U]):
  kind: Literal['subscription']
  channel: str
  data: U

Message = Response[T] | Subscription[U]

@dataclass
class MultiplexStreamsRPCSocketClient(RpcSocketClient[T], Generic[T, U]):
  """Multiplexed request/response and streams socket client. It uses IDs to identify requests and responses. It also supports subscription to multiple channels."""
  replies: dict[int, asyncio.Future[T]] = field(default_factory=dict, init=False, repr=False)
  counter: int = field(default=0, init=False, repr=False)
  subscribers: dict[str, asyncio.Queue[U]] = field(default_factory=dict, init=False, repr=False)

  async def req(self, msg: Mapping) -> T:
    id = self.counter
    self.counter += 1
    while True:
      self.replies[id] = asyncio.Future()
      await self.send(id, msg)
      res = await self.replies[id]
      del self.replies[id]
      return res
    
  @abstractmethod
  async def req_subscription(self, channel: str) -> T:
    ...

  @abstractmethod
  async def req_unsubscription(self, channel: str) -> T:
    ...

  @abstractmethod
  def parse_msg(self, msg: str | bytes) -> Message[T, U]:
    ...

  def on_msg(self, msg: str | bytes):
    res = self.parse_msg(msg)
    if res['kind'] == 'response':
      self.replies[res['id']].set_result(res['response'])
    else:
      self.subscribers[res['channel']].put_nowait(res['data'])

  @abstractmethod
  async def send(self, id: int, msg: Mapping):
    ...

  async def subscribe(self, channel: str) -> tuple[T, AsyncIterable[U]]:
    self.subscribers[channel] = asyncio.Queue()
    r = await self.req_subscription(channel)
    async def gen():
      while True:
        if (queue := self.subscribers.get(channel)) is None:
          return # unsubscribed
        val = await queue.get()
        yield val
    return r, gen()

  async def unsubscribe(self, channel: str):
    del self.subscribers[channel]
    await self.req_unsubscription(channel)
