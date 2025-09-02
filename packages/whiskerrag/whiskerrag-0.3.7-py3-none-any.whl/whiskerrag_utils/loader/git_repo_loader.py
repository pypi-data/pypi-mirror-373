import logging
import os
from typing import Any, List, Optional

from langchain_text_splitters import Language
from openai import BaseModel

from whiskerrag_types.interface.loader_interface import BaseLoader
from whiskerrag_types.model.knowledge import (
    Knowledge,
    KnowledgeSourceEnum,
    KnowledgeTypeEnum,
)
from whiskerrag_types.model.knowledge_source import GithubRepoSourceConfig
from whiskerrag_types.model.multi_modal import Text
from whiskerrag_types.model.splitter import (
    BaseCharSplitConfig,
    BaseCodeSplitConfig,
    ImageSplitConfig,
    JSONSplitConfig,
    KnowledgeSplitConfig,
    MarkdownSplitConfig,
    PDFSplitConfig,
    TextSplitConfig,
)
from whiskerrag_utils.loader.artifacts_extract import get_all_build_artifacts
from whiskerrag_utils.loader.file_pattern_manager import FilePatternManager
from whiskerrag_utils.loader.git_repo_manager import get_repo_manager
from whiskerrag_utils.registry import RegisterTypeEnum, register

logger = logging.getLogger("whisker")


class GitFileElementType(BaseModel):
    content: str
    path: str
    mode: str
    url: str
    branch: str
    repo_name: str
    size: int
    sha: str
    position: dict = {}  # VSCode position information


