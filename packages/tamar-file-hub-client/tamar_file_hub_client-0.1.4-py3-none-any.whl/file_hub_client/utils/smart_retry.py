"""
智能重试机制

提供基于错误类型的智能重试策略
"""
import asyncio
import functools
import time
import random
import grpc
from typing import TypeVar, Callable, Type, Tuple, Any, Optional, Dict, Set
from enum import Enum
import logging

T = TypeVar("T")
logger = logging.getLogger(__name__)


class RetryStrategy(Enum):
    """重试策略枚举"""
    NO_RETRY = "no_retry"              # 不重试
    IMMEDIATE = "immediate"            # 立即重试
    LINEAR = "linear"                  # 线性退避
    EXPONENTIAL = "exponential"        # 指数退避
    EXPONENTIAL_JITTER = "exp_jitter"  # 指数退避+抖动


class ErrorClassifier:
    """错误分类器，判断错误是否可重试"""
    
    # 可重试的 gRPC 状态码
    RETRYABLE_GRPC_CODES = {
        grpc.StatusCode.UNAVAILABLE,       # 服务不可用
        grpc.StatusCode.DEADLINE_EXCEEDED, # 超时
        grpc.StatusCode.RESOURCE_EXHAUSTED,# 资源耗尽（可能需要退避）
        grpc.StatusCode.ABORTED,           # 操作被中止（如锁冲突）
        grpc.StatusCode.INTERNAL,          # 内部错误（部分情况）
    }
    
    # 不可重试的 gRPC 状态码
    NON_RETRYABLE_GRPC_CODES = {
        grpc.StatusCode.INVALID_ARGUMENT,   # 参数无效
        grpc.StatusCode.NOT_FOUND,          # 资源不存在
        grpc.StatusCode.ALREADY_EXISTS,     # 资源已存在
        grpc.StatusCode.PERMISSION_DENIED,  # 权限拒绝
        grpc.StatusCode.UNAUTHENTICATED,    # 未认证
        grpc.StatusCode.FAILED_PRECONDITION,# 前置条件失败
        grpc.StatusCode.OUT_OF_RANGE,       # 超出范围
        grpc.StatusCode.UNIMPLEMENTED,      # 未实现
        grpc.StatusCode.DATA_LOSS,          # 数据丢失
    }
    
    # 可重试的 HTTP 状态码
    RETRYABLE_HTTP_CODES = {408, 429, 500, 502, 503, 504}
    
    # 可重试的错误消息关键词
    RETRYABLE_ERROR_KEYWORDS = [
        'timeout', 'timed out',
        'connection reset', 'connection refused', 'connection error',
        'temporarily unavailable', 'service unavailable',
        'too many requests', 'rate limit',
        'lock conflict', 'version conflict',
        'resource busy', 'resource contention',
        'gateway timeout', 'bad gateway',
        'network unreachable', 'dns resolution failed',
    ]
    
    # 不可重试的错误消息关键词
    NON_RETRYABLE_ERROR_KEYWORDS = [
        'invalid argument', 'invalid parameter', 'validation error',
        'not found', 'does not exist',
        'already exists', 'duplicate',
        'permission denied', 'forbidden', 'unauthorized',
        'authentication failed', 'invalid credentials',
        'insufficient funds', 'quota exceeded',
        'constraint violation', 'foreign key violation',
    ]
    
    @classmethod
    def is_retryable(cls, error: Exception) -> Tuple[bool, RetryStrategy]:
        """
        判断错误是否可重试
        
        Returns:
            (是否可重试, 重试策略)
        """
        # 1. 检查 gRPC 错误
        if isinstance(error, grpc.RpcError):
            code = error.code()
            if code in cls.NON_RETRYABLE_GRPC_CODES:
                return False, RetryStrategy.NO_RETRY
            if code in cls.RETRYABLE_GRPC_CODES:
                # 资源耗尽需要更长的退避时间
                if code == grpc.StatusCode.RESOURCE_EXHAUSTED:
                    return True, RetryStrategy.EXPONENTIAL_JITTER
                # 中止操作（如锁冲突）使用指数退避
                elif code == grpc.StatusCode.ABORTED:
                    return True, RetryStrategy.EXPONENTIAL
                # 其他使用指数退避
                else:
                    return True, RetryStrategy.EXPONENTIAL
        
        # 2. 检查 HTTP 错误（通过状态码）
        if hasattr(error, 'response') and hasattr(error.response, 'status_code'):
            status_code = error.response.status_code
            if status_code in cls.RETRYABLE_HTTP_CODES:
                # 429 需要更长的退避时间和抖动
                if status_code == 429:
                    return True, RetryStrategy.EXPONENTIAL_JITTER
                return True, RetryStrategy.EXPONENTIAL
            elif 400 <= status_code < 500:  # 客户端错误不重试
                return False, RetryStrategy.NO_RETRY
        
        # 3. 检查错误消息
        error_msg = str(error).lower()
        
        # 检查不可重试关键词
        for keyword in cls.NON_RETRYABLE_ERROR_KEYWORDS:
            if keyword in error_msg:
                return False, RetryStrategy.NO_RETRY
        
        # 检查可重试关键词
        for keyword in cls.RETRYABLE_ERROR_KEYWORDS:
            if keyword in error_msg:
                # 速率限制使用抖动策略
                if 'rate limit' in error_msg or 'too many requests' in error_msg:
                    return True, RetryStrategy.EXPONENTIAL_JITTER
                return True, RetryStrategy.EXPONENTIAL
        
        # 4. 特定异常类型检查
        from ..errors import (
            ConnectionError, TimeoutError,  # 可重试
            ValidationError, PermissionError, FileNotFoundError  # 不可重试
        )
        
        if isinstance(error, (ConnectionError, TimeoutError)):
            return True, RetryStrategy.EXPONENTIAL
        
        if isinstance(error, (ValidationError, PermissionError, FileNotFoundError)):
            return False, RetryStrategy.NO_RETRY
        
        # 5. 默认不重试未知错误
        return False, RetryStrategy.NO_RETRY
    
    @classmethod
    def get_retry_delay(
        cls,
        strategy: RetryStrategy,
        attempt: int,
        base_delay: float,
        max_delay: float,
        backoff_factor: float = 2.0
    ) -> float:
        """计算重试延迟时间"""
        if strategy == RetryStrategy.NO_RETRY:
            return 0
        
        elif strategy == RetryStrategy.IMMEDIATE:
            return 0
        
        elif strategy == RetryStrategy.LINEAR:
            delay = base_delay * attempt
            
        elif strategy == RetryStrategy.EXPONENTIAL:
            delay = base_delay * (backoff_factor ** (attempt - 1))
            
        elif strategy == RetryStrategy.EXPONENTIAL_JITTER:
            # 指数退避 + 随机抖动 (±25%)
            base = base_delay * (backoff_factor ** (attempt - 1))
            jitter = base * 0.25 * (2 * random.random() - 1)
            delay = base + jitter
        
        else:
            delay = base_delay
        
        return min(delay, max_delay)


