from datetime import datetime
from typing import Any, Dict, Optional, Union
from uuid import UUID

from odp.util.cheapdantic import BaseModel


class FileMetadataDto(BaseModel):
    """File Metadata Model."""

    name: str
    mime_type: Optional[str] = None
    dataset: Optional[UUID] = None
    metadata: Dict[str, Union[bool, int, str]] = {}
    geo_location: Optional[Any] = None
    size_bytes: Optional[int] = None
    checksum: Optional[str] = None
    created_time: Optional[datetime] = None
    modified_time: Optional[datetime] = None
    deleted_time: Optional[datetime] = None

    def __init__(self, name: str, **kwargs):
        if name.startswith("/"):
            raise ValueError("name cannot start with '/'. Absolute paths are not allowed.")
        super().__init__(name=name, **kwargs)
