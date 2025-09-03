"""
gRPC拦截器，用于自动记录请求和响应日志
"""
import time
import asyncio
from typing import Any, Callable, Optional, Dict, List, Tuple, Union
import grpc
from grpc import aio
import base64
import re

from ..utils.logging import get_logger, GrpcRequestLogger


def _extract_method_name(method: str) -> str:
    """从gRPC方法路径中提取方法名"""
    # 方法格式: /package.service/MethodName
    parts = method.split('/')
    if len(parts) >= 2:
        return parts[-1]
    return method

def _extract_request_id(metadata: List[Tuple[str, str]]) -> str:
    """从元数据中提取请求ID"""
    if not metadata:
        return "unknown"
    
    try:
        metadata_dict = dict(metadata)
        return metadata_dict.get('x-request-id', 'unknown')
    except Exception:
        # 如果元数据解析失败，返回unknown
        return "unknown"

def _metadata_to_dict(metadata: List[Tuple[str, str]]) -> Dict[str, str]:
    """将元数据转换为字典"""
    try:
        return dict(metadata) if metadata else {}
    except Exception:
        # 如果元数据解析失败，返回空字典
        return {}


def _is_base64_string(value: str, min_length: int = 100) -> bool:
    """检查字符串是否可能是base64编码的内容"""
    if not isinstance(value, str) or len(value) < min_length:
        return False
    
    # 基本的base64格式检查
    base64_pattern = re.compile(r'^[A-Za-z0-9+/]*={0,2}$')
    if not base64_pattern.match(value):
        return False
    
    # 尝试解码以验证
    try:
        decoded = base64.b64decode(value, validate=True)
        # 如果能成功解码且长度超过阈值，认为是base64
        return len(decoded) > 50
    except:
        return False


def _truncate_long_string(value: str, max_length: int = 200, placeholder: str = "...") -> str:
    """截断长字符串，保留开头和结尾部分"""
    if len(value) <= max_length:
        return value
    
    # 计算保留的开头和结尾长度
    keep_length = (max_length - len(placeholder)) // 2
    return f"{value[:keep_length]}{placeholder}{value[-keep_length:]}"


def _sanitize_request_data(data: Any, max_string_length: int = 200, max_binary_preview: int = 50) -> Any:
    """
    清理请求数据，截断长字符串和二进制内容
    
    Args:
        data: 要清理的数据
        max_string_length: 字符串的最大长度
        max_binary_preview: 二进制内容预览的最大长度
        
    Returns:
        清理后的数据
    """
    if isinstance(data, dict):
        # 递归处理字典
        result = {}
        for key, value in data.items():
            # 检查是否是需要特殊处理的字段
            if key.lower() in ['operations'] and isinstance(value, list):
                # 对于 operations 字段，特殊处理以显示操作类型和数量
                if len(value) > 5:
                    ops_summary = []
                    # 统计操作类型
                    op_types = {}
                    for op in value:
                        if isinstance(op, dict):
                            for op_type in ['edit', 'create', 'update', 'delete', 'clear']:
                                if op_type in op:
                                    op_types[op_type] = op_types.get(op_type, 0) + 1
                    
                    # 显示前3个操作
                    for i in range(min(3, len(value))):
                        ops_summary.append(_sanitize_request_data(value[i], max_string_length, max_binary_preview))
                    
                    # 添加统计信息
                    ops_summary.append(f"... 总计 {len(value)} 个操作: {', '.join(f'{k}={v}' for k, v in op_types.items())}")
                    result[key] = ops_summary
                else:
                    result[key] = _sanitize_request_data(value, max_string_length, max_binary_preview)
            elif key.lower() in ['content', 'data', 'file', 'file_content', 'binary', 'blob', 'bytes', 'image', 'attachment']:
                if isinstance(value, (bytes, bytearray)):
                    # 二进制内容，显示长度和预览
                    preview = base64.b64encode(value[:max_binary_preview]).decode('utf-8')
                    result[key] = f"<binary {len(value)} bytes, preview: {preview}...>"
                elif isinstance(value, str):
                    # 检查是否是base64字符串
                    if _is_base64_string(value):
                        result[key] = f"<base64 string, length: {len(value)}, preview: {value[:max_binary_preview]}...>"
                    elif len(value) > max_string_length:
                        result[key] = _truncate_long_string(value, max_string_length)
                    else:
                        result[key] = value
                else:
                    result[key] = _sanitize_request_data(value, max_string_length, max_binary_preview)
            else:
                result[key] = _sanitize_request_data(value, max_string_length, max_binary_preview)
        return result
    elif isinstance(data, list):
        # 递归处理列表，限制列表长度以避免日志过长
        max_list_items = 10  # 最多显示10个元素
        if len(data) > max_list_items:
            # 显示前5个和后5个元素
            preview_items = (
                [_sanitize_request_data(item, max_string_length, max_binary_preview) for item in data[:5]] +
                [f"... {len(data) - max_list_items} more items ..."] +
                [_sanitize_request_data(item, max_string_length, max_binary_preview) for item in data[-5:]]
            )
            return preview_items
        else:
            return [_sanitize_request_data(item, max_string_length, max_binary_preview) for item in data]
    elif isinstance(data, tuple):
        # 递归处理元组
        return tuple(_sanitize_request_data(item, max_string_length, max_binary_preview) for item in data)
    elif isinstance(data, (bytes, bytearray)):
        # 二进制内容
        preview = base64.b64encode(data[:max_binary_preview]).decode('utf-8')
        return f"<binary {len(data)} bytes, preview: {preview}...>"
    elif isinstance(data, str):
        # 字符串内容
        if _is_base64_string(data):
            return f"<base64 string, length: {len(data)}, preview: {data[:max_binary_preview]}...>"
        elif len(data) > max_string_length:
            return _truncate_long_string(data, max_string_length)
        else:
            return data
    else:
        # 其他类型直接返回
        return data


