"""
文件管理系统客户端

提供与文件管理系统交互的客户端接口
"""
import os
import threading
from asyncio import Lock
from typing import Optional, Dict

from .enums import Role
from .rpc.async_client import AsyncGrpcClient
from .rpc.sync_client import SyncGrpcClient
from .services import (
    AsyncBlobService,
    AsyncFileService,
    AsyncFolderService,
    AsyncTapleService,
    SyncBlobService,
    SyncFileService,
    SyncFolderService,
    SyncTapleService,
)
from .schemas.context import UserContext, RequestContext

MAX_MESSAGE_LENGTH = 2 ** 31 - 1  # 对于32位系统


class AsyncTamarFileHubClient:
    """异步文件管理系统客户端"""

    def __init__(
            self,
            host: Optional[str] = None,
            port: Optional[int] = None,
            secure: Optional[bool] = None,
            credentials: Optional[dict] = None,
            auto_connect: bool = True,
            retry_count: Optional[int] = None,
            retry_delay: Optional[float] = None,
            default_metadata: Optional[Dict[str, str]] = None,
            user_context: Optional[UserContext] = None,
            request_context: Optional[RequestContext] = None,
            enable_logging: bool = True,
            log_level: str = "INFO",
            options: Optional[list] = None,
    ):
        """
        初始化客户端
        
        Args:
            host: 服务器地址，可以是域名或IP（默认从环境变量 FILE_HUB_HOST 读取，否则使用 localhost）
            port: 服务器端口，可选参数，不指定时直接使用host作为完整地址（默认从环境变量 FILE_HUB_PORT 读取）
            secure: 是否使用TLS（默认从环境变量 FILE_HUB_SECURE 读取，否则使用 False）
            credentials: 认证凭据
            auto_connect: 是否自动连接（默认 True）
            retry_count: 连接重试次数（默认从环境变量 FILE_HUB_RETRY_COUNT 读取，否则使用 3）
            retry_delay: 重试延迟秒数（默认从环境变量 FILE_HUB_RETRY_DELAY 读取，否则使用 1.0）
            default_metadata: 默认的元数据（如 org_id, user_id 等）
            user_context: 用户上下文
            request_context: 请求上下文
            enable_logging: 是否启用日志
            log_level: 日志级别
            options: gRPC 通道选项列表，例如：
                [
                    ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
                    ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
                ]
            
        环境变量：
            FILE_HUB_HOST: gRPC 服务器地址
            FILE_HUB_PORT: gRPC 服务器端口
            FILE_HUB_SECURE: 是否启用 TLS（true/false）
            FILE_HUB_API_KEY: API 密钥（如果需要）
            FILE_HUB_RETRY_COUNT: 连接重试次数
            FILE_HUB_RETRY_DELAY: 重试延迟（秒）
        """
        # 从环境变量或参数获取配置
        self._host = host or os.getenv('FILE_HUB_HOST', 'localhost')
        # 端口处理：如果有环境变量且不为空，则使用；否则使用参数值（可能为None）
        env_port = os.getenv('FILE_HUB_PORT')
        if env_port:
            self._port = int(env_port)
        else:
            self._port = port
        self._secure = secure if secure is not None else os.getenv('FILE_HUB_SECURE', 'false').lower() == 'true'
        self._retry_count = retry_count or int(os.getenv('FILE_HUB_RETRY_COUNT', '3'))
        self._retry_delay = retry_delay or float(os.getenv('FILE_HUB_RETRY_DELAY', '1.0'))
        self._connect_lock = Lock()

        # 处理认证凭据
        if credentials is None and os.getenv('FILE_HUB_API_KEY'):
            credentials = {'api_key': os.getenv('FILE_HUB_API_KEY')}

        # 处理默认元数据
        if default_metadata is None:
            default_metadata = {}

        # 设置默认的 gRPC 选项（增加消息大小限制）
        if options is None:
            options = [
                ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
                ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
            ]

        self._client = AsyncGrpcClient(
            self._host,
            self._port,
            self._secure,
            credentials,
            options=options,
            retry_count=self._retry_count,
            retry_delay=self._retry_delay,
            default_metadata=default_metadata,
            user_context=user_context,
            request_context=request_context,
            enable_logging=enable_logging,
            log_level=log_level,
        )
        self._blob_service = None
        self._file_service = None
        self._folder_service = None
        self._taple_service = None
        self._auto_connect = auto_connect
        self._connected = False

    async def _ensure_connected(self):
        """确保客户端已连接"""
        if not self._connected and self._auto_connect:
            await self.connect()

    @property
    def blobs(self) -> AsyncBlobService:
        """获取文件服务"""
        if self._blob_service is None:
            self._blob_service = AsyncBlobService(self._client)
        return self._blob_service

    @property
    def files(self) -> AsyncFileService:
        """获取文件服务"""
        if self._file_service is None:
            self._file_service = AsyncFileService(self._client)
        return self._file_service

    @property
    def folders(self) -> AsyncFolderService:
        """获取文件夹服务"""
        if self._folder_service is None:
            self._folder_service = AsyncFolderService(self._client)
        return self._folder_service

    @property
    def taples(self) -> AsyncTapleService:
        """获取 Taple 服务"""
        if self._taple_service is None:
            self._taple_service = AsyncTapleService(self._client)
        return self._taple_service

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
        self._client.set_user_context(org_id, user_id, role, actor_id, user_ip)

    def set_user_ip(self, user_ip: Optional[str]):
        """
        设置或更新用户IP地址
        
        Args:
            user_ip: 用户IP地址（实际请求用户的IP，如前端用户的IP）
        """
        self._client.set_user_ip(user_ip)

    def get_user_context(self) -> Optional[UserContext]:
        """获取当前用户上下文"""
        return self._client.get_user_context()

    def clear_user_context(self):
        """清除用户上下文信息"""
        self._client.clear_user_context()

    def set_request_context(self, request_context: RequestContext):
        """设置请求上下文"""
        self._client.set_request_context(request_context)

    def get_request_context(self) -> RequestContext:
        """获取当前请求上下文"""
        return self._client.get_request_context()

    def update_request_context(self, **kwargs):
        """
        更新请求上下文的部分字段
        
        Args:
            client_ip: 客户端IP地址
            client_version: 客户端版本
            client_type: 客户端类型
            user_agent: User-Agent信息
            extra: 额外的元数据字典
        """
        self._client.update_request_context(**kwargs)

    def update_metadata(self, **kwargs):
        """
        更新默认元数据
        
        Args:
            **kwargs: 要更新的元数据键值对
        """
        self._client.update_default_metadata(**kwargs)

    async def connect(self):
        """连接到服务器"""
        if not self._connected:
            async with self._connect_lock:
                if not self._connected:
                    await self._client.connect()
                    self._connected = True

    async def close(self):
        """关闭连接"""
        if self._connected:
            await self._client.close()
            self._connected = False

    async def __aenter__(self) -> "AsyncTamarFileHubClient":
        await self._ensure_connected()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class TamarFileHubClient:
    """同步文件管理系统客户端"""

    def __init__(
            self,
            host: Optional[str] = None,
            port: Optional[int] = None,
            secure: Optional[bool] = None,
            credentials: Optional[dict] = None,
            auto_connect: bool = True,
            retry_count: Optional[int] = None,
            retry_delay: Optional[float] = None,
            default_metadata: Optional[Dict[str, str]] = None,
            user_context: Optional[UserContext] = None,
            request_context: Optional[RequestContext] = None,
            enable_logging: bool = True,
            log_level: str = "INFO",
            options: Optional[list] = None,
    ):
        """
        初始化客户端
        
        Args:
            host: 服务器地址，可以是域名或IP（默认从环境变量 FILE_HUB_HOST 读取，否则使用 localhost）
            port: 服务器端口，可选参数，不指定时直接使用host作为完整地址（默认从环境变量 FILE_HUB_PORT 读取）
            secure: 是否使用TLS（默认从环境变量 FILE_HUB_SECURE 读取，否则使用 False）
            credentials: 认证凭据
            auto_connect: 是否自动连接（默认 True）
            retry_count: 连接重试次数（默认从环境变量 FILE_HUB_RETRY_COUNT 读取，否则使用 3）
            retry_delay: 重试延迟秒数（默认从环境变量 FILE_HUB_RETRY_DELAY 读取，否则使用 1.0）
            default_metadata: 默认的元数据（如 org_id, user_id 等）
            user_context: 用户上下文
            request_context: 请求上下文
            enable_logging: 是否启用日志
            log_level: 日志级别
            options: gRPC 通道选项列表，例如：
                [
                    ('grpc.max_send_message_length', 100 * 1024 * 1024),  # 100MB
                    ('grpc.max_receive_message_length', 100 * 1024 * 1024),  # 100MB
                ]
            
        环境变量：
            FILE_HUB_HOST: gRPC 服务器地址
            FILE_HUB_PORT: gRPC 服务器端口
            FILE_HUB_SECURE: 是否启用 TLS（true/false）
            FILE_HUB_API_KEY: API 密钥（如果需要）
            FILE_HUB_RETRY_COUNT: 连接重试次数
            FILE_HUB_RETRY_DELAY: 重试延迟（秒）
        """
        # 从环境变量或参数获取配置
        self._host = host or os.getenv('FILE_HUB_HOST', 'localhost')
        # 端口处理：如果有环境变量且不为空，则使用；否则使用参数值（可能为None）
        env_port = os.getenv('FILE_HUB_PORT')
        if env_port:
            self._port = int(env_port)
        else:
            self._port = port
        self._secure = secure if secure is not None else os.getenv('FILE_HUB_SECURE', 'false').lower() == 'true'
        self._retry_count = retry_count or int(os.getenv('FILE_HUB_RETRY_COUNT', '3'))
        self._retry_delay = retry_delay or float(os.getenv('FILE_HUB_RETRY_DELAY', '1.0'))
        self._connect_lock = threading.Lock()

        # 处理认证凭据
        if credentials is None and os.getenv('FILE_HUB_API_KEY'):
            credentials = {'api_key': os.getenv('FILE_HUB_API_KEY')}

        # 处理默认元数据
        if default_metadata is None:
            default_metadata = {}

        # 设置默认的 gRPC 选项（增加消息大小限制）
        if options is None:
            options = [
                ('grpc.max_send_message_length', 100 * 1024 * 1024),  # 100MB
                ('grpc.max_receive_message_length', 100 * 1024 * 1024),  # 100MB
            ]

        self._client = SyncGrpcClient(
            self._host,
            self._port,
            self._secure,
            credentials,
            options=options,
            retry_count=self._retry_count,
            retry_delay=self._retry_delay,
            default_metadata=default_metadata,
            user_context=user_context,
            request_context=request_context,
            enable_logging=enable_logging,
            log_level=log_level,
        )
        self._blob_service = None
        self._file_service = None
        self._folder_service = None
        self._taple_service = None
        self._auto_connect = auto_connect
        self._connected = False

    def _ensure_connected(self):
        """确保客户端已连接"""
        if not self._connected and self._auto_connect:
            self.connect()

    @property
    def blobs(self) -> SyncBlobService:
        """获取文件服务"""
        self._ensure_connected()
        if self._blob_service is None:
            self._blob_service = SyncBlobService(self._client)
        return self._blob_service

    @property
    def files(self) -> SyncFileService:
        """获取文件服务"""
        self._ensure_connected()
        if self._file_service is None:
            self._file_service = SyncFileService(self._client)
        return self._file_service

    @property
    def folders(self) -> SyncFolderService:
        """获取文件夹服务"""
        self._ensure_connected()
        if self._folder_service is None:
            self._folder_service = SyncFolderService(self._client)
        return self._folder_service

    @property
    def taples(self) -> SyncTapleService:
        """获取 Taple 服务"""
        self._ensure_connected()
        if self._taple_service is None:
            self._taple_service = SyncTapleService(self._client)
        return self._taple_service

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
        self._client.set_user_context(org_id, user_id, role, actor_id, user_ip)

    def set_user_ip(self, user_ip: Optional[str]):
        """
        设置或更新用户IP地址

        Args:
            user_ip: 用户IP地址（实际请求用户的IP，如前端用户的IP）
        """
        self._client.set_user_ip(user_ip)

    def get_user_context(self) -> Optional[UserContext]:
        """获取当前用户上下文"""
        return self._client.get_user_context()

    def clear_user_context(self):
        """清除用户上下文信息"""
        self._client.clear_user_context()

    def set_request_context(self, request_context: RequestContext):
        """设置请求上下文"""
        self._client.set_request_context(request_context)

    def get_request_context(self) -> RequestContext:
        """获取当前请求上下文"""
        return self._client.get_request_context()

    def update_request_context(self, **kwargs):
        """
        更新请求上下文的部分字段
        
        Args:
            client_ip: 客户端IP地址
            client_version: 客户端版本
            client_type: 客户端类型
            user_agent: User-Agent信息
            extra: 额外的元数据字典
        """
        self._client.update_request_context(**kwargs)

    def update_metadata(self, **kwargs):
        """
        更新默认元数据
        
        Args:
            **kwargs: 要更新的元数据键值对
        """
        self._client.update_default_metadata(**kwargs)

    def connect(self):
        """连接到服务器"""
        if not self._connected:
            with self._connect_lock:
                if not self._connected:
                    self._client.connect()
                    self._connected = True

    def close(self):
        """关闭连接"""
        if self._connected:
            self._client.close()
            self._connected = False

    def __enter__(self) -> "TamarFileHubClient":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        """析构函数，确保连接被关闭"""
        try:
            self.close()
        except:
            pass


# 创建默认的单例客户端实例
_default_client = None
_default_async_client = None


def get_client(**kwargs) -> TamarFileHubClient:
    """
    获取默认的同步客户端实例（单例）
    
    Args:
        **kwargs: 客户端初始化参数，仅在第一次调用时生效
        
    Returns:
        TamarFileHubClient: 同步客户端实例
    """
    global _default_client
    if _default_client is None:
        _default_client = TamarFileHubClient(**kwargs)
    return _default_client


def get_async_client(**kwargs) -> AsyncTamarFileHubClient:
    """
    获取默认的异步客户端实例（单例）
    
    Args:
        **kwargs: 客户端初始化参数，仅在第一次调用时生效
        
    Returns:
        AsyncTamarFileHubClient: 异步客户端实例
    """
    global _default_async_client
    if _default_async_client is None:
        _default_async_client = AsyncTamarFileHubClient(**kwargs)
    return _default_async_client


# 默认客户端实例（自动从环境变量读取配置）
tamar_client = get_client()
async_tamar_client = get_async_client()
