import logging
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, List, Optional, TypeVar, Union

from pydantic import BaseModel

from whiskerrag_types.model import (
    APIKey,
    Knowledge,
    PageQueryParams,
    PageResponse,
    Space,
    Task,
    TaskStatus,
    Tenant,
)
from whiskerrag_types.model.artifact_index import ArtifactIndex, ArtifactIndexCreate
from whiskerrag_types.model.chunk import Chunk
from whiskerrag_types.model.retrieval import (
    RetrievalByKnowledgeRequest,
    RetrievalBySpaceRequest,
    RetrievalChunk,
    RetrievalRequest,
)
from whiskerrag_types.model.tag import Tag, TagCreate
from whiskerrag_types.model.tagging import Tagging, TaggingCreate

from .settings_interface import SettingsInterface

T = TypeVar("T", bound=BaseModel)


class DBPluginInterface(ABC):
    settings: SettingsInterface

    def __init__(self, settings: SettingsInterface) -> None:
        self.settings = settings
        self.logger = logging.getLogger("whisker")
        self._initialized: bool = False

    async def ensure_initialized(self) -> None:
        if not self._initialized:
            try:
                self.logger.info("DBEngine plugin is initializing...")
                await self.init()
                self._initialized = True
                self.logger.info("DBEngine plugin is initialized")
            except Exception as e:
                self.logger.error(f"DBEngine plugin init error: {e}")
                raise

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    @abstractmethod
    async def init(self) -> None:
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        pass

    @abstractmethod
    def get_db_client(self) -> Any:
        pass

    # =================== knowledge ===================
    @abstractmethod
    async def save_knowledge_list(
        self, knowledge_list: List[Knowledge]
    ) -> List[Knowledge]:
        pass

    @abstractmethod
    async def get_knowledge_list(
        self, tenant_id: str, page_params: PageQueryParams[Knowledge]
    ) -> PageResponse[Knowledge]:
        pass

    @abstractmethod
    async def get_knowledge(self, tenant_id: str, knowledge_id: str) -> Knowledge:
        pass

    @abstractmethod
    async def update_knowledge(self, knowledge: Knowledge) -> None:
        pass

    @abstractmethod
    async def delete_knowledge(
        self, tenant_id: str, knowledge_id_list: List[str], cascade: bool = False
    ) -> None:
        pass

    @abstractmethod
    async def batch_update_knowledge_retrieval_count(
        self, knowledge_id_list: dict[str, int]
    ) -> None:
        pass

    @abstractmethod
    async def update_knowledge_enabled_status(
        self, tenant_id: str, knowledge_id: str, enabled: bool
    ) -> None:
        pass

    # =================== Space ===================
    @abstractmethod
    async def save_space(self, space: Space) -> Space:
        pass

    @abstractmethod
    async def update_space(self, space: Space) -> Space:
        pass

    @abstractmethod
    async def get_space_list(
        self, tenant_id: str, page_params: PageQueryParams[Space]
    ) -> PageResponse[Space]:
        pass

    @abstractmethod
    async def get_space(self, tenant_id: str, space_id: str) -> Space:
        pass

    @abstractmethod
    async def delete_space(
        self, tenant_id: str, space_id: str
    ) -> Union[List[Space], None]:
        pass

    # =================== chunk ===================
    @abstractmethod
    async def save_chunk_list(self, chunks: List[Chunk]) -> List[Chunk]:
        pass

    @abstractmethod
    async def update_chunk_list(self, chunks: List[Chunk]) -> List[Chunk]:
        pass

    @abstractmethod
    async def get_chunk_list(
        self, tenant_id: str, page_params: PageQueryParams[Chunk]
    ) -> PageResponse[Chunk]:
        pass

    @abstractmethod
    async def get_chunk_by_id(
        self, tenant_id: str, chunk_id: str, embedding_model_name: str
    ) -> Union[Chunk, None]:
        pass

    @abstractmethod
    async def delete_chunk_by_id(
        self, tenant_id: str, chunk_id: str, embedding_model_name: str
    ) -> Union[Chunk, None]:
        pass

    @abstractmethod
    async def delete_knowledge_chunk(
        self, tenant_id: str, knowledge_ids: List[str]
    ) -> Union[List[Chunk], None]:
        pass

    # =================== retrieval ===================
    @abstractmethod
    async def search_space_chunk_list(
        self,
        tenant_id: str,
        params: RetrievalBySpaceRequest,
    ) -> List[RetrievalChunk]:
        pass

    @abstractmethod
    async def search_knowledge_chunk_list(
        self,
        tenant_id: str,
        params: RetrievalByKnowledgeRequest,
    ) -> List[RetrievalChunk]:
        pass

    @abstractmethod
    async def retrieve(
        self,
        tenant_id: str,
        params: RetrievalRequest,
    ) -> List[RetrievalChunk]:
        pass

    # =================== task ===================
    @abstractmethod
    async def save_task_list(self, task_list: List[Task]) -> List[Task]:
        pass

    @abstractmethod
    async def update_task_list(self, task_list: List[Task]) -> None:
        pass

    @abstractmethod
    async def get_task_list(
        self, tenant_id: str, page_params: PageQueryParams[Task]
    ) -> PageResponse[Task]:
        pass

    @abstractmethod
    async def get_task_by_id(self, tenant_id: str, task_id: str) -> Union[Task, None]:
        pass

    @abstractmethod
    async def delete_task_by_id(
        self, tenant_id: str, task_id: str
    ) -> Union[Task, None]:
        pass

    @abstractmethod
    async def task_statistics(
        self, space_id: str, status: TaskStatus
    ) -> Union[dict[TaskStatus, int], int]:
        pass

    @abstractmethod
    async def delete_knowledge_task(
        self, tenant_id: str, knowledge_ids: List[str]
    ) -> Union[List[Task], None]:
        pass

    # =================== tenant ===================
    @abstractmethod
    async def save_tenant(self, tenant: Tenant) -> Union[Tenant, None]:
        pass

    @abstractmethod
    async def get_tenant_by_sk(self, secret_key: str) -> Union[Tenant, None]:
        pass

    @abstractmethod
    async def update_tenant(self, tenant: Tenant) -> Union[Tenant, None]:
        pass

    @abstractmethod
    async def validate_tenant_name(self, tenant_name: str) -> bool:
        pass

    @abstractmethod
    async def get_tenant_by_id(self, tenant_id: str) -> Union[Tenant, None]:
        pass

    @abstractmethod
    async def get_tenant_list(
        self, page_params: PageQueryParams[Tenant]
    ) -> PageResponse[Tenant]:
        pass

    @abstractmethod
    async def delete_tenant_by_id(self, tenant_id: str) -> Union[Tenant, None]:
        pass

    # =================== api-key ===================
    @abstractmethod
    async def get_api_key_by_value(self, key_value: str) -> Union[APIKey, None]:
        pass

    @abstractmethod
    async def get_api_key_by_id(
        self, tenant_id: str, key_id: str
    ) -> Union[APIKey, None]:
        pass

    @abstractmethod
    async def get_tenant_api_keys(
        self, tenant_id: str, page_params: PageQueryParams[APIKey]
    ) -> PageResponse[APIKey]:
        pass

    @abstractmethod
    async def save_api_key(self, create_params: APIKey) -> APIKey:
        pass

    @abstractmethod
    async def update_api_key(self, update_params: APIKey) -> Union[APIKey, None]:
        pass

    @abstractmethod
    async def delete_api_key(self, key_id: str) -> bool:
        pass

    @abstractmethod
    async def get_all_expired_api_keys(self, tenant_id: str) -> List[APIKey]:
        pass

    # =================== rule ===================
    @abstractmethod
    async def get_tenant_rule(self, tenant_id: str) -> Optional[str]:
        pass

    @abstractmethod
    async def get_space_rule(self, tenant_id: str, space_id: str) -> Optional[str]:
        pass

    # =================== agent ===================
    @abstractmethod
    async def agent_invoke(self, params: Any) -> AsyncIterator[Any]:
        pass

    # =================== tag ===================
    @abstractmethod
    async def add_tag_list(
        self, tenant_id: str, tag_list: List[TagCreate]
    ) -> List[Tag]:
        pass

    @abstractmethod
    async def get_tag_list(
        self, tenant_id: str, page_params: PageQueryParams[Tag]
    ) -> PageResponse[Tag]:
        pass

    @abstractmethod
    async def get_tag_by_id(self, tenant_id: str, tag_id: str) -> Union[Tag, None]:
        pass

    @abstractmethod
    async def delete_tag_by_id(self, tenant_id: str, tag_id: str) -> Union[Tag, None]:
        pass

    @abstractmethod
    async def update_tag_name_description(
        self,
        tenant_id: str,
        tag_id: str,
        name: Optional[str],
        description: Optional[str],
    ) -> Tag:
        pass

    # =================== tagging ===================
    @abstractmethod
    async def add_tagging_list(
        self, tenant_id: str, tagging_list: List[TaggingCreate]
    ) -> List[Tagging]:
        pass

    @abstractmethod
    async def get_tagging_list(
        self, tenant_id: str, page_params: PageQueryParams[Tagging]
    ) -> PageResponse[Tagging]:
        pass

    @abstractmethod
    async def delete_tagging_by_id(
        self, tenant_id: str, tagging_id: str
    ) -> Union[Tagging, None]:
        pass

    # =================== artifacts ===================
    """
    ArtifactIndex 仓储层抽象接口
    """

    @abstractmethod
    async def add_artifact_list(
        self, artifact_list: List[ArtifactIndexCreate]
    ) -> List[ArtifactIndex]:
        """
        批量添加 artifact 记录
        返回实际插入成功的 ArtifactIndex 记录列表
        """
        pass

    @abstractmethod
    async def get_artifact_list(
        self, page_params: PageQueryParams[ArtifactIndex]
    ) -> PageResponse[ArtifactIndex]:
        """
        分页获取 artifact 列表
        """
        pass

    @abstractmethod
    async def get_artifact_by_id(self, artifact_id: str) -> Union[ArtifactIndex, None]:
        """
        根据 artifact_id 获取 ArtifactIndex 详情
        """
        pass

    @abstractmethod
    async def delete_artifact_by_id(
        self, artifact_id: str
    ) -> Union[ArtifactIndex, None]:
        """
        根据 artifact_id 删除 ArtifactIndex 记录
        返回被删除的记录（如果存在的话）
        """
        pass

    @abstractmethod
    async def update_artifact_space_id(
        self, artifact_id: str, new_space_id: str
    ) -> Union[ArtifactIndex, None]:
        """
        更新 artifact 的 space_id 绑定
        返回更新后的 ArtifactIndex 记录（如果存在的话）
        """
        pass

    # =================== dashboard ===================
    # TODO: add dashboard related methods

    # =================== webhook ===================
    @abstractmethod
    async def handle_webhook(
        self,
        tenant: Tenant,
        # webhook type, e.g. knowledge, chunk, etc.
        webhook_type: str,
        # webhook source, e.g. github, yuque, slack, etc.
        source: str,
        # knowledge base id
        knowledge_base_id: str,
        # webhook payload
        payload: Any,
    ) -> Optional[str]:
        pass