class LoggingInterceptor:
    """gRPC日志拦截器基类"""
    
    def __init__(self):
        self.logger = get_logger()
        self.request_logger = GrpcRequestLogger(self.logger)


class AsyncUnaryUnaryLoggingInterceptor(LoggingInterceptor, aio.UnaryUnaryClientInterceptor):
    """异步一元-一元gRPC日志拦截器"""
    
    async def intercept_unary_unary(
        self,
        continuation: Callable,
        client_call_details: grpc.aio.ClientCallDetails,
        request: Any
    ) -> Any:
        """拦截一元-一元调用"""
        # 安全提取方法名
        try:
            method = client_call_details.method
            if isinstance(method, bytes):
                method = method.decode('utf-8', errors='ignore')
            method_name = method.split('/')[-1] if '/' in method else method
        except:
            method_name = "unknown"
        
        # 安全提取request_id和metadata
        request_id = "unknown"
        metadata_dict = {}
        try:
            if hasattr(client_call_details, 'metadata') and client_call_details.metadata:
                metadata_dict = _metadata_to_dict(client_call_details.metadata)
                request_id = metadata_dict.get('x-request-id', 'unknown')
        except:
            pass
        
        start_time = time.time()
        
        # 记录请求开始
        if self.logger.handlers:
            try:
                # 安全地提取请求数据
                request_data = None
                try:
                    if hasattr(request, '__class__'):
                        # 将protobuf消息转换为字典
                        from google.protobuf.json_format import MessageToDict
                        request_data = MessageToDict(request, preserving_proto_field_name=True)
                        # 清理请求数据，截断长内容
                        request_data = _sanitize_request_data(request_data)
                except:
                    # 如果转换失败，尝试其他方法
                    try:
                        request_data = str(request)
                        if len(request_data) > 200:
                            request_data = _truncate_long_string(request_data)
                    except:
                        request_data = "<无法序列化>"
                
                self.request_logger.log_request_start(
                    method_name, request_id, metadata_dict, request_data
                )
            except:
                pass
        
        try:
            # 执行实际的gRPC调用
            response = await continuation(client_call_details, request)
            
            # 记录成功
            duration_ms = (time.time() - start_time) * 1000
            if self.logger.handlers:
                try:
                    self.request_logger.log_request_end(
                        method_name, request_id, duration_ms, None, metadata=metadata_dict
                    )
                except:
                    pass
            
            return response
            
        except Exception as e:
            # 记录错误
            duration_ms = (time.time() - start_time) * 1000
            if self.logger.handlers:
                try:
                    self.request_logger.log_request_end(
                        method_name, request_id, duration_ms, error=e, metadata=metadata_dict
                    )
                except:
                    pass
            raise


