import re
from typing import Any, Dict, List, Optional, Union

from whiskerrag_types.interface.loader_interface import BaseLoader
from whiskerrag_types.model.knowledge import (
    Knowledge,
    KnowledgeSourceEnum,
    KnowledgeTypeEnum,
)
from whiskerrag_types.model.knowledge_source import (
    OpenUrlSourceConfig,
    YuqueSourceConfig,
)
from whiskerrag_types.model.multi_modal import Text
from whiskerrag_types.model.splitter import ImageSplitConfig
from whiskerrag_utils.helper.yuque import ExtendedYuqueLoader
from whiskerrag_utils.registry import RegisterTypeEnum, register


@register(RegisterTypeEnum.KNOWLEDGE_LOADER, KnowledgeSourceEnum.YUQUE)
class WhiskerYuqueLoader(BaseLoader[Text]):
    _book_docs_cache: Optional[list]
    _doc_detail_cache: Dict[Union[str, int], Any]
    _yuque_loader: Optional[ExtendedYuqueLoader]

    def __init__(self, knowledge: Knowledge) -> None:
        super().__init__(knowledge)
        self._book_docs_cache = None
        self._doc_detail_cache = {}
        self._yuque_loader = None

    @property
    def yuque_loader(self) -> ExtendedYuqueLoader:
        if self._yuque_loader is None:
            if not isinstance(self.knowledge.source_config, YuqueSourceConfig):
                raise AttributeError("Invalid source config type for YuqueLoader")
            access_token = self.knowledge.source_config.auth_info
            api_url = self.knowledge.source_config.api_url
            self._yuque_loader = ExtendedYuqueLoader(
                access_token=access_token,
                api_url=api_url,
            )
        return self._yuque_loader

    def _create_doc_knowledge(self, parsed_document: Any) -> Knowledge:
        from copy import deepcopy

        source_config = deepcopy(self.knowledge.source_config)
        if hasattr(source_config, "document_id"):
            source_config.document_id = parsed_document.metadata.get(
                "slug"
            ) or parsed_document.metadata.get("id")
        return Knowledge(
            source_type=self.knowledge.source_type,
            knowledge_type=self.knowledge.knowledge_type,
            knowledge_name=f"{self.knowledge.knowledge_name}/{parsed_document.metadata.get('title', '')}",
            embedding_model_name=self.knowledge.embedding_model_name,
            source_config=source_config,
            tenant_id=self.knowledge.tenant_id,
            file_size=len(parsed_document.page_content.encode("utf-8")),
            file_sha=parsed_document.metadata.get("content_updated_at"),
            space_id=self.knowledge.space_id,
            split_config=self.knowledge.split_config,
            parent_id=self.knowledge.knowledge_id,
            enabled=True,
            metadata=parsed_document.metadata,
        )

    def _create_image_knowledges(self, parsed_document: Any) -> List[Knowledge]:
        image_knowledges = []
        image_pattern = r"!\[(.*?)\]\((.*?)\)"
        all_image_matches = re.findall(image_pattern, parsed_document.page_content)

        for img_idx, (alt_text, img_url) in enumerate(all_image_matches):
            if img_url.strip():
                img_metadata = parsed_document.metadata.copy()
                img_metadata["_img_idx"] = img_idx
                img_metadata["_img_url"] = img_url.strip()
                img_metadata["_alt_text"] = alt_text.strip() if alt_text.strip() else ""

                image_knowledge = Knowledge(
                    source_type=KnowledgeSourceEnum.CLOUD_STORAGE_IMAGE,
                    knowledge_type=KnowledgeTypeEnum.IMAGE,
                    knowledge_name=f"{self.knowledge.knowledge_name}/{parsed_document.metadata.get('title', '')}/image_{img_idx}",
                    embedding_model_name=self.knowledge.embedding_model_name,
                    source_config=OpenUrlSourceConfig(url=img_url.strip()),
                    tenant_id=self.knowledge.tenant_id,
                    space_id=self.knowledge.space_id,
                    split_config=ImageSplitConfig(),
                    parent_id=self.knowledge.knowledge_id,
                    enabled=True,
                    metadata=img_metadata,
                )
                image_knowledges.append(image_knowledge)
        return image_knowledges

    def get_doc_detail(
        self, group_login: str, book_slug: str, document_id: Optional[Union[str, int]]
    ) -> Any:
        if document_id in self._doc_detail_cache:
            return self._doc_detail_cache[document_id]
        if document_id is None:
            raise ValueError("document_id is required")
        parsed_document = self.yuque_loader.load_document_by_path(
            group_login, book_slug, document_id
        )
        self._doc_detail_cache[document_id] = parsed_document
        return parsed_document

    def get_book_docs(self, group_login: str, book_slug: str) -> list:
        if self._book_docs_cache is not None:
            return self._book_docs_cache
        docs = self.yuque_loader.get_book_documents_by_path(group_login, book_slug)
        self._book_docs_cache = docs
        return docs

    async def load(self) -> List[Text]:
        if not isinstance(self.knowledge.source_config, YuqueSourceConfig):
            raise AttributeError("Invalid source config type for YuqueLoader")
        group_login = self.knowledge.source_config.group_login
        book_slug = self.knowledge.source_config.book_slug
        document_id = self.knowledge.source_config.document_id
        text_list: List[Text] = []
        try:
            if not group_login:
                raise ValueError("group_login is needed for WhiskerYuqueLoader")
            if not book_slug:
                raise ValueError("book_slug is needed for WhiskerYuqueLoader")
            if not document_id:
                raise ValueError("document_id is needed for WhiskerYuqueLoader")
            parsed_document = self.get_doc_detail(group_login, book_slug, document_id)
            text_list.append(
                Text(
                    content=parsed_document.page_content,
                    metadata=parsed_document.metadata,
                )
            )
            return text_list
        except Exception as e:
            raise Exception(f"Failed to load content from Yuque: {e}")

    async def decompose(self) -> List[Knowledge]:
        if not isinstance(self.knowledge.source_config, YuqueSourceConfig):
            raise AttributeError("Invalid source config type for YuqueLoader")

        group_login = self.knowledge.source_config.group_login
        book_slug = self.knowledge.source_config.book_slug
        document_id = self.knowledge.source_config.document_id

        if not group_login:
            raise ValueError("group_login is needed for WhiskerYuqueLoader")
        if not book_slug:
            raise ValueError("book_slug is needed for WhiskerYuqueLoader")

        knowledge_list: List[Knowledge] = []

        # Decompose a specific document - only extract images
        if document_id:
            doc_knowledge_list = await self._decompose_document(
                group_login, book_slug, document_id, include_document=False
            )
            knowledge_list.extend(doc_knowledge_list)
        # Decompose a whole book - create sub-documents as knowledge, no images
        else:
            book_knowledges = await self._decompose_book(group_login, book_slug)
            knowledge_list.extend(book_knowledges)

        return knowledge_list

    async def _decompose_book(
        self, group_login: str, book_slug: str
    ) -> List[Knowledge]:
        knowledges: List[Knowledge] = []
        try:
            docs = self.get_book_docs(group_login, book_slug)
            for doc in docs:
                doc_knowledges = await self._decompose_document(
                    group_login,
                    book_slug,
                    doc["slug"],
                    include_document=True,
                    include_images=False,
                )
                knowledges.extend(doc_knowledges)
        except Exception as e:
            raise ValueError(f"Failed to get book documents: {e}")
        return knowledges

    async def _decompose_document(
        self,
        group_login: str,
        book_slug: str,
        document_id: Optional[Union[str, int]],
        include_document: bool = True,
        include_images: bool = True,
    ) -> List[Knowledge]:
        knowledges: List[Knowledge] = []
        try:
            parsed_document = self.get_doc_detail(group_login, book_slug, document_id)

            # Only create document knowledge if include_document is True
            if include_document:
                doc_knowledge = self._create_doc_knowledge(parsed_document)
                knowledges.append(doc_knowledge)

            # Only create image knowledges if include_images is True
            if include_images:
                image_knowledges = self._create_image_knowledges(parsed_document)
                knowledges.extend(image_knowledges)
        except Exception as e:
            raise ValueError(f"Failed to get document: {e}")
        return knowledges

    async def on_load_finished(self) -> None:
        pass
