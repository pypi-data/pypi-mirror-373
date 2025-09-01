from abc import ABC, abstractmethod
from typing import List, Optional

from whiskerrag_types.model.multi_modal import Image

from .async_utils import run_async_safe


class BaseEmbedding(ABC):

    @classmethod
    def sync_health_check(cls) -> bool:
        """
        同步健康检查方法，用于注册时验证

        Returns:
            True表示健康检查通过，False表示失败
        """
        try:
            return run_async_safe(cls.health_check)
        except Exception as e:
            print(f"Health check failed for {cls.__name__}: {e}")
            return False

    @classmethod
    @abstractmethod
    async def health_check(cls) -> bool:
        pass

    @abstractmethod
    async def embed_documents(
        self, documents: List[str], timeout: Optional[int]
    ) -> List[List[float]]:
        pass

    @abstractmethod
    async def embed_text(self, text: str, timeout: Optional[int]) -> List[float]:
        pass

    @abstractmethod
    async def embed_text_query(self, text: str, timeout: Optional[int]) -> List[float]:
        pass

    @abstractmethod
    async def embed_image(self, image: Image, timeout: Optional[int]) -> List[float]:
        pass