def smart_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    retry_on: Optional[Tuple[Type[Exception], ...]] = None,
    dont_retry_on: Optional[Tuple[Type[Exception], ...]] = None,
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    智能重试装饰器
    
    Args:
        max_retries: 最大重试次数
        base_delay: 基础延迟时间（秒）
        max_delay: 最大延迟时间（秒）
        backoff_factor: 退避因子
        retry_on: 只在这些异常时重试（如果指定）
        dont_retry_on: 不在这些异常时重试（优先级高于 retry_on）
        on_retry: 重试时的回调函数 (exception, attempt) -> None
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs) -> T:
                last_exception = None
                
                for attempt in range(1, max_retries + 2):
                    try:
                        result = await func(*args, **kwargs)
                        if attempt > 1:
                            logger.info(
                                f"✅ 重试成功 | 操作: {func.__name__} | "
                                f"在第 {attempt} 次尝试后成功"
                            )
                        return result
                    except Exception as e:
                        last_exception = e
                        
                        # 检查是否在不重试列表中
                        if dont_retry_on and isinstance(e, dont_retry_on):
                            logger.debug(f"错误类型 {type(e).__name__} 在不重试列表中，直接抛出")
                            raise
                        
                        # 检查是否在重试列表中（如果指定了）
                        if retry_on and not isinstance(e, retry_on):
                            logger.debug(f"错误类型 {type(e).__name__} 不在重试列表中，直接抛出")
                            raise
                        
                        # 使用错误分类器判断
                        is_retryable, strategy = ErrorClassifier.is_retryable(e)
                        
                        if not is_retryable or attempt > max_retries:
                            if attempt > max_retries:
                                logger.warning(f"达到最大重试次数 {max_retries}，停止重试")
                            else:
                                logger.debug(f"错误不可重试: {type(e).__name__}: {str(e)}")
                            raise
                        
                        # 计算延迟时间
                        delay = ErrorClassifier.get_retry_delay(
                            strategy, attempt, base_delay, max_delay, backoff_factor
                        )
                        
                        # 记录详细的重试日志
                        logger.warning(
                            f"🔄 触发重试机制 | "
                            f"操作: {func.__name__} | "
                            f"尝试: {attempt}/{max_retries + 1} | "
                            f"错误类型: {type(e).__name__} | "
                            f"错误信息: {str(e)} | "
                            f"重试策略: {strategy.value} | "
                            f"延迟时间: {delay:.1f}秒"
                        )
                        
                        # 如果是调试模式，记录更详细的信息
                        logger.debug(
                            f"重试详情 - 函数: {func.__module__}.{func.__name__}, "
                            f"参数: args={args}, kwargs={kwargs}"
                        )
                        
                        # 调用重试回调
                        if on_retry:
                            on_retry(e, attempt)
                        
                        # 等待后重试
                        if delay > 0:
                            await asyncio.sleep(delay)
                
                raise last_exception
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs) -> T:
                last_exception = None
                
                for attempt in range(1, max_retries + 2):
                    try:
                        result = func(*args, **kwargs)
                        if attempt > 1:
                            logger.info(
                                f"✅ 重试成功 | 操作: {func.__name__} | "
                                f"在第 {attempt} 次尝试后成功"
                            )
                        return result
                    except Exception as e:
                        last_exception = e
                        
                        # 检查是否在不重试列表中
                        if dont_retry_on and isinstance(e, dont_retry_on):
                            logger.debug(f"错误类型 {type(e).__name__} 在不重试列表中，直接抛出")
                            raise
                        
                        # 检查是否在重试列表中（如果指定了）
                        if retry_on and not isinstance(e, retry_on):
                            logger.debug(f"错误类型 {type(e).__name__} 不在重试列表中，直接抛出")
                            raise
                        
                        # 使用错误分类器判断
                        is_retryable, strategy = ErrorClassifier.is_retryable(e)
                        
                        if not is_retryable or attempt > max_retries:
                            if attempt > max_retries:
                                logger.warning(f"达到最大重试次数 {max_retries}，停止重试")
                            else:
                                logger.debug(f"错误不可重试: {type(e).__name__}: {str(e)}")
                            raise
                        
                        # 计算延迟时间
                        delay = ErrorClassifier.get_retry_delay(
                            strategy, attempt, base_delay, max_delay, backoff_factor
                        )
                        
                        # 记录详细的重试日志
                        logger.warning(
                            f"🔄 触发重试机制 | "
                            f"操作: {func.__name__} | "
                            f"尝试: {attempt}/{max_retries + 1} | "
                            f"错误类型: {type(e).__name__} | "
                            f"错误信息: {str(e)} | "
                            f"重试策略: {strategy.value} | "
                            f"延迟时间: {delay:.1f}秒"
                        )
                        
                        # 如果是调试模式，记录更详细的信息
                        logger.debug(
                            f"重试详情 - 函数: {func.__module__}.{func.__name__}, "
                            f"参数: args={args}, kwargs={kwargs}"
                        )
                        
                        # 调用重试回调
                        if on_retry:
                            on_retry(e, attempt)
                        
                        # 等待后重试
                        if delay > 0:
                            time.sleep(delay)
                
                raise last_exception
            return sync_wrapper
    
    return decorator


