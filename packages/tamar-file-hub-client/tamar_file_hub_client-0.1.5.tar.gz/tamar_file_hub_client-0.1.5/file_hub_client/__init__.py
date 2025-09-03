"""
文件管理系统客户端SDK

一个基于gRPC的文件管理系统Python客户端SDK，支持：
- 文件和文件夹的增删改查
- 多种上传模式（普通上传、断点续传、流式上传、客户端直传）
- 传统文件类型和自定义文件类型
- 文件导出（将自定义文件类型导出为传统格式）
- 直接操作对象存储
- 同时支持同步和异步API
"""

from .client import (
    AsyncTamarFileHubClient,
    TamarFileHubClient,
    tamar_client,  # 默认的同步客户端单例
    async_tamar_client,  # 默认的异步客户端单例
    get_client,  # 获取同步客户端单例的函数
    get_async_client,  # 获取异步客户端单例的函数
)

from .enums import Role, UploadMode, ExportFormat
from .errors import (
    FileHubError,
    FileNotFoundError,
    FolderNotFoundError,
    UploadError,
    DownloadError,
    ExportError,
    StorageError,
    ValidationError,
    ConnectionError,
    TimeoutError,
    PermissionError,
)
from .schemas import (
    File,
    UploadUrlResponse,
    ShareLinkRequest,
    FileVisitRequest,
    FileListRequest,
    FileListResponse,
    FolderInfo,
    FolderListResponse,
    UserContext,
    RequestContext,
    FullContext,
    # Taple 相关模型
    Table,
    Sheet,
    Column,
    Row,
    Cell,
    MergedCell,
    TableView,
    CellUpdate,
    TableViewResponse,
    BatchCreateTableViewResult,
    BatchCreateTableViewsResponse,
    ListTableViewsResponse,
)

# 幂等性工具
from .utils.idempotency import (
    IdempotencyKeyGenerator,
    IdempotencyManager,
    generate_idempotency_key,
)

__all__ = [
    # 客户端
    "AsyncTamarFileHubClient",
    "TamarFileHubClient",
    "tamar_client",  # 默认同步客户端单例
    "async_tamar_client",  # 默认异步客户端单例
    "get_client",
    "get_async_client",

    # 文件相关模型
    "File",
    "UploadUrlResponse",
    "ShareLinkRequest",
    "FileVisitRequest",
    "FileListRequest",
    "FileListResponse",

    # 文件夹相关模型
    "FolderInfo",
    "FolderListResponse",

    # Taple 相关模型
    "Table",
    "Sheet",
    "Column",
    "Row",
    "Cell",
    "MergedCell",
    "TableView",
    "CellUpdate",
    "TableViewResponse",
    "BatchCreateTableViewResult",
    "BatchCreateTableViewsResponse",
    "ListTableViewsResponse",

    # 枚举
    "Role",
    "UploadMode",
    "ExportFormat",

    # 异常
    "FileHubError",
    "FileNotFoundError",
    "FolderNotFoundError",
    "UploadError",
    "DownloadError",
    "ExportError",
    "StorageError",
    "ValidationError",
    "ConnectionError",
    "TimeoutError",
    "PermissionError",
    
    # 幂等性工具
    "IdempotencyKeyGenerator",
    "IdempotencyManager",
    "generate_idempotency_key",
]
