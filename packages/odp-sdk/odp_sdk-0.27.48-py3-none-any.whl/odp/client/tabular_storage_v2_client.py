from typing import Dict, Optional, Union

from odp.client.auth import TokenProvider
from odp.tabular_v2.client import Client


class ClientAuthorization(Client):
    def __init__(self, base_url, token_provider: TokenProvider):
        super().__init__(base_url)
        self.token_provider = token_provider

    def _request(
        self,
        path: str,
        data: Union[Dict, bytes, None] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        retry: bool = True,
    ) -> Client.Response:
        headers = headers or {}
        headers["Authorization"] = self.token_provider.get_token()
        headers["user-agent"] = self.token_provider.user_agent
        return super()._request(path, data, params, headers, retry)
