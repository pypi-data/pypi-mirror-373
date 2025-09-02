import re
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator

from whiskerrag_types.model.timeStampedModel import TimeStampedModel


class TagObjectType(str, Enum):
    """
    可打标签的对象类型。
    """

    SPACE = "space"
    KNOWLEDGE = "knowledge"


class TaggingCreate(BaseModel):

    tag_name: str = Field(
        ..., max_length=64, description="标签名称（在 object_type 内唯一）"
    )
    object_type: TagObjectType = Field(
        default=TagObjectType.SPACE, description='对象类型，当前仅支持 "space"'
    )
    object_id: str = Field(
        ..., max_length=255, description="被打标签对象ID（如 space_id）"
    )

    @field_validator("tag_name", mode="before")
    @classmethod
    def _normalize_tag_name(cls, v: Any) -> Any:
        if isinstance(v, str):
            s = v.strip().lower()
            if re.search(
                r"[~`!@#$%^&*()+={}\[\]|\\:;\"'<>,.?/￥…（）—【】「」‘’”“]", s
            ):
                raise ValueError("tag name 不允许包含空格或常见特殊字符")
            return s
        return v

    @field_validator("object_id", mode="before")
    @classmethod
    def _trim_object_id(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip()
        return v

    @model_validator(mode="before")
    def _normalize(cls, data: dict) -> dict:
        # 归一对象类型大小写，兼容字符串入参
        if isinstance(data.get("object_type"), str):
            data["object_type"] = data["object_type"].lower()
        return data


class Tagging(TimeStampedModel):
    tagging_id: str = Field(
        default_factory=lambda: str(uuid4()), description="标签绑定ID（UUID字符串）"
    )
    tenant_id: str = Field(..., max_length=64, description="所属租户ID")
    tag_id: str = Field(..., description="标签ID（FK -> tag.tag_id，UUID字符串）")
    tag_name: str = Field(
        ..., max_length=64, description="标签名称（在 object_type 内唯一）"
    )
    object_id: str = Field(
        ..., max_length=255, description="被打标签对象ID（如 space_id）"
    )
    object_type: TagObjectType = Field(
        default=TagObjectType.SPACE,
        description='对象类型，当前仅支持 "space"',
        max_length=32,
    )

    def update(self, **kwargs: Any) -> "Tagging":
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.updated_at = datetime.now(timezone.utc)
        return self

    @model_validator(mode="before")
    def _preprocess(cls, data: dict) -> dict:
        # UUID -> str
        for field, value in list(data.items()):
            if isinstance(value, UUID):
                data[field] = str(value)

        # 归一对象类型大小写
        if isinstance(data.get("object_type"), str):
            data["object_type"] = data["object_type"].lower()

        return data
