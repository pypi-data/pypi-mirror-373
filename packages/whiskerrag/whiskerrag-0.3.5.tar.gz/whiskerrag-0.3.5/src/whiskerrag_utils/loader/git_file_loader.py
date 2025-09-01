import base64
import os
from typing import List, Union
from urllib.parse import quote

import chardet
import requests
from pydantic import HttpUrl

from whiskerrag_types.interface.loader_interface import BaseLoader
from whiskerrag_types.model import (
    GithubFileSourceConfig,
    Knowledge,
    KnowledgeSourceEnum,
)
from whiskerrag_types.model.knowledge import KnowledgeTypeEnum
from whiskerrag_types.model.knowledge_source import GithubRepoSourceConfig
from whiskerrag_types.model.multi_modal import Blob, Image, Text
from whiskerrag_utils.loader.git_repo_manager import get_repo_manager
from whiskerrag_utils.registry import RegisterTypeEnum, register


def file_to_text(full_path: str) -> Union[str, None]:
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        pass
    try:
        with open(full_path, "rb") as f:
            content_bytes = f.read()
            guess = chardet.detect(content_bytes)
            encoding = guess["encoding"] if guess["confidence"] > 0.7 else None
            if encoding:
                try:
                    return content_bytes.decode(encoding)
                except Exception:
                    return None
    except Exception:
        return None
    return None


def file_to_base64(full_path: str) -> str:
    with open(full_path, "rb") as f:
        content = f.read()
        return base64.b64encode(content).decode("utf-8")


def get_github_default_branch(owner_repo: str) -> str:
    url = f"https://api.github.com/repos/{owner_repo}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    resp = requests.get(url, headers=headers)
    if resp.ok:
        return resp.json()["default_branch"]  # type: ignore
    return "master"


def get_github_file_content(
    owner_repo: str,
    branch: str,
    path: str,
    knowledge_type: KnowledgeTypeEnum,
    token: Union[str, None] = None,
) -> Union[Text, Image, Blob]:
    url = f"https://api.github.com/repos/{owner_repo}/contents/{path}?ref={branch}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    resp = requests.get(url, headers=headers)
    if not resp.ok:
        raise RuntimeError(f"Github API获取文件失败: {resp.status_code} {resp.text}")
    info = resp.json()
    if info.get("encoding") == "base64" and "content" in info:
        content_b64 = info["content"]
        # github可能换行符分割base64，要去掉换行
        content_b64 = content_b64.replace("\n", "")
        content_bin = base64.b64decode(content_b64)
        if knowledge_type == KnowledgeTypeEnum.IMAGE:
            # Image类型兜底
            return Image(b64_json=content_b64, metadata={})
        else:
            # 尝试解码文本
            try:
                content_txt = content_bin.decode("utf-8")
                return Text(content=content_txt, metadata={})
            except Exception:
                guess = chardet.detect(content_bin)
                enc2 = guess["encoding"] if guess["confidence"] > 0.7 else None
                if enc2:
                    try:
                        content_txt = content_bin.decode(enc2)
                        return Text(content=content_txt, metadata={})
                    except Exception:
                        pass
                # Blob 兜底，推荐直接用 Blob.from_data
                # 带metadata/source/path都可以补上
                return Blob.from_data(content_bin, metadata={"path": path})
    else:
        # 极少数二进制 raw 返回
        raise RuntimeError("Github接口未返回base64编码内容，无法读取。")


def get_gitlab_file_content(
    url: str,
    owner_repo: str,
    branch: str,
    path: str,
    knowledge_type: KnowledgeTypeEnum,
    token: Union[str, None] = None,
) -> Union[Text, Image, Blob]:
    headers = {}
    if token:
        if isinstance(token, str) and token.startswith("git:"):
            token = token[4:]
        headers["PRIVATE-TOKEN"] = token
    # step1: 查项目id
    project_url = f"{url.rstrip('/')}/api/v3/project"
    resp = requests.get(project_url, params={"path": owner_repo}, headers=headers)
    if not resp.ok or "id" not in resp.json():
        raise RuntimeError(f"获取GitLab项目ID失败: {resp.status_code} {resp.text}")
    project_id = resp.json()["id"]
    if not branch:
        branch = resp.json().get("default_branch", "master")
    file_path_enc = quote(path, safe="")
    # step2: 查文件内容
    file_api_url = f"{url.rstrip('/')}/api/v4/projects/{project_id}/repository/files/{file_path_enc}"
    resp2 = requests.get(file_api_url, params={"ref": branch}, headers=headers)
    if not resp2.ok or "content" not in resp2.json():
        raise RuntimeError(f"获取GitLab文件失败: {resp2.status_code} {resp2.text}")
    info = resp2.json()
    content_b64 = info["content"]
    encoding = info["encoding"]
    content_b64 = content_b64.replace("\n", "")  # 防止意外有换行
    if encoding == "base64":
        content_bin = base64.b64decode(content_b64)
        if knowledge_type == KnowledgeTypeEnum.IMAGE:
            return Image(b64_json=content_b64, metadata={})
        else:
            try:
                content_txt = content_bin.decode("utf-8")
                return Text(content=content_txt, metadata={})
            except Exception:
                guess = chardet.detect(content_bin)
                enc2 = guess["encoding"] if guess["confidence"] > 0.7 else None
                if enc2:
                    try:
                        content_txt = content_bin.decode(enc2)
                        return Text(content=content_txt, metadata={})
                    except Exception:
                        pass
                return Blob.from_data(content_bin, metadata={"path": path})
    else:
        raise RuntimeError("暂不支持非base64编码内容")


