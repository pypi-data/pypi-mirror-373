"""
异步 Taple 服务
"""
import json
import traceback

import grpc
import tempfile
import os
from pathlib import Path
from typing import Optional, List, Dict, Any, Union, Callable
import uuid
import aiofiles
import asyncio

from .base_taple_service import BaseTapleService
from ...rpc.async_client import AsyncGrpcClient
from ...schemas.taple import (
    TableResponse, SheetResponse, ColumnResponse, RowResponse, CellResponse,
    ListSheetsResponse, CloneTableDataResponse, ExportTableDataResponse
)
from ...enums.export_format import ExportFormat
from ...errors import ValidationError
from ...utils.retry import retry_with_backoff, retry_on_lock_conflict
from ...utils.converter import timestamp_to_datetime


class AsyncTapleService(BaseTapleService):
    """异步 Taple 服务"""

    def __init__(self, client: AsyncGrpcClient):
        """
        初始化 Taple 服务
        
        Args:
            client: 异步 gRPC 客户端
        """
        self.client = client

    # Table operations
    @retry_with_backoff(max_retries=3)
    async def create_table(
            self,
            name: str,
            *,
            folder_id: Optional[str] = None,
            description: Optional[str] = None,
            idempotency_key: Optional[str] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> TableResponse:
        """
        创建表格
        
        Args:
            name: 表格名称
            folder_id: 父文件夹ID（可选，默认为"我的文件夹"）
            description: 表格描述
            idempotency_key: 幂等性键（可选）
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据
            
        Returns:
            创建的表格信息
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.CreateTableRequest(name=name)

        if folder_id:
            request.folder_id = folder_id
        if description:
            request.description = description
        if idempotency_key is not None:
            request.idempotency_key = idempotency_key

        response = await stub.CreateTable(request,
                                          metadata=self.client.build_metadata(request_id=request_id, **metadata))
        return TableResponse(table=self._convert_table(response.table))

    @retry_with_backoff(max_retries=3)
    async def get_table(
            self,
            *,
            table_id: Optional[str] = None,
            file_id: Optional[str] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> TableResponse:
        """
        获取表格信息
        
        Args:
            table_id: 表格ID
            file_id: 文件ID
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据
            
        Returns:
            表格信息
        """
        if not table_id and not file_id:
            raise ValidationError("table_id 或 file_id 必须提供一个")

        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.GetTableRequest()
        if table_id:
            request.table_id = table_id
        if file_id:
            request.file_id = file_id

        response = await stub.GetTable(request, metadata=self.client.build_metadata(request_id=request_id, **metadata))
        return TableResponse(table=self._convert_table(response.table))

    @retry_with_backoff(max_retries=3)
    async def update_table(
            self,
            table_id: str,
            *,
            name: Optional[str] = None,
            description: Optional[str] = None,
            idempotency_key: Optional[str] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> TableResponse:
        """
        更新表格信息
        
        Args:
            table_id: 表格ID
            name: 表格名称
            description: 表格描述
            idempotency_key: 幂等性键（可选）
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据
            
        Returns:
            更新后的表格信息
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.UpdateTableRequest(table_id=table_id)

        if name is not None:
            request.name = name
        if description is not None:
            request.description = description
        if idempotency_key is not None:
            request.idempotency_key = idempotency_key

        response = await stub.UpdateTable(request,
                                          metadata=self.client.build_metadata(request_id=request_id, **metadata))
        return TableResponse(table=self._convert_table(response.table))

    @retry_with_backoff(max_retries=3)
    async def delete_table(self, table_id: str, *, idempotency_key: Optional[str] = None,
                           request_id: Optional[str] = None,
                           **metadata) -> None:
        """
        删除表格
        
        Args:
            table_id: 表格ID
            idempotency_key: 幂等性键（可选）
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.DeleteTableRequest(table_id=table_id)

        if idempotency_key is not None:
            request.idempotency_key = idempotency_key

        await stub.DeleteTable(request, metadata=self.client.build_metadata(request_id=request_id, **metadata))

    # Sheet operations
    @retry_with_backoff(max_retries=3)
    async def create_sheet(
            self,
            table_id: str,
            name: str,
            *,
            description: Optional[str] = None,
            position: Optional[int] = None,
            idempotency_key: Optional[str] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> SheetResponse:
        """
        创建工作表
        
        Args:
            table_id: 表格ID
            name: 工作表名称
            description: 工作表描述
            position: 工作表位置
            idempotency_key: 幂等性键（可选）
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据
            
        Returns:
            创建的工作表信息
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.CreateSheetRequest(
            table_id=table_id,
            name=name
        )

        if description:
            request.description = description
        if position is not None:
            request.position = position
        if idempotency_key is not None:
            request.idempotency_key = idempotency_key

        response = await stub.CreateSheet(request,
                                          metadata=self.client.build_metadata(request_id=request_id, **metadata))
        return SheetResponse(sheet=self._convert_sheet(response.sheet))

    @retry_with_backoff(max_retries=3)
    async def get_sheet(self, sheet_id: str, request_id: Optional[str] = None,
                        **metadata) -> SheetResponse:
        """
        获取工作表信息
        
        Args:
            sheet_id: 工作表ID
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据
            
        Returns:
            工作表信息
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.GetSheetRequest(sheet_id=sheet_id)
        response = await stub.GetSheet(request, metadata=self.client.build_metadata(request_id=request_id, **metadata))
        return SheetResponse(sheet=self._convert_sheet(response.sheet))

    @retry_with_backoff(max_retries=3)
    async def list_sheets(self, table_id: str, request_id: Optional[str] = None,
                          **metadata) -> ListSheetsResponse:
        """
        列出工作表
        
        Args:
            table_id: 表格ID
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据
            
        Returns:
            工作表列表
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.ListSheetsRequest(table_id=table_id)
        response = await stub.ListSheets(request,
                                         metadata=self.client.build_metadata(request_id=request_id, **metadata))

        sheets = [self._convert_sheet(sheet) for sheet in response.sheets]
        return ListSheetsResponse(sheets=sheets)

    @retry_with_backoff(max_retries=3)
    async def update_sheet(
            self,
            sheet_id: str,
            *,
            name: Optional[str] = None,
            description: Optional[str] = None,
            position: Optional[int] = None,
            idempotency_key: Optional[str] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> SheetResponse:
        """
        更新工作表
        
        Args:
            sheet_id: 工作表ID
            name: 工作表名称
            description: 工作表描述
            position: 工作表位置
            idempotency_key: 幂等性键（可选）
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据
            
        Returns:
            更新后的工作表信息
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.UpdateSheetRequest(sheet_id=sheet_id)

        if name is not None:
            request.name = name
        if description is not None:
            request.description = description
        if position is not None:
            request.position = position
        if idempotency_key is not None:
            request.idempotency_key = idempotency_key

        response = await stub.UpdateSheet(request,
                                          metadata=self.client.build_metadata(request_id=request_id, **metadata))
        return SheetResponse(sheet=self._convert_sheet(response.sheet))

    @retry_with_backoff(max_retries=3)
    async def delete_sheet(self, sheet_id: str, *, idempotency_key: Optional[str] = None,
                           request_id: Optional[str] = None,
                           **metadata) -> None:
        """
        删除工作表
        
        Args:
            sheet_id: 工作表ID
            idempotency_key: 幂等性键（可选）
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.DeleteSheetRequest(sheet_id=sheet_id)

        if idempotency_key is not None:
            request.idempotency_key = idempotency_key

        await stub.DeleteSheet(request, metadata=self.client.build_metadata(request_id=request_id, **metadata))

    # Column operations
    @retry_with_backoff(max_retries=3)
    @retry_on_lock_conflict()
    async def create_column(
            self,
            sheet_id: str,
            name: str,
            column_type: str = "text",
            *,
            sheet_version: Optional[int] = None,
            client_id: Optional[str] = None,
            position: Optional[int] = None,
            width: Optional[int] = None,
            description: Optional[str] = None,
            properties: Optional[Dict[str, Any]] = None,
            idempotency_key: Optional[str] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> ColumnResponse:
        """
        创建列
        
        Args:
            sheet_id: 工作表ID
            name: 列名称
            column_type: 列类型
            sheet_version: 版本号（可选，不传则自动获取）
            client_id: 客户端ID（可选，不传则自动生成）
            position: 列位置
            width: 列宽度
            description: 列描述信息
            properties: 列属性
            idempotency_key: 幂等性键（可选）
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据
            
        Returns:
            创建的列信息
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc
        import uuid

        # 如果没有提供sheet_version，自动获取
        if sheet_version is None:
            version_result = await self.get_sheet_version(sheet_id=sheet_id, **metadata)
            sheet_version = version_result.version

        # 如果没有提供client_id，自动生成
        if client_id is None:
            client_id = str(uuid.uuid4())

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.CreateColumnRequest(
            sheet_id=sheet_id,
            sheet_version=sheet_version,
            client_id=client_id,
            name=name,
            column_type=column_type
        )

        if position is not None:
            request.position = position
        if width is not None:
            request.width = width
        if description is not None:
            request.description = description
        if properties:
            request.properties.CopyFrom(self._convert_dict_to_struct(properties))
        if idempotency_key is not None:
            request.idempotency_key = idempotency_key

        response = await stub.CreateColumn(request,
                                           metadata=self.client.build_metadata(request_id=request_id, **metadata))

        from ...schemas.taple import ColumnResponse
        return ColumnResponse(
            column=self._convert_column(response.column) if response.column else None,
            current_version=response.current_version if hasattr(response, 'current_version') else None,
            applied_immediately=response.applied_immediately if hasattr(response, 'applied_immediately') else None
        )

    @retry_with_backoff(max_retries=3)
    @retry_on_lock_conflict()
    async def update_column(
            self,
            sheet_id: str,
            column_key: str,
            *,
            sheet_version: Optional[int] = None,
            client_id: Optional[str] = None,
            name: Optional[str] = None,
            column_type: Optional[str] = None,
            width: Optional[int] = None,
            hidden: Optional[bool] = None,
            description: Optional[str] = None,
            properties: Optional[Dict[str, Any]] = None,
            idempotency_key: Optional[str] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> ColumnResponse:
        """
        更新列
        
        Args:
            sheet_id: 工作表ID
            column_key: 列key
            sheet_version: 版本号（可选，不传则自动获取）
            client_id: 客户端ID（可选，不传则自动生成）
            name: 列名称
            column_type: 列类型
            width: 列宽度
            hidden: 是否隐藏
            description: 列描述信息
            properties: 列属性
            idempotency_key: 幂等性键（可选）
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据
            
        Returns:
            更新后的列信息
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc
        import uuid

        # 如果没有提供sheet_version，自动获取
        if sheet_version is None:
            version_result = await self.get_sheet_version(sheet_id=sheet_id, **metadata)
            sheet_version = version_result.version

        # 如果没有提供client_id，自动生成
        if client_id is None:
            client_id = str(uuid.uuid4())

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.UpdateColumnRequest(
            sheet_id=sheet_id,
            sheet_version=sheet_version,
            client_id=client_id,
            column_key=column_key
        )

        if name is not None:
            request.name = name
        if column_type is not None:
            request.column_type = column_type
        if width is not None:
            request.width = width
        if hidden is not None:
            request.hidden = hidden
        if description is not None:
            request.description = description
        if properties:
            request.properties.CopyFrom(self._convert_dict_to_struct(properties))
        if idempotency_key is not None:
            request.idempotency_key = idempotency_key

        response = await stub.UpdateColumn(request,
                                           metadata=self.client.build_metadata(request_id=request_id, **metadata))

        from ...schemas.taple import ColumnResponse
        return ColumnResponse(
            column=self._convert_column(response.column) if response.column else None,
            current_version=response.current_version if hasattr(response, 'current_version') else None,
            applied_immediately=response.applied_immediately if hasattr(response, 'applied_immediately') else None
        )

    @retry_with_backoff(max_retries=3)
    @retry_on_lock_conflict()
    async def delete_column(
            self,
            sheet_id: str,
            column_key: str,
            *,
            sheet_version: Optional[int] = None,
            client_id: Optional[str] = None,
            idempotency_key: Optional[str] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> None:
        """
        删除列
        
        Args:
            sheet_id: 工作表ID
            column_key: 列key
            sheet_version: 版本号（可选，不传则自动获取）
            client_id: 客户端ID（可选，不传则自动生成）
            idempotency_key: 幂等性键（可选）
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc
        import uuid

        # 如果没有提供sheet_version，自动获取
        if sheet_version is None:
            version_result = await self.get_sheet_version(sheet_id=sheet_id, **metadata)
            sheet_version = version_result.version

        # 如果没有提供client_id，自动生成
        if client_id is None:
            client_id = str(uuid.uuid4())

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.DeleteColumnRequest(
            sheet_id=sheet_id,
            sheet_version=sheet_version,
            client_id=client_id,
            column_key=column_key
        )

        if idempotency_key is not None:
            request.idempotency_key = idempotency_key

        await stub.DeleteColumn(request, metadata=self.client.build_metadata(request_id=request_id, **metadata))

    # 以下是在 proto 中定义的方法
    @retry_with_backoff(max_retries=3)
    async def get_sheet_version(
            self,
            sheet_id: str,
            request_id: Optional[str] = None,
            **metadata
    ) -> Any:
        """
        Get sheet version (lightweight).
        
        Args:
            sheet_id: Sheet ID
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: Extra metadata
            
        Returns:
            GetSheetVersionResponse
        """
        if not sheet_id:
            raise ValidationError("sheet_id 不能为空")

        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.GetSheetVersionRequest(sheet_id=sheet_id)
        response = await stub.GetSheetVersion(request,
                                              metadata=self.client.build_metadata(request_id=request_id, **metadata))

        from ...schemas.taple import GetSheetVersionResponse
        return GetSheetVersionResponse(
            sheet_id=response.sheet_id,
            version=response.version,
            metadata=self._convert_sheet(response.metadata) if response.metadata else None
        )

    @retry_with_backoff(max_retries=3)
    async def get_sheet_data(
            self,
            sheet_id: str,
            version: Optional[int] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> Any:
        """
        Get complete sheet data.
        
        Args:
            sheet_id: Sheet ID
            version: Optional version to get changes since
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: Extra metadata
            
        Returns:
            GetSheetDataResponse
        """
        if not sheet_id:
            raise ValidationError("sheet_id 不能为空")

        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.GetSheetDataRequest(sheet_id=sheet_id)
        if version is not None:
            request.version = version

        response = await stub.GetSheetData(request,
                                           metadata=self.client.build_metadata(request_id=request_id, **metadata))

        from ...schemas.taple import GetSheetDataResponse
        return GetSheetDataResponse(
            sheet_id=response.sheet_id,
            version=response.version,
            metadata=self._convert_sheet(response.metadata) if response.metadata else None,
            columns=[self._convert_column(col) for col in response.columns] if response.columns else [],
            rows=[self._convert_row(row) for row in response.rows] if response.rows else [],
            cells=[self._convert_cell(cell) for cell in response.cells] if response.cells else [],
            last_updated=timestamp_to_datetime(response.last_updated) if response.last_updated else None
        )

    @retry_with_backoff(max_retries=3)
    @retry_on_lock_conflict()
    async def batch_edit_sheet(
            self,
            sheet_id: str,
            operations: List[Any],
            sheet_version: Optional[int] = None,
            client_id: Optional[str] = None,
            *,
            idempotency_key: Optional[str] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> Any:
        """
        Execute batch operations on a sheet.
        
        Args:
            sheet_id: Sheet ID
            operations: List of operations
            sheet_version: Current version for optimistic locking (optional, auto-fetched if not provided)
            client_id: Client ID (optional, auto-generated if not provided)
            idempotency_key: Idempotency key (optional)
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: Extra metadata
            
        Returns:
            BatchEditSheetResponse
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc
        import uuid

        # 如果没有提供sheet_version，自动获取
        if sheet_version is None:
            version_result = await self.get_sheet_version(sheet_id=sheet_id, **metadata)
            sheet_version = version_result.version

        # 如果没有提供client_id，自动生成
        if client_id is None:
            client_id = str(uuid.uuid4())

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.BatchEditSheetRequest(
            sheet_id=sheet_id,
            operations=operations,
            sheet_version=sheet_version,
            client_id=client_id
        )

        if idempotency_key is not None:
            request.idempotency_key = idempotency_key

        response = await stub.BatchEditSheet(request,
                                             metadata=self.client.build_metadata(request_id=request_id, **metadata))

        from ...schemas.taple import BatchEditSheetResponse, ConflictInfo

        conflict_info = None
        if response.conflict_info:
            conflict_info = ConflictInfo(
                has_conflict=response.conflict_info.has_conflict,
                server_version=response.conflict_info.server_version,
                conflict_type=response.conflict_info.conflict_type,
                conflicted_columns=list(response.conflict_info.conflicted_columns),
                resolution_suggestion=response.conflict_info.resolution_suggestion
            )

        return BatchEditSheetResponse(
            success=response.success,
            batch_id=response.batch_id,
            current_version=response.current_version,
            results=list(response.results),
            error_message=response.error_message,
            conflict_info=conflict_info
        )

    @retry_with_backoff(max_retries=3)
    @retry_on_lock_conflict()
    async def create_row(
            self,
            sheet_id: str,
            *,
            sheet_version: Optional[int] = None,
            client_id: Optional[str] = None,
            position: Optional[int] = None,
            height: Optional[int] = None,
            hidden: Optional[bool] = None,
            idempotency_key: Optional[str] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> RowResponse:
        """
        Create a row with version control.
        
        Args:
            sheet_id: Sheet ID
            sheet_version: Version for optimistic locking (optional, auto-fetched if not provided)
            client_id: Client ID (optional, auto-generated if not provided)
            position: Row position
            height: Row height
            hidden: Whether row is hidden
            idempotency_key: Idempotency key (optional)
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: Extra metadata
            
        Returns:
            Created row info
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc
        import uuid

        # 如果没有提供sheet_version，自动获取
        if sheet_version is None:
            version_result = await self.get_sheet_version(sheet_id=sheet_id, **metadata)
            sheet_version = version_result.version

        # 如果没有提供client_id，自动生成
        if client_id is None:
            client_id = str(uuid.uuid4())

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.CreateRowRequest(
            sheet_id=sheet_id,
            sheet_version=sheet_version,
            client_id=client_id
        )

        if position is not None:
            request.position = position
        if height is not None:
            request.height = height
        if hidden is not None:
            request.hidden = hidden
        if idempotency_key is not None:
            request.idempotency_key = idempotency_key

        response = await stub.CreateRow(request, metadata=self.client.build_metadata(request_id=request_id, **metadata))

        from ...schemas.taple import RowResponse, ConflictInfo

        conflict_info = None
        if hasattr(response, 'conflict_info') and response.conflict_info:
            conflict_info = ConflictInfo(
                has_conflict=response.conflict_info.has_conflict,
                server_version=response.conflict_info.server_version,
                conflict_type=response.conflict_info.conflict_type,
                conflicted_columns=list(response.conflict_info.conflicted_columns),
                resolution_suggestion=response.conflict_info.resolution_suggestion
            )

        return RowResponse(
            row=self._convert_row(response.row) if response.row else None,
            current_version=response.current_version if hasattr(response, 'current_version') else None,
            applied_immediately=response.applied_immediately if hasattr(response, 'applied_immediately') else None,
            success=response.success if hasattr(response, 'success') else None,
            error_message=response.error_message if hasattr(response, 'error_message') else None,
            conflict_info=conflict_info
        )

    @retry_with_backoff(max_retries=3)
    @retry_on_lock_conflict()
    async def update_row(
            self,
            sheet_id: str,
            row_key: str,
            *,
            sheet_version: Optional[int] = None,
            client_id: Optional[str] = None,
            position: Optional[int] = None,
            height: Optional[int] = None,
            hidden: Optional[bool] = None,
            idempotency_key: Optional[str] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> RowResponse:
        """
        Update a row with version control.
        
        Args:
            sheet_id: Sheet ID
            row_key: Row key to update
            sheet_version: Version for optimistic locking (optional, auto-fetched if not provided)
            client_id: Client ID (optional, auto-generated if not provided)
            position: New row position
            height: New row height
            hidden: Whether row is hidden
            idempotency_key: Idempotency key (optional)
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: Extra metadata
            
        Returns:
            Updated row info
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc
        import uuid

        # 如果没有提供sheet_version，自动获取
        if sheet_version is None:
            version_result = await self.get_sheet_version(sheet_id=sheet_id, **metadata)
            sheet_version = version_result.version

        # 如果没有提供client_id，自动生成
        if client_id is None:
            client_id = str(uuid.uuid4())

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.UpdateRowRequest(
            sheet_id=sheet_id,
            sheet_version=sheet_version,
            client_id=client_id,
            row_key=row_key
        )

        if position is not None:
            request.position = position
        if height is not None:
            request.height = height
        if hidden is not None:
            request.hidden = hidden
        if idempotency_key is not None:
            request.idempotency_key = idempotency_key

        response = await stub.UpdateRow(request, metadata=self.client.build_metadata(request_id=request_id, **metadata))

        from ...schemas.taple import RowResponse, ConflictInfo

        conflict_info = None
        if hasattr(response, 'conflict_info') and response.conflict_info:
            conflict_info = ConflictInfo(
                has_conflict=response.conflict_info.has_conflict,
                server_version=response.conflict_info.server_version,
                conflict_type=response.conflict_info.conflict_type,
                conflicted_columns=list(response.conflict_info.conflicted_columns),
                resolution_suggestion=response.conflict_info.resolution_suggestion
            )

        return RowResponse(
            row=self._convert_row(response.row) if response.row else None,
            current_version=response.current_version if hasattr(response, 'current_version') else None,
            applied_immediately=response.applied_immediately if hasattr(response, 'applied_immediately') else None,
            success=response.success if hasattr(response, 'success') else None,
            error_message=response.error_message if hasattr(response, 'error_message') else None,
            conflict_info=conflict_info
        )

    @retry_with_backoff(max_retries=3)
    @retry_on_lock_conflict()
    async def delete_row(
            self,
            sheet_id: str,
            row_key: str,
            *,
            sheet_version: Optional[int] = None,
            client_id: Optional[str] = None,
            idempotency_key: Optional[str] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> None:
        """
        Delete a row with version control.
        
        Args:
            sheet_id: Sheet ID
            row_key: Row key to delete
            sheet_version: Version for optimistic locking (optional, auto-fetched if not provided)
            client_id: Client ID (optional, auto-generated if not provided)
            idempotency_key: Idempotency key (optional)
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: Extra metadata
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc
        import uuid

        # 如果没有提供sheet_version，自动获取
        if sheet_version is None:
            version_result = await self.get_sheet_version(sheet_id=sheet_id, **metadata)
            sheet_version = version_result.version

        # 如果没有提供client_id，自动生成
        if client_id is None:
            client_id = str(uuid.uuid4())

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.DeleteRowRequest(
            sheet_id=sheet_id,
            sheet_version=sheet_version,
            client_id=client_id,
            row_key=row_key
        )

        if idempotency_key is not None:
            request.idempotency_key = idempotency_key

        await stub.DeleteRow(request, metadata=self.client.build_metadata(request_id=request_id, **metadata))

    @retry_with_backoff(max_retries=3)
    @retry_on_lock_conflict()
    async def edit_cell(
            self,
            sheet_id: str,
            column_key: str,
            row_key: str,
            *,
            sheet_version: Optional[int] = None,
            client_id: Optional[str] = None,
            raw_value: Optional[str] = None,
            formatted_value: Optional[str] = None,
            formula: Optional[str] = None,
            data_type: Optional[str] = None,
            styles: Optional[Dict[str, Any]] = None,
            idempotency_key: Optional[str] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> CellResponse:
        """
        Edit a cell with version control (create or update).
        
        Args:
            sheet_id: Sheet ID
            column_key: Column key
            row_key: Row key
            sheet_version: Version for optimistic locking (optional, auto-fetched if not provided)
            client_id: Client ID (optional, auto-generated if not provided)
            raw_value: Cell value
            formatted_value: Formatted value
            formula: Cell formula
            data_type: Data type
            styles: Cell styles
            idempotency_key: Idempotency key (optional)
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: Extra metadata
            
        Returns:
            Cell response with updated info
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc
        import uuid

        # 如果没有提供sheet_version，自动获取
        if sheet_version is None:
            version_result = await self.get_sheet_version(sheet_id=sheet_id, **metadata)
            sheet_version = version_result.version

        # 如果没有提供client_id，自动生成
        if client_id is None:
            client_id = str(uuid.uuid4())

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.EditCellRequest(
            sheet_id=sheet_id,
            sheet_version=sheet_version,
            client_id=client_id,
            column_key=column_key,
            row_key=row_key
        )

        if raw_value is not None:
            request.raw_value = raw_value
        if formatted_value is not None:
            request.formatted_value = formatted_value
        if formula is not None:
            request.formula = formula
        if data_type is not None:
            request.data_type = data_type
        if styles:
            request.styles.CopyFrom(self._convert_dict_to_struct(styles))
        if idempotency_key is not None:
            request.idempotency_key = idempotency_key

        response = await stub.EditCell(request, metadata=self.client.build_metadata(request_id=request_id, **metadata))

        from ...schemas.taple import CellResponse, ConflictInfo

        conflict_info = None
        if hasattr(response, 'conflict_info') and response.conflict_info:
            conflict_info = ConflictInfo(
                has_conflict=response.conflict_info.has_conflict,
                server_version=response.conflict_info.server_version,
                conflict_type=response.conflict_info.conflict_type,
                conflicted_columns=list(response.conflict_info.conflicted_columns),
                resolution_suggestion=response.conflict_info.resolution_suggestion
            )

        return CellResponse(
            cell=self._convert_cell(response.cell) if response.cell else None,
            current_version=response.current_version if hasattr(response, 'current_version') else None,
            applied_immediately=response.applied_immediately if hasattr(response, 'applied_immediately') else None,
            success=response.success if hasattr(response, 'success') else None,
            error_message=response.error_message if hasattr(response, 'error_message') else None,
            conflict_info=conflict_info
        )

    @retry_with_backoff(max_retries=3)
    @retry_on_lock_conflict()
    async def delete_cell(
            self,
            sheet_id: str,
            column_key: str,
            row_key: str,
            *,
            sheet_version: Optional[int] = None,
            client_id: Optional[str] = None,
            idempotency_key: Optional[str] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> None:
        """
        Delete a cell with version control.
        
        Args:
            sheet_id: Sheet ID
            column_key: Column key
            row_key: Row key
            sheet_version: Version for optimistic locking (optional, auto-fetched if not provided)
            client_id: Client ID (optional, auto-generated if not provided)
            idempotency_key: Idempotency key (optional)
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: Extra metadata
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc
        import uuid

        # 如果没有提供sheet_version，自动获取
        if sheet_version is None:
            version_result = await self.get_sheet_version(sheet_id=sheet_id, **metadata)
            sheet_version = version_result.version

        # 如果没有提供client_id，自动生成
        if client_id is None:
            client_id = str(uuid.uuid4())

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.DeleteCellRequest(
            sheet_id=sheet_id,
            sheet_version=sheet_version,
            client_id=client_id,
            column_key=column_key,
            row_key=row_key
        )

        if idempotency_key is not None:
            request.idempotency_key = idempotency_key

        await stub.DeleteCell(request, metadata=self.client.build_metadata(request_id=request_id, **metadata))

    @retry_with_backoff(max_retries=3)
    @retry_on_lock_conflict()
    async def batch_edit_columns(
            self,
            sheet_id: str,
            operations: List[Dict[str, Any]],
            *,
            sheet_version: Optional[int] = None,
            client_id: Optional[str] = None,
            idempotency_key: Optional[str] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> Any:
        """
        Execute batch column operations.
        
        Args:
            sheet_id: Sheet ID
            operations: List of column operations
            sheet_version: Version for optimistic locking (optional, auto-fetched if not provided)
            client_id: Client ID (optional, auto-generated if not provided)
            idempotency_key: Idempotency key (optional)
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: Extra metadata
            
        Returns:
            BatchEditColumnsResponse
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc
        import uuid

        # 如果没有提供sheet_version，自动获取
        if sheet_version is None:
            version_result = await self.get_sheet_version(sheet_id=sheet_id, **metadata)
            sheet_version = version_result.version

        # 如果没有提供client_id，自动生成
        if client_id is None:
            client_id = str(uuid.uuid4())

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        # Convert operations to proto format
        proto_operations = []
        for op in operations:
            column_op = taple_service_pb2.ColumnOperation()

            if 'create' in op:
                create_data = taple_service_pb2.CreateColumnData(
                    name=op['create']['name']
                )
                if 'column_type' in op['create']:
                    create_data.column_type = op['create']['column_type']
                if 'position' in op['create']:
                    create_data.position = op['create']['position']
                if 'width' in op['create']:
                    create_data.width = op['create']['width']
                if 'description' in op['create']:
                    create_data.description = op['create']['description']
                if 'properties' in op['create']:
                    create_data.properties.CopyFrom(self._convert_dict_to_struct(op['create']['properties']))
                column_op.create.CopyFrom(create_data)

            elif 'update' in op:
                update_data = taple_service_pb2.UpdateColumnData(
                    column_key=op['update']['column_key']
                )
                if 'name' in op['update']:
                    update_data.name = op['update']['name']
                if 'column_type' in op['update']:
                    update_data.column_type = op['update']['column_type']
                if 'position' in op['update']:
                    update_data.position = op['update']['position']
                if 'width' in op['update']:
                    update_data.width = op['update']['width']
                if 'hidden' in op['update']:
                    update_data.hidden = op['update']['hidden']
                if 'description' in op['update']:
                    update_data.description = op['update']['description']
                if 'properties' in op['update']:
                    update_data.properties.CopyFrom(self._convert_dict_to_struct(op['update']['properties']))
                column_op.update.CopyFrom(update_data)

            elif 'delete' in op:
                delete_data = taple_service_pb2.DeleteColumnData(
                    column_key=op['delete']['column_key']
                )
                column_op.delete.CopyFrom(delete_data)

            proto_operations.append(column_op)

        request = taple_service_pb2.BatchEditColumnsRequest(
            sheet_id=sheet_id,
            sheet_version=sheet_version,
            client_id=client_id,
            operations=proto_operations
        )

        if idempotency_key is not None:
            request.idempotency_key = idempotency_key

        response = await stub.BatchEditColumns(request,
                                               metadata=self.client.build_metadata(request_id=request_id, **metadata))

        from ...schemas.taple import ConflictInfo

        conflict_info = None
        if response.conflict_info:
            conflict_info = ConflictInfo(
                has_conflict=response.conflict_info.has_conflict,
                server_version=response.conflict_info.server_version,
                conflict_type=response.conflict_info.conflict_type,
                conflicted_columns=list(response.conflict_info.conflicted_columns),
                resolution_suggestion=response.conflict_info.resolution_suggestion
            )

        # Return raw response for now, can create proper schema later
        return {
            'success': response.success,
            'current_version': response.current_version,
            'results': [
                {
                    'success': result.success,
                    'column': self._convert_column(result.column) if result.column else None,
                    'error_message': result.error_message,
                    'operation_type': result.operation_type
                } for result in response.results
            ],
            'error_message': response.error_message,
            'conflict_info': conflict_info
        }

    @retry_with_backoff(max_retries=3)
    @retry_on_lock_conflict()
    async def batch_edit_rows(
            self,
            sheet_id: str,
            operations: List[Dict[str, Any]],
            *,
            sheet_version: Optional[int] = None,
            client_id: Optional[str] = None,
            idempotency_key: Optional[str] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> Any:
        """
        Execute batch row operations.
        
        Args:
            sheet_id: Sheet ID
            operations: List of row operations
            sheet_version: Version for optimistic locking (optional, auto-fetched if not provided)
            client_id: Client ID (optional, auto-generated if not provided)
            idempotency_key: Idempotency key (optional)
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: Extra metadata
            
        Returns:
            BatchEditRowsResponse
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc
        import uuid

        # 如果没有提供sheet_version，自动获取
        if sheet_version is None:
            version_result = await self.get_sheet_version(sheet_id=sheet_id, **metadata)
            sheet_version = version_result.version

        # 如果没有提供client_id，自动生成
        if client_id is None:
            client_id = str(uuid.uuid4())

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        # Convert operations to proto format
        proto_operations = []
        for op in operations:
            row_op = taple_service_pb2.RowOperation()

            if 'create' in op:
                # Set fields directly on the nested message
                if 'position' in op['create']:
                    row_op.create.position = op['create']['position']
                if 'height' in op['create']:
                    row_op.create.height = op['create']['height']

            elif 'update' in op:
                # Set fields directly on the nested message
                row_op.update.row_key = op['update']['row_key']
                if 'position' in op['update']:
                    row_op.update.position = op['update']['position']
                if 'height' in op['update']:
                    row_op.update.height = op['update']['height']
                if 'hidden' in op['update']:
                    row_op.update.hidden = op['update']['hidden']

            elif 'delete' in op:
                # Set fields directly on the nested message
                row_op.delete.row_key = op['delete']['row_key']

            proto_operations.append(row_op)

        request = taple_service_pb2.BatchEditRowsRequest(
            sheet_id=sheet_id,
            sheet_version=sheet_version,
            client_id=client_id,
            operations=proto_operations
        )

        if idempotency_key is not None:
            request.idempotency_key = idempotency_key

        response = await stub.BatchEditRows(request,
                                            metadata=self.client.build_metadata(request_id=request_id, **metadata))

        from ...schemas.taple import ConflictInfo

        conflict_info = None
        if response.conflict_info:
            conflict_info = ConflictInfo(
                has_conflict=response.conflict_info.has_conflict,
                server_version=response.conflict_info.server_version,
                conflict_type=response.conflict_info.conflict_type,
                conflicted_columns=list(response.conflict_info.conflicted_columns),
                resolution_suggestion=response.conflict_info.resolution_suggestion
            )

        # Return raw response for now, can create proper schema later
        return {
            'success': response.success,
            'current_version': response.current_version,
            'results': [
                {
                    'success': result.success,
                    'row': self._convert_row(result.row) if result.row else None,
                    'error_message': result.error_message,
                    'operation_type': result.operation_type
                } for result in response.results
            ],
            'error_message': response.error_message,
            'conflict_info': conflict_info
        }

    @retry_with_backoff(max_retries=3)
    @retry_on_lock_conflict()
    async def batch_edit_cells(
            self,
            sheet_id: str,
            operations: List[Dict[str, Any]],
            *,
            sheet_version: Optional[int] = None,
            client_id: Optional[str] = None,
            idempotency_key: Optional[str] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> Any:
        """
        Execute batch cell operations.
        
        Args:
            sheet_id: Sheet ID
            operations: List of cell operations
            sheet_version: Version for optimistic locking (optional, auto-fetched if not provided)
            client_id: Client ID (optional, auto-generated if not provided)
            idempotency_key: Idempotency key (optional)
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: Extra metadata
            
        Returns:
            BatchEditCellsResponse
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc
        import uuid

        # 如果没有提供sheet_version，自动获取
        if sheet_version is None:
            version_result = await self.get_sheet_version(sheet_id=sheet_id, **metadata)
            sheet_version = version_result.version

        # 如果没有提供client_id，自动生成
        if client_id is None:
            client_id = str(uuid.uuid4())

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        # Convert operations to proto format
        proto_operations = []
        for op in operations:
            cell_op = taple_service_pb2.CellOperation()

            if 'edit' in op:
                edit_data = taple_service_pb2.EditCellData(
                    column_key=op['edit']['column_key'],
                    row_key=op['edit']['row_key']
                )
                if 'raw_value' in op['edit']:
                    edit_data.raw_value = op['edit']['raw_value']
                if 'formatted_value' in op['edit']:
                    edit_data.formatted_value = op['edit']['formatted_value']
                if 'formula' in op['edit']:
                    edit_data.formula = op['edit']['formula']
                if 'data_type' in op['edit']:
                    edit_data.data_type = op['edit']['data_type']
                if 'styles' in op['edit']:
                    edit_data.styles.CopyFrom(self._convert_dict_to_struct(op['edit']['styles']))
                cell_op.edit.CopyFrom(edit_data)

            elif 'clear' in op:
                clear_data = taple_service_pb2.ClearCellData(
                    column_key=op['clear']['column_key'],
                    row_key=op['clear']['row_key']
                )
                cell_op.clear.CopyFrom(clear_data)

            elif 'delete' in op:
                delete_data = taple_service_pb2.DeleteCellData(
                    column_key=op['delete']['column_key'],
                    row_key=op['delete']['row_key']
                )
                cell_op.delete.CopyFrom(delete_data)

            proto_operations.append(cell_op)

        request = taple_service_pb2.BatchEditCellsRequest(
            sheet_id=sheet_id,
            sheet_version=sheet_version,
            client_id=client_id,
            operations=proto_operations
        )

        if idempotency_key is not None:
            request.idempotency_key = idempotency_key

        response = await stub.BatchEditCells(request,
                                             metadata=self.client.build_metadata(request_id=request_id, **metadata))

        from ...schemas.taple import ConflictInfo

        conflict_info = None
        if response.conflict_info:
            conflict_info = ConflictInfo(
                has_conflict=response.conflict_info.has_conflict,
                server_version=response.conflict_info.server_version,
                conflict_type=response.conflict_info.conflict_type,
                conflicted_columns=list(response.conflict_info.conflicted_columns),
                resolution_suggestion=response.conflict_info.resolution_suggestion
            )

        # Return raw response for now, can create proper schema later
        return {
            'success': response.success,
            'current_version': response.current_version,
            'results': [
                {
                    'success': result.success,
                    'cell': self._convert_cell(result.cell) if result.cell else None,
                    'error_message': result.error_message,
                    'operation_type': result.operation_type
                } for result in response.results
            ],
            'error_message': response.error_message,
            'conflict_info': conflict_info
        }

    @retry_with_backoff(max_retries=3)
    async def get_column_data(
            self,
            sheet_id: str,
            column_key: str,
            request_id: Optional[str] = None,
            **metadata
    ) -> Any:
        """
        Get column data including all cells in the column.
        
        Args:
            sheet_id: Sheet ID
            column_key: Column key
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: Extra metadata
            
        Returns:
            ColumnDataResponse with column info and cells
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.GetColumnDataRequest(
            sheet_id=sheet_id,
            column_key=column_key
        )

        response = await stub.GetColumnData(request,
                                            metadata=self.client.build_metadata(request_id=request_id, **metadata))

        # Return raw response for now, can create proper schema later
        return {
            'column': self._convert_column(response.column) if response.column else None,
            'cells': [self._convert_cell(cell) for cell in response.cells]
        }

    @retry_with_backoff(max_retries=3)
    async def get_row_data(
            self,
            sheet_id: str,
            row_key: str,
            request_id: Optional[str] = None,
            **metadata
    ) -> Any:
        """
        Get row data including all cells in the row.
        
        Args:
            sheet_id: Sheet ID
            row_key: Row key
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: Extra metadata
            
        Returns:
            RowDataResponse with row info and cells
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.GetRowDataRequest(
            sheet_id=sheet_id,
            row_key=row_key
        )

        response = await stub.GetRowData(request,
                                         metadata=self.client.build_metadata(request_id=request_id, **metadata))

        # Return raw response for now, can create proper schema later
        return {
            'row': self._convert_row(response.row) if response.row else None,
            'cells': [self._convert_cell(cell) for cell in response.cells]
        }

    @retry_with_backoff(max_retries=3)
    async def get_cell_data(
            self,
            sheet_id: str,
            column_key: str,
            row_key: str,
            request_id: Optional[str] = None,
            **metadata
    ) -> Any:
        """
        Get cell data.
        
        Args:
            sheet_id: Sheet ID
            column_key: Column key
            row_key: Row key
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: Extra metadata
            
        Returns:
            CellDataResponse with cell info
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.GetCellDataRequest(
            sheet_id=sheet_id,
            column_key=column_key,
            row_key=row_key
        )

        response = await stub.GetCellData(request,
                                          metadata=self.client.build_metadata(request_id=request_id, **metadata))

        # Return raw response for now, can create proper schema later
        return {
            'cell': self._convert_cell(response.cell) if response.cell else None
        }

    @retry_with_backoff(max_retries=3)
    async def clone_table_data(
            self,
            source_table_id: str,
            target_org_id: str,
            target_user_id: str,
            *,
            target_folder_id: Optional[str] = None,
            new_table_name: Optional[str] = None,
            include_views: bool = False,
            idempotency_key: Optional[str] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> 'CloneTableDataResponse':
        """
        Clone table data to another organization.
        
        Args:
            source_table_id: Source table ID
            target_org_id: Target organization ID
            target_user_id: Target user ID
            target_folder_id: Target folder ID (optional)
            new_table_name: New table name (optional, defaults to original name + Copy)
            include_views: Whether to include view data (default: False)
            idempotency_key: Idempotency key (optional)
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: Extra metadata
            
        Returns:
            CloneTableDataResponse with clone operation result
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc
        from ...schemas.taple import CloneTableDataResponse

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.CloneTableDataRequest(
            source_table_id=source_table_id,
            target_org_id=target_org_id,
            target_user_id=target_user_id
        )

        if target_folder_id:
            request.target_folder_id = target_folder_id
        if new_table_name:
            request.new_table_name = new_table_name
        if include_views is not None:
            request.include_views = include_views
        if idempotency_key:
            request.idempotency_key = idempotency_key

        response = await stub.CloneTableData(request,
                                             metadata=self.client.build_metadata(request_id=request_id, **metadata))

        return CloneTableDataResponse(
            success=response.success,
            new_table_id=response.new_table_id,
            new_file_id=response.new_file_id,
            sheets_cloned=response.sheets_cloned,
            cells_cloned=response.cells_cloned,
            error_message=response.error_message if response.error_message else None,
            created_at=timestamp_to_datetime(response.created_at)
        )

    @retry_with_backoff(max_retries=3)
    async def export_table_data(
            self,
            table_id: str,
            format: 'ExportFormat',
            *,
            sheet_ids: Optional[List[str]] = None,
            options: Optional[Dict[str, Any]] = None,
            idempotency_key: Optional[str] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> 'ExportTableDataResponse':
        """
        Export table data to file.
        
        Args:
            table_id: Table ID to export
            format: Export format (EXCEL, CSV, JSON)
            sheet_ids: List of sheet IDs to export (optional, empty means all)
            options: Export options dict
            idempotency_key: Idempotency key (optional)
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: Extra metadata
            
        Returns:
            ExportTableDataResponse with export result
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc
        from ...schemas.taple import ExportTableDataResponse
        from google.protobuf import struct_pb2

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        # Convert format enum
        format_map = {
            ExportFormat.XLSX: taple_service_pb2.EXPORT_FORMAT_EXCEL,
            ExportFormat.CSV: taple_service_pb2.EXPORT_FORMAT_CSV,
            ExportFormat.JSON: taple_service_pb2.EXPORT_FORMAT_JSON,
        }

        request = taple_service_pb2.ExportTableDataRequest(
            table_id=table_id,
            format=format_map.get(format, taple_service_pb2.EXPORT_FORMAT_UNSPECIFIED)
        )

        if sheet_ids:
            request.sheet_ids.extend(sheet_ids)

        if options:
            # Create ExportOptions
            export_options = taple_service_pb2.ExportOptions()
            if 'include_formulas' in options:
                export_options.include_formulas = options['include_formulas']
            if 'include_styles' in options:
                export_options.include_styles = options['include_styles']
            if 'include_hidden_sheets' in options:
                export_options.include_hidden_sheets = options['include_hidden_sheets']
            if 'include_hidden_rows_cols' in options:
                export_options.include_hidden_rows_cols = options['include_hidden_rows_cols']
            if 'date_format' in options:
                export_options.date_format = options['date_format']
            if 'csv_delimiter' in options:
                export_options.csv_delimiter = options['csv_delimiter']
            if 'csv_encoding' in options:
                export_options.csv_encoding = options['csv_encoding']
            request.options.CopyFrom(export_options)

        if idempotency_key:
            request.idempotency_key = idempotency_key

        response = await stub.ExportTableData(request,
                                              metadata=self.client.build_metadata(request_id=request_id, **metadata))

        return ExportTableDataResponse(
            success=response.success,
            export_id=response.export_id,
            file_url=response.file_url,
            download_url=response.download_url,
            file_size=response.file_size,
            file_name=response.file_name,
            format=format.value if hasattr(format, 'value') else str(format),  # Convert enum to string
            sheets_exported=response.sheets_exported,
            error_message=response.error_message if response.error_message else None,
            created_at=timestamp_to_datetime(response.created_at),
            expires_at=timestamp_to_datetime(response.expires_at)
        )

    @retry_with_backoff(max_retries=3)
    async def import_table_data(
            self,
            file_id: str,
            *,
            target_table_id: Optional[str] = None,
            table_name: Optional[str] = None,
            folder_id: Optional[str] = None,
            import_mode: str = "APPEND",
            skip_first_row: bool = True,
            auto_detect_types: bool = True,
            clear_existing_data: bool = False,
            column_mapping: Optional[Dict[str, str]] = None,
            date_format: str = "YYYY-MM-DD",
            csv_delimiter: str = ",",
            csv_encoding: str = "UTF-8",
            max_rows: int = 0,
            idempotency_key: Optional[str] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> 'ImportTableDataResponse':
        """
        导入文件数据到表格
        
        Args:
            file_id: 要导入的文件ID
            target_table_id: 目标表格ID（可选，不提供则创建新表格）
            table_name: 表格名称（仅在创建新表格时使用）
            folder_id: 文件夹ID（仅在创建新表格时使用）
            import_mode: 导入模式（APPEND/REPLACE/MERGE）
            skip_first_row: 是否跳过第一行（标题行）
            auto_detect_types: 是否自动检测列类型
            clear_existing_data: 是否清空现有数据（仅在导入到现有表格时）
            column_mapping: 列映射（源列名 -> 目标列名）
            date_format: 日期格式
            csv_delimiter: CSV分隔符
            csv_encoding: CSV编码
            max_rows: 最大导入行数限制（0表示无限制）
            idempotency_key: 幂等性键
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据
            
        Returns:
            ImportTableDataResponse
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc
        from ...schemas.taple import ImportTableDataResponse

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        # 构建导入选项
        import_options = taple_service_pb2.ImportOptions(
            import_mode=self._get_import_mode_enum(import_mode),
            skip_first_row=skip_first_row,
            auto_detect_types=auto_detect_types,
            clear_existing_data=clear_existing_data,
            date_format=date_format,
            csv_delimiter=csv_delimiter,
            csv_encoding=csv_encoding,
            max_rows=max_rows
        )

        # 添加列映射
        if column_mapping:
            for source_col, target_col in column_mapping.items():
                import_options.column_mapping[source_col] = target_col

        # 构建请求
        request = taple_service_pb2.ImportTableDataRequest(
            file_id=file_id,
            options=import_options
        )

        if target_table_id:
            request.target_table_id = target_table_id
        if folder_id:
            request.folder_id = folder_id
        if table_name:
            request.table_name = table_name
        if idempotency_key:
            request.idempotency_key = idempotency_key

        # 调用RPC
        response = await stub.ImportTableData(
            request,
            metadata=self.client.build_metadata(request_id=request_id, **metadata)
        )

        # 转换响应
        return ImportTableDataResponse(
            success=response.success,
            table_id=response.table_id,
            file_id=response.file_id if response.file_id else None,
            sheets_imported=response.sheets_imported,
            rows_imported=response.rows_imported,
            cells_imported=response.cells_imported,
            sheet_results=[
                {
                    'sheet_name': result.sheet_name,
                    'sheet_id': result.sheet_id,
                    'rows_imported': result.rows_imported,
                    'cells_imported': result.cells_imported,
                    'success': result.success,
                    'error_message': result.error_message if result.error_message else None
                }
                for result in response.sheet_results
            ],
            error_message=response.error_message if response.error_message else None,
            warnings=[
                {
                    'type': warning.type,
                    'message': warning.message,
                    'sheet_name': warning.sheet_name if warning.sheet_name else None,
                    'row_number': warning.row_number if warning.row_number else None,
                    'column_name': warning.column_name if warning.column_name else None
                }
                for warning in response.warnings
            ],
            created_at=timestamp_to_datetime(response.created_at),
            processing_time_ms=response.processing_time_ms
        )

    def _get_import_mode_enum(self, mode: str) -> int:
        """将字符串导入模式转换为枚举值"""
        from ...rpc.gen import taple_service_pb2

        mode_map = {
            "APPEND": taple_service_pb2.IMPORT_MODE_APPEND,
            "REPLACE": taple_service_pb2.IMPORT_MODE_REPLACE,
            "MERGE": taple_service_pb2.IMPORT_MODE_MERGE
        }

        return mode_map.get(mode.upper(), taple_service_pb2.IMPORT_MODE_APPEND)

    # Table view operations
    @retry_with_backoff(max_retries=3)
    async def create_table_view(
            self,
            sheet_id: str,
            name: str,
            view_type: str,
            *,
            filter_criteria: Optional[Dict[str, Any]] = None,
            sort_criteria: Optional[Dict[str, Any]] = None,
            visible_columns: Optional[Dict[str, bool]] = None,
            group_criteria: Optional[Dict[str, Any]] = None,
            is_hidden: bool = False,
            is_default: bool = False,
            config: Optional[Dict[str, Any]] = None,
            idempotency_key: Optional[str] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> 'TableViewResponse':
        """
        创建表格视图
        
        Args:
            sheet_id: 所属工作表ID
            name: 视图名称
            view_type: 视图类型（table/gantt/calendar/kanban/gallery等）
            filter_criteria: 过滤条件（可选）
            sort_criteria: 排序条件（可选）
            visible_columns: 可见列配置（可选），字典格式 {column_id: bool}，值为True表示显示该列
            group_criteria: 分组条件（可选）
            is_hidden: 是否隐藏（默认False）
            is_default: 是否默认视图（默认False）
            config: 扩展配置（可选）
            idempotency_key: 幂等性键（可选）
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据
            
        Returns:
            TableViewResponse
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc
        from ...schemas.taple import TableViewResponse

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.CreateTableViewRequest(
            sheet_id=sheet_id,
            view_name=name,
            view_type=view_type,
            is_hidden=is_hidden,
            is_default=is_default,
        )

        # 处理可选的 JSON 字段
        if visible_columns:
            request.visible_columns.CopyFrom(self._convert_dict_to_struct(visible_columns))
        if filter_criteria:
            request.filter_criteria.CopyFrom(self._convert_dict_to_struct(filter_criteria))
        if sort_criteria:
            request.sort_criteria.CopyFrom(self._convert_dict_to_struct(sort_criteria))
        if group_criteria:
            request.group_criteria.CopyFrom(self._convert_dict_to_struct(group_criteria))
        if config:
            request.config.CopyFrom(self._convert_dict_to_struct(config))

        response = await stub.CreateTableView(
            request,
            metadata=self.client.build_metadata(request_id=request_id, **metadata)
        )

        return TableViewResponse(view=self._convert_table_view(response.view))

    @retry_with_backoff(max_retries=3)
    async def get_table_view(
            self,
            view_id: str,
            request_id: Optional[str] = None,
            **metadata
    ) -> 'TableViewResponse':
        """
        获取表格视图
        
        Args:
            view_id: 视图ID
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据
            
        Returns:
            TableViewResponse
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc
        from ...schemas.taple import TableViewResponse

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.GetTableViewRequest(view_id=view_id)

        response = await stub.GetTableView(
            request,
            metadata=self.client.build_metadata(request_id=request_id, **metadata)
        )

        return TableViewResponse(view=self._convert_table_view(response.view))

    @retry_with_backoff(max_retries=3)
    async def list_table_views(
            self,
            *,
            table_id: Optional[str] = None,
            sheet_id: Optional[str] = None,
            view_type: Optional[str] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> 'ListTableViewsResponse':
        """
        列出表格视图
        
        Args:
            table_id: 按表格ID查询（可选）
            sheet_id: 按工作表ID查询（可选）
            view_type: 筛选视图类型（可选）
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据
            
        Returns:
            ListTableViewsResponse
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc
        from ...schemas.taple import ListTableViewsResponse

        if not table_id and not sheet_id:
            raise ValidationError("必须提供 table_id 或 sheet_id 之一")

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.ListTableViewsRequest()

        if table_id:
            request.table_id = table_id
        elif sheet_id:
            request.sheet_id = sheet_id

        if view_type:
            request.view_type = view_type

        response = await stub.ListTableViews(
            request,
            metadata=self.client.build_metadata(request_id=request_id, **metadata)
        )

        return ListTableViewsResponse(
            views=[self._convert_table_view(view) for view in response.views],
            total_count=response.total_count
        )

    @retry_with_backoff(max_retries=3)
    async def update_table_view(
            self,
            view_id: str,
            *,
            name: Optional[str] = None,
            filter_criteria: Optional[Dict[str, Any]] = None,
            sort_criteria: Optional[Dict[str, Any]] = None,
            visible_columns: Optional[Dict[str, bool]] = None,
            group_criteria: Optional[Dict[str, Any]] = None,
            is_hidden: Optional[bool] = None,
            is_default: Optional[bool] = None,
            config: Optional[Dict[str, Any]] = None,
            idempotency_key: Optional[str] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> 'TableViewResponse':
        """
        更新表格视图
        
        Args:
            view_id: 视图ID
            name: 新名称（可选）
            filter_criteria: 过滤条件（可选）
            sort_criteria: 排序条件（可选）
            visible_columns: 可见列配置（可选），字典格式 {column_id: bool}，传入空字典清空可见列设置
            group_criteria: 分组条件（可选）
            is_hidden: 是否隐藏（可选）
            is_default: 是否默认视图（可选）
            config: 扩展配置（可选）
            idempotency_key: 幂等性键（可选）
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据
            
        Returns:
            TableViewResponse
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc
        from ...schemas.taple import TableViewResponse


        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.UpdateTableViewRequest(view_id=view_id)

        if name is not None:
            request.view_name = name
            
        # 处理可选的 JSON 字段
        if filter_criteria is not None:
            request.filter_criteria.CopyFrom(self._convert_dict_to_struct(filter_criteria))
        if sort_criteria is not None:
            request.sort_criteria.CopyFrom(self._convert_dict_to_struct(sort_criteria))
        if visible_columns is not None:
            request.visible_columns.CopyFrom(self._convert_dict_to_struct(visible_columns))
        if group_criteria is not None:
            request.group_criteria.CopyFrom(self._convert_dict_to_struct(group_criteria))
            
        # 处理布尔字段
        if is_hidden is not None:
            request.is_hidden = is_hidden
        if is_default is not None:
            request.is_default = is_default
            
        if config is not None:
            request.config.CopyFrom(self._convert_dict_to_struct(config))

        response = await stub.UpdateTableView(
            request,
            metadata=self.client.build_metadata(request_id=request_id, **metadata)
        )

        return TableViewResponse(view=self._convert_table_view(response.view))

    @retry_with_backoff(max_retries=3)
    async def delete_table_view(
            self,
            view_id: str,
            *,
            idempotency_key: Optional[str] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> None:
        """
        删除表格视图
        
        Args:
            view_id: 视图ID
            idempotency_key: 幂等性键（可选）
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.DeleteTableViewRequest(view_id=view_id)

        await stub.DeleteTableView(
            request,
            metadata=self.client.build_metadata(request_id=request_id, **metadata)
        )

    @retry_with_backoff(max_retries=3)
    async def update_table_view_config(
            self,
            view_id: str,
            config: Dict[str, Any],
            *,
            idempotency_key: Optional[str] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> 'TableViewResponse':
        """
        更新视图配置
        
        Args:
            view_id: 视图ID
            config: 新配置
            idempotency_key: 幂等性键（可选）
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据
            
        Returns:
            TableViewResponse
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc
        from ...schemas.taple import TableViewResponse

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        request = taple_service_pb2.UpdateTableViewConfigRequest(view_id=view_id)
        request.config.CopyFrom(self._convert_dict_to_struct(config))

        response = await stub.UpdateTableViewConfig(
            request,
            metadata=self.client.build_metadata(request_id=request_id, **metadata)
        )

        return TableViewResponse(view=self._convert_table_view(response.view))

    def _convert_table_view(self, proto_view) -> 'TableView':
        """转换 proto TableView 到 Python TableView 模型"""
        from ...schemas.taple import TableView
        from google.protobuf.json_format import MessageToDict

        # 处理 visible_columns 的转换
        if proto_view.HasField('visible_columns'):
            visible_columns_dict = MessageToDict(proto_view.visible_columns)
            # 如果服务器返回的是旧格式（包含 items 字段的结构），需要转换
            if isinstance(visible_columns_dict, dict) and 'items' in visible_columns_dict:
                # 旧格式：将列表转换为字典，默认所有列都显示
                if isinstance(visible_columns_dict['items'], list):
                    visible_columns = {col: True for col in visible_columns_dict['items']}
                else:
                    visible_columns = visible_columns_dict
            else:
                visible_columns = visible_columns_dict
        else:
            visible_columns = None

        return TableView(
            id=proto_view.id,
            table_id=proto_view.table_id,
            sheet_id=proto_view.sheet_id,
            org_id=proto_view.org_id,
            user_id=proto_view.user_id,
            file_id=proto_view.file_id,
            
            # 视图配置字段
            filter_criteria=MessageToDict(proto_view.filter_criteria) if proto_view.filter_criteria else None,
            sort_criteria=MessageToDict(proto_view.sort_criteria) if proto_view.sort_criteria else None,
            visible_columns=visible_columns,
            group_criteria=MessageToDict(proto_view.group_criteria) if proto_view.group_criteria else None,
            
            # 创建者信息
            created_by_role=proto_view.created_by_role,
            created_by=proto_view.created_by,
            
            # 视图基本信息
            view_name=proto_view.view_name,
            view_type=proto_view.view_type,
            
            # 视图状态
            is_hidden=proto_view.is_hidden,
            is_default=proto_view.is_default,
            
            # 扩展配置
            config=MessageToDict(proto_view.config) if proto_view.config else None,
            
            # 时间戳
            created_at=timestamp_to_datetime(proto_view.created_at),
            updated_at=timestamp_to_datetime(proto_view.updated_at),
            deleted_at=timestamp_to_datetime(proto_view.deleted_at) if proto_view.deleted_at else None
        )

    @retry_with_backoff(max_retries=3)
    async def batch_create_table_views(
            self,
            sheet_id: str,
            views: List[Dict[str, Any]],
            *,
            request_id: Optional[str] = None,
            **metadata
    ) -> 'BatchCreateTableViewsResponse':
        """
        批量创建表格视图
        
        Args:
            sheet_id: 所属工作表ID
            views: 要创建的视图列表，每个视图包含以下字段：
                - view_name: 视图名称
                - view_type: 视图类型
                - filter_criteria: 过滤条件（可选）
                - sort_criteria: 排序条件（可选）
                - visible_columns: 可见列配置（可选），字典格式 {column_id: bool}
                - group_criteria: 分组条件（可选）
                - is_hidden: 是否隐藏（可选，默认False）
                - is_default: 是否默认视图（可选，默认False）
                - config: 扩展配置（可选）
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据
            
        Returns:
            BatchCreateTableViewsResponse
        """
        from ...rpc.gen import taple_service_pb2, taple_service_pb2_grpc
        from ...schemas.taple import BatchCreateTableViewsResponse, BatchCreateTableViewResult

        stub = await self.client.get_stub(taple_service_pb2_grpc.TapleServiceStub)

        # 构建请求
        request = taple_service_pb2.BatchCreateTableViewsRequest(sheet_id=sheet_id)
        
        for view_data in views:
            view_req = taple_service_pb2.CreateTableViewData(
                view_name=view_data['view_name'],
                view_type=view_data['view_type'],
                is_hidden=view_data.get('is_hidden', False),
                is_default=view_data.get('is_default', False),
            )
            
            # 处理可选的 JSON 字段
            if 'visible_columns' in view_data:
                view_req.visible_columns.CopyFrom(self._convert_dict_to_struct(view_data['visible_columns']))
            if 'filter_criteria' in view_data:
                view_req.filter_criteria.CopyFrom(self._convert_dict_to_struct(view_data['filter_criteria']))
            if 'sort_criteria' in view_data:
                view_req.sort_criteria.CopyFrom(self._convert_dict_to_struct(view_data['sort_criteria']))
            if 'group_criteria' in view_data:
                view_req.group_criteria.CopyFrom(self._convert_dict_to_struct(view_data['group_criteria']))
            if 'config' in view_data:
                view_req.config.CopyFrom(self._convert_dict_to_struct(view_data['config']))
                
            request.views.append(view_req)

        response = await stub.BatchCreateTableViews(
            request,
            metadata=self.client.build_metadata(request_id=request_id, **metadata)
        )

        # 转换响应
        results = []
        for result in response.results:
            results.append(BatchCreateTableViewResult(
                success=result.success,
                view=self._convert_table_view(result.view) if result.view else None,
                error_message=result.error_message if result.error_message else None,
                view_name=result.view_name if result.view_name else None
            ))

        return BatchCreateTableViewsResponse(
            results=results,
            success_count=response.success_count,
            failed_count=response.failed_count
        )
