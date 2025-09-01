from __future__ import annotations

from typing import Any, Mapping

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .auth import SiigoAuth
from .config import Config
from .errors import APIConnectionError, APIResponseError, APITimeoutError


class SyncTransport:
    def __init__(self, cfg: Config, auth: SiigoAuth):
        self.cfg = cfg
        self.auth = auth
        self.client = httpx.Client(
            timeout=cfg.timeout, headers={"User-Agent": cfg.user_agent}
        )

    def close(self) -> None:
        self.client.close()

    def _headers(self) -> Mapping[str, str]:
        # Always include Partner-Id and Bearer token
        base = {"Partner-Id": self.cfg.partner_id or ""}
        tok = self.auth.token()
        return {**base, "Authorization": f"Bearer {tok}"}

    @retry(
        retry=retry_if_exception_type((httpx.ConnectError, httpx.ReadError)),
        wait=wait_exponential(multiplier=0.3, min=0.5, max=5),
        stop=stop_after_attempt(3),
    )
    def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        try:
            resp = self.client.request(
                method,
                url,
                headers={**self._headers(), **kwargs.pop("headers", {})},
                **kwargs,
            )
            if resp.status_code == 401:
                # token may be expired or invalid: refresh once and retry
                self.auth._fetch()
                resp = self.client.request(
                    method,
                    url,
                    headers={**self._headers(), **kwargs.pop("headers", {})},
                    **kwargs,
                )
        except httpx.ConnectTimeout as e:
            raise APITimeoutError(str(e)) from e
        except httpx.HTTPError as e:
            raise APIConnectionError(str(e)) from e
        if resp.status_code >= 400:
            raise APIResponseError(resp.status_code, resp.text)
        return resp
