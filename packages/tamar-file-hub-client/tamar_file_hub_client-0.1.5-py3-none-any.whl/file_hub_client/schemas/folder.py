"""
文件夹相关数据模型
"""
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class FolderInfo(BaseModel):
    """文件夹信息模型"""
    id: str = Field(..., description="文件夹ID")
    org_id: str = Field(..., description="组织ID")
    user_id: str = Field(..., description="用户ID")
    folder_name: str = Field(..., description="文件夹名称")
    parent_id: str = Field(..., description="父文件夹ID")
    created_by: str = Field(..., description="创建者")
    created_by_role: str = Field(..., description="创建者角色")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FolderListResponse(BaseModel):
    """文件夹列表响应"""
    items: List[FolderInfo] = Field(default_factory=list, description="文件夹列表")
