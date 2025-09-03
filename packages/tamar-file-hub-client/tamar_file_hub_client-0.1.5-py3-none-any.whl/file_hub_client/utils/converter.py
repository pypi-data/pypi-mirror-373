"""
Proto和Model之间的转换工具
"""
from datetime import datetime
from typing import Any
from google.protobuf.timestamp_pb2 import Timestamp

from ..schemas import File, FolderInfo


def timestamp_to_datetime(timestamp: Timestamp) -> datetime:
    """将protobuf timestamp转换为datetime"""
    return datetime.fromtimestamp(timestamp.seconds + timestamp.nanos / 1e9)
#
#
# def datetime_to_timestamp(dt: datetime) -> Timestamp:
#     """将datetime转换为protobuf timestamp"""
#     timestamp = Timestamp()
#     timestamp.FromDatetime(dt)
#     return timestamp
#
#
# def convert_proto_to_model(proto_obj: Any) -> Any:
#     """
#     将Proto对象转换为Model对象
#
#     Args:
#         proto_obj: Proto对象
#
#     Returns:
#         Model对象
#     """
#     # 动态导入，避免循环导入
#     from ..rpc.gen import file_service_pb2 as file_hub_pb2
#
#     if isinstance(proto_obj, file_hub_pb2.FileInfo):
#         return File(
#             id=proto_obj.id,
#             #name=proto_obj.name,
#             folder_id=proto_obj.folder_id or None,
#             #type=ModelFileType.TRADITIONAL if proto_obj.type == file_hub_pb2.FILE_TYPE_TRADITIONAL else ModelFileType.CUSTOM,
#             #size=proto_obj.size,
#             mime_type=proto_obj.mime_type or None,
#             created_at=timestamp_to_datetime(proto_obj.created_at),
#             updated_at=timestamp_to_datetime(proto_obj.updated_at),
#             #metadata=dict(proto_obj.metadata),
#             #storage_path=proto_obj.storage_path or None,
#         )
#
#     elif isinstance(proto_obj, file_hub_pb2.FolderInfo):
#         return FolderInfo(
#             id=proto_obj.id,
#             folder_name=proto_obj.name,
#             parent_id=proto_obj.parent_id or None,
#             created_at=timestamp_to_datetime(proto_obj.created_at),
#             updated_at=timestamp_to_datetime(proto_obj.updated_at),
#             #metadata=dict(proto_obj.metadata),
#         )
#
#     else:
#         raise ValueError(f"不支持的Proto类型: {type(proto_obj)}")
#
#
# def convert_model_to_proto(model_obj: Any) -> Any:
#     """
#     将Model对象转换为Proto对象
#
#     Args:
#         model_obj: Model对象
#
#     Returns:
#         Proto对象
#     """
#     # 动态导入，避免循环导入
#     from ..rpc.gen import file_service_pb2 as file_hub_pb2
#
#     if isinstance(model_obj, File):
#         proto_type = (
#             file_hub_pb2.FILE_TYPE_TRADITIONAL
#             if model_obj.type == ModelFileType.TRADITIONAL
#             else file_hub_pb2.FILE_TYPE_CUSTOM
#         )
#
#         return file_hub_pb2.FileInfo(
#             id=model_obj.id,
#             name=model_obj.name,
#             folder_id=model_obj.folder_id or "",
#             type=proto_type,
#             size=model_obj.size,
#             mime_type=model_obj.mime_type or "",
#             created_at=datetime_to_timestamp(model_obj.created_at),
#             updated_at=datetime_to_timestamp(model_obj.updated_at),
#             metadata=model_obj.metadata,
#             storage_path=model_obj.storage_path or "",
#         )
#
#     elif isinstance(model_obj, FolderInfo):
#         return file_hub_pb2.FolderInfo(
#             id=model_obj.id,
#             name=model_obj.name,
#             parent_id=model_obj.parent_id or "",
#             created_at=datetime_to_timestamp(model_obj.created_at),
#             updated_at=datetime_to_timestamp(model_obj.updated_at),
#             metadata=model_obj.metadata,
#         )
#
#     else:
#         raise ValueError(f"不支持的Model类型: {type(model_obj)}")