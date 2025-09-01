from typing import Any, List, Optional, Set

from ..resource import ResourceDto, ResourceSpec
from ..resource_registry import DEFAULT_RESOURCE_TYPE_REGISTRY
from .distribution import Distribution
from .observable import ObservableDto
from odp.util.cheapdantic import Field


class DataCollectionSpec(ResourceSpec):
    distribution: Optional[Distribution] = None
    """Information on how the dataset was distributed"""

    tags: Set[str] = Field(default_factory=set)
    """Tags for the dataset"""

    facets: Optional[dict[str, Any]] = None
    """Facets for the dataset"""

    observables: List[ObservableDto] = Field(default_factory=list)
    """Observables for the data collection"""


class DataCollectionDto(ResourceDto):
    _kind: str = "catalog.hubocean.io/dataCollection"
    _version: str = "v1alpha1"

    spec: DataCollectionSpec


DEFAULT_RESOURCE_TYPE_REGISTRY.add(DataCollectionDto)
