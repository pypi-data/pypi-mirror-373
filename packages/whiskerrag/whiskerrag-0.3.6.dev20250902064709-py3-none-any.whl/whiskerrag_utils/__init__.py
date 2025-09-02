import asyncio
import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple, TypedDict, Union

from whiskerrag_types.model.chunk import Chunk
from whiskerrag_types.model.knowledge import Knowledge, KnowledgeTypeEnum
from whiskerrag_types.model.multi_modal import Image, Text

from .registry import (
    RegisterTypeEnum,
    get_all_registered_with_metadata,
    get_register,
    get_register_metadata,
    get_register_order,
    init_register,
    register,
)

logger = logging.getLogger("whisker")


class DiffResult(TypedDict):
    to_add: List[Knowledge]
    to_delete: List[Knowledge]
    unchanged: List[Knowledge]


def _process_metadata_and_tags(
    knowledge: Knowledge, parse_item: Union[Text, Image]
) -> Tuple[Dict[str, Any], List[str]]:
    """
    Process metadata and tags for a parse item.
    Args:
        knowledge: The knowledge object.
        parse_item: The parse item (Text or Image).
    Returns:
        A tuple of (combined_metadata, tags).
    """
    combined_metadata = {**knowledge.metadata, **parse_item.metadata}
    combined_metadata["_knowledge_type"] = knowledge.knowledge_type
    combined_metadata["_reference_url"] = combined_metadata.get("_reference_url", "")

    # Extract tags from metadata
    tags = combined_metadata.get("_tags")
    if isinstance(tags, str):
        tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
    elif not isinstance(tags, list):
        tags = []

    return combined_metadata, tags


def _create_chunk(
    knowledge: Knowledge,
    parse_item: Union[Text, Image],
    embedding: List[float],
    combined_metadata: Dict[str, Any],
    tags: List[str],
) -> Chunk:
    """
    Create a Chunk object from the given parameters.
    Args:
        knowledge: The knowledge object.
        parse_item: The parse item (Text or Image).
        embedding: The embedding vector.
        combined_metadata: The combined metadata.
        tags: The tags.
    Returns:
        A Chunk object.
    """
    return Chunk(
        chunk_id=str(uuid.uuid4()),
        space_id=knowledge.space_id,
        tenant_id=knowledge.tenant_id,
        knowledge_id=knowledge.knowledge_id,
        context=parse_item.content if isinstance(parse_item, Text) else "",
        embedding=embedding,
        enabled=knowledge.enabled,
        embedding_model_name=knowledge.embedding_model_name,
        metadata=combined_metadata,
        tags=tags,
        f1=combined_metadata.get("_f1"),
        f2=combined_metadata.get("_f2"),
        f3=combined_metadata.get("_f3"),
        f4=combined_metadata.get("_f4"),
        f5=combined_metadata.get("_f5"),
    )


def _get_unique_origin_list(
    origin_list: List[Knowledge],
) -> Tuple[List[Knowledge], List[Knowledge]]:
    to_delete = []
    seen_file_shas = set()
    unique_origin_list = []
    for item in origin_list:
        if item.file_sha not in seen_file_shas:
            seen_file_shas.add(item.file_sha)
            unique_origin_list.append(item)
        else:
            to_delete.append(item)
    return to_delete, unique_origin_list


async def decompose_knowledge(
    knowledge: Knowledge,
    semaphore: Optional[asyncio.Semaphore] = None,
    max_concurrency: int = 4,
) -> List[Knowledge]:
    if semaphore is None:
        semaphore = asyncio.Semaphore(max_concurrency)
    LoaderCls = get_register(RegisterTypeEnum.KNOWLEDGE_LOADER, knowledge.source_type)
    async with semaphore:
        knowledge_list = await LoaderCls(knowledge).decompose()
    if not knowledge_list:
        return []
    tasks = [decompose_knowledge(k, semaphore) for k in knowledge_list]
    results = await asyncio.gather(*tasks)
    flat = [item for sublist in results for item in sublist]
    return flat if flat else knowledge_list


