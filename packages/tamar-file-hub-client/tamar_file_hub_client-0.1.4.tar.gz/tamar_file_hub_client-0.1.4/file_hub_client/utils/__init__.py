"""
工具函数模块
"""
from .converter import (
    timestamp_to_datetime
)
from .file_utils import (
    get_file_mime_type,
    get_file_extension,
    humanize_file_size,
    calculate_file_hash,
    split_file_chunks,
)
from .retry import (
    retry_with_backoff,
    retry_on_lock_conflict
)
from .smart_retry import (
    smart_retry,
    retry_on_network_errors,
    retry_on_conflict,
    no_retry,
    ErrorClassifier,
    RetryStrategy
)
from .upload_helper import (
    HttpUploader,
    AsyncHttpUploader,
    UploadProgress,
    calculate_file_md5,
)
from .download_helper import (
    HttpDownloader,
    AsyncHttpDownloader,
    DownloadProgress,
)
from .idempotency import (
    IdempotencyKeyGenerator,
    IdempotencyManager,
    generate_idempotency_key
)
from .logging import (
    setup_logging,
    get_logger,
    GrpcRequestLogger,
    grpc_request_context,
    log_grpc_call,
)
from .ip_detector import (
    get_current_user_ip,
    set_current_user_ip,
    set_user_ip_extractor,
    UserIPContext,
    flask_auto_user_ip,
)

__all__ = [
    # 文件工具
    "get_file_mime_type",
    "get_file_extension",
    "humanize_file_size",
    "calculate_file_hash",
    "split_file_chunks",

    # 重试工具
    "retry_with_backoff",
    "retry_on_lock_conflict",
    "smart_retry",
    "retry_on_network_errors",
    "retry_on_conflict",
    "no_retry",
    "ErrorClassifier",
    "RetryStrategy",

    # 上传助手
    "HttpUploader",
    "AsyncHttpUploader",
    "UploadProgress",
    "calculate_file_md5",

    # 下载助手
    "HttpDownloader",
    "AsyncHttpDownloader",
    "DownloadProgress",
    
    # 幂等性工具
    "IdempotencyKeyGenerator",
    "IdempotencyManager",
    "generate_idempotency_key",
    
    # 日志工具
    "setup_logging",
    "get_logger",
    "GrpcRequestLogger",
    "grpc_request_context",
    "log_grpc_call",
    
    # IP检测工具
    "get_current_user_ip",
    "set_current_user_ip", 
    "set_user_ip_extractor",
    "UserIPContext",
    "flask_auto_user_ip",
]
