import re
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator

from whiskerrag_types.model.tagging import TagObjectType
from whiskerrag_types.model.timeStampedModel import TimeStampedModel


class TagCreate(BaseModel):
    name: str = Field(..., max_length=64, description="标签名称（租户内唯一）")
    description: Optional[str] = Field(
        default=None, max_length=255, description="标签描述"
    )
    object_type: TagObjectType = Field(
        default=TagObjectType.SPACE, description='标签作用对象类型（如 "space"）'
    )

    @field_validator("name", mode="before")
    @classmethod
    def _normalize_name(cls, v: Any) -> Any:
        if isinstance(v, str):
            s = v.strip().lower()
            # 禁止常见特殊字符
            if re.search(
                r"[~`!@#$%^&*()+={}\[\]|\\:;\"'<>,.?/￥…（）—【】「」‘’”“]", s
            ):
                raise ValueError("name 不允许包含空格或常见特殊字符")
            return s
        return v

    @model_validator(mode="before")
    def _normalize_object_type(cls, data: dict) -> dict:
        if isinstance(data.get("object_type"), str):
            data["object_type"] = data["object_type"].lower()
        return data


class Tag(TagCreate, TimeStampedModel):
    tag_id: str = Field(
        default_factory=lambda: str(uuid4()), description="标签ID（UUID字符串）"
    )
    tenant_id: str = Field(..., max_length=64, description="所属租户ID")
    object_type: TagObjectType = Field(
        default=TagObjectType.SPACE, description='标签作用对象类型（如 "space"）'
    )

    def update(self, **kwargs: Any) -> "Tag":
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.updated_at = datetime.now(timezone.utc)
        return self

    @model_validator(mode="before")
    def _convert_uuid_to_str(cls, data: dict) -> dict:
        for field, value in list(data.items()):
            if isinstance(value, UUID):
                data[field] = str(value)
        return data
