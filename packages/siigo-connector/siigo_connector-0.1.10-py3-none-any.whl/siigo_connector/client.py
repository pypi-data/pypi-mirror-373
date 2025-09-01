from __future__ import annotations

from ._http import SyncTransport
from .auth import SiigoAuth
from .config import Config
from .resources.customers import CustomersResource
from .resources.products import ProductsResource


class Client:
    def __init__(
        self,
        *,
        username: str,
        access_key: str,
        partner_id: str,
        base_url: str | None = None,
        timeout: float | None = None,
    ):
        cfg = Config(
            base_url=base_url or Config.base_url,
            timeout=timeout or Config.timeout,
            username=username,
            access_key=access_key,
            partner_id=partner_id,
        )
        auth = SiigoAuth(cfg)
        self._http = SyncTransport(cfg, auth)
        self._base_url = cfg.base_url
        # resources
        self.customers = CustomersResource(_request=self._request, base_url=self._base_url)
        self.products = ProductsResource(_request=self._request, base_url=self._base_url)

    def _request(self, method: str, url: str, **kwargs):
        return self._http.request(method, url, **kwargs)

    def close(self) -> None:
        self._http.close()
