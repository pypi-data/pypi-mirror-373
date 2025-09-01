import hashlib
import json
import logging
import os
import shutil
import tempfile
import time
import uuid
import zipfile
from contextlib import contextmanager
from threading import Lock
from typing import Any, Dict, Iterator, Optional, Union

from whiskerrag_types.model.knowledge_source import GithubRepoSourceConfig

from .utils import log_system_info

logger = logging.getLogger(__name__)


# ===== Mock 类型（ZIP 模式下 GitPython 无法工作） =====
class MockCommit:
    def __init__(
        self,
        sha: str,
        author_name: str = "Unknown",
        author_email: str = "unknown@example.com",
        message: str = "Mock commit",
    ) -> None:
        self.hexsha = sha
        self.author = MockAuthor(author_name, author_email)
        self.message = message
        self.tree: Optional[MockTree] = None


class MockAuthor:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email


class MockTreeItem:
    def __init__(self, full_path: str, relative_path: str, item_type: str):
        self.full_path = full_path
        self.path = relative_path
        self.type = item_type  # "blob" / "tree"


class MockTree:
    def __init__(self, repo_path: str = ""):
        self.repo_path = repo_path

    def __truediv__(self, path: str) -> "MockBlob":
        return MockBlob(os.path.join(self.repo_path, path), path)

    def traverse(self) -> Iterator[MockTreeItem]:
        if not os.path.exists(self.repo_path):
            return
        for root, dirs, files in os.walk(self.repo_path):
            if ".git" in dirs:
                dirs.remove(".git")
            for d in dirs:
                dp = os.path.join(root, d)
                yield MockTreeItem(dp, os.path.relpath(dp, self.repo_path), "tree")
            for f in files:
                fp = os.path.join(root, f)
                yield MockTreeItem(fp, os.path.relpath(fp, self.repo_path), "blob")


class MockBlob:
    def __init__(self, file_path: str, relative_path: str):
        self.file_path = file_path
        self.relative_path = relative_path
        self.path = relative_path
        self.type = "blob"

    @property
    def hexsha(self) -> str:
        try:
            with open(self.file_path, "rb") as f:
                return hashlib.sha1(f.read()).hexdigest()
        except Exception:
            return "0" * 40

    @property
    def size(self) -> int:
        try:
            return os.path.getsize(self.file_path)
        except Exception:
            return 0

    @property
    def mode(self) -> int:
        try:
            return os.stat(self.file_path).st_mode
        except Exception:
            return 0o100644


class MockHead:
    def __init__(self, commit: MockCommit):
        self.commit = commit


class MockBranch:
    def __init__(self, name: str):
        self.name = name


class MockRepo:
    def __init__(
        self, repo_path: str, config: GithubRepoSourceConfig, repo_info: Dict[str, Any]
    ):
        self.working_dir = repo_path
        self.repo_path = repo_path
        self.config = config
        self.repo_info = repo_info
        sha = repo_info.get("default_branch_sha", "unknown")
        author_name = repo_info.get("owner", {}).get("login", "Unknown")
        self._commit = MockCommit(sha, author_name)
        self._commit.tree = MockTree(repo_path)
        self.head = MockHead(self._commit)
        branch_name = config.branch or repo_info.get("default_branch", "main")
        self.active_branch = MockBranch(branch_name)

    def iter_commits(self, **kwargs: Any) -> Iterator[MockCommit]:
        yield self._commit


# ===== 全局锁表（防止相同 repo_key 并发冲突） =====
_repo_locks: dict[str, Lock] = {}


@contextmanager
def repo_lock(key: str) -> Any:
    lock = _repo_locks.setdefault(key, Lock())
    lock.acquire()
    try:
        yield
    finally:
        lock.release()


