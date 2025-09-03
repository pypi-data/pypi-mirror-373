"""
重试工具

提供向后兼容的重试机制，同时支持智能重试
"""
import asyncio
import functools
import time
from typing import TypeVar, Callable, Type, Tuple, Any, Dict
import logging

# 导入智能重试功能
from .smart_retry import (
    smart_retry,
    retry_on_network_errors,
    retry_on_conflict,
    no_retry,
    ErrorClassifier,
    RetryStrategy
)

T = TypeVar("T")
logger = logging.getLogger(__name__)


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    带退避策略的重试装饰器
    
    现在会智能判断错误是否可重试，避免对明显不可恢复的错误进行重试
    
    Args:
        max_retries: 最大重试次数
        initial_delay: 初始延迟（秒）
        backoff_factor: 退避因子
        max_delay: 最大延迟（秒）
        exceptions: 需要重试的异常类型
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs) -> T:
                delay = initial_delay
                last_exception = None
                
                for attempt in range(max_retries + 1):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        
                        # 使用 ErrorClassifier 检查错误是否可重试
                        is_retryable, _ = ErrorClassifier.is_retryable(e)
                        
                        if not is_retryable:
                            # 尝试从 kwargs 中获取 request_id
                            request_id = kwargs.get('request_id', 'unknown')
                            
                            logger.debug(
                                f"🚫 不可重试错误 | 操作: {func.__name__} | "
                                f"request_id: {request_id} | "
                                f"错误: {type(e).__name__}: {str(e)} | "
                                f"直接抛出异常"
                            )
                            raise
                        
                        if attempt < max_retries:
                            # 提取更详细的错误信息
                            error_details = str(e)
                            if hasattr(e, 'code') and hasattr(e, 'details'):
                                # gRPC 错误
                                error_details = f"gRPC {e.code().name}: {e.details()}"
                            elif hasattr(e, 'response') and hasattr(e.response, 'status_code'):
                                # HTTP 错误
                                error_details = f"HTTP {e.response.status_code}: {str(e)}"
                            
                            # 尝试从 kwargs 中获取 request_id
                            request_id = kwargs.get('request_id', 'unknown')
                            
                            logger.warning(
                                f"🔄 触发重试 | 操作: {func.__name__} | "
                                f"request_id: {request_id} | "
                                f"尝试: {attempt + 1}/{max_retries + 1} | "
                                f"错误类型: {type(e).__name__} | "
                                f"错误详情: {error_details} | "
                                f"延迟: {delay:.1f}秒"
                            )
                            await asyncio.sleep(delay)
                            delay = min(delay * backoff_factor, max_delay)
                        else:
                            # 尝试从 kwargs 中获取 request_id
                            request_id = kwargs.get('request_id', 'unknown')
                            
                            logger.error(
                                f"❌ 重试失败 | 操作: {func.__name__} | "
                                f"request_id: {request_id} | "
                                f"已达最大重试次数: {max_retries} | "
                                f"最终错误: {type(e).__name__}: {str(e)}"
                            )
                            raise
                            
                raise last_exception
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs) -> T:
                delay = initial_delay
                last_exception = None
                
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        
                        # 使用 ErrorClassifier 检查错误是否可重试
                        is_retryable, _ = ErrorClassifier.is_retryable(e)
                        
                        if not is_retryable:
                            # 尝试从 kwargs 中获取 request_id
                            request_id = kwargs.get('request_id', 'unknown')
                            
                            logger.debug(
                                f"🚫 不可重试错误 | 操作: {func.__name__} | "
                                f"request_id: {request_id} | "
                                f"错误: {type(e).__name__}: {str(e)} | "
                                f"直接抛出异常"
                            )
                            raise
                        
                        if attempt < max_retries:
                            # 提取更详细的错误信息
                            error_details = str(e)
                            if hasattr(e, 'code') and hasattr(e, 'details'):
                                # gRPC 错误
                                error_details = f"gRPC {e.code().name}: {e.details()}"
                            elif hasattr(e, 'response') and hasattr(e.response, 'status_code'):
                                # HTTP 错误
                                error_details = f"HTTP {e.response.status_code}: {str(e)}"
                            
                            # 尝试从 kwargs 中获取 request_id
                            request_id = kwargs.get('request_id', 'unknown')
                            
                            logger.warning(
                                f"🔄 触发重试 | 操作: {func.__name__} | "
                                f"request_id: {request_id} | "
                                f"尝试: {attempt + 1}/{max_retries + 1} | "
                                f"错误类型: {type(e).__name__} | "
                                f"错误详情: {error_details} | "
                                f"延迟: {delay:.1f}秒"
                            )
                            time.sleep(delay)
                            delay = min(delay * backoff_factor, max_delay)
                        else:
                            # 尝试从 kwargs 中获取 request_id
                            request_id = kwargs.get('request_id', 'unknown')
                            
                            logger.error(
                                f"❌ 重试失败 | 操作: {func.__name__} | "
                                f"request_id: {request_id} | "
                                f"已达最大重试次数: {max_retries} | "
                                f"最终错误: {type(e).__name__}: {str(e)}"
                            )
                            raise
                            
                raise last_exception
            return sync_wrapper
            
    return decorator


