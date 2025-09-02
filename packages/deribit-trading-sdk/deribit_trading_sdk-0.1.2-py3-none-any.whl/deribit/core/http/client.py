from dataclasses import dataclass, field
from functools import wraps
import httpx

from deribit.core import (
  Client, ApiResponse, DERIBIT_MAINNET, path_join, validate_response,
  UserError, NetworkError
)

@dataclass
class HttpClient(Client):
  domain: str = field(default=DERIBIT_MAINNET, kw_only=True)
  base_path: str = field(default='/api/v2', kw_only=True)

  @property
  def base_url(self) -> str:
    return path_join(f'https://{self.domain}', self.base_path)

  async def __aenter__(self):
    self._client = httpx.AsyncClient()
    await self._client.__aenter__()
    return self
  
  async def __aexit__(self, exc_type, exc_value, traceback):
    if (client := getattr(self, '_client', None)) is not None:
      await client.__aexit__(exc_type, exc_value, traceback)
      self._client = None

  @property
  def client(self) -> httpx.AsyncClient:
    if (client := getattr(self, '_client', None)) is None:
      raise UserError('Client must be used as context manager: `async with ...: ...`')
    return client
  
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

  @with_client
  async def request(self, path: str, params=None) -> ApiResponse:
    try:
      r = await self.client.post(self.base_url, json={
        'jsonrpc': '2.0',
        'method': path,
        'params': params,
      }, headers={
        'User-Agent': 'trading-sdk',
      })
      return validate_response(r.text) if self.validate else r.json()
    except httpx.HTTPError as e:
      raise NetworkError from e
  
  @with_client
  async def get(self, path: str, params=None) -> ApiResponse:
    url = path_join(self.base_url, path)
    try:
      r = await self.client.get(url, params=params, headers={
        'User-Agent': 'trading-sdk',
      })
      return validate_response(r.text) if self.validate else r.json()
    except httpx.HTTPError as e:
      raise NetworkError from e