from typing import Any, Dict, List, Optional, Set

from ..common.contact_info import ContactInfo
from ..resource import ResourceDto, ResourceSpec
from ..resource_registry import DEFAULT_RESOURCE_TYPE_REGISTRY
from ..validators import validate_at_least_one_not_null, validate_doi
from .distribution import Distribution
from .observable import ObservableDto
from odp.util.cheapdantic import BaseModel, Field


class Citation(BaseModel):
    """Citation information"""

    cite_as: Optional[str] = None
    """Directions on how to cite the dataset"""

    doi: Optional[str] = None

    def __init__(self, **kwargs):
        kwargs = validate_at_least_one_not_null(kwargs)
        kwargs["doi"] = validate_doi(kwargs.get("doi"))

        super().__init__(**kwargs)


class Attribute(BaseModel):
    """Dataset attribute"""

    name: str
    """Attribute name. This can be a column name in a table, a dimension in an array, etc."""

    description: Optional[str] = None
    """Attribute description"""

    traits: list[str]
    """List of traits. Traits are used to describe the attribute in more detail.

    Traits are based on Microsoft Common Data Model (CDM) traits. See the [CDM documentation]
    (https://learn.microsoft.com/en-us/common-data-model/sdk/trait-concepts-and-use-cases#what-are-traits)
    for more information.
    """


class DatasetSpec(ResourceSpec):
    distribution: Optional[Distribution] = None
    """Information on how the dataset was distributed"""

    storage_class: str
    """Storage class qualified name"""

    storage_controller: Optional[str] = None
    """Storage controller qualified name"""

    data_collection: Optional[str] = None
    """Data collection qualified name"""

    maintainer: ContactInfo
    """Active maintainer information"""

    citation: Optional[Citation] = None
    """Citation information"""

    documentation: List[str] = Field(default_factory=list)
    """Links to any relevant documentation"""

    attributes: List[Attribute] = Field(default_factory=list)
    """Dataset attributes"""

    facets: Optional[Dict[str, Any]] = None
    """Facets for the dataset"""

    observables: List[ObservableDto] = Field(default_factory=list)
    """Observables for the dataset"""

    tags: Set[str] = Field(default_factory=set)


class DatasetDto(ResourceDto):
    _kind: str = "catalog.hubocean.io/dataset"
    _version: str = "v1alpha3"

    spec: DatasetSpec


DEFAULT_RESOURCE_TYPE_REGISTRY.add(DatasetDto)
