"""
日志配置和工具
"""
import logging
import sys
import time
import json
import traceback
from typing import Optional, Any, Dict
from functools import wraps
from contextlib import contextmanager
from datetime import datetime

# 创建SDK专用的日志记录器 - 使用独立的命名空间避免冲突
SDK_LOGGER_NAME = "file_hub_client.grpc"
logger = logging.getLogger(SDK_LOGGER_NAME)


class GrpcJSONFormatter(logging.Formatter):
    """gRPC请求的JSON格式化器"""
    
    def format(self, record):
        log_type = getattr(record, "log_type", "info")
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "type": log_type,
            "uri": getattr(record, "uri", None),
            "request_id": getattr(record, "request_id", None),
            "data": getattr(record, "data", None),
            "message": record.getMessage(),
            "duration": getattr(record, "duration", None),
            "logger": record.name,  # 添加logger名称以区分SDK日志
        }
        
        # 增加 trace 支持
        if hasattr(record, "trace"):
            log_data["trace"] = getattr(record, "trace")
            
        # 添加异常信息（如果有的话）
        if hasattr(record, "exc_info") and record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info)
            }
            
        # 过滤掉None值
        log_data = {k: v for k, v in log_data.items() if v is not None}
        
        return json.dumps(log_data, ensure_ascii=False)


def get_default_formatter() -> logging.Formatter:
    """获取默认的JSON格式化器"""
    return GrpcJSONFormatter()


def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    enable_grpc_logging: bool = True,
    log_request_payload: bool = False,
    log_response_payload: bool = False,
    handler: Optional[logging.Handler] = None,
    use_json_format: bool = True
):
    """
    设置SDK日志记录配置
    
    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: 自定义日志格式（当use_json_format=False时使用）
        enable_grpc_logging: 是否启用gRPC请求日志
        log_request_payload: 是否记录请求载荷
        log_response_payload: 是否记录响应载荷
        handler: 自定义日志处理器
        use_json_format: 是否使用JSON格式（默认True）
    """
    # 设置日志级别
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # 清除现有的处理器（只清除SDK的logger）
    logger.handlers.clear()
    
    # 创建处理器
    if handler is None:
        handler = logging.StreamHandler(sys.stdout)
    
    # 设置日志格式
    if use_json_format:
        formatter = get_default_formatter()
    else:
        if format_string is None:
            format_string = "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
        formatter = logging.Formatter(format_string, datefmt="%Y-%m-%d %H:%M:%S")
    
    handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(handler)
    
    # 设置gRPC日志配置
    logger.grpc_logging_enabled = enable_grpc_logging
    logger.log_request_payload = log_request_payload
    logger.log_response_payload = log_response_payload
    
    # 防止日志传播到根日志记录器 - 保持SDK日志独立
    logger.propagate = False
    
    # 对整个 file_hub_client 包设置隔离，确保所有子模块的日志都不会传播
    parent_logger = logging.getLogger('file_hub_client')
    parent_logger.propagate = False
    
    # 初始化日志（使用JSON格式）
    if enable_grpc_logging:
        log_record = logging.LogRecord(
            name=logger.name,
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="📡 文件中心客户端 gRPC 日志已初始化",
            args=(),
            exc_info=None
        )
        log_record.log_type = "info"
        log_record.data = {
            "level": level,
            "grpc_logging": enable_grpc_logging,
            "json_format": use_json_format
        }
        logger.handle(log_record)


def get_logger() -> logging.Logger:
    """获取SDK日志记录器"""
    return logger


