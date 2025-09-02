from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from deprecated import deprecated
from pydantic import BaseModel, Field, model_validator

T = TypeVar("T")


class Operator(str, Enum):
    AND = "and"
    OR = "or"


class Condition(BaseModel):
    field: str
    operator: str  # eq, neq, gt, gte, lt, lte, like, ilike
    value: Any


class FilterGroup(BaseModel):
    operator: Operator
    conditions: List[Union[Condition, "FilterGroup"]]


# 允许 FilterGroup 递归引用
FilterGroup.model_rebuild()


# 标签筛选允许的字段白名单
TAGGING_ALLOWED_FIELDS = {"tag_name", "tag_id"}


class TagFilter(BaseModel):
    """
    针对 Tagging 表的过滤条件。
    注意：object_id / object_type 不作为用户输入过滤字段。
    """

    advanced_filter: Optional[FilterGroup] = Field(
        default=None, description="标签过滤条件，只允许 tag_name 和 tag_id"
    )

    @model_validator(mode="after")
    def validate_tag_fields(self) -> "TagFilter":
        if self.advanced_filter:
            invalid_fields = self._validate_tag_filter_group(self.advanced_filter)
            if invalid_fields:
                raise ValueError(
                    f"Invalid tag_filter fields: {invalid_fields}; "
                    f"only {TAGGING_ALLOWED_FIELDS} are supported"
                )
        return self

    def _validate_tag_filter_group(self, filter_group: FilterGroup) -> set[str]:
        invalid = set()
        for condition in filter_group.conditions:
            if isinstance(condition, Condition):
                if condition.field not in TAGGING_ALLOWED_FIELDS:
                    invalid.add(condition.field)
            elif isinstance(condition, FilterGroup):
                invalid.update(self._validate_tag_filter_group(condition))
        return invalid


class QueryParams(BaseModel, Generic[T]):
    order_by: Optional[str] = Field(default=None, description="order by field")
    order_direction: Optional[str] = Field(default="asc", description="asc or desc")
    eq_conditions: Optional[Dict[str, Any]] = Field(
        default=None,
        description="list of equality conditions, each as a dict with key and value",
    )
    advanced_filter: Optional[FilterGroup] = Field(
        default=None,
        description="advanced filter with nested conditions",
    )
    # 标签过滤
    tag_filter: Optional[TagFilter] = Field(
        default=None, description="标签过滤条件 tag_name 和 tag_id"
    )

    def _validate_fields_against_model(self, fields: set[str]) -> set[str]:
        """validate fields against model"""
        args = self.__class__.__pydantic_generic_metadata__["args"]
        if not args:
            return set()

        model_type = args[0]
        if isinstance(model_type, TypeVar):
            return set()

        # Get all valid field names including aliases
        valid_fields = set()
        for field_name, field_info in model_type.model_fields.items():
            valid_fields.add(field_name)
            # Add alias if it exists
            if field_info.alias:
                valid_fields.add(field_info.alias)

        return fields - valid_fields

    def _validate_filter_group(self, filter_group: FilterGroup) -> set[str]:
        """recursively validate all fields in FilterGroup"""
        invalid_fields = set()

        for condition in filter_group.conditions:
            if isinstance(condition, Condition):
                invalid_fields.add(condition.field)
            elif isinstance(condition, FilterGroup):
                invalid_fields.update(self._validate_filter_group(condition))

        return invalid_fields

    @model_validator(mode="after")
    def validate_conditions(self) -> "QueryParams[T]":
        invalid_fields = set()

        # validate eq_conditions
        if self.eq_conditions:
            invalid_fields.update(
                self._validate_fields_against_model(set(self.eq_conditions.keys()))
            )

        # validate advanced_filter
        if self.advanced_filter:
            filter_fields = self._validate_filter_group(self.advanced_filter)
            invalid_fields.update(self._validate_fields_against_model(filter_fields))

        # if invalid fields, raise exception
        if invalid_fields:
            raise ValueError(f"Invalid fields found: {invalid_fields}")

        return self


class PageQueryParams(QueryParams[T], Generic[T]):
    page: int = Field(default=1, ge=1, description="page number")
    page_size: int = Field(default=10, ge=1, le=1000, description="page size")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


@deprecated(reason="Use PageQueryParams instead")
class PageParams(PageQueryParams[T], Generic[T]):
    pass


class PageResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class StatusStatisticsPageResponse(PageResponse, Generic[T]):
    """
    TaskStatus
    """

    success: int = 0
    failed: int = 0
    cancelled: int = 0
    pending: int = 0
    running: int = 0
    pending_retry: int = 0
    deleted: int = 0
