from typing import Dict

from ..resource import ResourceDto, ResourceSpec
from ..resource_registry import DEFAULT_RESOURCE_TYPE_REGISTRY
from ..validators import validate_resource_name


class ObservableSpec(ResourceSpec):
    observable_class: str
    """Qualified name of the observable class"""

    ref: str
    """Qualified name of associated dataset or data collection"""

    details: Dict
    """Full observable object"""

    _validate_ref = validate_resource_name(
        "ref",
    )
    _validate_observable_class = validate_resource_name(
        "observable_class",
    )


class ObservableDto(ResourceDto):
    _kind: str = "catalog.hubocean.io/observable"
    _version: str = "v1alpha2"

    spec: ObservableSpec


DEFAULT_RESOURCE_TYPE_REGISTRY.add(ObservableDto)
