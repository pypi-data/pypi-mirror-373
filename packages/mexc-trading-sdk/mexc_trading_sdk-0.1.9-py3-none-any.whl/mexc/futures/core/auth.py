from typing_extensions import Any, Mapping
from dataclasses import dataclass, field
from urllib.parse import quote
import json as jsonlib
import hashlib
import hmac
import httpx
from mexc.core import HttpClient, HttpMixin, timestamp

def sign(payload: str, *, secret: str) -> str:
  return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

def query_string(params: Mapping) -> str:
  def fix(v):
    # fix bools, which would show otherwise as "hello=True" instead of "hello=true"
    if isinstance(v, bool):
      return str(v).lower()
    else:
      return v
  return '&'.join([
    f'{k}={quote(str(fix(v)))}'
    for k, v in sorted(params.items())
  ])
  

@dataclass
class AuthHttpClient(HttpClient):
  api_key: str
  api_secret: str

  def headers(self, *, timestamp: int, signature: str) -> dict:
    return {
      'ApiKey': self.api_key,
      'Request-Time': str(timestamp),
      'Signature': signature,
    }

  async def signed_request(
    self, method: str, path: str,
    *,
    params: Mapping | None = None,
    headers: Mapping[str, str] | None = None,
    cookies: httpx._types.CookieTypes | None = None,
    follow_redirects: bool | httpx._client.UseClientDefault = httpx.USE_CLIENT_DEFAULT,
    timeout: httpx._types.TimeoutTypes | httpx._client.UseClientDefault = httpx.USE_CLIENT_DEFAULT,
    extensions: httpx._types.RequestExtensions | None = None,
  ):
    """Non-POST request"""
    ts = timestamp.now()
    query = query_string(params) if params else ''
    path = path + '?' + query
    signature = sign(f'{self.api_key}{ts}{query}', secret=self.api_secret)
    headers = {**self.headers(timestamp=ts, signature=signature), **(headers or {})}
    
    return await self.request(
      method, path, headers=headers,
      follow_redirects=follow_redirects, cookies=cookies,
      timeout=timeout, extensions=extensions,
    )
  
  async def signed_post(
    self, path: str,
    *,
    json: Any | None = None,
    headers: Mapping[str, str] | None = None,
    cookies: httpx._types.CookieTypes | None = None,
    follow_redirects: bool | httpx._client.UseClientDefault = httpx.USE_CLIENT_DEFAULT,
    timeout: httpx._types.TimeoutTypes | httpx._client.UseClientDefault = httpx.USE_CLIENT_DEFAULT,
    extensions: httpx._types.RequestExtensions | None = None,
  ):
    ts = timestamp.now()
    body = jsonlib.dumps(json) if json else ''
    headers = dict(headers or {})
    
    signature = sign(f'{self.api_key}{ts}{body}', secret=self.api_secret)
    headers = {
      'Content-Type': 'application/json',
      **self.headers(timestamp=ts, signature=signature),
      **(headers or {}),
    }
    return await self.request(
      'POST', path, headers=headers, content=body,
      follow_redirects=follow_redirects, cookies=cookies,
      timeout=timeout, extensions=extensions,
    )
  
@dataclass
class AuthHttpMixin(HttpMixin):
  base_url: str = field(kw_only=True)
  auth_http: AuthHttpClient

  def __init__(self, *, base_url: str, auth_http: AuthHttpClient):
    self.base_url = base_url
    self.http = self.auth_http = auth_http

  @classmethod
  def new(cls, api_key: str, api_secret: str, *, base_url: str):
    client = AuthHttpClient(api_key=api_key, api_secret=api_secret)
    return cls(base_url=base_url, auth_http=client)
  
  async def __aenter__(self):
    await self.auth_http.__aenter__()
    return self
  
  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.auth_http.__aexit__(exc_type, exc_value, traceback)

  async def signed_request(
    self, method: str, path: str,
    *,
    params: Mapping | None = None,
    headers: Mapping[str, str] | None = None,
    cookies: httpx._types.CookieTypes | None = None,
    follow_redirects: bool | httpx._client.UseClientDefault = httpx.USE_CLIENT_DEFAULT,
    timeout: httpx._types.TimeoutTypes | httpx._client.UseClientDefault = httpx.USE_CLIENT_DEFAULT,
    extensions: httpx._types.RequestExtensions | None = None,
  ):
    return await self.auth_http.signed_request(
      method, self.base_url + path, headers=headers,
      follow_redirects=follow_redirects, cookies=cookies,
      timeout=timeout, extensions=extensions, params=params,
    )
  
  async def signed_post(
    self, path: str,
    *,
    json: Any | None = None,
    headers: Mapping[str, str] | None = None,
    cookies: httpx._types.CookieTypes | None = None,
    follow_redirects: bool | httpx._client.UseClientDefault = httpx.USE_CLIENT_DEFAULT,
    timeout: httpx._types.TimeoutTypes | httpx._client.UseClientDefault = httpx.USE_CLIENT_DEFAULT,
    extensions: httpx._types.RequestExtensions | None = None,
  ):
    return await self.auth_http.signed_post(
      self.base_url + path, headers=headers, json=json,
      follow_redirects=follow_redirects, cookies=cookies,
      timeout=timeout, extensions=extensions,
    )