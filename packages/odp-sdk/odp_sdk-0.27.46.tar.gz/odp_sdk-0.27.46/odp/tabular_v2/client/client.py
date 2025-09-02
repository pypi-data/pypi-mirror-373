import io
import json
import logging
import typing
from typing import TYPE_CHECKING, Dict, Iterator, Optional, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from odp.tabular_v2.util import Iter2Reader
from odp.util.util import size2human

if TYPE_CHECKING:
    from odp.tabular_v2.client.table import Table

read_retry_strategy = Retry(
    total=8,
    status_forcelist=[429, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
    backoff_factor=1,  # exponential sleep (1s, 2s, 4s…)
)

write_retry_strategy = Retry(
    total=8,
    status_forcelist=[429],
    allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
    backoff_factor=2,
)


class Client:
    def __init__(self, base_url: str):
        self._base_url = base_url

    class Response:
        # Abstraction for response object, shared between http client and test client
        def __init__(self, res: Union[requests.Response, Iterator[bytes], Dict, bytes]):
            if isinstance(res, requests.Response):
                if res.status_code == 204:
                    raise FileNotFoundError(res.text)
                if res.status_code == 400:
                    raise ValueError(res.text)
                res.raise_for_status()
            # logging.debug("response: %s", res)
            self.res = res

        def reader(self):
            if isinstance(self.res, bytes):
                return io.BytesIO(self.res)
            if isinstance(self.res, Iterator):
                return Iter2Reader(self.res)
            if isinstance(self.res, requests.Response):
                if self.res.status_code == 204:
                    raise FileNotFoundError(self.res.text)
                self.res.raise_for_status()
                if self.res.raw is None:
                    return io.BytesIO(self.res.content)
            if isinstance(self.res, dict):
                return io.BytesIO(bytes(str(self.res), "utf-8"))
            if isinstance(self.res, io.IOBase):
                return self.res
            if isinstance(self.res, requests.Response):
                return self.res.raw
            if isinstance(self.res, list):  # assuming list of bytes
                return Iter2Reader(iter(self.res))
            raise ValueError(f"unexpected type {type(self.res)}")

        def iter(self) -> Iterator[bytes]:
            if isinstance(self.res, bytes):
                return iter([self.res])
            if isinstance(self.res, Iterator):
                return self.res
            if isinstance(self.res, requests.Response):
                if self.res.status_code == 204:
                    raise FileNotFoundError(self.res.text)
                self.res.raise_for_status()
                if self.res.raw is None:
                    return iter([self.res.content])
                return self.res.raw
            if isinstance(self.res, dict):
                return iter([bytes(str(self.res), "utf-8")])
            raise ValueError(f"unexpected type {type(self.res)}")

        def all(self) -> bytes:
            if isinstance(self.res, bytes):
                return self.res
            if isinstance(self.res, Iterator):
                return b"".join(self.res)
            if isinstance(self.res, requests.Response):
                if self.res.status_code == 204:
                    raise FileNotFoundError(self.res.text)
                self.res.raise_for_status()
                if self.res.raw is None:
                    return self.res.content
                return self.res.raw.read()
            if isinstance(self.res, dict):
                return bytes(str(self.res), "utf-8")
            raise ValueError(f"unexpected type {type(self.res)}")

        def json(self) -> typing.Union[dict, list, None]:
            if isinstance(self.res, requests.Response):
                return self.res.json()
            if self.res is None:
                return None
            if isinstance(self.res, dict):
                return self.res
            if isinstance(self.res, list):
                return self.res
            if isinstance(self.res, bytes):
                return json.loads(self.res.decode("utf-8"))
            if isinstance(self.res, requests.Response):
                if self.res.status_code == 204:
                    raise FileNotFoundError(self.res.text)
                self.res.raise_for_status()
                if self.res.raw is None:
                    return None
                return json.loads(self.res.raw.read().decode("utf-8"))
            raise ValueError(f"unexpected type {type(self.res)}")

    def _request(
        self,
        path: str,
        data: Union[Dict, bytes, Iterator[bytes], io.IOBase, None] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        retry: bool = True,  # if it is safe to retry the request on failure
    ) -> Response:
        if retry:
            retry_strategy = read_retry_strategy  # read operations are safe to retry in many cases
        else:
            retry_strategy = write_retry_strategy  # more restrictive

        with requests.Session() as s:
            adapter = HTTPAdapter(pool_connections=4, pool_maxsize=4, max_retries=retry_strategy)
            s.mount("http://", adapter)
            s.mount("https://", adapter)
            if isinstance(data, dict):
                logging.debug("sending %s %s %s", path, params, data)
                res = s.post(self._base_url + path, headers=headers, params=params, json=data, stream=True)
            elif isinstance(data, bytes):
                logging.debug("sending %s %s (%s)", path, params, size2human(len(data)) if data else "-")
                res = s.post(self._base_url + path, headers=headers, params=params, data=data, stream=True)
            elif isinstance(data, io.IOBase):
                logging.debug("sending file-like %s %s", path, params)
                res = s.post(self._base_url + path, headers=headers, params=params, data=data, stream=True)
            elif isinstance(data, Iterator):
                logging.debug("sending %s %s iterator...", path, params)
                res = s.post(self._base_url + path, headers=headers, params=params, data=data, stream=True)
            elif data is None:
                logging.debug("sending %s %s no data", path, params)
                res = s.post(self._base_url + path, headers=headers, params=params, stream=True)
            else:
                raise ValueError(f"unexpected type {type(data)}")
        clen = res.headers.get("Content-Length", "")
        if not clen:
            clen = res.headers.get("Transfer-Encoding", "")
        logging.debug("got response %s (%s) for %s", res.status_code, clen, path)
        return self.Response(res)

    def table(self, table_id: str) -> "Table":
        """
        create a table handler for the given table_id
        @param table_id:
        @return:
        """
        from odp.tabular_v2.client import Table

        return Table(self, table_id)
