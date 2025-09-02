from typing import Optional, Union
from uuid import UUID

from ..tabular_v2.client import Table
from ..util.cheapdantic import BaseModel, Field, PrivateAttr
from .auth import ApiKeyTokenProvider, TokenProvider, get_default_token_provider
from .http_client import OdpHttpClient
from .iam_client import OdpIamClient
from .raw_storage_client import OdpRawStorageClient
from .resource_client import OdpResourceClient
from .tabular_storage_client import OdpTabularStorageClient
from .tabular_storage_v2_client import ClientAuthorization
from odp.client.catalog_client import CatalogClient
from odp.dto import DatasetDto


class OdpClient(BaseModel):
    """Client for the ODP API"""

    base_url: str = "https://api.hubocean.earth"
    token_provider: TokenProvider = Field(default_factory=get_default_token_provider)
    api_key: Optional[str] = None

    _http_client: OdpHttpClient = PrivateAttr(None)
    _catalog_client: OdpResourceClient = PrivateAttr(None)
    _raw_storage_client: OdpRawStorageClient = PrivateAttr(None)
    _tabular_storage_client: OdpTabularStorageClient = PrivateAttr(None)
    _tabular_storage_v2_client: ClientAuthorization = PrivateAttr(None)
    _iam_client: OdpIamClient = PrivateAttr(None)
    _catalog_v2_client: CatalogClient = PrivateAttr(None)

    def __init__(self, **data):
        super().__init__(**data)

        if self.api_key:
            self.token_provider = ApiKeyTokenProvider(self.base_url, self.api_key)
        self._http_client = OdpHttpClient(base_url=self.base_url, token_provider=self.token_provider)
        self._catalog_client = OdpResourceClient(http_client=self._http_client, resource_endpoint="/catalog")
        self._raw_storage_client = OdpRawStorageClient(http_client=self._http_client)
        self._tabular_storage_client = OdpTabularStorageClient(http_client=self._http_client)
        self._tabular_storage_v2_client = ClientAuthorization(
            base_url=self.base_url, token_provider=self.token_provider
        )
        self._iam_client = OdpIamClient(http_client=self._http_client)
        self._catalog_v2_client = CatalogClient(http_client=self._http_client)

    def personalize_name(self, name: str, fmt: Optional[str] = None) -> str:
        """Personalize a name by adding a postfix unique to the user

        Args:
            name: The name to personalize
            fmt: Used to override the default format string. Should be a python format-string with placeholders
                for the variables `uid` and `name`. For example: `"{uid}-{name}"`

        Returns:
            The personalized name
        """
        fmt = fmt or "{name}-{uid}"
        uid = self.token_provider.get_user_id()

        # Attempt to simplify the UID by only using the node part of the UUID
        try:
            uid = UUID(uid).node
        except ValueError:
            # User ID is not a valid UUID, use it as-is
            pass

        return fmt.format(uid=uid, name=name)

    @property
    def resource_store(self):
        # TODO: Implement resource store
        raise NotImplementedError("Resource store not implemented")

    @property
    def catalog(self) -> OdpResourceClient:
        return self._catalog_client

    @property
    def catalog_v2_experimental(self) -> CatalogClient:
        """Experimental catalog v2 client"""
        return self._catalog_v2_client

    @property
    def catalog_v2(self) -> CatalogClient:
        """Catalog v2 client"""
        return self._catalog_v2_client

    @property
    def iam(self) -> OdpIamClient:
        return self._iam_client

    @property
    def registry(self):
        # TODO: Implement registry/core controller
        raise NotImplementedError("Registry not implemented")

    @property
    def raw(self) -> OdpRawStorageClient:
        return self._raw_storage_client

    @property
    def tabular(self) -> OdpTabularStorageClient:
        return self._tabular_storage_client

    def table_v2(self, dataset_dto: Union[DatasetDto, str]) -> Table:
        if isinstance(dataset_dto, str):
            return self._tabular_storage_v2_client.table(dataset_dto)
        return self._tabular_storage_v2_client.table(str(dataset_dto.uuid))
