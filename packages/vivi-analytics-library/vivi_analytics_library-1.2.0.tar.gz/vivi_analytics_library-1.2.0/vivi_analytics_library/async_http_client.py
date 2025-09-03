from typing import Any, Dict, Optional

import aiohttp
from pydantic import BaseModel


class HttpResponse(BaseModel):
    success: bool
    status: int
    headers: Dict[str, str]
    content: Any

    class Config:
        from_attributes = True


async def get_async(
    url: str,
    accessToken: Optional[str] = None,
    verifySSL: bool = True,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
) -> HttpResponse:
    try:
        async with aiohttp.ClientSession() as session:
            request_headers = headers or {"Accept": "application/json"}
            if accessToken:
                request_headers["Authorization"] = f"Bearer {accessToken}"

            async with session.get(
                url, headers=request_headers, params=params, ssl=verifySSL
            ) as response:
                content = await (
                    response.json()
                    if response.content_type == "application/json"
                    else response.text()
                )
                return HttpResponse(
                    success=200 <= response.status < 300,
                    status=response.status,
                    headers=dict(response.headers),
                    content=content,
                )
    except Exception as e:
        print(f"GET failed: {e}")
        raise


async def post_async(
    url: str,
    accessToken: Optional[str] = None,
    verifySSL: bool = True,
    params: Optional[dict] = None,
    data: Optional[Any] = None,
    json: Optional[Any] = None,
    headers: Optional[dict] = None,
) -> HttpResponse:
    if data and json:
        raise ValueError("Cannot provide both 'data' and 'json' in the same request.")

    try:
        async with aiohttp.ClientSession() as session:
            request_headers = headers or {"Accept": "application/json"}
            if accessToken:
                request_headers["Authorization"] = f"Bearer {accessToken}"

            async with session.post(
                url,
                headers=request_headers,
                params=params,
                data=data,
                json=json,
                ssl=verifySSL,
            ) as response:
                content = await (
                    response.json()
                    if response.content_type == "application/json"
                    else response.text()
                )
                return HttpResponse(
                    success=200 <= response.status < 300,
                    status=response.status,
                    headers=dict(response.headers),
                    content=content,
                )
    except Exception as e:
        print(f"POST failed: {e}")
        raise