class AsyncUnaryStreamLoggingInterceptor(LoggingInterceptor, aio.UnaryStreamClientInterceptor):
    """异步一元-流gRPC日志拦截器"""
    
    async def intercept_unary_stream(
        self,
        continuation: Callable,
        client_call_details: grpc.aio.ClientCallDetails,
        request: Any
    ) -> Any:
        """拦截一元-流调用"""
        # 安全提取方法名
        try:
            method = client_call_details.method
            if isinstance(method, bytes):
                method = method.decode('utf-8', errors='ignore')
            method_name = method.split('/')[-1] if '/' in method else method
        except:
            method_name = "unknown"
        
        # 安全提取request_id
        request_id = "unknown"
        try:
            if hasattr(client_call_details, 'metadata') and client_call_details.metadata:
                for key, value in client_call_details.metadata:
                    if key == 'x-request-id':
                        request_id = value
                        break
        except:
            pass
        
        start_time = time.time()
        
        # 记录请求开始
        if self.logger.handlers:
            try:
                # 安全地提取请求数据
                request_data = None
                try:
                    if hasattr(request, '__class__'):
                        from google.protobuf.json_format import MessageToDict
                        request_data = MessageToDict(request, preserving_proto_field_name=True)
                        # 清理请求数据，截断长内容
                        request_data = _sanitize_request_data(request_data)
                except:
                    try:
                        request_data = str(request)
                        if len(request_data) > 200:
                            request_data = _truncate_long_string(request_data)
                    except:
                        request_data = "<无法序列化>"
                
                self.request_logger.log_request_start(
                    method_name, request_id, {}, request_data
                )
            except:
                pass
        
        try:
            # 执行实际的gRPC调用
            response_stream = await continuation(client_call_details, request)
            
            # 记录流开始
            duration_ms = (time.time() - start_time) * 1000
            if self.logger.handlers:
                try:
                    self.request_logger.log_request_end(
                        method_name, request_id, duration_ms, "<Stream started>"
                    )
                except:
                    pass
            
            return response_stream
            
        except Exception as e:
            # 记录请求错误
            duration_ms = (time.time() - start_time) * 1000
            if self.logger.handlers:
                try:
                    self.request_logger.log_request_end(
                        method_name, request_id, duration_ms, error=e
                    )
                except:
                    pass
            raise


class AsyncStreamUnaryLoggingInterceptor(LoggingInterceptor, aio.StreamUnaryClientInterceptor):
    """异步流-一元gRPC日志拦截器"""
    
    async def intercept_stream_unary(
        self,
        continuation: Callable,
        client_call_details: grpc.aio.ClientCallDetails,
        request_iterator: Any
    ) -> Any:
        """拦截流-一元调用"""
        # 安全提取方法名
        try:
            method = client_call_details.method
            if isinstance(method, bytes):
                method = method.decode('utf-8', errors='ignore')
            method_name = method.split('/')[-1] if '/' in method else method
        except:
            method_name = "unknown"
        
        # 安全提取request_id
        request_id = "unknown"
        try:
            if hasattr(client_call_details, 'metadata') and client_call_details.metadata:
                for key, value in client_call_details.metadata:
                    if key == 'x-request-id':
                        request_id = value
                        break
        except:
            pass
        
        start_time = time.time()
        
        # 记录请求开始
        if self.logger.handlers:
            try:
                self.request_logger.log_request_start(
                    method_name, request_id, {}, "<Stream request>"
                )
            except:
                pass
        
        try:
            # 执行实际的gRPC调用
            response = await continuation(client_call_details, request_iterator)
            
            # 记录请求成功结束
            duration_ms = (time.time() - start_time) * 1000
            if self.logger.handlers:
                try:
                    self.request_logger.log_request_end(
                        method_name, request_id, duration_ms, None
                    )
                except:
                    pass
            
            return response
            
        except Exception as e:
            # 记录请求错误
            duration_ms = (time.time() - start_time) * 1000
            if self.logger.handlers:
                try:
                    self.request_logger.log_request_end(
                        method_name, request_id, duration_ms, error=e
                    )
                except:
                    pass
            raise


