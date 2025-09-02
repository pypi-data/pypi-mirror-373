"""
异步gRPC客户端
"""
from enum import Enum

import grpc
import asyncio
import uuid
import platform
import socket
from typing import Optional, Dict, List, Tuple

from ..enums import Role
from ..errors import ConnectionError
from ..schemas.context import UserContext, RequestContext, FullContext
from ..utils.logging import get_logger, setup_logging
from .interceptors import create_async_interceptors
import logging


class AsyncGrpcClient:
    """异步gRPC客户端基类"""

    def __init__(
            self,
            host: str = "localhost",
            port: Optional[int] = None,
            secure: bool = False,
            credentials: Optional[dict] = None,
            options: Optional[list] = None,
            retry_count: int = 3,
            retry_delay: float = 1.0,
            default_metadata: Optional[Dict[str, str]] = None,
            user_context: Optional[UserContext] = None,
            request_context: Optional[RequestContext] = None,
            enable_logging: bool = True,
            log_level: str = "INFO",
    ):
        """
        初始化异步gRPC客户端
        
        Args:
            host: 服务器地址（可以是域名或IP）
            port: 服务器端口（可选，如果不指定则根据secure自动选择）
            secure: 是否使用安全连接（TLS）
            credentials: 认证凭据字典（如 {'api_key': 'xxx'}）
            options: gRPC通道选项
            retry_count: 连接重试次数
            retry_delay: 重试延迟（秒）
            default_metadata: 默认的元数据（如 org_id, user_id 等）
            user_context: 用户上下文
            request_context: 请求上下文
            enable_logging: 是否启用日志记录
            log_level: 日志级别
        """
        self.host = host
        self.port = port
        
        # 构建地址：如果没有指定端口，则使用域名作为地址
        if port is not None:
            self.address = f"{host}:{port}"
        else:
            # 如果没有指定端口，直接使用host
            # gRPC会自动根据secure选择默认端口（80/443）
            self.address = host
        self.secure = secure
        self.credentials = credentials
        self.options = options or []
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.default_metadata = default_metadata or {}
        self._channel: Optional[grpc.aio.Channel] = None
        self._stubs = {}
        self._stub_lock = asyncio.Lock()
        
        # 日志配置
        self.enable_logging = enable_logging
        self.log_level = log_level
        
        # 只有在明确启用日志时才设置SDK日志
        # 默认不设置，让用户自己控制
        if enable_logging:
            # 检查是否已经有处理器，避免重复设置
            sdk_logger = get_logger()
            if not sdk_logger.handlers:
                setup_logging(level=log_level, enable_grpc_logging=True, use_json_format=True)
        
        self.logger = get_logger()

        # 上下文管理
        self._user_context = user_context
        self._request_context = request_context or self._create_default_request_context()

        # 如果提供了user_context，将其添加到default_metadata
        if self._user_context:
            self.default_metadata.update(self._user_context.to_metadata())

        # 添加请求上下文到default_metadata
        self.default_metadata.update(self._request_context.to_metadata())

    def _create_default_request_context(self) -> RequestContext:
        """创建默认的请求上下文"""
        # 尝试获取客户端IP
        client_ip = None
        try:
            # 获取本机IP（适用于内网环境）
            hostname = socket.gethostname()
            client_ip = socket.gethostbyname(hostname)
        except:
            pass

        # 获取客户端信息
        return RequestContext(
            client_ip=client_ip,
            client_type="python-sdk",
            client_version="1.0.0",
            user_agent=f"FileHubClient/1.0.0 Python/{platform.python_version()} {platform.system()}/{platform.release()}"
        )

    def _create_channel_credentials(self) -> Optional[grpc.ChannelCredentials]:
        """创建通道凭据"""
        if not self.secure:
            return None

        # 使用默认的SSL凭据
        channel_credentials = grpc.ssl_channel_credentials()

        # 如果有API密钥，创建组合凭据
        if self.credentials and 'api_key' in self.credentials:
            # 创建元数据凭据
            def metadata_callback(context, callback):
                metadata = [('authorization', f"Bearer {self.credentials['api_key']}")]
                callback(metadata, None)

            call_credentials = grpc.metadata_call_credentials(metadata_callback)
            channel_credentials = grpc.composite_channel_credentials(
                channel_credentials,
                call_credentials
            )

        return channel_credentials

    async def connect(self):
        """连接到gRPC服务器（带重试）"""
        if self._channel is not None:
            return

        last_error = None
        for attempt in range(self.retry_count):
            try:
                if attempt > 0:
                    await asyncio.sleep(self.retry_delay)

                channel_credentials = self._create_channel_credentials()

                # 创建拦截器
                interceptors = create_async_interceptors() if self.enable_logging else []

                if channel_credentials:
                    self._channel = grpc.aio.secure_channel(
                        self.address,
                        channel_credentials,
                        options=self.options,
                        interceptors=interceptors
                    )
                else:
                    self._channel = grpc.aio.insecure_channel(
                        self.address,
                        options=self.options,
                        interceptors=interceptors
                    )

                # 连接
                try:
                    await asyncio.wait_for(self._channel.channel_ready(), timeout=5.0)
                except asyncio.TimeoutError:
                    raise ConnectionError(f"连接超时：{self.address}")

                # 连接成功
                if self.enable_logging:
                    log_record = logging.LogRecord(
                        name=self.logger.name,
                        level=logging.INFO,
                        pathname="",
                        lineno=0,
                        msg=f"🔗 已连接到 gRPC 服务器",
                        args=(),
                        exc_info=None
                    )
                    log_record.log_type = "info"
                    log_record.data = {"server": self.address}
                    self.logger.handle(log_record)
                return

            except Exception as e:
                last_error = e
                if attempt < self.retry_count - 1:
                    if self.enable_logging:
                        log_record = logging.LogRecord(
                            name=self.logger.name,
                            level=logging.WARNING,
                            pathname="",
                            lineno=0,
                            msg=f"⚠️ 连接失败，正在重试",
                            args=(),
                            exc_info=None
                        )
                        log_record.log_type = "info"
                        log_record.data = {
                            "attempt": attempt + 1,
                            "max_attempts": self.retry_count,
                            "error": str(e)
                        }
                        self.logger.handle(log_record)
                    if self._channel:
                        await self._channel.close()
                        self._channel = None
                else:
                    # 最后一次尝试失败
                    if self._channel:
                        await self._channel.close()
                        self._channel = None

        # 所有重试都失败
        raise ConnectionError(
            f"无法连接到gRPC服务器 {self.address} (尝试了 {self.retry_count} 次): {str(last_error)}"
        )

    async def close(self):
        """关闭连接"""
        if self._channel:
            if self.enable_logging:
                log_record = logging.LogRecord(
                    name=self.logger.name,
                    level=logging.INFO,
                    pathname="",
                    lineno=0,
                    msg=f"👋 正在关闭 gRPC 连接",
                    args=(),
                    exc_info=None
                )
                log_record.log_type = "info"
                log_record.data = {"server": self.address}
                self.logger.handle(log_record)
            await self._channel.close()
            self._channel = None
            self._stubs.clear()

    async def get_stub(self, stub_class):
        """
        获取gRPC stub实例
        
        Args:
            stub_class: Stub类
            
        Returns:
            Stub实例
        """
        if not self._channel:
            raise ConnectionError("未连接到gRPC服务器")

        stub_name = stub_class.__name__
        async with self._stub_lock:
            if stub_name not in self._stubs:
                self._stubs[stub_name] = stub_class(self._channel)
            return self._stubs[stub_name]

    def build_metadata(self, *, request_id: Optional[str] = None, **kwargs) -> List[Tuple[str, str]]:
        """
        构建请求元数据
        
        Args:
            request_id: 显式指定的请求ID，如果提供则优先使用
            **kwargs: 要覆盖或添加的元数据
            
        Returns:
            元数据列表
        """
        metadata = {}

        # 添加默认元数据
        metadata.update(self.default_metadata)

        # 自动检测用户真实IP
        from ..utils.ip_detector import get_current_user_ip
        auto_detected_ip = get_current_user_ip()
        if auto_detected_ip and 'x-user-ip' not in metadata:
            # 只有在没有设置过user_ip的情况下才使用自动检测的IP
            metadata['x-user-ip'] = auto_detected_ip

        # 添加/覆盖传入的元数据，但跳过None值以避免覆盖有效的默认值
        for k, v in kwargs.items():
            if v is not None:
                metadata[k] = v

        # 处理 request_id（优先级：显式传入 > metadata中的x-request-id > RequestContext > 自动生成）
        if request_id is not None:
            # 优先使用显式传入的 request_id
            metadata['x-request-id'] = request_id
        elif 'x-request-id' not in metadata:
            # 如果没有显式传入且metadata中也没有，则尝试从RequestContext获取或自动生成
            metadata['x-request-id'] = (
                    self._request_context.extra.get("request_id") or str(uuid.uuid4())
            )

        # 转换为 gRPC 需要的格式
        result = []
        for k, v in metadata.items():
            if v is None:
                continue
            if isinstance(v, Enum):
                v = v.value
            result.append((k, str(v)))

        return result

    def update_default_metadata(self, **kwargs):
        """
        更新默认元数据
        
        Args:
            **kwargs: 要更新的元数据键值对
        """
        self.default_metadata.update(kwargs)

    def set_user_context(self, org_id: str, user_id: str, role: Role = Role.ACCOUNT, actor_id: Optional[str] = None, user_ip: Optional[str] = None):
        """
        设置用户上下文信息
        
        Args:
            org_id: 组织ID
            user_id: 用户ID
            role: 用户角色（默认为 ACCOUNT）
            actor_id: 操作者ID（如果不同于 user_id）
            user_ip: 用户IP地址（实际请求用户的IP，如前端用户的IP）
        """
        self._user_context = UserContext(
            org_id=org_id,
            user_id=user_id,
            role=role,
            actor_id=actor_id,
            user_ip=user_ip
        )
        # 更新到默认元数据
        self.update_default_metadata(**self._user_context.to_metadata())

    def set_user_ip(self, user_ip: Optional[str]):
        """
        设置或更新用户IP地址
        
        Args:
            user_ip: 用户IP地址（实际请求用户的IP，如前端用户的IP）
        """
        if self._user_context:
            self._user_context.user_ip = user_ip
            # 先移除旧的x-user-ip（如果存在）
            self.default_metadata.pop('x-user-ip', None)
            # 更新到默认元数据（只有非None值会被添加）
            self.update_default_metadata(**self._user_context.to_metadata())
        else:
            raise ValueError("必须先调用 set_user_context 设置用户上下文，然后才能设置用户IP")

    def get_user_context(self) -> Optional[UserContext]:
        """获取当前用户上下文"""
        return self._user_context

    def clear_user_context(self):
        """清除用户上下文信息"""
        self._user_context = None
        for key in ['x-org-id', 'x-user-id', 'x-role', 'x-actor-id']:
            self.default_metadata.pop(key, None)

    def set_request_context(self, request_context: RequestContext):
        """设置请求上下文"""
        self._request_context = request_context
        # 更新到默认元数据
        self.update_default_metadata(**self._request_context.to_metadata())

    def get_request_context(self) -> RequestContext:
        """获取当前请求上下文"""
        return self._request_context

    def update_request_context(self, **kwargs):
        """
        更新请求上下文的部分字段
        
        Args:
            **kwargs: 要更新的字段
        """
        if kwargs.get('client_ip'):
            self._request_context.client_ip = kwargs['client_ip']
        if kwargs.get('client_version'):
            self._request_context.client_version = kwargs['client_version']
        if kwargs.get('client_type'):
            self._request_context.client_type = kwargs['client_type']
        if kwargs.get('user_agent'):
            self._request_context.user_agent = kwargs['user_agent']

        # 处理extra字段
        extra = kwargs.get('extra')
        if extra and isinstance(extra, dict):
            self._request_context.extra.update(extra)

        # 更新到默认元数据
        self.update_default_metadata(**self._request_context.to_metadata())

    def get_full_context(self) -> FullContext:
        """获取完整的上下文信息"""
        return FullContext(
            user_context=self._user_context,
            request_context=self._request_context
        )

    async def __aenter__(self) -> "AsyncGrpcClient":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
