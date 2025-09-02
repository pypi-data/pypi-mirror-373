import hashlib
from pathlib import Path
from typing import Optional, Union, BinaryIO, Tuple, Any

from ...schemas import File, UploadFile
from ...utils.file_utils import get_file_mime_type
from ...errors import ValidationError, FileNotFoundError


class BaseFileService:
    """
    文件服务核心逻辑，提供与上传/下载无关的通用工具方法。
    """

    def _extract_file_info(
            self,
            file: Union[str, Path, BinaryIO, bytes]
    ) -> Tuple[Optional[str], bytes, int, str, str, str]:
        """
        提取文件信息并返回统一的 bytes 内容与 SHA256 哈希

        Returns:
            (文件名, 内容（bytes）, 文件大小, MIME类型, 文件扩展名, 文件hash)
        """

        def get_file_type_and_mime(file_path: Path) -> Tuple[str, str]:
            # 获取文件扩展名，如果没有扩展名则默认为 'dat'
            file_ext = file_path.suffix.lstrip('.').lower() if file_path.suffix else 'dat'
            return (
                file_ext,
                get_file_mime_type(file_path)
            )

        def calculate_sha256_and_bytes(f: BinaryIO) -> Tuple[bytes, str]:
            sha256 = hashlib.sha256()
            content = bytearray()
            while chunk := f.read(4 * 1024 * 1024):
                content.extend(chunk)
                sha256.update(chunk)
            f.seek(0)  # 复位以防止外部再用
            return bytes(content), sha256.hexdigest()

        # Case 1: 文件路径
        if isinstance(file, (str, Path)):
            file_path = Path(file)
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            file_name = file_path.name
            file_type, mime_type = get_file_type_and_mime(file_path)
            with file_path.open("rb") as f:
                content, file_hash = calculate_sha256_and_bytes(f)
            file_size = len(content)
            return file_name, content, file_size, mime_type, file_type, file_hash

        # Case 2: 原始字节流
        elif isinstance(file, bytes):
            sha256 = hashlib.sha256(file).hexdigest()
            # 为字节流生成默认文件名
            file_name = f"upload_{sha256[:8]}.dat"
            return file_name, file, len(file), "application/octet-stream", 'dat', sha256

        # Case 3: 可读文件对象
        elif hasattr(file, 'read'):
            file_name = getattr(file, 'name', None)
            
            if hasattr(file, 'seek'):
                file.seek(0)
            content, file_hash = calculate_sha256_and_bytes(file)
            file_size = len(content)
            
            # 如果没有文件名，生成一个默认的
            if not file_name:
                file_name = f"upload_{file_hash[:8]}.dat"
                file_type = 'dat'
                mime_type = "application/octet-stream"
            else:
                file_type = Path(file_name).suffix.lstrip('.').lower()
                mime_type = get_file_mime_type(Path(file_name))
                file_name = Path(file_name).name
            
            return file_name, content, file_size, mime_type, file_type, file_hash

        else:
            raise ValidationError(f"不支持的文件类型: {type(file)}")

    def _convert_file_info(self, proto_file: Any) -> File:
        """转换Proto文件信息为模型"""
        from ...utils.converter import timestamp_to_datetime

        return File(
            id=proto_file.id,
            folder_id=proto_file.folder_id,
            file_name=proto_file.file_name,
            file_type=proto_file.file_type,
            created_at=timestamp_to_datetime(proto_file.created_at),
            updated_at=timestamp_to_datetime(proto_file.updated_at)
        )

    def _convert_upload_file_info(self, proto_upload_file: Any) -> UploadFile:
        """转换Proto文件信息为模型"""
        from ...utils.converter import timestamp_to_datetime

        return UploadFile(
            id=proto_upload_file.id,
            folder_id=proto_upload_file.folder_id,
            storage_type=proto_upload_file.storage_type,
            stored_name=proto_upload_file.stored_name,
            stored_path=proto_upload_file.stored_path,
            file_id=proto_upload_file.file_id,
            file_name=proto_upload_file.file_name,
            file_size=proto_upload_file.file_size,
            file_ext=proto_upload_file.file_ext,
            mime_type=proto_upload_file.mime_type,
            created_at=timestamp_to_datetime(proto_upload_file.created_at),
            updated_at=timestamp_to_datetime(proto_upload_file.updated_at)
        )
