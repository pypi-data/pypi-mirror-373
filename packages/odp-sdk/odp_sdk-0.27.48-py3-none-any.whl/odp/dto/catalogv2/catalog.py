from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from odp.util.cheapdantic import BaseModel, Field


class Visibility(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"


class PublishStatus(str, Enum):
    PUBLISHED = "published"
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    ARCHIVED = "archived"


class LicenseEntryType(str, Enum):
    CUSTOM = "custom"
    ENUM = "enum"


class ContributorEntryType(str, Enum):
    CURATED = "curated"
    CUSTOM = "custom"


class ContributorKind(str, Enum):
    PERSON = "person"
    ORG = "org"


class DatasetPropertyType(str, Enum):
    STATIC = "static"
    COMPUTED = "computed"


class DatasetPropertyDataType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATE_RANGE = "date_range"
    GEO = "geo"
    BIG = "big"


class ContributorRole(str, Enum):
    PUBLISHER = "publisher"
    AGGREGATOR = "aggregator"
    MAINTAINER = "maintainer"
    CREATOR = "creator"
    RIGHTS_HOLDER = "rights_holder"
    CONTRIBUTOR = "contributor"


class AuditFields(BaseModel):
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_by: Optional[str] = None
    updated_at: Optional[str] = None


class Constraint(BaseModel):
    text: str


class Citation(BaseModel):
    text: str
    link: Optional[str] = None


class Aggregation(BaseModel):
    value: str
    audit_fields: Optional[AuditFields] = None


class DatasetProperty(BaseModel):
    name: str
    description: Optional[str] = None
    type: DatasetPropertyType
    value: Any
    aggregations: Dict[str, Aggregation] = Field(default_factory=dict)
    unit: Optional[str] = None
    annotations: Dict[str, str] = Field(default_factory=dict)


class LicenseEntity(BaseModel):
    id: UUID
    name: Optional[str] = None
    enum_val: Optional[str] = None
    entry_type: LicenseEntryType
    text: Optional[str] = None
    url: Optional[str] = None
    audit_fields: Optional[AuditFields] = None


class Contributor(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    parent_id: Optional[UUID] = None
    kind: Optional[ContributorKind] = None
    entry_type: ContributorEntryType
    audit_fields: Optional[AuditFields] = None


class DataCollection(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    owner: Optional[str] = None
    visibility: Visibility
    deleted: bool = False
    datasets: List["Dataset"] = Field(default_factory=list)
    audit_fields: Optional[AuditFields] = None


class Dataset(BaseModel):
    id: Optional[UUID] = None
    name: Optional[str] = None
    description: Optional[str] = None
    provider: Optional[Contributor] = None
    constraints: List[Constraint] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)
    contributors: Dict[ContributorRole, List[Contributor]] = Field(default_factory=dict)
    license: Optional[LicenseEntity] = None
    lineage: Optional[Dict[str, List["Dataset"]]] = None
    tags: List[str] = Field(default_factory=list)
    visibility: Visibility
    deleted: bool = False
    read_only: bool = False
    publish_status: PublishStatus
    published_at: Optional[str] = None
    properties: List[DatasetProperty] = Field(default_factory=list)
    owner: Optional[str] = None
    collection: Optional[DataCollection] = None
    additional_info: Dict[str, Any] = Field(default_factory=dict)
    internal_data: Dict[str, Any] = Field(default_factory=dict)
    documentation: List[str] = Field(default_factory=list)
    last_check_for_update: Optional[str] = None
    audit_fields: AuditFields


class CustomContributor(BaseModel):
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    kind: Optional[ContributorKind] = None


class DatasetContributorRequest(BaseModel):
    contributor_id: str


class DatasetLicenseDto(BaseModel):
    name: str
    text: str
    url: str


class CreateDatasetRequest(BaseModel):
    id: Optional[UUID] = None
    name: str
    description: str
    provider_id: Optional[str] = None
    custom_provider: Optional[CustomContributor] = None
    constraints: List[Constraint] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)
    contributors: Dict[str, List[DatasetContributorRequest]] = Field(default_factory=dict)
    custom_license: Optional[DatasetLicenseDto] = None
    license_enum: Optional[str] = None
    lineage: Dict[str, List[str]] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    additional_info: Dict[str, Any] = Field(default_factory=dict)
    internal_data: Dict[str, Any] = Field(default_factory=dict)
    last_check_for_update: Optional[str] = None
    documentation: List[str] = Field(default_factory=list)


class UpdateDatasetRequest(CreateDatasetRequest):
    name: str
    description: str
    provider_id: Optional[str] = None
    custom_provider: Optional[CustomContributor] = None
    constraints: List[Constraint] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)
    contributors: Dict[str, List[DatasetContributorRequest]] = Field(default_factory=dict)
    custom_license: Optional[DatasetLicenseDto] = None
    license_enum: Optional[str] = None
    lineage: Dict[str, List[str]] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    additional_info: Dict[str, Any] = Field(default_factory=dict)
    last_check_for_update: Optional[str] = None
    documentation: List[str] = Field(default_factory=list)


class CreateDataCollectionRequest(BaseModel):
    id: Optional[UUID] = None
    name: str
    description: str


class UpdateDataCollectionRequest(BaseModel):
    name: str
    description: str


class DatasetPermissionStates(BaseModel):
    visibility: str
    read_only: bool
    publish_status: str


class DataCollectionPermissionStates(BaseModel):
    visibility: str


class CreateStaticPropertyRequest(BaseModel):
    name: str
    description: Optional[str] = None
    data_type: DatasetPropertyDataType
    value: Any
    unit: Optional[str] = None
    annotations: Dict[str, str] = Field(default_factory=dict)


class UpdateStaticPropertyMetadataRequest(BaseModel):
    description: Optional[str] = None
    unit: Optional[str] = None
    annotations: Dict[str, str] = Field(default_factory=dict)


class UpdateStaticPropertyValueRequest(BaseModel):
    value: Any


class CreateCustomLicenseRequest(BaseModel):
    id: str
    name: str
    text: str
    url: str


class CreateCustomContributorRequest(BaseModel):
    id: str
    name: str
    description: str
    website: Optional[str] = None
    email: Optional[str] = None
    kind: ContributorKind
