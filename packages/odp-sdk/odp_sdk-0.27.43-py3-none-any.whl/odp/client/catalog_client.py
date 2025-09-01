import json
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

import requests

from odp.client.exc import OdpValidationError
from odp.client.http_client import OdpHttpClient
from odp.dto.catalogv2.catalog import (
    Contributor,
    CreateCustomContributorRequest,
    CreateCustomLicenseRequest,
    CreateDataCollectionRequest,
    CreateDatasetRequest,
    CreateStaticPropertyRequest,
    DataCollection,
    Dataset,
    DatasetProperty,
    LicenseEntity,
    UpdateDataCollectionRequest,
    UpdateDatasetRequest,
    UpdateStaticPropertyMetadataRequest,
    UpdateStaticPropertyValueRequest,
)
from odp.dto.catalogv2.search import (
    AutoCompletionGroupedResult,
    AutoCompletionRequest,
    AutoCompletionResult,
    AutoCompletionResultItem,
    AutoCompletionResultType,
    AutoCompletionScore,
    CollectionSearchResultPayload,
    DatasetSearchResultPayload,
    PayloadType,
    ResultItem,
    SearchRequest,
    SearchResult,
    SearchScore,
)
from odp.util.cheapdantic.cheapdantic import BaseModel


class CatalogClient(BaseModel):

    """Client for interacting with Datasets."""

    http_client: OdpHttpClient
    catalog_base_url: str = "/api/catalog/v2"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create_dataset(
        self,
        request: CreateDatasetRequest,
    ) -> Dataset:
        """Create a dataset.

        Args:
            request: The dataset creation request object

        Returns:
            The created dataset

        Raises:
            OdpValidationError: If the request is invalid
            requests.HTTPError: For other unexpected HTTP errors
        """
        res = self.http_client.post(self.catalog_base_url + "/datasets", content=request)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 400:
                raise OdpValidationError("Invalid input", res.text) from e
            if res.status_code == 500:
                raise requests.HTTPError(f"Internal server error ({res.status_code}): {res.text}") from e
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}")

        return Dataset(**res.json())

    def update_dataset(
        self,
        dataset_id: str,
        request: UpdateDatasetRequest,
    ) -> Dataset:
        """Update a dataset.

        Args:
            dataset_id: The ID of the dataset to update.
            request: The dataset update request object.

        Returns:
            The updated dataset.

        Raises:
            OdpValidationError: If the request is invalid.
            requests.HTTPError: For other unexpected HTTP errors.
        """
        url = f"{self.catalog_base_url}/datasets/{dataset_id}"
        res = self.http_client.put(url, content=request)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 400:
                raise OdpValidationError("Invalid input", res.text) from e
            if res.status_code == 500:
                raise requests.HTTPError(f"Internal server error ({res.status_code}): {res.text}") from e
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}")

        return Dataset(**res.json())

    def update_dataset_internal_data(
        self,
        dataset_id: Union[str, UUID],
        internal_data: Dict[str, Any],
    ) -> Dataset:
        """Update the internal data of a dataset.

        Args:
            dataset_id: The ID of the dataset to update.
            internal_data: A dictionary representing the internal data.

        Returns:
            The updated Dataset object.

        Raises:
            OdpValidationError: If the input is invalid.
            requests.HTTPError: For other unexpected HTTP errors.
        """
        url = f"{self.catalog_base_url}/datasets/{dataset_id}/internal-data"
        json_body = json.dumps(internal_data)
        res = self.http_client.put(url, content=json_body)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 400:
                raise OdpValidationError("Invalid input", res.text) from e
            if res.status_code == 500:
                raise requests.HTTPError(f"Internal server error ({res.status_code}): {res.text}") from e
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}") from e

        return Dataset(**res.json())

    def get_datasets(self) -> List[Dataset]:
        """Fetch all datasets accessible to the user.

        Returns:
            A list of Dataset objects.

        Raises:
            requests.HTTPError: For unexpected HTTP errors.
        """
        url = f"{self.catalog_base_url}/datasets"
        res = self.http_client.get(url)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 500:
                raise requests.HTTPError(f"Internal server error ({res.status_code}): {res.text}") from e
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}")

        return [Dataset(**item) for item in res.json()]

    def get_dataset_by_id(self, dataset_id: Union[str, UUID]) -> Dataset:
        """Fetch a dataset by ID.

        Args:
            dataset_id: The ID of the dataset to fetch.

        Returns:
            A Dataset object.

        Raises:
            OdpValidationError: If the ID is malformed or request is invalid.
            requests.HTTPError: For other unexpected HTTP errors.
        """
        url = f"{self.catalog_base_url}/datasets/{dataset_id}"
        res = self.http_client.get(url)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 400:
                raise OdpValidationError("Invalid input", res.text) from e
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}") from e

        return Dataset(**res.json())

    def delete_dataset(self, dataset_id: Union[str, UUID]) -> None:
        """Delete a dataset by ID.

        Args:
            dataset_id: The ID of the dataset to delete.

        Raises:
            OdpValidationError: If the ID is malformed or request is invalid.
            requests.HTTPError: For other unexpected HTTP errors.
        """
        url = f"{self.catalog_base_url}/datasets/{dataset_id}"
        res = self.http_client.delete(url)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 400:
                raise OdpValidationError("Invalid input", res.text) from e
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}") from e

    def archive_dataset(self, dataset_id: Union[str, UUID]) -> Dataset:
        """Archive a dataset by ID.

        Args:
            dataset_id: The ID of the dataset to archive.

        Returns:
            The updated Dataset object.

        Raises:
            OdpValidationError: If the request input is invalid.
            requests.HTTPError: For other unexpected HTTP errors.
        """
        url = f"{self.catalog_base_url}/datasets/{dataset_id}/archive"
        res = self.http_client.patch(url)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 400:
                raise OdpValidationError("Invalid input", res.text) from e
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}") from e

        return Dataset(**res.json())

    def make_dataset_public(self, dataset_id: Union[str, UUID]) -> Dataset:
        """Make a dataset public by ID.

        Args:
            dataset_id: The ID of the dataset to make public.

        Returns:
            The updated Dataset object.

        Raises:
            OdpValidationError: If the request input is invalid.
            requests.HTTPError: For other unexpected HTTP errors.
        """
        url = f"{self.catalog_base_url}/datasets/{dataset_id}/visibility/public"
        res = self.http_client.patch(url)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 400:
                raise OdpValidationError("Invalid input", res.text) from e
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}") from e

        return Dataset(**res.json())

    def make_dataset_private(self, dataset_id: Union[str, UUID]) -> Dataset:
        """Make a dataset private by ID.

        Args:
            dataset_id: The ID of the dataset to make private.

        Returns:
            The updated Dataset object.

        Raises:
            OdpValidationError: If the request input is invalid.
            requests.HTTPError: For other unexpected HTTP errors.
        """
        url = f"{self.catalog_base_url}/datasets/{dataset_id}/visibility/private"
        res = self.http_client.patch(url)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 400:
                raise OdpValidationError("Invalid input", res.text) from e
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}") from e

        return Dataset(**res.json())

    def create_data_collection(self, request: CreateDataCollectionRequest) -> DataCollection:
        """Create a data collection.

        Args:
            request: The data collection creation request object.

        Returns:
            The created DataCollection object.

        Raises:
            OdpValidationError: If the request input is invalid.
            requests.HTTPError: For other unexpected HTTP errors.
        """
        url = f"{self.catalog_base_url}/data-collections"
        res = self.http_client.post(url, content=request)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 400:
                raise OdpValidationError("Invalid input", res.text) from e
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}") from e

        return DataCollection(**res.json())

    def get_data_collections(self) -> List[DataCollection]:
        """Fetch all data collections accessible to the user.

        Returns:
            A list of DataCollection objects.

        Raises:
            requests.HTTPError: For unexpected HTTP errors.
        """
        url = f"{self.catalog_base_url}/data-collections"
        res = self.http_client.get(url)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}") from e

        return [DataCollection(**item) for item in res.json()]

    def get_data_collection_by_id(self, data_collection_id: Union[str, UUID]) -> DataCollection:
        """Fetch a data collection by ID.

        Args:
            data_collection_id: The ID of the data collection to fetch.

        Returns:
            A DataCollection object.

        Raises:
            OdpValidationError: If the input is invalid.
            requests.HTTPError: For other unexpected HTTP errors.
        """
        url = f"{self.catalog_base_url}/data-collections/{data_collection_id}"
        res = self.http_client.get(url)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 400:
                raise OdpValidationError("Invalid input", res.text) from e
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}") from e

        return DataCollection(**res.json())

    def update_data_collection(
        self,
        data_collection_id: Union[str, UUID],
        request: UpdateDataCollectionRequest,
    ) -> DataCollection:
        """Update a data collection.

        Args:
            data_collection_id: The ID of the data collection to update.
            request: The update request object.

        Returns:
            The updated DataCollection object.

        Raises:
            OdpValidationError: If the request input is invalid.
            requests.HTTPError: For other unexpected HTTP errors.
        """
        url = f"{self.catalog_base_url}/data-collections/{data_collection_id}"
        res = self.http_client.put(url, content=request)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 400:
                raise OdpValidationError("Invalid input", res.text) from e
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}") from e

        return DataCollection(**res.json())

    def delete_data_collection(self, data_collection_id: Union[str, UUID]) -> None:
        """Delete a data collection by ID.

        Args:
            data_collection_id: The ID of the data collection to delete.

        Raises:
            OdpValidationError: If the input is invalid.
            requests.HTTPError: For other unexpected HTTP errors.
        """
        url = f"{self.catalog_base_url}/data-collections/{data_collection_id}"
        res = self.http_client.delete(url)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 400:
                raise OdpValidationError("Invalid input", res.text) from e
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}") from e

    def make_data_collection_public(self, data_collection_id: Union[str, UUID]) -> DataCollection:
        """Make a data collection public by ID.

        Args:
            data_collection_id: The ID of the data collection to make public.

        Returns:
            The updated DataCollection object.

        Raises:
            OdpValidationError: If the request input is invalid.
            requests.HTTPError: For other unexpected HTTP errors.
        """
        url = f"{self.catalog_base_url}/data-collections/{data_collection_id}/visibility/public"
        res = self.http_client.patch(url)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 400:
                raise OdpValidationError("Invalid input", res.text) from e
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}") from e

        return DataCollection(**res.json())

    def make_data_collection_private(self, data_collection_id: Union[str, UUID]) -> DataCollection:
        """Make a data collection private by ID.

        Args:
            data_collection_id: The ID of the data collection to make private.

        Returns:
            The updated DataCollection object.

        Raises:
            OdpValidationError: If the request input is invalid.
            requests.HTTPError: For other unexpected HTTP errors.
        """
        url = f"{self.catalog_base_url}/data-collections/{data_collection_id}/visibility/private"
        res = self.http_client.patch(url)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 400:
                raise OdpValidationError("Invalid input", res.text) from e
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}") from e

        return DataCollection(**res.json())

    def add_dataset_to_data_collection(
        self,
        data_collection_id: Union[str, UUID],
        dataset_id: Union[str, UUID],
    ) -> DataCollection:
        """Add a dataset to a data collection.

        Args:
            data_collection_id: The ID of the data collection.
            dataset_id: The ID of the dataset to add.

        Returns:
            The updated DataCollection object.

        Raises:
            OdpValidationError: If the request input is invalid.
            requests.HTTPError: For other unexpected HTTP errors.
        """
        url = f"{self.catalog_base_url}/data-collections/{data_collection_id}/datasets/{dataset_id}"
        res = self.http_client.post(url)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 400:
                raise OdpValidationError("Invalid input", res.text) from e
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}") from e

        return DataCollection(**res.json())

    def remove_dataset_from_data_collection(
        self,
        data_collection_id: Union[str, UUID],
        dataset_id: Union[str, UUID],
    ) -> DataCollection:
        """Remove a dataset from a data collection.

        Args:
            data_collection_id: The ID of the data collection.
            dataset_id: The ID of the dataset to remove.

        Returns:
            The updated DataCollection object.

        Raises:
            OdpValidationError: If the request input is invalid.
            requests.HTTPError: For other unexpected HTTP errors.
        """
        url = f"{self.catalog_base_url}/data-collections/{data_collection_id}/datasets/{dataset_id}"
        res = self.http_client.delete(url)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 400:
                raise OdpValidationError("Invalid input", res.text) from e
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}") from e

        return DataCollection(**res.json())

    def get_dataset_properties(
        self,
        dataset_id: str,
    ) -> List[DatasetProperty]:
        """Retrieve all static properties for a dataset.

        Args:
            dataset_id: The ID of the dataset

        Returns:
            A list of DatasetProperty objects

        Raises:
            requests.HTTPError: For unexpected HTTP errors
        """
        url = f"{self.catalog_base_url}/datasets/{dataset_id}/properties"
        res = self.http_client.get(url)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}") from e

        if res.json():
            return [DatasetProperty(**item) for item in res.json()]
        return []

    def get_property_by_name(
        self,
        dataset_id: str,
        property_name: str,
    ) -> DatasetProperty:
        """Retrieve a specific static property by name from a dataset.

        Args:
            dataset_id: The ID of the dataset
            property_name: The name of the property

        Returns:
            The DatasetProperty object

        Raises:
            requests.HTTPError: For unexpected HTTP errors
        """
        url = f"{self.catalog_base_url}/datasets/{dataset_id}/properties/{property_name}"
        res = self.http_client.get(url)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}") from e

        return DatasetProperty(**res.json())

    def create_static_property(
        self,
        dataset_id: str,
        request: CreateStaticPropertyRequest,
    ) -> DatasetProperty:
        """Create a static property for a dataset.

        Args:
            dataset_id: The ID of the dataset
            request: The property creation request

        Returns:
            The created static property

        Raises:
            OdpValidationError: If the request is invalid
            requests.HTTPError: For other unexpected HTTP errors
        """
        url = f"{self.catalog_base_url}/datasets/{dataset_id}/properties"
        res = self.http_client.post(url, content=request)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 400:
                raise OdpValidationError("Invalid input", res.text) from e
            if res.status_code == 500:
                raise requests.HTTPError(f"Internal server error ({res.status_code}): {res.text}") from e
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}")

        return DatasetProperty(**res.json())

    def update_static_property_metadata(
        self,
        dataset_id: str,
        property_name: str,
        request: UpdateStaticPropertyMetadataRequest,
    ) -> DatasetProperty:
        """Update metadata of a static property for a dataset.

        Args:
            dataset_id: The ID of the dataset
            property_name: The name of the static property
            request: Metadata update request

        Returns:
            The updated DatasetProperty

        Raises:
            OdpValidationError: If the request is invalid
            requests.HTTPError: For other unexpected HTTP errors
        """
        url = f"{self.catalog_base_url}/datasets/{dataset_id}/properties/{property_name}"
        res = self.http_client.put(url, content=request)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 400:
                raise OdpValidationError("Invalid input", res.text) from e
            if res.status_code == 500:
                raise requests.HTTPError(f"Internal server error ({res.status_code}): {res.text}") from e
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}")

        return DatasetProperty(**res.json())

    def update_static_property_value(
        self,
        dataset_id: str,
        property_name: str,
        request: UpdateStaticPropertyValueRequest,
    ) -> DatasetProperty:
        """Update the value of a static property.

        Args:
            dataset_id: The ID of the dataset
            property_name: The name of the static property
            request: Value update request

        Returns:
            The updated DatasetProperty

        Raises:
            OdpValidationError: If the request is invalid
            requests.HTTPError: For other unexpected HTTP errors
        """
        url = f"{self.catalog_base_url}/datasets/{dataset_id}/properties/{property_name}/value"
        res = self.http_client.put(url, content=request)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 400:
                raise OdpValidationError("Invalid input", res.text) from e
            if res.status_code == 500:
                raise requests.HTTPError(f"Internal server error ({res.status_code}): {res.text}") from e
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}")

        return DatasetProperty(**res.json())

    def delete_static_property(
        self,
        dataset_id: str,
        property_name: str,
    ) -> bool:
        """Delete a static property from a dataset.

        Args:
            dataset_id: The ID of the dataset
            property_name: The name of the property to delete

        Returns:
            True if the deletion was successful

        Raises:
            OdpValidationError: If the request is invalid
            requests.HTTPError: For other unexpected HTTP errors
        """
        url = f"{self.catalog_base_url}/datasets/{dataset_id}/properties/{property_name}"
        res = self.http_client.delete(url)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 400:
                raise OdpValidationError("Invalid input", res.text) from e
            if res.status_code == 500:
                raise requests.HTTPError(f"Internal server error ({res.status_code}): {res.text}") from e
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}")

        return res.json() is True

    def search(self, request: SearchRequest) -> SearchResult:
        """Perform a search with typed payloads."""
        url = f"{self.catalog_base_url}/search"
        res = self.http_client.post(url, content=request)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 400:
                raise OdpValidationError("Invalid input", res.text) from e
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}") from e

        raw = res.json()
        search_result = SearchResult(
            total=raw["total"],
            top_score=SearchScore(**raw["top_score"]) if raw.get("top_score") else None,
            match=raw["match"],
            results=[],
        )

        for item in raw["results"]:
            payload_type = item.get("payload_type")

            if payload_type == PayloadType.DATASET:
                payload = DatasetSearchResultPayload(**item["payload"])
            elif payload_type == PayloadType.DATA_COLLECTION:
                payload = CollectionSearchResultPayload(**item["payload"])
            else:
                payload = item["payload"]

            result_item = ResultItem(
                id=item["id"],
                title=item["title"],
                description=item["description"],
                highlights=item.get("highlights", []),
                match_type=item["match_type"],
                payload_type=payload_type,
                score=SearchScore(**item["score"]),
                payload=payload,
            )
            search_result.results.append(result_item)

        return search_result

    def autocomplete(self, request: AutoCompletionRequest) -> AutoCompletionResult:
        """Perform an autocomplete search.

        Args:
            request: The autocomplete request payload.

        Returns:
            An AutoCompletionResult object.

        Raises:
            OdpValidationError: If the request input is invalid.
            requests.HTTPError: For other unexpected HTTP errors.
        """
        url = f"{self.catalog_base_url}/autocomplete"
        res = self.http_client.post(url, content=request)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 400:
                raise OdpValidationError("Invalid input", res.text) from e
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}") from e

        raw = res.json()
        auto_completion_result = AutoCompletionResult(
            total=raw["total"],
            top_score=AutoCompletionScore(**raw["top_score"]) if raw.get("top_score") else None,
            results=[],
        )

        for item in raw["results"]:
            result_item = AutoCompletionResultItem(
                id=item["id"],
                type=AutoCompletionResultType(item["type"]),
                title=item["title"],
                description=item["description"],
                score=AutoCompletionScore(**item["score"]),
            )
            auto_completion_result.results.append(result_item)

        return auto_completion_result

    def autocomplete_grouped(self, request: AutoCompletionRequest) -> List[AutoCompletionGroupedResult]:
        """Perform a grouped autocomplete search.

        Args:
            request: The autocomplete request payload.

        Returns:
            A list of AutoCompletionGroupedResult objects.

        Raises:
            OdpValidationError: If the request input is invalid.
            requests.HTTPError: For other unexpected HTTP errors.
        """
        url = f"{self.catalog_base_url}/autocomplete/grouped"
        res = self.http_client.post(url, content=request)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 400:
                raise OdpValidationError("Invalid input", res.text) from e
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}") from e

        raw = res.json()
        grouped_results = []

        for group_item in raw:
            result_items = [
                AutoCompletionResultItem(
                    id=item["id"],
                    type=AutoCompletionResultType(item["type"]),
                    title=item["title"],
                    description=item["description"],
                    score=AutoCompletionScore(**item["score"]),
                )
                for item in (group_item["result"].get("results") or [])
            ]

            result = AutoCompletionResult(
                total=group_item["result"]["total"],
                top_score=AutoCompletionScore(**group_item["result"]["top_score"])
                if group_item["result"].get("top_score")
                else None,
                results=result_items,
            )

            grouped_result = AutoCompletionGroupedResult(
                group=AutoCompletionResultType(group_item["group"]), result=result
            )

            grouped_results.append(grouped_result)

        return grouped_results

    def get_all_contributors(
        self,
    ) -> List[Contributor]:
        """Retrieve all contributors.

        Returns:
            A list of Contributor objects

        Raises:
            requests.HTTPError: For unexpected HTTP errors
        """
        url = f"{self.catalog_base_url}/contributors"
        res = self.http_client.get(url)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}") from e

        if res.json():
            return [Contributor(**item) for item in res.json().get("items", [])]
        return []

    def get_contributor(
        self,
        contributor_id: UUID,
    ) -> Optional[Contributor]:
        """Retrieve a contributor.

        Args:
            contributor_id: The ID of the contributor

        Returns:
            A Contributor object

        Raises:
            requests.HTTPError: For unexpected HTTP errors
        """
        url = f"{self.catalog_base_url}/contributors/{str(contributor_id)}"
        res = self.http_client.get(url)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}") from e

        if res.json():
            return Contributor(**res.json())
        return None

    def add_custom_contributor(
        self,
        request: CreateCustomContributorRequest,
    ) -> Contributor:
        """Create a custom contributor.

        Args:
            request: The property creation request

        Returns:
            The created custom contributor

        Raises:
            OdpValidationError: If the request is invalid
            requests.HTTPError: For other unexpected HTTP errors
        """
        url = f"{self.catalog_base_url}/custom-contributors"
        res = self.http_client.post(url, content=request)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 400:
                raise OdpValidationError("Invalid input", res.text) from e
            if res.status_code == 500:
                raise requests.HTTPError(f"Internal server error ({res.status_code}): {res.text}") from e
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}")

        return Contributor(**res.json())

    def add_provider_to_dataset(
        self,
        dataset_id: UUID,
        contributor_id: UUID,
    ) -> Contributor:
        """Add a provider to a dataset.

        Args:
            dataset_id: The ID of the dataset
            contributor_id: The ID of the contributor

        Returns:
            The updated contributor

        Raises:
            OdpValidationError: If the request is invalid
            requests.HTTPError: For other unexpected HTTP errors
        """
        url = f"{self.catalog_base_url}/datasets/{dataset_id}/provider"
        res = self.http_client.post(url, content={"id": str(contributor_id)})
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 400:
                raise OdpValidationError("Invalid input", res.text) from e
            if res.status_code == 500:
                raise requests.HTTPError(f"Internal server error ({res.status_code}): {res.text}") from e
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}")

        return Contributor(**res.json())

    def add_custom_license(
        self,
        request: CreateCustomLicenseRequest,
    ) -> LicenseEntity:
        """Create a custom license.

        Args:
            request: The property creation request

        Returns:
            The created custom license

        Raises:
            OdpValidationError: If the request is invalid
            requests.HTTPError: For other unexpected HTTP errors
        """
        url = f"{self.catalog_base_url}/custom-licenses"
        res = self.http_client.post(url, content=request)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 400:
                raise OdpValidationError("Invalid input", res.text) from e
            if res.status_code == 500:
                raise requests.HTTPError(f"Internal server error ({res.status_code}): {res.text}") from e
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}")

        return LicenseEntity(**res.json())

    def get_all_licenses(
        self,
    ) -> List[LicenseEntity]:
        """Retrieve all licenses.

        Returns:
            A list of LicenseEntity objects

        Raises:
            requests.HTTPError: For unexpected HTTP errors
        """
        url = f"{self.catalog_base_url}/licenses"
        res = self.http_client.get(url)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}") from e

        if res.json():
            return [LicenseEntity(**item) for item in res.json().get("items", [])]
        return []

    def get_license(
        self,
        license_id: UUID,
    ) -> Optional[LicenseEntity]:
        """Retrieve a license.

        Args:
            license_id: The ID of the license

        Returns:
            A LicenseEntity object

        Raises:
            requests.HTTPError: For unexpected HTTP errors
        """
        url = f"{self.catalog_base_url}/licenses/{str(license_id)}"
        res = self.http_client.get(url)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}") from e

        if res.json():
            return LicenseEntity(**res.json())
        return None

    def add_license_to_dataset(
        self,
        dataset_id: UUID,
        license_id: UUID,
    ) -> LicenseEntity:
        """Add a license to a dataset.

        Args:
            dataset_id: The ID of the dataset
            license_id: The ID of the license

        Returns:
            The updated license

        Raises:
            OdpValidationError: If the request is invalid
            requests.HTTPError: For other unexpected HTTP errors
        """
        url = f"{self.catalog_base_url}/datasets/{dataset_id}/license"
        res = self.http_client.post(url, content={"id": str(license_id)})
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == 400:
                raise OdpValidationError("Invalid input", res.text) from e
            if res.status_code == 500:
                raise requests.HTTPError(f"Internal server error ({res.status_code}): {res.text}") from e
            raise requests.HTTPError(f"HTTP Error - {res.status_code}: {res.text}")

        return LicenseEntity(**res.json())
