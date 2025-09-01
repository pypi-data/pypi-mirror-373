from decorator import decorator
import time
from typing import Any

from sycommon.logging.kafka_log import SYLogger


@decorator
def timing(func, tag: str = None, *args, **kw):
    """
    记录函数执行耗时的装饰器，支持普通函数、生成器和异步生成器

    参数:
        tag: 日志前缀标签
    """
    start_time = time.perf_counter()

    try:
        result = func(*args, **kw)
    except Exception as e:
        end_time = time.perf_counter()
        _log_timing(func, end_time - start_time, tag, error=str(e))
        raise e

    # 处理同步生成器
    if _is_generator(result):
        def wrapped_generator():
            try:
                yield from result
            finally:
                end_time = time.perf_counter()
                _log_timing(func, end_time - start_time, tag)
        return wrapped_generator()

    # 处理异步生成器
    elif _is_async_generator(result):
        async def wrapped_async_generator():
            try:
                async for item in result:
                    yield item
            finally:
                end_time = time.perf_counter()
                _log_timing(func, end_time - start_time, tag)
        return wrapped_async_generator()

    # 普通函数返回值
    else:
        end_time = time.perf_counter()
        _log_timing(func, end_time - start_time, tag)
        return result


def _is_generator(obj: Any) -> bool:
    """检查对象是否为生成器"""
    return hasattr(obj, '__iter__') and hasattr(obj, '__next__')


def _is_async_generator(obj: Any) -> bool:
    """检查对象是否为异步生成器"""
    return hasattr(obj, '__aiter__') and hasattr(obj, '__anext__')


def _log_timing(func, duration: float, tag: str = None, error: str = None):
    """格式化并记录耗时信息"""
    base_msg = f"Function '{func.__name__}' executed in {duration:.4f} seconds"

    if tag:
        base_msg = f"{tag} {base_msg}"

    if error:
        SYLogger.error(f"{base_msg} (Error: {error})")
    else:
        SYLogger.info(base_msg)
