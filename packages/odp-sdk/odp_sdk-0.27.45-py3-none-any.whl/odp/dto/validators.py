import re
from typing import Any, Dict, Mapping, Optional, Union

import jsonschema

RX_RESOURCE_NAME = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9\-_.]*")
RX_RESOURCE_KIND = re.compile(r"^(?:[a-zA-Z0-9][a-zA-Z0-9\-_\.]*)\/(?:[a-zA-Z0-9][a-zA-Z0-9\-_\.]*)$")
RX_RESOURCE_VERSION = re.compile(r"^v[0-9]+(?:(?:alpha|beta)[0-9]+)?$")
RX_DOI = r"^(?:doi:\/\/)?(10\.[0-9]{4,9}(?:\.[0-9]+)*\/(?:(?![%\"#?\s])\S)+)$"


def validate_resource_version(val: str) -> str:
    if not RX_RESOURCE_VERSION.fullmatch(val):
        raise ValueError(f"Invalid resource version: {val}")
    return val


def validate_resource_kind(val: str) -> str:
    if not RX_RESOURCE_KIND.fullmatch(val):
        raise ValueError(f"Invalid resource kind: {val}")
    return val


def validate_resource_name(val: str) -> str:
    if not RX_RESOURCE_NAME.fullmatch(val):
        raise ValueError(f"Invalid resource component: {val}")
    return val


def validate_doi(val: Optional[str]) -> Optional[str]:
    if val is not None and not re.fullmatch(RX_DOI, val):
        raise ValueError(f"Invalid DOI: {val}")
    return val


def validate_json_schema(v: Union[bool, Mapping[str, Any]]) -> Union[bool, Mapping[str, Any]]:
    try:
        jsonschema.Draft4Validator.check_schema(v)
    except jsonschema.SchemaError as e:
        raise ValueError(f"Schema is invalid: {e.message}") from e
    return v


def validate_at_least_one_not_null(values: Dict[Any, Any]) -> Dict[Any, Any]:
    if not any(values.values()):
        raise ValueError(f"One of the fields must be set: {list(values.keys())}")

    return values
