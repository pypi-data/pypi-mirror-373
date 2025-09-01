import re
from typing import Dict, List, Tuple, Union

from langchain_text_splitters import RecursiveCharacterTextSplitter

from whiskerrag_types.interface.parser_interface import BaseParser, ParseResult
from whiskerrag_types.model.knowledge import Knowledge, KnowledgeTypeEnum
from whiskerrag_types.model.multi_modal import Text
from whiskerrag_types.model.splitter import YuqueSplitConfig
from whiskerrag_utils.registry import RegisterTypeEnum, register


@register(RegisterTypeEnum.PARSER, KnowledgeTypeEnum.YUQUEDOC)
class YuqueParser(BaseParser[Text]):
    def _extract_headings(self, content: str) -> List[Tuple[int, str, int]]:
        """
        Extract headings from markdown content.
        Returns list of (level, title, position) tuples.
        """
        heading_pattern = r"^(#{1,6})\s+(.+)$"
        headings = []

        for match in re.finditer(heading_pattern, content, re.MULTILINE):
            level = len(match.group(1))  # number of # characters
            title = match.group(2).strip()
            position = match.start()
            headings.append((level, title, position))

        return headings

    def _build_heading_hierarchy(
        self, headings: List[Tuple[int, str, int]]
    ) -> Dict[int, List[str]]:
        """
        Build heading hierarchy for heading positions only.
        Returns a mapping from heading position to list of hierarchical headings.
        Optimized to store only heading positions instead of every character position.
        """
        hierarchy_map = {}
        current_hierarchy: List[Union[str, None]] = [
            None
        ] * 6  # Support up to 6 levels of headings

        for level, title, position in headings:
            # Update current hierarchy
            current_hierarchy[level - 1] = title
            # Clear deeper levels
            for j in range(level, 6):
                if j > level - 1:
                    current_hierarchy[j] = None

            # Store hierarchy only for this heading position
            active_hierarchy = [h for h in current_hierarchy if h is not None]
            hierarchy_map[position] = active_hierarchy.copy()

        return hierarchy_map

    def _find_chunk_headings(
        self,
        chunk_text: str,
        original_content: str,
        hierarchy_map: Dict[int, List[str]],
    ) -> List[str]:
        """
        Find the relevant headings for a given chunk based on its position in the original content.
        Uses binary search for efficient lookup of the closest heading position.
        """
        # Find the position of this chunk in the original content
        chunk_start = original_content.find(chunk_text)
        if chunk_start == -1:
            # If exact match not found, try to find the best match
            # This can happen due to text processing differences
            return []

        # Get sorted heading positions for binary search
        heading_positions = sorted(hierarchy_map.keys())

        if not heading_positions:
            return []

        # Find the closest heading position that is <= chunk_start
        # Using binary search for efficiency
        left, right = 0, len(heading_positions) - 1
        best_position = -1

        while left <= right:
            mid = (left + right) // 2
            if heading_positions[mid] <= chunk_start:
                best_position = heading_positions[mid]
                left = mid + 1
            else:
                right = mid - 1

        # Return the hierarchy for the best position found
        if best_position != -1:
            return hierarchy_map[best_position]
        else:
            return []

    async def parse(
        self,
        knowledge: Knowledge,
        content: Text,
    ) -> ParseResult:
        split_config = knowledge.split_config
        if not isinstance(split_config, YuqueSplitConfig):
            raise TypeError("knowledge.split_config must be of type YuqueSplitConfig")

        # Extract headings and build hierarchy
        headings = self._extract_headings(content.content)
        hierarchy_map = self._build_heading_hierarchy(headings)

        separators = split_config.separators or [
            # First, try to split along Markdown headings (starting with level 2)
            "\n#{1,6} ",
            # Note the alternative syntax for headings (below) is not handled here
            # Heading level 2
            # ---------------
            # End of code block
            "```\n",
            # Horizontal lines
            "\n\\*\\*\\*+\n",
            "\n---+\n",
            "\n___+\n",
            # Note that this splitter doesn't handle horizontal lines defined
            # by *three or more* of ***, ---, or ___, but this is not handled
            "\n\n",
            "\n",
            " ",
            "",
        ]
        if "" not in separators:
            separators.append("")
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=split_config.chunk_size,
            chunk_overlap=split_config.chunk_overlap,
            separators=separators,
            keep_separator=False,
        )
        result: ParseResult = []
        # split text
        split_texts = splitter.split_text(content.content)

        for idx, text in enumerate(split_texts):
            metadata = content.metadata.copy()
            metadata["_idx"] = idx

            # Find relevant headings for this chunk
            chunk_headings = self._find_chunk_headings(
                text, content.content, hierarchy_map
            )

            # Build context with knowledge name and headings
            context_parts = []
            if knowledge.knowledge_name:
                context_parts.append(knowledge.knowledge_name)
                metadata["_knowledge_name"] = knowledge.knowledge_name

            if chunk_headings:
                metadata["_headings"] = chunk_headings
                metadata["_heading_path"] = " > ".join(chunk_headings)
                context_parts.extend(chunk_headings)

            # Add context information to content
            if context_parts:
                full_context = " > ".join(context_parts)
                # Prepend context to the chunk content for better retrieval
                # This creates a more context-rich chunk that includes knowledge name and hierarchical path
                enhanced_content = f"[Context: {full_context}]\n\n{text}"
                result.append(Text(content=enhanced_content, metadata=metadata))
            else:
                result.append(Text(content=text, metadata=metadata))

        return result

    async def batch_parse(
        self,
        knowledge: Knowledge,
        content_list: List[Text],
    ) -> List[ParseResult]:
        return [await self.parse(knowledge, content) for content in content_list]
