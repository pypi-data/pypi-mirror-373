import io
import json
import logging
import os
from typing import TYPE_CHECKING, Dict, Iterator, Union

import requests
from requests.adapters import HTTPAdapter

from odp.tabular_v2.client.client import read_retry_strategy, write_retry_strategy

# NOTE(oha): deferred imports to avoid circular dependencies, will be fixed when we remove the old client
# from odp.client.auth import InteractiveTokenProvider
# from odp.client.catalog_client import CatalogClient
from odp.tabular_v2.util import Iter2Reader

if TYPE_CHECKING:
    from dataset import Dataset


class _Response:
    # Abstraction for the response object, shared between http client and test client
    def __init__(self, res: Union[requests.Response, Iterator[bytes], Dict, bytes]):
        logging.info("response: %s", res)
        if isinstance(res, requests.Response):
            if res.status_code == 204:
                raise FileNotFoundError(res.text)
            res.raise_for_status()
        # logging.info("response: %s", res)
        self.res = res

    def reader(self):
        if isinstance(self.res, bytes):
            return io.BytesIO(self.res)
        if isinstance(self.res, Iterator):
            return Iter2Reader(self.res)
        return self.res.raw

    def iter(self) -> Iterator[bytes]:
        if isinstance(self.res, bytes):
            return iter([self.res])
        if isinstance(self.res, Iterator):
            return self.res
        return self.res.iter_content()

    def all(self) -> bytes:
        if isinstance(self.res, bytes):
            return self.res
        if isinstance(self.res, Iterator):
            return b"".join(self.res)
        return self.res.content

    def json(self) -> dict:
        if self.res is None:
            return None
        if isinstance(self.res, dict):
            return self.res
        return self.res.json()


class Client:
    """
    New ODP client for accessing datasets and other resources.
    supersedes the old odp.OdpClient
    """

    def __init__(self, base_url: str = "https://api.hubocean.earth/", jwt_bearer: str = "", api_key: str = ""):
        if api_key:
            self._auth = lambda: f"ApiKey {api_key}"
        elif jwt_bearer:
            if not jwt_bearer.startswith("Bearer "):
                jwt_bearer = "Bearer " + jwt_bearer
            self._auth = lambda: jwt_bearer
        elif os.getenv("JUPYTERHUB_API_TOKEN"):

            def get_token():
                res = requests.post("http://localhost:8000/access_token")
                res.raise_for_status()
                token: str = res.json()["token"]
                return "Bearer " + token

            self._auth = get_token
        else:
            self._setup_jwt()

        self.base_url = base_url.rstrip("/")

        # FIXME: this is wrong, sessions can't be this long
        self._http_client = requests.Session()
        self._http_client.headers.setdefault("User-Agent", "odp-sdk-python")
        from odp.client.catalog_client import CatalogClient

        self._catalog = CatalogClient(http_client=self._http_client)

    def _setup_jwt(self):
        """
        fire up the JWT setup process on the browser
        """
        client_id = os.getenv("ODP_CLIENT_ID", "f96fc4a5-195b-43cc-adb2-10506a82bb82")
        from odp.client.auth import InteractiveTokenProvider

        prov = InteractiveTokenProvider(client_id=client_id)
        self._auth = lambda: f"Bearer {prov.get_token()}"
        # raise NotImplementedError("JWT authentication is not implemented yet.")

    def _request(self, req: requests.Request, retry: bool = True) -> requests.Response:
        """
        base implementation to send a request to ODP
        may be overridden to use mechanisms other than http
        """
        req.headers.setdefault("Authorization", self._auth())  # allow override
        req.headers.setdefault("User-Agent", "odp-sdk-python")
        if isinstance(req.data, dict):
            req.data = json.dumps(req.data)
            req.headers.setdefault("Content-Type", "application/json")
        preq = req.prepare()
        # logging.info("request: %s %s %s", preq.method, preq.url, preq.body)
        if retry:
            retry_strategy = read_retry_strategy
        else:
            retry_strategy = write_retry_strategy

        with requests.Session() as s:
            adapter = HTTPAdapter(pool_connections=4, pool_maxsize=4, max_retries=retry_strategy)
            s.mount("http://", adapter)
            s.mount("https://", adapter)
            res = s.send(preq, stream=True)
        logging.info("response: %s in %.2fs from %s", res.status_code, res.elapsed.total_seconds(), res.url)
        return res

    def dataset(self, id: str) -> "Dataset":
        """fetch a dataset by id"""
        from .dataset import Dataset

        # NOTE(oha): ktable does not strictly need a catalog, and catalog v2 is not ready yet
        # we just silently pass a dataset with not catalog features for now, and add more later
        return Dataset(self, id)
        # req = requests.Request("GET", self.base_url + "/api/catalog/v2/datasets/" + safe_id(id))
        # req.timeout = 10
        # res = self._request(req)
        # if res.status_code in (204, 404):
        #    raise FileNotFoundError(f"Dataset {id} not found: %s %s", res.status_code, res.content)
        # return Dataset._from_catalog_v2(self, res.json())
