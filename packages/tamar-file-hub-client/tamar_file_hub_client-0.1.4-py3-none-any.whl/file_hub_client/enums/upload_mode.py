"""
上传模式枚举
"""
from enum import Enum


class UploadMode(str, Enum):
    """上传模式"""
    NORMAL = "normal"  # 普通上传
    STREAM = "stream"  # 流式上传
    RESUMABLE = "resumable"  # 断点续传