def retry_on_lock_conflict(
    max_retries: int = 5,
    initial_delay: float = 0.5,
    backoff_factor: float = 1.5,
    max_delay: float = 10.0
):
    """
    专门处理锁冲突的重试装饰器
    
    当响应中包含 conflict_type: "lock_conflict" 时进行重试
    
    Args:
        max_retries: 最大重试次数（默认5次）
        initial_delay: 初始延迟（默认0.5秒）
        backoff_factor: 退避因子（默认1.5）
        max_delay: 最大延迟（默认10秒）
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs) -> T:
                delay = initial_delay
                last_result = None
                
                for attempt in range(max_retries + 1):
                    result = await func(*args, **kwargs)
                    
                    # 检查是否是锁冲突
                    if _is_lock_conflict(result):
                        last_result = result
                        if attempt < max_retries:
                            # 提取冲突详细信息
                            conflict_details = "lock_conflict"
                            if isinstance(result, dict):
                                conflict_info = result.get('conflict_info', {})
                                if conflict_info:
                                    conflict_details = f"{conflict_info.get('conflict_type', 'lock_conflict')}"
                                    if 'resolution_suggestion' in conflict_info:
                                        conflict_details += f" - {conflict_info['resolution_suggestion']}"
                                if 'error_message' in result:
                                    conflict_details += f" - {result['error_message']}"
                            
                            # 尝试从 kwargs 中获取 request_id
                            request_id = kwargs.get('request_id', 'unknown')
                            
                            logger.warning(
                                f"🔒 锁冲突重试 | 操作: {func.__name__} | "
                                f"request_id: {request_id} | "
                                f"尝试: {attempt + 1}/{max_retries + 1} | "
                                f"冲突详情: {conflict_details} | "
                                f"延迟: {delay:.1f}秒"
                            )
                            await asyncio.sleep(delay)
                            delay = min(delay * backoff_factor, max_delay)
                            continue
                        else:
                            # 尝试从 kwargs 中获取 request_id
                            request_id = kwargs.get('request_id', 'unknown')
                            
                            logger.error(
                                f"❌ 锁冲突重试失败 | 操作: {func.__name__} | "
                                f"request_id: {request_id} | "
                                f"已达最大重试次数: {max_retries} | "
                                f"返回最后的冲突结果"
                            )
                    
                    return result
                
                # 如果所有重试都失败了，返回最后的结果
                return last_result
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs) -> T:
                delay = initial_delay
                last_result = None
                
                for attempt in range(max_retries + 1):
                    result = func(*args, **kwargs)
                    
                    # 检查是否是锁冲突
                    if _is_lock_conflict(result):
                        last_result = result
                        if attempt < max_retries:
                            # 提取冲突详细信息
                            conflict_details = "lock_conflict"
                            if isinstance(result, dict):
                                conflict_info = result.get('conflict_info', {})
                                if conflict_info:
                                    conflict_details = f"{conflict_info.get('conflict_type', 'lock_conflict')}"
                                    if 'resolution_suggestion' in conflict_info:
                                        conflict_details += f" - {conflict_info['resolution_suggestion']}"
                                if 'error_message' in result:
                                    conflict_details += f" - {result['error_message']}"
                            
                            # 尝试从 kwargs 中获取 request_id
                            request_id = kwargs.get('request_id', 'unknown')
                            
                            logger.warning(
                                f"🔒 锁冲突重试 | 操作: {func.__name__} | "
                                f"request_id: {request_id} | "
                                f"尝试: {attempt + 1}/{max_retries + 1} | "
                                f"冲突详情: {conflict_details} | "
                                f"延迟: {delay:.1f}秒"
                            )
                            time.sleep(delay)
                            delay = min(delay * backoff_factor, max_delay)
                            continue
                        else:
                            # 尝试从 kwargs 中获取 request_id
                            request_id = kwargs.get('request_id', 'unknown')
                            
                            logger.error(
                                f"❌ 锁冲突重试失败 | 操作: {func.__name__} | "
                                f"request_id: {request_id} | "
                                f"已达最大重试次数: {max_retries} | "
                                f"返回最后的冲突结果"
                            )
                    
                    return result
                
                # 如果所有重试都失败了，返回最后的结果
                return last_result
            return sync_wrapper
            
    return decorator


def _is_lock_conflict(result: Any) -> bool:
    """
    检查结果是否包含锁冲突
    
    Args:
        result: API调用的结果
        
    Returns:
        是否是锁冲突
    """
    if result is None:
        return False
    
    # 检查错误信息中是否包含锁冲突的关键字（统一转换为小写比对）
    lock_conflict_messages = [
        'failed to acquire necessary locks',
        'lock_conflict',
        'lock conflict'
    ]
    
    # 添加调试信息
    import logging
    logger = logging.getLogger(__name__)
    logger.debug(f"Checking for lock conflict in result: {type(result)}")
    
    # 处理字典格式的响应
    if isinstance(result, dict):
        # 检查 conflict_info
        conflict_info = result.get('conflict_info', {})
        if isinstance(conflict_info, dict):
            # 检查 conflict_type
            if conflict_info.get('conflict_type') == 'lock_conflict':
                return True
            # 检查 resolution_suggestion 中的信息
            suggestion = conflict_info.get('resolution_suggestion', '').lower()
            if any(msg in suggestion for msg in lock_conflict_messages):
                return True
        
        # 检查顶层的 conflict_type
        if result.get('conflict_type') == 'lock_conflict':
            return True
            
        # 检查 error_message
        error_msg = result.get('error_message', '').lower()
        logger.debug(f"Checking error_message: '{error_msg}'")
        if any(msg in error_msg for msg in lock_conflict_messages):
            logger.debug(f"Found lock conflict in error_message: '{error_msg}'")
            return True
            
    # 处理对象格式的响应
    elif hasattr(result, 'conflict_info'):
        conflict_info = getattr(result, 'conflict_info', None)
        if conflict_info:
            # 检查 conflict_type
            if hasattr(conflict_info, 'conflict_type'):
                if getattr(conflict_info, 'conflict_type') == 'lock_conflict':
                    return True
            # 检查 resolution_suggestion
            if hasattr(conflict_info, 'resolution_suggestion'):
                suggestion = getattr(conflict_info, 'resolution_suggestion', '').lower()
                if any(msg in suggestion for msg in lock_conflict_messages):
                    return True
    
    # 检查 success 字段和 error_message
    if hasattr(result, 'success') and not getattr(result, 'success', True):
        # 检查 conflict_info
        if hasattr(result, 'conflict_info'):
            conflict_info = getattr(result, 'conflict_info', None)
            if conflict_info and hasattr(conflict_info, 'conflict_type'):
                if getattr(conflict_info, 'conflict_type') == 'lock_conflict':
                    return True
        
        # 检查 error_message
        if hasattr(result, 'error_message'):
            error_msg = getattr(result, 'error_message', '').lower()
            if any(msg in error_msg for msg in lock_conflict_messages):
                return True
    
    # 对于纯对象响应，检查 error_message 字段
    if hasattr(result, 'error_message'):
        error_msg = getattr(result, 'error_message', '').lower()
        if any(msg in error_msg for msg in lock_conflict_messages):
            return True
    
    return False 