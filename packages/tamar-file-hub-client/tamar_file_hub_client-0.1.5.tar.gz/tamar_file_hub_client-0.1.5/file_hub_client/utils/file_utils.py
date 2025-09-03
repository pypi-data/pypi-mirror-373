"""
文件工具函数
"""
import hashlib
import mimetypes
from pathlib import Path
from typing import Generator, Optional, BinaryIO, Union


def get_file_mime_type(file_path: Union[str, Path]) -> str:
    """
    获取文件的MIME类型
    
    Args:
        file_path: 文件路径
        
    Returns:
        MIME类型
    """
    import json
    
    file_path = Path(file_path)
    
    # 定义常见文件扩展名到MIME类型的映射，确保跨平台一致性
    extension_mime_map = {
        '.csv': 'text/csv',
        '.txt': 'text/plain',
        '.json': 'application/json',
        '.xml': 'application/xml',
        '.html': 'text/html',
        '.htm': 'text/html',
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.ppt': 'application/vnd.ms-powerpoint',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.webp': 'image/webp',
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.mp4': 'video/mp4',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime',
        '.zip': 'application/zip',
        '.rar': 'application/vnd.rar',
        '.7z': 'application/x-7z-compressed',
        '.tar': 'application/x-tar',
        '.gz': 'application/gzip',
    }
    
    # 获取文件扩展名（转为小写）
    extension = file_path.suffix.lower()
    
    # 对于JSON文件，进行内容验证
    if extension == '.json':
        if file_path.exists():
            try:
                # 尝试不同的编码方式读取文件
                content = None
                for encoding in ['utf-8-sig', 'utf-8', 'latin-1']:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            content = f.read().strip()
                            break
                    except UnicodeDecodeError:
                        continue
                
                if content is None:
                    # 无法读取文件，返回text/plain
                    return 'text/plain'
                
                if not content:
                    # 空文件，按扩展名处理
                    return extension_mime_map[extension]
                
                # 尝试解析JSON
                json.loads(content)
                # 如果解析成功，确实是JSON格式
                return 'application/json'
            except (json.JSONDecodeError, OSError):
                # JSON解析失败或文件读取失败，可能是格式错误的JSON文件
                # 返回text/plain避免服务器端的类型不匹配错误
                return 'text/plain'
    
    # 优先使用自定义映射，确保常见文件类型的一致性
    if extension in extension_mime_map:
        return extension_mime_map[extension]
    
    # 如果自定义映射中没有，尝试使用magic进行内容检测
    try:
        import magic
        mime = magic.Magic(mime=True)
        return mime.from_file(str(file_path))
    except ImportError:
        # 如果magic不可用，使用mimetypes作为fallback
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type or "application/octet-stream"


def get_file_extension(file_name: str) -> str:
    """
    获取文件扩展名
    
    Args:
        file_name: 文件名
        
    Returns:
        文件扩展名（包含点号）
    """
    return Path(file_name).suffix.lower()


def humanize_file_size(size_bytes: int) -> str:
    """
    将文件大小转换为人类可读的格式
    
    Args:
        size_bytes: 文件大小（字节）
        
    Returns:
        人类可读的文件大小
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def calculate_file_hash(file_path: Union[str, Path], algorithm: str = "sha256") -> str:
    """
    计算文件哈希值
    
    Args:
        file_path: 文件路径
        algorithm: 哈希算法（md5, sha1, sha256等）
        
    Returns:
        文件哈希值（十六进制）
    """
    file_path = Path(file_path)
    hash_obj = hashlib.new(algorithm)

    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hash_obj.update(chunk)

    return hash_obj.hexdigest()


def split_file_chunks(
        file_obj: BinaryIO,
        chunk_size: int = 1024 * 1024,  # 默认1MB
        start_offset: int = 0
) -> Generator[tuple[bytes, int, bool], None, None]:
    """
    将文件分割成块
    
    Args:
        file_obj: 文件对象
        chunk_size: 块大小（字节）
        start_offset: 起始偏移量
        
    Yields:
        (块数据, 偏移量, 是否最后一块)
    """
    file_obj.seek(start_offset)
    offset = start_offset

    while True:
        chunk = file_obj.read(chunk_size)
        if not chunk:
            break

        is_last = len(chunk) < chunk_size
        yield chunk, offset, is_last

        offset += len(chunk)
        if is_last:
            break
