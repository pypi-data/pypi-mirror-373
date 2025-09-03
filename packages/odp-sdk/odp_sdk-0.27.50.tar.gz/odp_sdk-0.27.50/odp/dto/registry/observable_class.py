from typing import Any, Dict

import jsonschema

from ..resource import ResourceDto, ResourceSpec
from ..resource_registry import DEFAULT_RESOURCE_TYPE_REGISTRY
from ..validators import validate_json_schema


class ObservableClassSpec(ResourceSpec):
    observable_schema: Dict
    """JSON Schema for the observable class"""

    def __init__(self, **kwargs):
        kwargs["observable_schema"] = validate_json_schema(kwargs.get("observable_schema"))
        super().__init__(**kwargs)

    def validate_dict(self, d: Dict[str, Any]):
        try:
            jsonschema.validate(instance=d, schema=self.observable_schema)
        except jsonschema.ValidationError as e:
            raise ValueError(f"Observable details do not match schema: {e.message}") from e


class ObservableClassDto(ResourceDto):
    _kind: str = "catalog.hubocean.io/observableClass"
    _version: str = "v1alpha1"

    spec: ObservableClassSpec


DEFAULT_RESOURCE_TYPE_REGISTRY.add(ObservableClassDto)