async def get_chunks_by_knowledge(knowledge: Knowledge) -> List[Chunk]:
    """
    Convert knowledge into vectorized chunks with controlled concurrency
    """
    source_type = knowledge.source_type
    knowledge_type = knowledge.knowledge_type
    parse_type = getattr(
        knowledge.split_config,
        "type",
        "base_image" if knowledge_type is KnowledgeTypeEnum.IMAGE else "base_text",
    )
    LoaderCls = get_register(RegisterTypeEnum.KNOWLEDGE_LOADER, source_type)
    ParserCls = get_register(RegisterTypeEnum.PARSER, parse_type)
    EmbeddingCls = get_register(
        RegisterTypeEnum.EMBEDDING, knowledge.embedding_model_name
    )
    # If no parser, return empty list
    if ParserCls is None:
        logger.warning(f"No parser found for type: {parse_type}")
        return []
    # If no embedding model, return empty list
    if EmbeddingCls is None:
        logger.warning(
            f"[warn]: No embedding model found for name: {knowledge.embedding_model_name}"
        )
        return []
    loaded_contents = []
    if LoaderCls is None:
        # If no loader, directly parse the knowledge object itself
        logger.warning(
            f"No loader found for source type: {knowledge.source_type}, attempting to parse knowledge directly."
        )
        parse_results = await ParserCls().parse(knowledge, None)
    else:
        # Use loader to load contents
        loaded_contents = await LoaderCls(knowledge).load()
        if not loaded_contents:
            logger.warning(
                f"Loader returned no content for source type: {knowledge.source_type}."
            )
            return []
        # Parse loaded contents
        parse_results = []
        for content in loaded_contents:
            split_result = await ParserCls().parse(knowledge, content)
            parse_results.extend(split_result)

    # Classify parse_results by type
    text_items = []
    image_items = []
    for parse_item in parse_results:
        if isinstance(parse_item, Text):
            text_items.append(parse_item)
        elif isinstance(parse_item, Image):
            image_items.append(parse_item)
        else:
            logger.warning(f"[warn]: illegal parse item: {parse_item}")

    chunks = []

    # Batch process Text items using embed_documents
    if text_items:
        try:
            logger.info(f"Processing {len(text_items)} text items in batch")
            documents = [text_item.content for text_item in text_items]
            embeddings = await EmbeddingCls().embed_documents(documents, timeout=30)
            for text_item, embedding in zip(text_items, embeddings):
                combined_metadata, tags = _process_metadata_and_tags(
                    knowledge, text_item
                )
                chunk = _create_chunk(
                    knowledge, text_item, embedding, combined_metadata, tags
                )
                chunks.append(chunk)
        except Exception as e:
            logger.error(f"Error processing text items in batch: {e}")

    # Process Image items individually
    if image_items:
        for image_item in image_items:
            try:
                logger.info(f"Processing image item: {image_item}")
                embedding = await EmbeddingCls().embed_image(image_item, timeout=60 * 5)
                if not embedding:
                    logger.warning(
                        f"[warn]: embed image failed, image item: {image_item}"
                    )
                    continue
                combined_metadata, tags = _process_metadata_and_tags(
                    knowledge, image_item
                )
                chunk = _create_chunk(
                    knowledge, image_item, embedding, combined_metadata, tags
                )
                chunks.append(chunk)
            except Exception as e:
                logger.error(f"Error processing image item: {e}")
                continue

    return chunks


def get_diff_knowledge_by_sha(
    origin_list: Optional[List[Knowledge]] = None,
    new_list: Optional[List[Knowledge]] = None,
) -> DiffResult:
    try:
        origin_list = origin_list or []
        new_list = new_list or []

        to_delete = []
        to_delete_origin, unique_origin_list = _get_unique_origin_list(origin_list)
        to_delete.extend(to_delete_origin)
        _, unique_new_list = _get_unique_origin_list(new_list)

        origin_map = {item.file_sha: item for item in unique_origin_list}

        to_add = []
        unchanged = []
        for new_item in unique_new_list:
            if new_item.file_sha not in origin_map:
                to_add.append(new_item)
            else:
                unchanged.append(new_item)
                del origin_map[new_item.file_sha]

        to_delete.extend(list(origin_map.values()))

        return {"to_add": to_add, "to_delete": to_delete, "unchanged": unchanged}
    except Exception as error:
        logger.error(f"Error in _get_diff_knowledge_by_sha: {error}")
        return {"to_add": [], "to_delete": [], "unchanged": []}


__all__ = [
    "get_register",
    "get_register_metadata",
    "get_register_order",
    "get_all_registered_with_metadata",
    "register",
    "RegisterTypeEnum",
    "init_register",
    "decompose_knowledge",
    "get_chunks_by_knowledge",
    "DiffResult",
    "get_diff_knowledge_by_sha",
]
