"""
异常类定义
"""
from typing import Optional, Any


class FileHubError(Exception):
    """文件管理系统基础异常"""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details


class FileNotFoundError(FileHubError):
    """文件不存在异常"""
    
    def __init__(self, file_id: str):
        super().__init__(f"文件不存在: {file_id}", code="FILE_NOT_FOUND")
        self.file_id = file_id


class FolderNotFoundError(FileHubError):
    """文件夹不存在异常"""
    
    def __init__(self, folder_id: str):
        super().__init__(f"文件夹不存在: {folder_id}", code="FOLDER_NOT_FOUND")
        self.folder_id = folder_id


class PermissionError(FileHubError):
    """权限不足异常"""
    
    def __init__(self, message: str):
        super().__init__(message, code="PERMISSION_DENIED")


class StorageError(FileHubError):
    """存储操作异常"""
    
    def __init__(self, message: str, operation: Optional[str] = None):
        super().__init__(message, code="STORAGE_ERROR")
        self.operation = operation


class UploadError(FileHubError):
    """上传异常"""
    
    def __init__(self, message: str, upload_id: Optional[str] = None):
        super().__init__(message, code="UPLOAD_ERROR")
        self.upload_id = upload_id


class DownloadError(FileHubError):
    """下载异常"""
    
    def __init__(self, message: str, file_id: Optional[str] = None):
        super().__init__(message, code="DOWNLOAD_ERROR")
        self.file_id = file_id


class ExportError(FileHubError):
    """导出异常"""
    
    def __init__(self, message: str, file_id: Optional[str] = None, format: Optional[str] = None):
        super().__init__(message, code="EXPORT_ERROR")
        self.file_id = file_id
        self.format = format


class ValidationError(FileHubError):
    """验证异常"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message, code="VALIDATION_ERROR")
        self.field = field


class ConnectionError(FileHubError):
    """连接异常"""
    
    def __init__(self, message: str):
        super().__init__(message, code="CONNECTION_ERROR")


class TimeoutError(FileHubError):
    """超时异常"""
    
    def __init__(self, message: str, timeout: Optional[float] = None):
        super().__init__(message, code="TIMEOUT_ERROR")
        self.timeout = timeout 