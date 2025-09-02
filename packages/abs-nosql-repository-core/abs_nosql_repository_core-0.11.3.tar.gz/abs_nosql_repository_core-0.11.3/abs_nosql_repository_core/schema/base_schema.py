from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from enum import Enum
from typing import Optional, Union, List, Any, Literal
from bson import ObjectId

class Operator(str, Enum):
    EQ = "eq"
    NE = "ne"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    IN = "in"
    NIN = "nin"
    LIKE = "like"
    ILIKE = "ilike"
    BETWEEN = "between"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"

class LogicalOperator(str, Enum):
    AND = "and"
    OR = "or"

class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"

class FieldTypeEnum(str, Enum):
    STR = "str"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    LIST = "list"
    DICT = "dict"
    DATETIME = "datetime"

class BaseSchema(BaseModel):
    _id: str
    uuid: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BaseDraftSchema(BaseSchema):
    is_draft: bool = Field(default=True)

# Schema for getting distinct values of a field
class FindUniqueByFieldInput(BaseModel):
    field_name: str
    ordering: Optional[Literal["asc", "desc"]] = None
    page: Optional[int] = Field(default=1)
    page_size: Optional[int] = Field(default=10)
    search: Optional[str] = None

# Primitive field condition
class FieldOperatorCondition(BaseModel):
    field: str
    operator: Operator
    value: Any

# Base structure for a logical group
class LogicalCondition(BaseModel):
    operator: LogicalOperator
    conditions: List["ConditionType"]

# Each item in conditions list can be:
# 1. a logical condition (nested group)
# 2. a dict like {field: ..., operator: ..., value: ...}
ConditionType = Union["LogicalCondition", "FieldOperatorCondition"]

# Top-level filter schema
class FilterSchema(BaseModel):
    operator: LogicalOperator
    conditions: List[ConditionType]

# Sort schema
class SortSchema(BaseModel):
    field: str
    direction: SortDirection

# Schema for displaying search operations
class SearchOptions(BaseModel):
    search: Optional[str] = None
    sort_order: Optional[List[SortSchema]] = None
    page: Optional[int] = None
    page_size: Optional[int] = None
    total_pages: Optional[int] = None
    total_count: Optional[int] = None

# Schema for displaying find operations' result
class ListResponse(BaseModel):
    founds: List[Any]
    search_options: SearchOptions

class AggregationType(str, Enum):
    SUM = "sum"
    AVG = "avg"
    COUNT = "count"
    MAX = "max"
    MIN = "min"

class AggregationSpec(BaseModel):
    field: str
    type: AggregationType
    alias: str

class GroupOptions(BaseModel):
    page: Optional[int] = Field(default=1, description="Page number for group pagination")
    page_size: Optional[int] = Field(default=10, description="Number of groups per page")
    group_id: Optional[dict] = Field(default=None, description="Filter to apply to grouped _id after grouping (was group_filter)")
    sort_by: Optional[List[SortSchema]] = Field(default=None, description="Sort order for groups (columns) (was group_sort_order)")

class Aggregations(BaseModel):
    group_by: List[str]
    document_inclusion_mode: Optional[Literal["none", "all", "partial"]] = Field(
        default="none",
        description="Options: 'none', 'all', 'partial' . 'none' means no document fields will be included in the response, 'all' means all document fields will be included in the response, 'partial' means only the document fields that match the included_fields will be included in the response"
    )
    included_fields: Optional[List[str|dict]] = Field(
        default=None,
        description="Fields to include when document_inclusion_mode is 'partial'"
    )
    aggregation_fields: Optional[List[AggregationSpec]] = None
    group_options: Optional[GroupOptions] = Field(default=None, description="Group-level pagination, filtering, and sorting options")

class FieldRule(BaseModel):
    action: Literal["include", "exclude"]
    field: str
    conditions: Optional[FilterSchema] = None

# Type for aggregation pipeline stages
class AggregationStage(BaseModel):
    pipeline: list = Field(description="The pipeline configuration for the stage")

# Field filter schema for including/excluding specific fields
class FieldFilterSchema(BaseModel):
    type: Literal["include", "exclude"] = Field(
        description="Whether to include or exclude the specified fields"
    )
    fields: List[str|dict] = Field(
        description="List of field names to include or exclude"
    )
class ListFilter(BaseModel):
    pre_filters: Optional[FilterSchema] = None
    filters: Optional[FilterSchema] = None
    sort_order: Optional[List[SortSchema]] = None
    page: Optional[int] = Field(default=1)
    page_size: Optional[int] = Field(default=20)
    search: Optional[str] = None
    searchable_fields: Optional[List[str]] = None
    field_rules: Optional[List[FieldRule]] = None
    reference_fields: Optional[AggregationStage] = None
    aggregations: Optional[Aggregations] = None
    field_filter: Optional[FieldFilterSchema] = None

class EmbeddingSchema(BaseModel):
    container_name: str

class AuditActionType(str,Enum):
    CREATION = "creation"
    UPDATION = "updation"
    DELETION = "deletion"
    BULK_CREATION = "bulk_creation"
    BULK_UPDATION = "bulk_updation"
    BULK_DELETION = "bulk_deletion"
    OTHER = "other"

class AuditSourceSchema(BaseModel):
    ip: Optional[str] = None

class AuditLogSchema(BaseModel):
    target_type: Optional[str] = None
    target_id: Optional[Union[str,ObjectId]] = None
    action_type: Optional[AuditActionType] = None
    user_id: Optional[Union[str,ObjectId,int]] = None
    app_id: Optional[Union[str,ObjectId]] = None
    entity_id: Optional[Union[str,ObjectId]] = None
    source: Optional[AuditSourceSchema] = None
    collection_name: Optional[str] = None
    data: Optional[Any] = None
    ai_system_generated: bool = Field(default=False)

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
