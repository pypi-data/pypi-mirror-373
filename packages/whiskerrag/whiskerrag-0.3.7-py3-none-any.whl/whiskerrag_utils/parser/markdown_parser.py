import re
from typing import Dict, List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from whiskerrag_types.interface.parser_interface import BaseParser, ParseResult
from whiskerrag_types.model import Knowledge, MarkdownSplitConfig
from whiskerrag_types.model.knowledge import KnowledgeTypeEnum
from whiskerrag_types.model.multi_modal import Text
from whiskerrag_utils.registry import RegisterTypeEnum, register


@register(RegisterTypeEnum.PARSER, KnowledgeTypeEnum.MARKDOWN)
class MarkdownParser(BaseParser[Text]):
    async def parse(
        self,
        knowledge: Knowledge,
        content: Text,
    ) -> ParseResult:
        split_config = knowledge.split_config
        if not isinstance(split_config, MarkdownSplitConfig):
            raise TypeError(
                "knowledge.split_config must be of type MarkdownSplitConfig"
            )
        texts_to_process = (
            self._split_by_headers(content)
            if split_config.extract_header_first
            else [content]
        )
        final_chunks: ParseResult = []
        splitter = self._create_recursive_splitter(split_config)

        for text_item in texts_to_process:
            split_texts = splitter.split_text(text_item.content)
            chunks = []
            for split_text in split_texts:
                code_list = self._extract_code_list(split_text)
                chunk_metadata = text_item.metadata.copy()
                chunk_metadata["_code_list"] = code_list
                chunks.append(Text(content=split_text, metadata=chunk_metadata))

            final_chunks.extend(chunks)
        return final_chunks

    def _extract_code_list(self, text: str) -> List[str]:
        code_list = []
        # 从 markdown 中提取 code
        code_match = re.findall(r"```(.*?)```", text, re.DOTALL)
        for code in code_match:
            code_list.append(code.strip())
        return code_list

    def _split_by_headers(self, content: Text) -> List[Text]:
        chunks = []
        current_chunk: List[str] = []
        current_headers: List[dict] = []

        lines = content.content.split("\n")

        for line in lines:
            header_match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if header_match:
                if current_chunk:
                    chunks.append(
                        self._create_text_chunk(
                            content="\n".join(current_chunk),
                            headers=current_headers.copy(),
                            original_metadata=content.metadata,
                        )
                    )
                    current_chunk = []

                level = header_match.group(1)
                title = header_match.group(2)

                while current_headers and len(level) <= len(
                    current_headers[-1]["level"]
                ):
                    current_headers.pop()

                current_headers.append(
                    {"level": level, "title": title, "full_title": line.strip()}
                )

                current_chunk.append(line)
            else:
                current_chunk.append(line)

        if current_chunk:
            chunks.append(
                self._create_text_chunk(
                    content="\n".join(current_chunk),
                    headers=current_headers.copy(),
                    original_metadata=content.metadata,
                )
            )

        return chunks

    def _create_text_chunk(
        self, content: str, headers: List[Dict], original_metadata: Dict
    ) -> Text:
        metadata = original_metadata.copy()
        metadata.update(
            {
                "headers": headers,
                "level": len(headers[-1]["level"]) if headers else 0,
                "header_path": (
                    " > ".join(h["title"] for h in headers) if headers else ""
                ),
                "is_header_chunk": bool(headers),
            }
        )

        return Text(content=content, metadata=metadata)

    def _create_recursive_splitter(
        self, config: MarkdownSplitConfig
    ) -> RecursiveCharacterTextSplitter:
        if "" not in config.separators:
            config.separators.append("")
        return RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=config.separators,
            is_separator_regex=config.is_separator_regex,
            keep_separator=config.keep_separator or False,
        )

    async def batch_parse(
        self,
        knowledge: Knowledge,
        content_list: List[Text],
    ) -> List[ParseResult]:
        return [await self.parse(knowledge, content) for content in content_list]
