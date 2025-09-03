"""
文件相关数据模型
"""
from datetime import datetime
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field


class File(BaseModel):
    """文件信息模型"""
    id: str = Field(..., description="文件ID")
    folder_id: str = Field(..., description="所属文件夹ID")
    file_name: str = Field(..., description="原始文件名")
    file_type: str = Field(..., description="文件类型")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UploadFile(BaseModel):
    """上传文件信息模型"""
    id: str = Field(..., description="上传文件ID")
    folder_id: str = Field(..., description="所属文件夹ID")
    storage_type: str = Field(..., description="存储类型")
    stored_name: str = Field(..., description="存储文件名")
    stored_path: str = Field(..., description="存储路径")
    file_id: str = Field(..., description="所属文件ID")
    file_name: str = Field(..., description="原始文件名")
    file_size: int = Field(0, description="文件大小（字节）")
    file_ext: str = Field(..., description="文件后缀")
    mime_type: str = Field(..., description="MIME类型")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FileUploadResponse(BaseModel):
    """文件上传返回"""
    file: File = Field(..., description="文件信息")
    upload_file: UploadFile = Field(..., description="上传文件信息")


class UploadUrlResponse(BaseModel):
    """上传URL响应"""
    file: File = Field(..., description="文件信息")
    upload_file: UploadFile = Field(..., description="上传文件信息")
    upload_url: str = Field(..., description="上传URL")


class ShareLinkRequest(BaseModel):
    """生成分享链接请求"""
    file_id: str = Field(..., description="文件ID")
    is_public: bool = Field(True, description="是否公开")
    access_scope: str = Field("view", description="访问范围")
    expire_seconds: int = Field(86400, description="过期时间（秒）")
    max_access: Optional[int] = Field(None, description="最大访问次数")
    password: Optional[str] = Field(None, description="访问密码")


class FileVisitRequest(BaseModel):
    """文件访问请求"""
    file_share_id: str = Field(..., description="分享ID")
    access_type: str = Field(..., description="访问类型")
    access_duration: int = Field(..., description="访问时长")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class FileListRequest(BaseModel):
    """文件列表请求"""
    folder_id: str = Field(..., description="文件夹ID")
    file_name: Optional[str] = Field(None, description="文件名")
    file_type: Optional[List[str]] = Field(None, description="文件类型")
    created_by_role: Optional[str] = Field(None, description="创建者角色")
    created_by: Optional[str] = Field(None, description="创建者")
    page_size: int = Field(20, description="每页大小")
    page: int = Field(1, description="页码")


class FileListResponse(BaseModel):
    """文件列表响应"""
    files: List[File] = Field(default_factory=list, description="文件列表")


class GetFileResponse(BaseModel):
    """获取文件响应"""
    file: File = Field(..., description="文件信息")
    upload_file: Optional[UploadFile] = Field(None, description="上传文件信息")


class DownloadUrlInfo(BaseModel):
    """下载URL信息"""
    file_id: str = Field(..., description="文件ID")
    url: str = Field(..., description="下载URL")
    mime_type: str = Field(..., description="MIME类型")
    error: Optional[str] = Field(None, description="错误信息")


class BatchDownloadUrlResponse(BaseModel):
    """批量下载URL响应"""
    download_urls: List[DownloadUrlInfo] = Field(default_factory=list, description="下载URL列表")


class GcsUrlInfo(BaseModel):
    """GCS URL信息"""
    file_id: str = Field(..., description="文件ID")
    gcs_url: str = Field(..., description="GCS URL")
    mime_type: str = Field(..., description="MIME类型")
    error: Optional[str] = Field(None, description="错误信息")


class GetGcsUrlResponse(BaseModel):
    """获取GCS URL响应"""
    gcs_url: str = Field(..., description="GCS URL")
    mime_type: str = Field(..., description="MIME类型")


class BatchGcsUrlResponse(BaseModel):
    """批量GCS URL响应"""
    gcs_urls: List[GcsUrlInfo] = Field(default_factory=list, description="GCS URL列表")


# ========= 压缩服务相关模型 =========

class CompressedVariant(BaseModel):
    """压缩变体信息"""
    variant_name: str = Field(..., description="变体名称")
    variant_type: str = Field(..., description="变体类型")
    media_type: str = Field(..., description="媒体类型")
    width: int = Field(..., description="宽度")
    height: int = Field(..., description="高度")
    file_size: int = Field(..., description="文件大小")
    format: str = Field(..., description="格式")
    quality: Optional[int] = Field(None, description="质量")
    duration: Optional[float] = Field(None, description="时长")
    bitrate: Optional[int] = Field(None, description="比特率")
    fps: Optional[int] = Field(None, description="帧率")
    compression_ratio: float = Field(..., description="压缩比")
    stored_path: str = Field(..., description="存储路径")


class CompressionStatusResponse(BaseModel):
    """压缩状态响应"""
    status: str = Field(..., description="状态: pending, processing, completed, failed")
    error_message: Optional[str] = Field(None, description="错误信息")
    variants: List[CompressedVariant] = Field(default_factory=list, description="压缩变体列表")


class GetVariantsResponse(BaseModel):
    """获取变体响应"""
    variants: List[CompressedVariant] = Field(default_factory=list, description="压缩变体列表")


class RecompressionResponse(BaseModel):
    """重新压缩响应"""
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="状态")


class VariantDownloadUrlResponse(BaseModel):
    """变体下载URL响应"""
    url: str = Field(..., description="下载URL")
    error: Optional[str] = Field(None, description="错误信息")
    variant_info: Optional[CompressedVariant] = Field(None, description="变体详细信息")