@register(RegisterTypeEnum.KNOWLEDGE_LOADER, KnowledgeSourceEnum.GITHUB_REPO)
class GithubRepoLoader(BaseLoader):
    """简化的Git仓库加载器，使用统一的仓库管理器"""

    def __init__(self, knowledge: Knowledge):
        # Type annotations for instance variables
        self.repo_path: Optional[str] = None
        self.local_repo: Optional[Any] = None
        """
        初始化GithubRepoLoader

        Args:
            knowledge: Knowledge实例，包含仓库源配置

        Raises:
            ValueError: 无效的仓库配置
        """
        if not isinstance(knowledge.source_config, GithubRepoSourceConfig):
            raise ValueError("source_config should be GithubRepoSourceConfig")

        self.knowledge = knowledge
        self.repo_manager = get_repo_manager()
        self.source_config = knowledge.source_config

        # 从配置中获取信息
        self.repo_name = knowledge.source_config.repo_name
        self.branch_name = knowledge.source_config.branch
        self.base_url = knowledge.source_config.url.rstrip("/")

        # 获取仓库路径和Repo对象
        try:
            self.repo_path = self.repo_manager.get_repo_path(knowledge.source_config)
            self.local_repo = self.repo_manager.get_repo(knowledge.source_config)

            # 如果没有指定分支，获取默认分支
            if not self.branch_name and self.local_repo:
                try:
                    self.branch_name = self.local_repo.active_branch.name
                except Exception as e:
                    logger.warning(f"Failed to get default branch name: {str(e)}")
                    self.branch_name = "main"

            logger.info(f"Loaded repo {self.repo_name} with branch {self.branch_name}")
        except Exception as e:
            logger.error(f"Failed to load repo: {e}")
            raise ValueError(
                f"Failed to load repo {self.repo_name} with branch "
                f"{self.branch_name}. Error: {str(e)}"
            )

    @staticmethod
    def get_knowledge_type_by_ext(ext: str) -> Optional[KnowledgeTypeEnum]:
        ext = ext.lower()
        ext_to_type = {
            ".md": KnowledgeTypeEnum.MARKDOWN,
            ".mdx": KnowledgeTypeEnum.MARKDOWN,
            ".txt": KnowledgeTypeEnum.TEXT,
            ".json": KnowledgeTypeEnum.JSON,
            ".pdf": KnowledgeTypeEnum.PDF,
            ".docx": KnowledgeTypeEnum.DOCX,
            ".rst": KnowledgeTypeEnum.RST,
            ".py": KnowledgeTypeEnum.PYTHON,
            ".js": KnowledgeTypeEnum.JS,
            ".ts": KnowledgeTypeEnum.TS,
            ".go": KnowledgeTypeEnum.GO,
            ".java": KnowledgeTypeEnum.JAVA,
            ".cpp": KnowledgeTypeEnum.CPP,
            ".c": KnowledgeTypeEnum.C,
            ".h": KnowledgeTypeEnum.C,
            ".hpp": KnowledgeTypeEnum.CPP,
            ".cs": KnowledgeTypeEnum.CSHARP,
            ".kt": KnowledgeTypeEnum.KOTLIN,
            ".swift": KnowledgeTypeEnum.SWIFT,
            ".php": KnowledgeTypeEnum.PHP,
            ".rb": KnowledgeTypeEnum.RUBY,
            ".rs": KnowledgeTypeEnum.RUST,
            ".scala": KnowledgeTypeEnum.SCALA,
            ".sol": KnowledgeTypeEnum.SOL,
            ".html": KnowledgeTypeEnum.HTML,
            ".css": KnowledgeTypeEnum.TEXT,
            ".lua": KnowledgeTypeEnum.LUA,
            ".m": KnowledgeTypeEnum.TEXT,  # Objective-C/MATLAB等
            ".sh": KnowledgeTypeEnum.TEXT,
            ".yml": KnowledgeTypeEnum.TEXT,
            ".yaml": KnowledgeTypeEnum.TEXT,
            ".tex": KnowledgeTypeEnum.LATEX,
            ".jpg": KnowledgeTypeEnum.IMAGE,
            ".jpeg": KnowledgeTypeEnum.IMAGE,
            ".png": KnowledgeTypeEnum.IMAGE,
            ".gif": KnowledgeTypeEnum.IMAGE,
            ".bmp": KnowledgeTypeEnum.IMAGE,
            ".svg": KnowledgeTypeEnum.IMAGE,
        }
        return ext_to_type.get(ext, KnowledgeTypeEnum.TEXT)

    def _get_split_config_for_knowledge_type(
        self, knowledge_type: KnowledgeTypeEnum
    ) -> KnowledgeSplitConfig:
        """
        根据知识类型生成适当的分割配置

        Args:
            knowledge_type: 知识类型

        Returns:
            适合该知识类型的分割配置
        """
        # 使用默认的chunk_size和chunk_overlap
        default_chunk_size = 1500
        default_chunk_overlap = 200

        if knowledge_type == KnowledgeTypeEnum.MARKDOWN:
            return MarkdownSplitConfig(
                chunk_size=default_chunk_size,
                chunk_overlap=default_chunk_overlap,
                separators=[
                    "\n#{1,3} ",
                    "\n\\*\\*\\*+\n",
                    "\n---+\n",
                    "\n___+\n",
                    "\n\n",
                    "",
                ],
                is_separator_regex=True,
                keep_separator="start",
                extract_header_first=True,
            )
        elif knowledge_type == KnowledgeTypeEnum.JSON:
            return JSONSplitConfig(
                max_chunk_size=default_chunk_size,
                min_chunk_size=min(200, default_chunk_size - 200),
            )
        elif knowledge_type == KnowledgeTypeEnum.PDF:
            return PDFSplitConfig(
                chunk_size=default_chunk_size,
                chunk_overlap=default_chunk_overlap,
                extract_images=False,
                table_extract_mode="text",
            )
        elif knowledge_type in [
            KnowledgeTypeEnum.PYTHON,
            KnowledgeTypeEnum.JS,
            KnowledgeTypeEnum.TS,
            KnowledgeTypeEnum.GO,
            KnowledgeTypeEnum.JAVA,
            KnowledgeTypeEnum.CPP,
            KnowledgeTypeEnum.C,
            KnowledgeTypeEnum.CSHARP,
            KnowledgeTypeEnum.KOTLIN,
            KnowledgeTypeEnum.SWIFT,
            KnowledgeTypeEnum.PHP,
            KnowledgeTypeEnum.RUBY,
            KnowledgeTypeEnum.RUST,
            KnowledgeTypeEnum.SCALA,
            KnowledgeTypeEnum.SOL,
            KnowledgeTypeEnum.LUA,
        ]:
            # 映射知识类型到Language枚举
            language_map = {
                KnowledgeTypeEnum.PYTHON: Language.PYTHON,
                KnowledgeTypeEnum.JS: Language.JS,
                KnowledgeTypeEnum.TS: Language.TS,
                KnowledgeTypeEnum.GO: Language.GO,
                KnowledgeTypeEnum.JAVA: Language.JAVA,
                KnowledgeTypeEnum.CPP: Language.CPP,
                KnowledgeTypeEnum.C: Language.C,
                KnowledgeTypeEnum.CSHARP: Language.CSHARP,
                KnowledgeTypeEnum.KOTLIN: Language.KOTLIN,
                KnowledgeTypeEnum.SWIFT: Language.SWIFT,
                KnowledgeTypeEnum.PHP: Language.PHP,
                KnowledgeTypeEnum.RUBY: Language.RUBY,
                KnowledgeTypeEnum.RUST: Language.RUST,
                KnowledgeTypeEnum.SCALA: Language.SCALA,
                KnowledgeTypeEnum.SOL: Language.SOL,
                KnowledgeTypeEnum.LUA: Language.LUA,
                KnowledgeTypeEnum.HTML: Language.HTML,
                KnowledgeTypeEnum.LATEX: Language.LATEX,
            }
            return BaseCodeSplitConfig(
                language=language_map.get(knowledge_type, Language.MARKDOWN),
                chunk_size=default_chunk_size,
                chunk_overlap=default_chunk_overlap,
            )
        elif knowledge_type == KnowledgeTypeEnum.TEXT:
            return TextSplitConfig(
                chunk_size=default_chunk_size,
                chunk_overlap=default_chunk_overlap,
                separators=["\n\n", "\n", " ", ""],
                is_separator_regex=False,
                keep_separator=False,
            )
        elif knowledge_type == KnowledgeTypeEnum.IMAGE:
            return ImageSplitConfig(
                type="image",
            )
        else:
            # 对于其他类型（HTML, RST, LATEX等），使用BaseSplitConfig
            return BaseCharSplitConfig(
                chunk_size=default_chunk_size,
                chunk_overlap=default_chunk_overlap,
                separators=["\n\n", "\n", " ", ""],
                split_regex=None,
            )

    def _get_file_position_info(self, file_path: str, relative_path: str) -> dict:
        """
        获取可用于URL构建和远程跳转的位置信息

        Args:
            file_path: 文件的完整路径
            relative_path: 相对于仓库根目录的路径

        Returns:
            dict: 用于远程仓库跳转的位置信息
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                total_lines = len(lines)

            return {
                "file_path": relative_path,
                "start_line": 1,
                "end_line": total_lines,
                "total_lines": total_lines,
            }
        except Exception as e:
            logger.warning(
                f"Could not read file for position info {relative_path}: {e}"
            )
            return {
                "file_path": relative_path,
                "start_line": 1,
                "end_line": None,
                "total_lines": None,
            }

    def generate_jump_url(
        self,
        relative_path: str,
        line: Optional[int] = None,
        end_line: Optional[int] = None,
    ) -> str:
        """
        生成跳转URL，供外部系统创建可点击链接

        Args:
            relative_path: 文件的相对路径
            line: 可选的跳转行号
            end_line: 可选的结束行号（用于范围跳转）

        Returns:
            str: 可用于跳转到文件/行的完整URL
        """
        base_url = (
            f"{self.base_url}/{self.repo_name}/blob/{self.branch_name}/{relative_path}"
        )

        if line is not None:
            if end_line is not None and end_line != line:
                return f"{base_url}#L{line}-L{end_line}"
            else:
                return f"{base_url}#L{line}"
        return base_url

    async def decompose(self) -> List[Knowledge]:
        """
        分解仓库中的知识单元

        Returns:
            List[Knowledge]: 知识列表

        Raises:
            ValueError: 当仓库未正确初始化时
        """
        if not self.local_repo or not self.repo_path:
            raise ValueError("Repository not properly initialized")

        # 初始化文件模式管理器
        split_config = getattr(self.knowledge, "split_config", None)
        if split_config and getattr(split_config, "type", None) == "github_repo":
            pattern_manager = FilePatternManager(
                config=split_config, repo_path=self.repo_path
            )
            warnings = pattern_manager.validate_patterns()
            if warnings:
                logger.warning(
                    "Pattern configuration warnings:\n" + "\n".join(warnings)
                )
        else:
            # 创建兼容的配置字典
            dummy_config = {
                "include_patterns": ["*.md", "*.mdx"],
                "ignore_patterns": [],
                "no_gitignore": True,
                "no_default_ignore_patterns": False,
            }
            pattern_manager = FilePatternManager(
                config=dummy_config, repo_path=self.repo_path
            )

        current_commit = self.local_repo.head.commit

        github_repo_list: List[Knowledge] = []

        for root, _, files in os.walk(self.repo_path):
            if ".git" in root:
                continue

            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, self.repo_path)
                    if not pattern_manager.should_include_file(relative_path):
                        continue
                    file_size = os.path.getsize(file_path)
                    ext = os.path.splitext(relative_path)[1].lower()
                    git_file_path = relative_path.replace("\\", "/")
                    blob = current_commit.tree / git_file_path
                    file_sha = blob.hexsha
                    knowledge_type = self.get_knowledge_type_by_ext(ext)
                    if not knowledge_type:
                        continue
                    file_url = (
                        f"{self.base_url}/{self.repo_name}/blob/"
                        f"{self.branch_name}/{relative_path}"
                    )
                    # 为这个知识类型生成适当的分割配置
                    knowledge_split_config = self._get_split_config_for_knowledge_type(
                        knowledge_type
                    )
                    # 获取准确的位置信息
                    position_info = self._get_file_position_info(
                        file_path, relative_path
                    )
                    source_config = {
                        **self.knowledge.source_config.model_dump(),
                        "path": relative_path,
                    }
                    embedding_model_name = self.knowledge.embedding_model_name
                    knowledge = Knowledge(
                        source_type=KnowledgeSourceEnum.GITHUB_FILE,
                        knowledge_type=knowledge_type,
                        knowledge_name=f"{self.repo_name}/{relative_path}",
                        embedding_model_name=embedding_model_name,
                        source_config=source_config,
                        tenant_id=self.knowledge.tenant_id,
                        file_size=file_size,
                        file_sha=file_sha,
                        space_id=self.knowledge.space_id,
                        split_config=knowledge_split_config,
                        parent_id=self.knowledge.knowledge_id,
                        enabled=True,
                        metadata={
                            "_reference_url": file_url,
                            "branch": self.branch_name,
                            "repo_name": self.repo_name,
                            "path": relative_path,
                            "position": position_info,
                        },
                    )
                    github_repo_list.append(knowledge)

                except Exception as e:
                    logger.warning(f"Error processing file {relative_path}: {e}")
                    continue

        return github_repo_list

    async def load(self) -> List[Text]:
        """
        返回项目的文件目录树结构信息和作者信息，便于大模型理解
        """
        if not self.repo_path:
            raise ValueError("Repository not properly initialized")

        def build_tree(path: str, prefix: str = "") -> str:
            entries = sorted(os.listdir(path))
            tree_lines = []
            for idx, entry in enumerate(entries):
                full_path = os.path.join(path, entry)
                connector = "└── " if idx == len(entries) - 1 else "├── "
                tree_lines.append(f"{prefix}{connector}{entry}")
                if os.path.isdir(full_path) and entry != ".git":
                    extension = "    " if idx == len(entries) - 1 else "│   "
                    tree_lines.append(build_tree(full_path, prefix + extension))
            return "\n".join(tree_lines)

        root_name = os.path.basename(self.repo_path.rstrip(os.sep))
        tree_str = (
            f"repo: {root_name}\n" + "project tree: " + build_tree(self.repo_path)
        )

        artifacts_info = []
        try:
            artifacts_info = get_all_build_artifacts(self.repo_path)
        except Exception as e:
            logger.warning(f"Error getting build artifacts: {e}")

        try:
            if not self.local_repo:
                raise ValueError("Repository not initialized")

            first_commit = next(
                self.local_repo.iter_commits(
                    rev=self.branch_name, max_count=1, reverse=True
                )
            )
            author_name = first_commit.author.name
            author_email = first_commit.author.email
        except Exception:
            author_name = None
            author_email = None

        return [
            Text(
                content=tree_str,
                metadata={
                    "_artifacts_info": artifacts_info,
                    **self.knowledge.metadata,
                    "repo_name": self.repo_name,
                    "author_name": author_name,
                    "author_email": author_email,
                },
            )
        ]

    async def on_load_finished(self) -> None:
        """清理资源"""
        try:
            # 使用仓库管理器清理资源
            self.repo_manager.cleanup_repo(self.source_config)
            self.repo_path = None
            self.local_repo = None
            logger.info(f"Cleaned up temporary directory for {self.repo_name}")
        except Exception as e:
            logger.error(f"Error cleaning up resources: {e}")
