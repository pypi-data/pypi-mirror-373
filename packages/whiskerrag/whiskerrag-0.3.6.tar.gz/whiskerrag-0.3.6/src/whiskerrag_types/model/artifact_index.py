from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator

from whiskerrag_types.model.timeStampedModel import TimeStampedModel


class ArtifactIndexCreate(BaseModel):
    """
    创建 whisker_artifact_index 条目的入参模型
    """

    ecosystem: str = Field(
        ...,
        max_length=32,
        description="制品来源生态系统（pypi / npm / maven / go / php）",
    )
    name: str = Field(
        ...,
        max_length=255,
        description="制品名（构建产物名，如 requests / @company/sdk）",
    )
    version: Optional[str] = Field(
        default=None, max_length=64, description="版本号（可为空）"
    )
    space_id: str = Field(
        ...,
        max_length=255,
        pattern=r"^[A-Za-z0-9._@/-]{1,255}$",
        description="关联的 whisker_space.space_id",
    )
    extra: Dict[str, Any] = Field(
        default={}, description="额外元数据信息，扩展用，如构建参数、标签、扫描信息等"
    )

    @field_validator("space_id")
    @classmethod
    def check_forbidden_sequences(cls, v: str) -> str:
        if ".." in v:
            raise ValueError("space_id cannot contain consecutive dots '..'")
        if "//" in v:
            raise ValueError("space_id cannot contain consecutive slashes '//'")
        return v

    @field_validator("ecosystem")
    @classmethod
    def normalize_ecosystem(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("name")
    @classmethod
    def normalize_name(cls, v: str) -> str:
        return v.strip() if isinstance(v, str) else v


class ArtifactIndex(ArtifactIndexCreate, TimeStampedModel):
    """
    whisker_artifact_index 模型
    """

    artifact_id: str = Field(
        default_factory=lambda: str(uuid4()), description="制品索引表主键（UUID字符串）"
    )

    def update(self, **kwargs: Any) -> "ArtifactIndex":
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.updated_at = datetime.now(timezone.utc)
        return self

    @model_validator(mode="before")
    def preprocess(cls, data: dict) -> dict:
        for field, value in list(data.items()):
            if isinstance(value, UUID):
                data[field] = str(value)
        return data