class GrpcRequestLogger:
    """gRPC请求日志记录器"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.enable_grpc_logging = getattr(logger, 'grpc_logging_enabled', True)
        self.log_request_payload = getattr(logger, 'log_request_payload', False)
        self.log_response_payload = getattr(logger, 'log_response_payload', False)
    
    def log_request_start(self, method_name: str, request_id: str, metadata: Dict[str, Any], 
                         request_payload: Any = None):
        """记录请求开始"""
        if not self.enable_grpc_logging:
            return
            
        # 提取关键元数据
        user_info = {}
        if metadata:
            metadata_dict = dict(metadata) if isinstance(metadata, list) else metadata
            user_info = {
                'org_id': metadata_dict.get('x-org-id'),
                'user_id': metadata_dict.get('x-user-id'),
                'client_ip': metadata_dict.get('x-client-ip'),  # SDK客户端服务IP
                'user_ip': metadata_dict.get('x-user-ip'),      # 用户真实IP
                'client_version': metadata_dict.get('x-client-version')
            }
            user_info = {k: v for k, v in user_info.items() if v is not None}
        
        # 创建日志记录
        log_record = logging.LogRecord(
            name=self.logger.name,
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=f"📤 gRPC 请求: {method_name}",
            args=(),
            exc_info=None
        )
        
        # 添加自定义字段
        log_record.log_type = "request"
        log_record.uri = method_name
        log_record.request_id = request_id
        log_record.data = user_info
        
        # 记录请求载荷
        if request_payload is not None:
            if isinstance(request_payload, dict):
                # 已经是字典格式，直接合并
                log_record.data.update(request_payload)
            else:
                # 其他格式，添加到payload字段
                log_record.data["payload"] = request_payload
        
        self.logger.handle(log_record)
    
    def log_request_end(self, method_name: str, request_id: str, duration_ms: float, 
                   response_payload: Any = None, error: Exception = None, metadata: Dict[str, Any] = None):
        """记录请求结束"""
        if not self.enable_grpc_logging:
            return
            
        if error:
            # 错误日志
            log_record = logging.LogRecord(
                name=self.logger.name,
                level=logging.ERROR,
                pathname="",
                lineno=0,
                msg=f"❌ gRPC 错误: {method_name} - {str(error)}",
                args=(),
                exc_info=(type(error), error, error.__traceback__) if error else None
            )
            log_record.log_type = "error"
            log_record.uri = method_name
            log_record.request_id = request_id
            log_record.duration = duration_ms
            log_record.data = {"error": str(error)}
            
            self.logger.handle(log_record)
        else:
            # 响应日志
            log_record = logging.LogRecord(
                name=self.logger.name,
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg=f"✅ gRPC 响应: {method_name}",
                args=(),
                exc_info=None
            )
            log_record.log_type = "response"
            log_record.uri = method_name
            log_record.request_id = request_id
            log_record.duration = duration_ms
            
            # 初始化data字段用于存储metadata信息
            log_record.data = {}
            
            # 记录metadata信息
            if metadata:
                metadata_dict = dict(metadata) if isinstance(metadata, list) else metadata
                user_info = {
                    'org_id': metadata_dict.get('x-org-id'),
                    'user_id': metadata_dict.get('x-user-id'),
                    'client_ip': metadata_dict.get('x-client-ip'),  # SDK客户端服务IP
                    'user_ip': metadata_dict.get('x-user-ip'),      # 用户真实IP
                    'client_version': metadata_dict.get('x-client-version')
                }
                user_info = {k: v for k, v in user_info.items() if v is not None}
                log_record.data.update(user_info)
            
            # 记录响应载荷（如果启用）
            if self.log_response_payload and response_payload is not None:
                log_record.data["response_payload"] = self._safe_serialize(response_payload)
            
            self.logger.handle(log_record)
    
    def _safe_serialize(self, obj: Any) -> str:
        """安全地序列化对象，避免敏感信息泄露"""
        try:
            if hasattr(obj, 'SerializeToString'):
                # protobuf 对象
                return f"<Proto object: {type(obj).__name__}>"
            elif hasattr(obj, '__dict__'):
                # 普通对象
                return f"<Object: {type(obj).__name__}>"
            else:
                # 基本类型
                return str(obj)[:200]  # 限制长度
        except Exception:
            return f"<Unserializable: {type(obj).__name__}>"


@contextmanager
def grpc_request_context(method_name: str, request_id: str, metadata: Dict[str, Any], 
                        request_payload: Any = None):
    """gRPC请求上下文管理器"""
    request_logger = GrpcRequestLogger(get_logger())
    start_time = time.time()
    
    try:
        # 记录请求开始
        request_logger.log_request_start(method_name, request_id, metadata, request_payload)
        yield request_logger
        
    except Exception as e:
        # 记录请求错误
        duration_ms = (time.time() - start_time) * 1000
        request_logger.log_request_end(method_name, request_id, duration_ms, error=e, metadata=metadata)
        raise
        
    else:
        # 记录请求成功结束
        duration_ms = (time.time() - start_time) * 1000
        request_logger.log_request_end(method_name, request_id, duration_ms, metadata=metadata)


def log_grpc_call(method_name: str):
    """gRPC调用日志装饰器"""
    def decorator(func):
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 提取request_id和metadata
            request_id = kwargs.get('request_id', 'unknown')
            metadata = kwargs.get('metadata', {})
            
            with grpc_request_context(method_name, request_id, metadata) as request_logger:
                result = func(*args, **kwargs)
                request_logger.log_request_end(method_name, request_id, 0, response_payload=result, metadata=metadata)
                return result
                
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 提取request_id和metadata
            request_id = kwargs.get('request_id', 'unknown')
            metadata = kwargs.get('metadata', {})
            
            with grpc_request_context(method_name, request_id, metadata) as request_logger:
                result = await func(*args, **kwargs)
                request_logger.log_request_end(method_name, request_id, 0, response_payload=result, metadata=metadata)
                return result
        
        # 根据函数类型返回对应的包装器
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# 默认初始化（可以被用户重新配置）
if not logger.handlers:
    setup_logging()