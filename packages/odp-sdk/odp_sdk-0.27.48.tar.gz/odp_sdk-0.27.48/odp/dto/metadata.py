from typing import Dict, Optional
from uuid import UUID

from odp.dto.validators import validate_resource_name
from odp.util.cheapdantic import BaseModel, Field


class MetadataDto(BaseModel):
    """Resource manifest metadata"""

    name: str
    """Resource name. Must consist of alphanumeric characters, dashes or underscores and must start
    with an alphanumeric character"""

    display_name: Optional[str] = None
    """Human-friendly name"""

    description: Optional[str] = None
    """Resource description"""

    uuid: Optional[UUID] = None
    """System-assigned unique identifier"""

    labels: Dict = Field(default_factory=dict)
    """Resource labels"""

    owner: Optional[UUID] = None

    def __init__(self, **kwargs):
        kwargs["name"] = validate_resource_name(kwargs.get("name"))
        super().__init__(**kwargs)