# ===== Git 仓库管理器 =====
def _check_git_installation() -> bool:
    try:
        import subprocess

        subprocess.run(["git", "--version"], check=True, capture_output=True, text=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def _lazy_import_git() -> Any:
    try:
        from git import Repo
        from git.exc import GitCommandNotFound, InvalidGitRepositoryError

        return Repo, GitCommandNotFound, InvalidGitRepositoryError
    except ImportError as e:
        raise ImportError(
            "GitPython is required, install with `pip install GitPython`"
        ) from e


def _lazy_import_requests() -> Any:
    try:
        import requests

        return requests
    except ImportError as e:
        raise ImportError(
            "requests is required, install with `pip install requests`"
        ) from e


class GitRepoManager:
    CACHE_TTL_HOURS = 24  # 缓存有效时间

    def __init__(self) -> None:
        self.repos_dir = os.environ.get("WHISKER_REPO_SAVE_PATH") or os.path.join(
            tempfile.gettempdir(), "repo_download"
        )
        self._repos_cache: Dict[str, str] = {}
        self._repo_info_cache: Dict[str, Dict[str, Any]] = {}
        os.makedirs(self.repos_dir, exist_ok=True)

    # ==== 缓存时间标记 ====
    def _is_cache_expired(self, repo_path: str) -> bool:
        meta_path = os.path.join(repo_path, ".whisker_meta")
        if not os.path.exists(meta_path):
            return True
        try:
            with open(meta_path, "r") as f:
                last_time = float(json.load(f).get("last_update", 0))
            return (time.time() - last_time) > self.CACHE_TTL_HOURS * 3600
        except Exception:
            return True

    def _mark_cache_updated(self, repo_path: str) -> None:
        try:
            with open(os.path.join(repo_path, ".whisker_meta"), "w") as f:
                json.dump({"last_update": time.time()}, f)
        except Exception as e:
            logger.warning(f"Failed to mark cache update: {e}")

    def _safe_rmtree(self, path: str) -> None:
        try:
            shutil.rmtree(path)
        except OSError as e:
            logger.warning(f"Safe cleanup failed for {path}: {e}, trying rename")
            try:
                renamed = f"{path}_old_{uuid.uuid4().hex[:6]}"
                os.rename(path, renamed)
            except Exception as e2:
                logger.error(f"Rename also failed: {e2}")

    def _generate_repo_key(self, config: GithubRepoSourceConfig) -> str:
        parts = [config.repo_name]
        if config.branch:
            parts.append(config.branch)
        if config.commit_id:
            parts.append(config.commit_id)
        return "_".join(parts).replace("/", "_")

    def _is_github_repo(self, config: GithubRepoSourceConfig) -> bool:
        return "github.com" in config.url.lower()

    # ==== 核心 API ====
    def get_repo_path(self, config: GithubRepoSourceConfig) -> str:
        repo_key = self._generate_repo_key(config)
        with repo_lock(repo_key):
            repo_path = os.path.join(self.repos_dir, repo_key)
            if os.path.exists(repo_path) and not self._is_cache_expired(repo_path):
                logger.info(f"Using cached repository: {repo_path}")
                self._repos_cache[repo_key] = repo_path
                return repo_path
            if os.path.exists(repo_path):
                self._safe_rmtree(repo_path)
            repo_path = self._download_repo(config, repo_path)
            self._repos_cache[repo_key] = repo_path
            return repo_path

    def get_repo(self, config: GithubRepoSourceConfig) -> Union[Any, MockRepo]:
        """返回 GitPython Repo 或 MockRepo"""
        repo_path = self.get_repo_path(config)
        git_dir = os.path.join(repo_path, ".git")
        if os.path.exists(git_dir):
            try:
                Repo, _, _ = _lazy_import_git()
                return Repo(repo_path)
            except Exception as e:
                logger.warning(f"Failed to create GitPython Repo: {e}")
        if self._is_github_repo(config):
            repo_key = self._generate_repo_key(config)
            return MockRepo(repo_path, config, self._repo_info_cache.get(repo_key, {}))
        raise ValueError("Repository is not a git repo and not on GitHub")

    def cleanup_repo(self, config: GithubRepoSourceConfig) -> None:
        """
        清理指定仓库缓存目录和缓存信息
        """
        repo_key = self._generate_repo_key(config)
        if repo_key in self._repos_cache:
            repo_path = self._repos_cache[repo_key]
            try:
                if os.path.exists(repo_path):
                    self._safe_rmtree(repo_path)
                    logger.info(f"Cleaned up repository: {repo_path}")
            except Exception as e:
                logger.error(f"Error cleaning up repository {repo_path}: {e}")
            finally:
                del self._repos_cache[repo_key]
        if repo_key in self._repo_info_cache:
            del self._repo_info_cache[repo_key]

    # ==== 下载逻辑 ====
    def _download_repo(
        self, config: GithubRepoSourceConfig, repo_saved_path: str
    ) -> str:
        if os.path.exists(repo_saved_path):
            self._safe_rmtree(repo_saved_path)
        if _check_git_installation():
            try:
                clone_url = self._build_clone_url(config)
                self._clone_repo(
                    clone_url, repo_saved_path, config.branch, config.commit_id
                )
                self._mark_cache_updated(repo_saved_path)
                return repo_saved_path
            except Exception as e:
                logger.warning(f"Git clone failed: {e}")
                log_system_info()
                if os.path.exists(repo_saved_path):
                    self._safe_rmtree(repo_saved_path)
        if self._is_github_repo(config):
            self._download_github_zip(config, repo_saved_path)
            self._mark_cache_updated(repo_saved_path)
            return repo_saved_path
        raise ValueError(f"Failed to download repository: {config.repo_name}")

    def _build_clone_url(self, config: GithubRepoSourceConfig) -> str:
        base_url = config.url.rstrip("/")
        repo_name = config.repo_name
        if base_url.startswith("https://"):
            url_no_scheme = base_url[8:]
        elif base_url.startswith("http://"):
            url_no_scheme = base_url[7:]
        else:
            url_no_scheme = base_url
        if config.auth_info:
            return f"https://{config.auth_info}@{url_no_scheme}/{repo_name}.git"
        return f"https://{url_no_scheme}/{repo_name}.git"

    def _clone_repo(
        self,
        clone_url: str,
        repo_path: str,
        branch: Optional[str] = None,
        commit_id: Optional[str] = None,
        initial_depth: int = 1,
        max_fetch_tries: int = 5,
        depth_step: int = 20,
        max_retry_attempts: int = 3,
        retry_delay: float = 2.0,
    ) -> None:
        Repo, GitCommandNotFound, InvalidGitRepositoryError = _lazy_import_git()
        last_exception = None
        import subprocess

        for attempt in range(max_retry_attempts):
            try:
                if attempt > 0 and os.path.exists(repo_path):
                    self._safe_rmtree(repo_path)
                logger.info(
                    f"Cloning repository (attempt {attempt + 1}/{max_retry_attempts}):{clone_url}"
                )
                if branch:
                    repo = Repo.clone_from(
                        clone_url,
                        repo_path,
                        multi_options=["--filter=blob:limit=5m"],
                        branch=branch,
                        depth=initial_depth,
                    )
                else:
                    repo = Repo.clone_from(
                        clone_url,
                        repo_path,
                        multi_options=["--filter=blob:limit=5m"],
                        depth=initial_depth,
                    )

                # 放开 git 安全校验
                try:
                    subprocess.run(
                        [
                            "git",
                            "config",
                            "--global",
                            "--add",
                            "safe.directory",
                            repo_path,
                        ],
                        check=False,
                    )
                except Exception as se:
                    logger.warning(f"Could not set safe.directory for git: {se}")

                if commit_id:
                    for i in range(max_fetch_tries):
                        try:
                            repo.git.checkout(commit_id)
                            break
                        except Exception as e:
                            if any(
                                k in str(e).lower()
                                for k in ["not found", "unknown revision", "pathspec"]
                            ):
                                repo.git.fetch("origin", f"--deepen={depth_step}")
                                if branch:
                                    repo.git.checkout(branch)
                                continue
                            else:
                                raise
                    else:
                        raise ValueError(f"Failed to fetch commit {commit_id}")
                self._mark_cache_updated(repo_path)
                return
            except GitCommandNotFound:
                raise ValueError("Git command not found.")
            except InvalidGitRepositoryError as e:
                raise ValueError(f"Invalid git repository: {e}")
            except Exception as e:
                last_exception = e
                if attempt < max_retry_attempts - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2

        if last_exception:
            raise ValueError(
                f"Failed to clone after {max_retry_attempts} attempts: {last_exception}"
            )

    def _download_github_zip(
        self, config: GithubRepoSourceConfig, repo_path: str
    ) -> None:
        requests = _lazy_import_requests()
        repo_info = self._get_github_repo_info(config)
        ref = (
            config.commit_id or config.branch or repo_info.get("default_branch", "main")
        )
        zip_url = f"https://api.github.com/repos/{config.repo_name}/zipball/{ref}"
        headers = {}
        if config.auth_info:
            headers["Authorization"] = f"token {config.auth_info}"
        resp = requests.get(zip_url, headers=headers, stream=True)
        resp.raise_for_status()
        zip_path = os.path.join(
            self.repos_dir, f"{config.repo_name.replace('/', '_')}_{ref}.zip"
        )
        with open(zip_path, "wb") as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
        try:
            if os.path.exists(repo_path):
                self._safe_rmtree(repo_path)
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(self.repos_dir)
                part = config.repo_name.split("/")[-1]
                candidates = [
                    d
                    for d in os.listdir(self.repos_dir)
                    if os.path.isdir(os.path.join(self.repos_dir, d))
                ]
                for d in sorted(candidates):
                    if part in d:
                        shutil.move(os.path.join(self.repos_dir, d), repo_path)
                        return
                raise ValueError(f"Could not find extracted repo for {part}")
        finally:
            if os.path.exists(zip_path):
                os.unlink(zip_path)

    def _get_github_repo_info(self, config: GithubRepoSourceConfig) -> Dict[str, Any]:
        requests = _lazy_import_requests()
        repo_key = self._generate_repo_key(config)
        if repo_key in self._repo_info_cache:
            return self._repo_info_cache[repo_key]
        api_url = f"https://api.github.com/repos/{config.repo_name}"
        headers = {}
        if config.auth_info:
            headers["Authorization"] = f"token {config.auth_info}"
        resp = requests.get(api_url, headers=headers)
        resp.raise_for_status()
        info: Dict[str, Any] = resp.json()
        ref = config.commit_id or config.branch or info.get("default_branch", "main")
        branch_url = f"https://api.github.com/repos/{config.repo_name}/branches/{ref}"
        br_resp = requests.get(branch_url, headers=headers)
        if br_resp.status_code == 200:
            info["default_branch_sha"] = br_resp.json()["commit"]["sha"]
        else:
            info["default_branch_sha"] = "unknown"
        self._repo_info_cache[repo_key] = info
        return info


# ===== 提供全局单例 =====
_repo_manager = GitRepoManager()


def get_repo_manager() -> GitRepoManager:
    return _repo_manager
