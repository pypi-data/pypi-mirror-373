from __future__ import annotations

import time
from typing import Optional

import httpx

from .config import Config
from .errors import APIResponseError


class SiigoAuth:
    def __init__(self, cfg: Config):
        self._cfg = cfg
        self._token: Optional[str] = None
        self._exp_ts: Optional[float] = None  # naive cache; Siigo may not return exp

    def token(self) -> str:
        if self._token and self._exp_ts and time.time() < self._exp_ts - 30:
            return self._token
        self._fetch()
        return self._token  # type: ignore

    def _fetch(self) -> None:
        if not (self._cfg.username and self._cfg.access_key and self._cfg.partner_id):
            raise ValueError("username, access_key and partner_id are required for Siigo auth")

        url = f"{self._cfg.base_url}/auth"
        headers = {
            "Content-Type": "application/json",
            "Partner-Id": self._cfg.partner_id,
            "User-Agent": self._cfg.user_agent,
        }
        payload = {"username": self._cfg.username, "access_key": self._cfg.access_key}
        with httpx.Client(timeout=self._cfg.timeout, headers=headers) as c:
            r = c.post(url, json=payload)
        if r.status_code >= 400:
            # Include response body for easier debugging
            raise APIResponseError(r.status_code, r.text)

        data = r.json()
        self._token = data.get("access_token")
        # If Siigo returns expires_in (seconds), cache it; otherwise keep None.
        if "expires_in" in data and isinstance(data["expires_in"], (int, float)):
            self._exp_ts = time.time() + float(data["expires_in"])
        else:
            self._exp_ts = None
        if not self._token:
            raise APIResponseError(500, "No access_token in Siigo auth response")
