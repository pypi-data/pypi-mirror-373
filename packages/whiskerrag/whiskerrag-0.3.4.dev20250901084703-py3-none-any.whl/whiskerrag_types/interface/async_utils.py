"""
异步转同步的通用工具模块

提供了在不同环境下（有/无事件循环）安全执行异步代码的工具函数。
"""

import asyncio
import functools
from typing import Any, Awaitable, Callable, Coroutine, TypeVar, cast

T = TypeVar("T")


def run_async_safe(
    coro_func: Callable[..., Awaitable[T]], *args: Any, **kwargs: Any
) -> T:
    """
    安全地运行异步函数，自动处理事件循环检测

    这个函数会：
    1. 检测当前是否已经在事件循环中
    2. 如果在事件循环中，使用 asyncio.create_task 在当前循环中执行
    3. 如果不在事件循环中，直接使用 asyncio.run

    Args:
        coro_func: 异步函数
        *args: 传递给异步函数的位置参数
        **kwargs: 传递给异步函数的关键字参数

    Returns:
        异步函数的返回值

    Raises:
        Exception: 异步函数执行过程中的任何异常

    Example:
        >>> async def async_task(x: int) -> int:
        ...     await asyncio.sleep(0.1)
        ...     return x * 2
        >>>
        >>> result = run_async_safe(async_task, 5)
        >>> print(result)  # 10
    """
    try:
        # 检查是否已经在事件循环中
        asyncio.get_running_loop()
        # 如果在事件循环中，需要在新线程中运行
        import concurrent.futures

        def run_in_thread() -> T:
            # 将 Awaitable 转换为 Coroutine 以满足 asyncio.run 的类型要求
            coro = coro_func(*args, **kwargs)
            return asyncio.run(cast(Coroutine[Any, Any, T], coro))

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result()

    except RuntimeError:
        # 没有运行中的事件循环，可以直接使用 asyncio.run
        coro = coro_func(*args, **kwargs)
        return asyncio.run(cast(Coroutine[Any, Any, T], coro))


def async_to_sync(coro_func: Callable[..., Awaitable[T]]) -> Callable[..., T]:
    """
    装饰器：将异步函数转换为同步函数

    这个装饰器会自动处理事件循环检测，让异步函数可以在同步环境中安全调用。

    Args:
        coro_func: 要转换的异步函数

    Returns:
        转换后的同步函数

    Example:
        >>> @async_to_sync
        ... async def async_task(x: int) -> int:
        ...     await asyncio.sleep(0.1)
        ...     return x * 2
        >>>
        >>> result = async_task(5)  # 现在可以同步调用
        >>> print(result)  # 10
    """

    @functools.wraps(coro_func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        return run_async_safe(coro_func, *args, **kwargs)

    return wrapper


class AsyncToSyncMixin:
    """
    混入类：为类提供异步转同步的能力

    继承这个混入类后，可以使用 _run_async_safe 方法来安全执行异步代码。

    Example:
        >>> class MyClass(AsyncToSyncMixin):
        ...     async def async_method(self, x: int) -> int:
        ...         await asyncio.sleep(0.1)
        ...         return x * 2
        ...
        ...     def sync_method(self, x: int) -> int:
        ...         return self._run_async_safe(self.async_method, x)
        >>>
        >>> obj = MyClass()
        >>> result = obj.sync_method(5)
        >>> print(result)  # 10
    """

    def _run_async_safe(
        self, coro_func: Callable[..., Awaitable[T]], *args: Any, **kwargs: Any
    ) -> T:
        """
        安全地运行异步方法

        Args:
            coro_func: 异步方法
            *args: 传递给异步方法的位置参数
            **kwargs: 传递给异步方法的关键字参数

        Returns:
            异步方法的返回值
        """
        return run_async_safe(coro_func, *args, **kwargs)
