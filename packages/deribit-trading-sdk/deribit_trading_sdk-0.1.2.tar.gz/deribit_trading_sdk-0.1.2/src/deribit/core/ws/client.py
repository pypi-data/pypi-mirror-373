from typing_extensions import TypedDict, Mapping, Any, TypeVar, Generic, NotRequired, Literal, AsyncIterable
from dataclasses import dataclass
import json
import asyncio
import websockets

from deribit.core import (
  Client, ClientMixin, validator,
  DERIBIT_MAINNET, DERIBIT_TESTNET,
  NetworkError,
  OkResponse as BaseOkResponse,
  ErrorResponse as BaseErrorResponse,
)
from .multiplex_streams_rpc import MultiplexStreamsRPCSocketClient, Message

T = TypeVar('T', default=Any)

class BaseMessage(TypedDict):
  jsonrpc: str

class BaseResponse(BaseMessage):
  id: int
  testnet: bool
  usIn: int
  usOut: int
  usDiff: int

class OkResponse(BaseResponse, BaseOkResponse[T], Generic[T]):
  ...

class ErrorResponse(BaseResponse, BaseErrorResponse):
  ...

ApiResponse = OkResponse[T] | ErrorResponse

ApiResponseT: type[ApiResponse] = ApiResponse # type: ignore
validate_response = validator(ApiResponseT)

class MessageParams(TypedDict):
  channel: str
  label: NotRequired[str|None]
  data: Any

class ApiNotification(BaseMessage):
  method: Literal['subscription']
  params: MessageParams

ApiMessage = ApiNotification | ApiResponse[T]

ApiMessageT: type[ApiMessage] = ApiMessage # type: ignore
validate_message = validator(ApiMessageT)

SubscribeResponse = ApiResponse[list[str]]
SubscribeResponseT: type[SubscribeResponse] = SubscribeResponse # type: ignore
validate_subscribe_response = validator(SubscribeResponseT)

@dataclass
class SocketClient(MultiplexStreamsRPCSocketClient[ApiResponse, Any], Client):

  @classmethod
  def new(cls, *, mainnet: bool = True, validate: bool = True):
    return cls(
      domain=DERIBIT_MAINNET if mainnet else DERIBIT_TESTNET,
      validate=validate,
    )
  
  async def req_subscription(self, channel: str) -> SubscribeResponse:
    r = await self.request('/public/subscribe', {
      'channels': [channel],
    })
    return validate_subscribe_response(r) if self.validate else r

  
  async def req_unsubscription(self, channel: str):
    return await self.request('/public/unsubscribe', {
      'channels': [channel],
    })
  
  async def send(self, id: int, msg: Mapping):
    data = {
      'jsonrpc': '2.0',
      'id': id,
      **msg,
    }
    ws = await self.ws
    try:
      await ws.send(json.dumps(data), text=True)
    except websockets.exceptions.WebSocketException as e:
      raise NetworkError from e
  
  def parse_msg(self, msg: str | bytes) -> Message[ApiResponse, Any]:
    r: ApiMessage = validate_message(msg) if self.validate else json.loads(msg)
    if 'error' in r or 'result' in r:
      return {
        'kind': 'response',
        'id': r['id'],
        'response': r
      }
    else:
      return {
        'kind': 'subscription',
        'channel': r['params']['channel'],
        'data': r['params']['data'],
      }


  async def request(self, path: str, params=None, /) -> ApiResponse:
    r = await self.req({
      'jsonrpc': '2.0',
      'method': path,
      'params': params,
    })
    if 'error' in r and r['error']['code'] == 10028: # too many requests
      await asyncio.sleep(0.2)
      return await self.request(path, params)
    else:
      return r
    

@dataclass(frozen=True)
class SocketMixin(ClientMixin):
  client: SocketClient

  async def subscribe(self, channel: str) -> tuple[SubscribeResponse, AsyncIterable]:
    return await self.client.subscribe(channel)