class AsyncStreamStreamLoggingInterceptor(LoggingInterceptor, aio.StreamStreamClientInterceptor):
    """异步流-流gRPC日志拦截器"""
    
    async def intercept_stream_stream(
        self,
        continuation: Callable,
        client_call_details: grpc.aio.ClientCallDetails,
        request_iterator: Any
    ) -> Any:
        """拦截流-流调用"""
        # 安全提取方法名
        try:
            method = client_call_details.method
            if isinstance(method, bytes):
                method = method.decode('utf-8', errors='ignore')
            method_name = method.split('/')[-1] if '/' in method else method
        except:
            method_name = "unknown"
        
        # 安全提取request_id
        request_id = "unknown"
        try:
            if hasattr(client_call_details, 'metadata') and client_call_details.metadata:
                for key, value in client_call_details.metadata:
                    if key == 'x-request-id':
                        request_id = value
                        break
        except:
            pass
        
        start_time = time.time()
        
        # 记录请求开始
        if self.logger.handlers:
            try:
                self.request_logger.log_request_start(
                    method_name, request_id, {}, "<Stream request>"
                )
            except:
                pass
        
        try:
            # 执行实际的gRPC调用
            response_stream = await continuation(client_call_details, request_iterator)
            
            # 记录流开始
            duration_ms = (time.time() - start_time) * 1000
            if self.logger.handlers:
                try:
                    self.request_logger.log_request_end(
                        method_name, request_id, duration_ms, "<Stream started>"
                    )
                except:
                    pass
            
            return response_stream
            
        except Exception as e:
            # 记录请求错误
            duration_ms = (time.time() - start_time) * 1000
            if self.logger.handlers:
                try:
                    self.request_logger.log_request_end(
                        method_name, request_id, duration_ms, error=e
                    )
                except:
                    pass
            raise


class SyncUnaryUnaryLoggingInterceptor(grpc.UnaryUnaryClientInterceptor):
    """同步一元-一元gRPC日志拦截器"""
    
    def intercept_unary_unary(self, continuation, client_call_details, request):
        logger = get_logger()
        request_logger = GrpcRequestLogger(logger)
        
        # 安全提取方法名
        try:
            method = client_call_details.method
            if isinstance(method, bytes):
                method = method.decode('utf-8', errors='ignore')
            method_name = method.split('/')[-1] if '/' in method else method
        except:
            method_name = "unknown"
        
        # 安全提取request_id和metadata
        request_id = "unknown"
        metadata_dict = {}
        try:
            if hasattr(client_call_details, 'metadata') and client_call_details.metadata:
                metadata_dict = _metadata_to_dict(client_call_details.metadata)
                request_id = metadata_dict.get('x-request-id', 'unknown')
        except:
            pass
        
        start_time = time.time()
        
        # 记录请求开始
        if logger.handlers:
            try:
                # 安全地提取请求数据
                request_data = None
                try:
                    if hasattr(request, '__class__'):
                        from google.protobuf.json_format import MessageToDict
                        request_data = MessageToDict(request, preserving_proto_field_name=True)
                        # 清理请求数据，截断长内容
                        request_data = _sanitize_request_data(request_data)
                except:
                    try:
                        request_data = str(request)
                        if len(request_data) > 200:
                            request_data = _truncate_long_string(request_data)
                    except:
                        request_data = "<无法序列化>"
                
                request_logger.log_request_start(
                    method_name, request_id, metadata_dict, request_data
                )
            except:
                pass
        
        try:
            # 执行实际的gRPC调用
            response = continuation(client_call_details, request)
            
            # 记录请求成功结束
            duration_ms = (time.time() - start_time) * 1000
            if logger.handlers:
                try:
                    request_logger.log_request_end(
                        method_name, request_id, duration_ms, None, metadata=metadata_dict
                    )
                except:
                    pass
            
            return response
            
        except Exception as e:
            # 记录请求错误
            duration_ms = (time.time() - start_time) * 1000
            if logger.handlers:
                try:
                    request_logger.log_request_end(
                        method_name, request_id, duration_ms, error=e, metadata=metadata_dict
                    )
                except:
                    pass
            raise


def create_async_interceptors() -> List[aio.ClientInterceptor]:
    """创建异步gRPC拦截器列表"""
    return [
        AsyncUnaryUnaryLoggingInterceptor(),
        AsyncUnaryStreamLoggingInterceptor(),
        AsyncStreamUnaryLoggingInterceptor(),
        AsyncStreamStreamLoggingInterceptor(),
    ]


def create_sync_interceptors() -> List:
    """创建同步gRPC拦截器列表"""
    return [
        SyncUnaryUnaryLoggingInterceptor(),
    ]