@register(RegisterTypeEnum.KNOWLEDGE_LOADER, KnowledgeSourceEnum.GITHUB_FILE)
class GithubFileLoader(BaseLoader[Union[Text, Image, Blob]]):
    """
    从Git仓库加载单个文件的加载器
    """

    def __init__(self, knowledge: Knowledge):
        """
        初始化GithubFileLoader

        Args:
            knowledge: Knowledge实例，包含文件源配置

        Raises:
            ValueError: 无效的文件配置
        """
        if not isinstance(knowledge.source_config, GithubFileSourceConfig):
            raise ValueError("source_config should be GithubFileSourceConfig")
        self.knowledge = knowledge
        self.source_config = knowledge.source_config
        self.path = knowledge.source_config.path
        self.repo_name = knowledge.source_config.repo_name
        self.knowledge_type = knowledge.knowledge_type
        self.repo_manager = get_repo_manager()
        self.source_url = knowledge.source_config.url

        # 从文件配置中提取仓库配置
        self.repo_config = GithubRepoSourceConfig(
            **knowledge.source_config.model_dump(exclude={"path"}),
        )
        self.is_github = str(self.source_url).startswith("https://github.com")
        self.is_gitlab = not self.is_github

    async def load(self) -> List[Union[Text, Image, Blob]]:
        # 特殊处理图片
        if self.knowledge_type == KnowledgeTypeEnum.IMAGE and self.is_github:
            branch = self.source_config.branch
            repo_name = self.source_config.repo_name
            github_image_file_url = (
                f"https://raw.githubusercontent.com/{repo_name}/{branch}/{self.path}"
            )
            return [
                Image(
                    url=HttpUrl(github_image_file_url),
                    metadata=self.knowledge.metadata,
                )
            ]
        # 获取仓库本地路径
        repo_path = self.repo_manager.get_repo_path(self.repo_config)
        full_path = os.path.join(repo_path, self.path)
        # 1. 本地优先读
        if os.path.exists(full_path):
            text = file_to_text(full_path)
            if text is not None:
                return [Text(content=text, metadata=self.knowledge.metadata)]
            b64 = file_to_base64(full_path)
            if self.knowledge_type == KnowledgeTypeEnum.IMAGE:
                return [Image(b64_json=b64, metadata=self.knowledge.metadata)]
            else:
                return [Blob.from_data(b64, metadata=self.knowledge.metadata)]
        # 2. API 单文件获取兜底
        out = None
        if self.is_github:
            repo_name = self.source_config.repo_name
            branch = self.source_config.branch or get_github_default_branch(repo_name)
            # 直接用API获取单文件内容
            out = get_github_file_content(
                repo_name,
                branch,
                self.path,
                self.knowledge_type,
                self.source_config.auth_info,
            )
        elif self.is_gitlab:
            branch = self.source_config.branch or "master"
            out = get_gitlab_file_content(
                self.source_url,
                self.repo_name,
                branch,
                self.path,
                self.knowledge_type,
                self.source_config.auth_info,
            )
        else:
            raise ValueError("不支持的仓库类型，或请先本地clone仓库。")
        # 回填 metadata
        if out is not None:
            out.metadata = self.knowledge.metadata
            return [out]
        raise ValueError(f"File not found both local and remote: {self.path}")

    async def decompose(self) -> List[Knowledge]:
        """
        文件加载器不需要分解，返回空列表

        Returns:
            List[Knowledge]: 空列表
        """
        return []

    async def on_load_finished(self) -> None:
        """
        加载完成后的生命周期方法
        这里不清理仓库，因为可能还有其他文件需要访问
        """
        pass
