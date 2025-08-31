import logging
from typing import Any, Dict, Optional, Self, Union

import httpx
from httpx import HTTPError

from snakestack.httpx.exceptions import RequestHTTPError

logger = logging.getLogger(__name__)


class SnakeHttpClient:

    def __init__(
        self: Self,
        base_url: str,
        verify_ssl: bool = True
    ) -> None:
        self._base_url = base_url
        self._verify_ssl = verify_ssl

    async def handle(
        self: Self,
        method: str,
        url: str,
        content: Optional[Union[str, bytes]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        auth: Optional[Any] = None,
        follow_redirects: bool = False,
        timeout: Optional[Union[float, httpx.Timeout]] = None,
        extensions: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        async with httpx.AsyncClient(
            base_url=self._base_url, verify=self._verify_ssl
        ) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    content=content,
                    data=data,
                    files=files,
                    json=json,
                    params=params,
                    headers=headers,
                    cookies=cookies,
                    auth=auth,
                    follow_redirects=follow_redirects,
                    timeout=timeout,
                    extensions=extensions
                )
                response.raise_for_status()
            except HTTPError as error:
                logger.debug("Error on request", exc_info=error)
                raise RequestHTTPError(api=f"{self._base_url}{url}", original_exception=error)
            else:
                return response
