from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from odp.util.cheapdantic import BaseModel, Field


class PayloadType(str, Enum):
    DATASET = "dataset"
    DATA_COLLECTION = "data_collection"


class AutoCompletionResultType(str, Enum):
    DATASET = "dataset"
    DATA_COLLECTION = "data_collection"
    TAG = "tag"
    CONTRIBUTOR = "contributor"
    REGION = "region"
    LICENSE = "license"


class SearchScore(BaseModel):
    full_text_search_score: Optional[float] = None
    exact_match_score: Optional[float] = None
    trigram_match_score: Optional[float] = None
    levenshtein_match_score: Optional[float] = None
    total_score: Optional[float] = None


class DatasetSearchResultPayload(BaseModel):
    id: str
    title: str
    title_highlight: str
    description: str
    description_highlight: str
    tags: List[str] = Field(default_factory=list)
    tags_highlight: str


class CollectionSearchResultPayload(BaseModel):
    id: str
    title: str
    title_highlight: str
    description: str
    description_highlight: str


class ResultItem(BaseModel):
    id: str
    title: str
    description: str
    highlights: List[str] = Field(default_factory=list)
    match_type: str
    payload_type: PayloadType
    score: SearchScore
    payload: Union[DatasetSearchResultPayload, CollectionSearchResultPayload, dict]


class SearchResult(BaseModel):
    total: int
    top_score: Optional[SearchScore] = None
    match: bool
    results: List[ResultItem] = Field(default_factory=list)


# --- Search Request ---


class SearchFilter(BaseModel):
    tags: List[str] = Field(default_factory=list)
    types: List[PayloadType] = Field(default_factory=list)
    contributor_id: Optional[str] = None
    license_id: Optional[str] = None
    from_time: Optional[datetime] = None
    to_time: Optional[datetime] = None
    within: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    size: Optional[int] = None
    page: Optional[int] = None
    filter: Optional[SearchFilter]


class AutoCompletionScore(BaseModel):
    rank: float
    similarity: float
    edit_distance: int


class AutoCompletionResultItem(BaseModel):
    id: str
    type: AutoCompletionResultType
    title: str
    description: str
    score: AutoCompletionScore


class AutoCompletionResult(BaseModel):
    total: int
    top_score: Optional[AutoCompletionScore] = None
    results: List[AutoCompletionResultItem] = Field(default_factory=list)


class AutoCompletionGroupedResult(BaseModel):
    group: AutoCompletionResultType
    result: AutoCompletionResult


class AutoCompletionRequest(BaseModel):
    query: str
    size: Optional[int] = None
