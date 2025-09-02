"""
异步文件夹服务
"""
import grpc
from typing import Optional, Any

from ...rpc.async_client import AsyncGrpcClient
from ...schemas import (
    FolderInfo,
    FolderListResponse,
)
from ...errors import FolderNotFoundError, ValidationError
from ...utils.retry import retry_with_backoff


class AsyncFolderService:
    """异步文件夹服务"""

    def __init__(self, client: AsyncGrpcClient):
        """
        初始化文件夹服务
        
        Args:
            client: 异步gRPC客户端
        """
        self.client = client

    @retry_with_backoff(max_retries=3)
    async def create_folder(
            self,
            folder_name: str,
            *,
            parent_id: Optional[str] = None,
            request_id: Optional[str] = None,
        **metadata
    ) -> FolderInfo:
        """
        创建文件夹
        
        Args:
            folder_name: 文件夹名称
            parent_id: 父文件夹ID
            **metadata: 额外的元数据（如 x-org-id, x-user-id 等）
            
        Returns:
            创建的文件夹信息
        """
        from ...rpc.gen import folder_service_pb2, folder_service_pb2_grpc

        stub = await self.client.get_stub(folder_service_pb2_grpc.FolderServiceStub)

        request = folder_service_pb2.CreateFolderRequest(
            folder_name=folder_name,
            parent_id=parent_id
        )

        # 构建元数据
        grpc_metadata = self.client.build_metadata(request_id=request_id, **metadata)

        response = await stub.CreateFolder(request, metadata=grpc_metadata)
        return self._convert_folder_info(response)

    async def rename_folder(self, folder_id: str, new_name: str, request_id: Optional[str] = None,
        **metadata) -> FolderInfo:
        """
        重命名文件夹
        
        Args:
            folder_id: 文件夹ID
            new_name: 新名称
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据（如 x-org-id, x-user-id 等）
        """
        from ...rpc.gen import folder_service_pb2, folder_service_pb2_grpc

        if not new_name:
            raise ValidationError("文件夹名称不能为空")

        stub = await self.client.get_stub(folder_service_pb2_grpc.FolderServiceStub)

        request = folder_service_pb2.RenameFolderRequest(
            folder_id=folder_id,
            new_name=new_name
        )

        # 构建元数据
        grpc_metadata = self.client.build_metadata(request_id=request_id, **metadata)

        try:
            response = await stub.RenameFolder(request, metadata=grpc_metadata)
            return self._convert_folder_info(response)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                raise FolderNotFoundError(folder_id)
            raise

    async def move_folder(self, folder_id: str, new_parent_id: str, request_id: Optional[str] = None,
        **metadata) -> FolderInfo:
        """
        移动文件夹
        
        Args:
            folder_id: 文件夹ID
            new_parent_id: 新父文件夹ID
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据（如 x-org-id, x-user-id 等）
        """
        from ...rpc.gen import folder_service_pb2, folder_service_pb2_grpc

        stub = await self.client.get_stub(folder_service_pb2_grpc.FolderServiceStub)

        request = folder_service_pb2.MoveFolderRequest(
            folder_id=folder_id,
            new_parent_id=new_parent_id
        )

        # 构建元数据
        grpc_metadata = self.client.build_metadata(request_id=request_id, **metadata)

        try:
            response = await stub.MoveFolder(request, metadata=grpc_metadata)
            return self._convert_folder_info(response)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                raise FolderNotFoundError(folder_id)
            raise

    async def delete_folder(self, folder_id: str, request_id: Optional[str] = None,
        **metadata) -> None:
        """
        删除文件夹
        
        Args:
            folder_id: 文件夹ID
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据（如 x-org-id, x-user-id 等）
        """
        from ...rpc.gen import folder_service_pb2, folder_service_pb2_grpc

        stub = await self.client.get_stub(folder_service_pb2_grpc.FolderServiceStub)

        request = folder_service_pb2.DeleteFolderRequest(folder_id=folder_id)

        # 构建元数据
        grpc_metadata = self.client.build_metadata(request_id=request_id, **metadata)

        try:
            await stub.DeleteFolder(request, metadata=grpc_metadata)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                raise FolderNotFoundError(folder_id)
            raise

    async def list_folders(
            self,
            parent_id: Optional[str] = None,
            folder_name: Optional[str] = None,
            created_by_role: Optional[str] = None,
            created_by: Optional[str] = None,
            request_id: Optional[str] = None,
        **metadata
    ) -> FolderListResponse:
        """
        列出文件夹
        
        Args:
            parent_id: 父文件夹ID
            folder_name: 文件夹名称
            created_by_role: 创建者角色
            created_by: 创建者
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据（如 x-org-id, x-user-id 等）
            
        Returns:
            文件夹列表响应
        """
        from ...rpc.gen import folder_service_pb2, folder_service_pb2_grpc

        stub = await self.client.get_stub(folder_service_pb2_grpc.FolderServiceStub)

        request = folder_service_pb2.ListFoldersRequest()

        if parent_id:
            request.parent_id = parent_id
        if folder_name:
            request.folder_name = folder_name
        if created_by_role:
            request.created_by_role = created_by_role
        if created_by:
            request.created_by = created_by

        # 构建元数据
        grpc_metadata = self.client.build_metadata(request_id=request_id, **metadata)

        response = await stub.ListFolders(request, metadata=grpc_metadata)

        folders = [self._convert_folder_info(f) for f in response.folders]

        return FolderListResponse(items=folders)

    def _convert_folder_info(self, proto_folder: Any) -> FolderInfo:
        """转换Proto文件夹信息为模型"""
        from ...utils.converter import timestamp_to_datetime

        return FolderInfo(
            id=proto_folder.id,
            org_id=proto_folder.org_id,
            user_id=proto_folder.user_id,
            folder_name=proto_folder.folder_name,
            parent_id=proto_folder.parent_id,
            created_by=proto_folder.created_by,
            created_by_role=proto_folder.created_by_role,
            created_at=timestamp_to_datetime(proto_folder.created_at),
            updated_at=timestamp_to_datetime(proto_folder.updated_at)
        )
