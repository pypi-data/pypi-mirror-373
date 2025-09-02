from abc import ABC
from datetime import datetime
from typing import Optional, Union
from uuid import UUID

from .metadata import MetadataDto
from .resource_registry import DEFAULT_RESOURCE_TYPE_REGISTRY
from .resource_status import ResourceStatus
from .validators import validate_resource_kind, validate_resource_version
from odp.util.cheapdantic import BaseModel


class ResourceSpec(BaseModel, ABC):
    class Config:
        extra = "allow"


class ResourceDto(BaseModel):
    """Resource Data Transmission Object (DTO) representing a resource manifest"""

    kind: str = None
    """kind is the kind of the resource."""

    version: str = None
    """version is the version of the resource."""

    metadata: MetadataDto
    """metadata is the metadata of the resource."""

    status: Optional[ResourceStatus] = None
    """status is the status of the resource."""

    spec: ResourceSpec
    """Resource spec"""

    def __init__(self, **kwargs):
        kwargs["kind"] = self._populate_kind(kwargs.get("kind"))
        kwargs["version"] = self._populate_version(kwargs.get("version"))
        super().__init__(**kwargs)

    @classmethod
    def create(
        cls,
        kind: str,
        version: str,
        metadata: MetadataDto,
        spec: ResourceSpec,
        status: Optional[ResourceStatus] = None,
    ) -> "ResourceDto":
        promoted_cls = DEFAULT_RESOURCE_TYPE_REGISTRY.get(kind, version, ResourceDto)
        return promoted_cls(kind=kind, version=version, metadata=metadata, spec=spec, status=status)

    def _populate_kind(cls, v) -> str:
        kind = cls.get_kind()
        if not kind:
            kind = v
        elif v and v != kind:
            raise ValueError(f"Invalid kind '{v}' for resource '{cls.__name__}' - expected '{kind}'")
        return validate_resource_kind(kind)

    def _populate_version(cls, v) -> str:
        version = cls.get_version()
        if not version:
            version = v
        elif v and v != version:
            raise ValueError(f"Invalid version '{v}' for resource '{cls.__name__}' - expected '{version}")
        return validate_resource_version(version)

    def populate_status(self, created_by: UUID):
        cls = DEFAULT_RESOURCE_TYPE_REGISTRY.get(self.kind, self.version, None)

        if cls and cls != type(self):
            cls.populate_status(self, created_by)
        else:
            if self.status is not None:
                raise ValueError("Resource status already set")

            self.status = ResourceStatus.create(created_by)

    def update_status(self, updated_by: UUID):
        cls = DEFAULT_RESOURCE_TYPE_REGISTRY.get(self.kind, self.version, None)

        if cls and cls != type(self):
            cls.update_status(self, updated_by)
        else:
            if self.status is None:
                raise ValueError("Resource status not set")

            self.status.num_updates += 1
            self.status.updated_time = datetime.now()
            self.status.updated_by = updated_by

    @property
    def qualified_name(self) -> str:
        """Return the qualified name of the resource

        The qualified name of resource is the concatenation of the resource kind and name, separated by a slash.
        """
        return f"{self.kind}/{self.metadata.name}"

    @property
    def uuid(self) -> Optional[UUID]:
        """Return the UUID of the resource"""
        return self.metadata.uuid

    @classmethod
    def get_kind(cls) -> str:
        """Return the kind of the resource"""
        return getattr(cls, "_kind", None)

    @classmethod
    def get_version(cls) -> str:
        """Return the version of the resource"""
        return getattr(cls, "_version", None)

    def get_ref(self) -> Union[UUID, str]:
        """Get a valid reference to the resource

        Returns:
            The resource UUID if it is set, the qualified name otherwise
        """
        return self.uuid or self.qualified_name
