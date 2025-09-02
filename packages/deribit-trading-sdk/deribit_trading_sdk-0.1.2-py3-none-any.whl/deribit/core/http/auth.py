from dataclasses import dataclass, field
import hmac
import hashlib
from uuid import uuid4
import json
import httpx

from deribit.core import (
  timestamp, AuthedClient, ApiResponse, path_join, validate_response,
  NetworkError
)
from .client import HttpClient

def sign(data: bytes, *, secret: str):
  return hmac.new(secret.encode(), data, hashlib.sha256).hexdigest()

def signature_data(*, http_method: str, uri: str, body: str|bytes, ts: int, nonce: str):
  return f'{ts}\n{nonce}\n{http_method}\n{uri}\n{body}\n'.encode()

@dataclass
class AuthedHTTPClient(HttpClient, AuthedClient):
  client_id: str
  client_secret: str = field(repr=False)

  def auth_header(
    self, *, http_method: str, body: str|bytes|None = None,
    ts: int | None = None, nonce: str | None = None, uri: str,
  ):
    ts = ts or timestamp.now()
    nonce = nonce or uuid4().hex
    data = signature_data(http_method=http_method, uri=uri, ts=ts, nonce=nonce, body=body or '')
    signature = sign(data, secret=self.client_secret)
    return f'deri-hmac-sha256 id={self.client_id},ts={ts},sig={signature},nonce={nonce}'
  
  @HttpClient.with_client
  async def authed_request(self, path: str, params=None) -> ApiResponse:
    msg = {
      'jsonrpc': '2.0',
      'method': path,
    }
    if params is not None:
      msg['params'] = params
    body = json.dumps(msg)
    uri = path_join(self.base_path, path)
    url = path_join(self.base_url, path)
    auth_header = self.auth_header(http_method='POST', body=body, uri=uri)
    try:
      r = await self.client.post(url, content=body, headers={
        'Authorization': auth_header,
        'Content-Type': 'application/json',
        'User-Agent': 'trading-sdk',
      })
      return validate_response(r.text) if self.validate else json.loads(r.text)
    except httpx.HTTPError as e:
      raise NetworkError from e
