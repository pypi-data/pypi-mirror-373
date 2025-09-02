import requests

from ..util.cheapdantic import BaseModel
from .http_client import OdpHttpClient
from odp.client.exc import OdpUnauthorizedError


class OdpIamClient(BaseModel):
    http_client: OdpHttpClient

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def share_with_hubocean_internal(self, resourceId: str, kind="dataset") -> str:
        """Share a resource with HubOcean Internal group as editor.

        Args:
            ref: Resource uuid
            subject_id: Subject ID
            role: Role to assign to the subject
        """

        if kind not in ["dataset", "dataCollection"]:
            raise ValueError("kind must be either 'dataset' or 'dataCollection'")

        role = "2"  # Editor
        subject_id = "0ee75a5a-6fcc-47db-8d0c-8f61f0641126"  # HubOcean Internal group ID
        params = {
            "object": {"id": resourceId, "kind": kind},
            "role": role,
            "subject": {"id": subject_id, "type": "group"},
        }
        path = "/api/permissions/v1/resources/relationships/"
        res = self.http_client.post(f"{path}", content=params)

        try:
            res.raise_for_status()
        except requests.HTTPError:
            if res.status_code == 409:
                return "The resource is already shared with HubOcean Internal group"
            elif res.status_code == 401:
                raise OdpUnauthorizedError("Unauthorized access")
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}")
        return "Success"
