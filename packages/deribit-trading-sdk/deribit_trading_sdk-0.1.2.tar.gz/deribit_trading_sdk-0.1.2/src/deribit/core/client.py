from typing_extensions import TypedDict, NotRequired, Any, Self, Literal, TypeVar, Generic
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from .validation import validator
from .util import getenv

T = TypeVar('T', default=Any)

class BaseResponse(TypedDict):
  jsonrpc: str

class OkResponse(BaseResponse, Generic[T]):
  result: T

class ErrorData(TypedDict):
  code: int
  message: str
  data: NotRequired[Any|None]

class ErrorResponse(BaseResponse):
  error: ErrorData

ApiResponse = OkResponse[T] | ErrorResponse

ApiResponseT: type[ApiResponse] = ApiResponse # type: ignore
validate_response = validator(ApiResponseT)

DERIBIT_MAINNET = 'www.deribit.com'
DERIBIT_HISTORY = 'history.deribit.com'
DERIBIT_TESTNET = 'test.deribit.com'

@dataclass
class Client(ABC):
  validate: bool = field(kw_only=True, default=True)

  @abstractmethod
  async def request(self, path: str, params=None, /) -> ApiResponse:
    ...
  
  async def get(self, path: str, params=None, /) -> ApiResponse:
    return await self.request(path, params)

  @abstractmethod
  async def __aenter__(self) -> Self:
    ...
  
  @abstractmethod
  async def __aexit__(self, exc_type, exc_value, traceback):
    ...

class AuthedClient(Client):
  @abstractmethod
  async def authed_request(self, path: str, params=None, /) -> ApiResponse:
    ...

@dataclass(frozen=True)
class ClientMixin:
  client: Client

  @classmethod
  def new(
    cls, *, validate: bool = True, mainnet: bool = True, protocol: Literal['http', 'ws'] = 'ws'
  ):
    
    domain = DERIBIT_MAINNET if mainnet else DERIBIT_TESTNET
    
    if protocol == 'http':
      from deribit.core import HttpClient
      client = HttpClient(validate=validate, domain=domain)
    else:
      from deribit.core import SocketClient
      client = SocketClient(validate=validate, domain=domain)
    return cls(client)

  def validate(self, validate: bool | None = None) -> bool:
    return self.client.validate if validate is None else validate

  async def request(self, path: str, params=None, /) -> ApiResponse:
    return await self.client.request(path, params)
  
  async def get(self, path: str, params=None, /) -> ApiResponse:
    return await self.client.get(path, params)
  
  async def __aenter__(self) -> Self:
    await self.client.__aenter__()
    return self
  
  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)
  
@dataclass(frozen=True)
class AuthedClientMixin(ClientMixin):
  client: AuthedClient

  async def authed_request(self, path: str, params=None, /) -> ApiResponse:
    return await self.client.authed_request(path, params)
  
  @classmethod
  def new(
    cls, client_id: str | None = None, client_secret: str | None = None, *,
    validate: bool = True, mainnet: bool = True, protocol: Literal['http', 'ws'] = 'ws'
  ):
    
    if mainnet:
      client_id = client_id or getenv('DERIBIT_CLIENT_ID')
      client_secret = client_secret or getenv('DERIBIT_CLIENT_SECRET')
      domain = DERIBIT_MAINNET
    else:
      client_id = client_id or getenv('TEST_DERIBIT_CLIENT_ID')
      client_secret = client_secret or getenv('TEST_DERIBIT_CLIENT_SECRET')
      domain = DERIBIT_TESTNET
    
    if protocol == 'http':
      from deribit.core import AuthedHTTPClient
      client = AuthedHTTPClient(client_id, client_secret, validate=validate, domain=domain)
    else:
      from deribit.core import AuthedSocketClient
      client = AuthedSocketClient.new(mainnet=mainnet, validate=validate)
    return cls(client)