# 保留原有的装饰器兼容性
def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    兼容旧版本的重试装饰器，内部使用智能重试
    """
    return smart_retry(
        max_retries=max_retries,
        base_delay=initial_delay,
        max_delay=max_delay,
        backoff_factor=backoff_factor,
        retry_on=exceptions if exceptions != (Exception,) else None
    )


# 特定场景的预配置装饰器
def retry_on_network_errors(max_retries: int = 3):
    """只在网络错误时重试"""
    from ..errors import ConnectionError, TimeoutError
    return smart_retry(
        max_retries=max_retries,
        base_delay=1.0,
        max_delay=30.0,
        retry_on=(ConnectionError, TimeoutError, grpc.RpcError)
    )


def retry_on_conflict(max_retries: int = 5):
    """在冲突时重试（如锁冲突、版本冲突）"""
    return smart_retry(
        max_retries=max_retries,
        base_delay=0.5,
        max_delay=10.0,
        backoff_factor=1.5
    )


def no_retry():
    """不进行任何重试"""
    return smart_retry(max_retries=0)


def retry_on_transient_errors(max_retries: int = 2):
    """
    只在临时性错误时重试（适用于查询操作）
    
    - 网络临时故障会重试
    - NOT_FOUND、权限错误等不会重试
    - 重试次数较少，延迟较短
    """
    return smart_retry(
        max_retries=max_retries,
        base_delay=0.5,
        max_delay=5.0,
        backoff_factor=2.0
    )