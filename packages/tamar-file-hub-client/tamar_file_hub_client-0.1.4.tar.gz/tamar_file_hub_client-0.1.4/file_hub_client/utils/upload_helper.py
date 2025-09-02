"""
上传助手模块

提供HTTP上传、断点续传、进度监控等功能
"""
import os
import time
import asyncio
import aiohttp
import requests
from pathlib import Path
from typing import Union, BinaryIO, Optional, Callable, Dict, Any, AsyncGenerator
from dataclasses import dataclass
import hashlib


@dataclass
class UploadProgress:
    """上传进度信息"""
    total_size: int
    uploaded_size: int
    percentage: float
    speed: float  # bytes per second
    remaining_time: float  # seconds

    @property
    def is_completed(self) -> bool:
        return self.uploaded_size >= self.total_size


class HttpUploader:
    """HTTP上传器，支持同步上传"""

    def __init__(self, chunk_size: int = 1024 * 1024 * 5, total_retries: int = 3, retry_delay_seconds: int = 5):
        self.chunk_size = chunk_size  # 默认5MB分片
        self.total_retries = total_retries
        self.retry_delay_seconds = retry_delay_seconds

    def start_resumable_session(self, url: str, total_file_size: Optional[int] = None,
                                mine_type: Optional[str] = None) -> str:
        """
        启动 GCS 的断点续传会话，返回 session URI。

        Args:
            url (str): GCS 预签名上传初始化 URL。
            total_file_size (Optional[int]): 文件总大小（可选）。
             mine_type (Optional[str]): 文件 Content-Type。
        Returns:
            str: GCS 返回的会话 URI。
        """
        content_range_header = f"bytes */{total_file_size}" if total_file_size is not None else "bytes */*"
        headers = {"Content-Range": content_range_header, "x-goog-resumable": "start"}
        if mine_type is not None:
            headers["Content-Type"] = mine_type

        response = self._request("POST", url, headers=headers)
        if response.status_code in [200, 201]:
            session_uri = response.headers.get("Location")
            if session_uri:
                print(f"成功获取断点续传 URI: {session_uri}")
                return session_uri

        raise Exception(f"Failed to start resumable session: {response.status_code} - {response.text}")

    def check_uploaded_size(self, url: str, total_file_size: Optional[int] = None,
                            mine_type: Optional[str] = None) -> int:
        """
        查询 GCS 可恢复上传的当前进度（已上传的字节数）。

        Args:
            url (str): GCS 可恢复上传的会话 URI。
            total_file_size (Optional[int]): 文件的总大小（可选）。
                                             如果已知，提供此参数可以帮助 GCS 进行更精确的判断。
                                             如果 GCS 响应 200 OK，且提供了此参数，则直接返回此值。
            mine_type (Optional[str]): 文件 Content-Type。
         Returns:
            int: 已上传的字节数。
                - 如果上传已完成 (200 OK)，返回 total_file_size。如果 total_file_size 未知，则返回 0（表示需要服务器端后续验证）。
                - 如果上传仍在进行 (308 Resume Incomplete)，返回已上传的字节数。
                - 如果查询失败或会话无效，返回 0（表示从头开始或会话已失效）。
        """
        # 构建 Content-Range 头。如果知道总大小，提供它更准确。
        content_range_header = f"bytes */{total_file_size}" if total_file_size is not None else "bytes */*"
        headers = {"Content-Range": content_range_header}
        if mine_type is not None:
            headers["Content-Type"] = mine_type

        # 执行查询
        response = self._request("PUT", url, headers=headers)
        if response.status_code == 200:
            # GCS 响应 200 OK 表示整个文件已经完整上传。
            # 此时，如果知道文件总大小，可以直接返回它。
            # 如果不知道，通过 headers 获取文件大小，通常为 'x-goog-stored-content-length'
            if total_file_size:
                print(f"查询当前已上传文件大小：{total_file_size} bytes")
                return total_file_size
            else:
                content_length = response.headers.get("x-goog-stored-content-length")
                print(f"查询当前已上传文件大小：{content_length} bytes")
                if content_length:
                    return int(content_length)
        elif response.status_code == 308:
            # GCS 响应 308 Resume Incomplete，表示部分上传成功。
            content_length = response.headers.get("Content-Length")
            print(f"查询当前已上传文件大小：{content_length} bytes")
            if content_length is not None:
                return int(content_length)
            else:
                # 理论上 308 响应应该有 Content-Length 头，但作为健壮性处理
                print(f"查询当前已上传文件大小：0 bytes")
                return 0  # 没有 Content-Length 头，从头开始

        raise Exception(f"Failed to check uploaded size: {response.status_code} - {response.text}")

    def upload(
            self,
            url: str,
            content: Optional[Union[bytes, BinaryIO, Path]] = None,
            headers: Optional[Dict[str, str]] = None,
            progress_callback: Optional[Callable[[UploadProgress], None]] = None,
            total_size: Optional[int] = None,
            is_resume: bool = False,
    ) -> requests.Response:
        """
        上传文件到指定URL
        
        Args:
            url: 上传URL
            content: 文件内容
            method: HTTP方法
            headers: 请求头
            progress_callback: 进度回调函数
            is_resume: 是否断点续传
        """
        headers = headers or {}

        # 获取文件大小（不生成 chunk，避免提前读取）
        final_total_size = self._calculate_total_size(content) if total_size is None else total_size

        # 若断点续传，查询 resume_from 位置
        if is_resume:
            resume_from = self.check_uploaded_size(url, final_total_size, mine_type=headers.get("Content-Type"))
        else:
            resume_from = 0

        # 生成从 resume_from 开始的 chunk
        chunks = self._generate_chunks(content, resume_from)

        # 如果是断点续传，设置Range头
        if is_resume:
            headers['Content-Range'] = f'bytes {resume_from}-{final_total_size - 1}/{final_total_size}'

        return self._request(
            method="PUT",
            url=url,
            headers=headers,
            data=self._wrap_chunks_with_progress(chunks, final_total_size, resume_from, time.time(), progress_callback)
        )

    def _request(
            self,
            method: str,
            url: str,
            headers: Optional[Dict[str, str]] = None,
            data: Optional[Union[bytes, BinaryIO, any]] = None
    ) -> requests.Response:
        """通用请求方法，带重试机制"""
        for attempt in range(self.total_retries):
            try:
                response = requests.request(method=method, url=url, headers=headers, data=data, timeout=None)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if attempt < self.total_retries - 1:
                    print(f"[{attempt + 1}/{self.total_retries}] 请求失败，{self.retry_delay_seconds}s 后重试: {e}")
                    time.sleep(self.retry_delay_seconds)
                else:
                    print(f"[{self.total_retries}] 最后一次重试失败: {e}")
                    raise e

    def _calculate_total_size(self, content: Union[bytes, Path, BinaryIO]) -> int:
        if isinstance(content, bytes):
            return len(content)
        elif isinstance(content, Path):
            if not content.exists():
                raise FileNotFoundError(f"File not found: {content}")
            return content.stat().st_size
        elif hasattr(content, 'seek') and hasattr(content, 'tell'):
            current = content.tell()
            content.seek(0, 2)
            size = content.tell()
            content.seek(current)
            return size
        else:
            raise ValueError("Unsupported content type")

    def _bytes_to_chunks(self, data: bytes, start: int = 0):
        """将字节数据转换为分块"""
        for i in range(start, len(data), self.chunk_size):
            yield data[i:i + self.chunk_size]

    def _file_to_chunks(self, file_path: Path, start: int = 0):
        """将文件转换为分块"""
        with open(file_path, 'rb') as f:
            f.seek(start)
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break
                yield chunk

    def _stream_to_chunks(self, stream: BinaryIO):
        """将流转换为分块"""
        while True:
            chunk = stream.read(self.chunk_size)
            if not chunk:
                break
            yield chunk

    def _generate_chunks(self, content: Union[bytes, Path, BinaryIO], start: int):
        if isinstance(content, bytes):
            return self._bytes_to_chunks(content, start)
        elif isinstance(content, Path):
            return self._file_to_chunks(content, start)
        elif hasattr(content, 'seek') and hasattr(content, 'read'):
            content.seek(start)
            return self._stream_to_chunks(content)
        else:
            raise ValueError("Unsupported content type")

    def _wrap_chunks_with_progress(self, chunks, total_size, uploaded_size, start_time, callback):
        """包装分块迭代器，添加进度回调"""
        for chunk in chunks:
            yield chunk
            uploaded_size += len(chunk)

            if callback:
                elapsed = time.time() - start_time
                speed = uploaded_size / elapsed if elapsed > 0 else 0
                remaining = (total_size - uploaded_size) / speed if speed > 0 else 0

                progress = UploadProgress(
                    total_size=total_size,
                    uploaded_size=uploaded_size,
                    percentage=uploaded_size / total_size * 100,
                    speed=speed,
                    remaining_time=remaining
                )
                callback(progress)


class AsyncHttpUploader:
    """异步HTTP上传器"""

    def __init__(self, chunk_size: int = 1024 * 1024 * 5, total_retries: int = 3, retry_delay_seconds: int = 5):
        self.chunk_size = chunk_size  # 默认5MB分片
        self.total_retries = total_retries
        self.retry_delay_seconds = retry_delay_seconds

    async def start_resumable_session(self, url: str, total_file_size: Optional[int] = None,
                                      mine_type: Optional[str] = None) -> str:
        """
        启动 GCS 的断点续传会话，返回 session URI。

        Args:
            url (str): GCS 预签名上传初始化 URL。
            total_file_size (Optional[int]): 文件总大小（可选）。
            mine_type (Optional[str]): 文件 Content-Type。
        Returns:
            str: GCS 返回的会话 URI。
        """
        content_range_header = f"bytes */{total_file_size}" if total_file_size is not None else "bytes */*"
        headers = {"Content-Range": content_range_header, "x-goog-resumable": "start"}
        if mine_type is not None:
            headers["Content-Type"] = mine_type

        response = await self._request("POST", url, headers=headers)
        if response.status in [200, 201]:
            session_uri = response.headers.get("Location")
            if session_uri:
                print(f"成功获取断点续传 URI: {session_uri}")
                return session_uri

        text = await response.text()
        raise Exception(f"Failed to start resumable session: {response.status} - {text}")

    async def check_uploaded_size(self, url: str, total_file_size: Optional[int] = None,
                            mine_type: Optional[str] = None) -> int:
        """
        查询 GCS 可恢复上传的当前进度（已上传的字节数）。

        Args:
            url (str): GCS 可恢复上传的会话 URI。
            total_file_size (Optional[int]): 文件的总大小（可选）。
                                              如果已知，提供此参数可以帮助 GCS 进行更精确的判断。
                                              如果 GCS 响应 200 OK，且提供了此参数，则直接返回此值。
            mine_type (Optional[str]): 文件 Content-Type。
        Returns:
            int: 已上传的字节数。
                 - 如果上传已完成 (200 OK)，返回 total_file_size。如果 total_file_size 未知，则返回 0（表示需要服务器端后续验证）。
                 - 如果上传仍在进行 (308 Resume Incomplete)，返回已上传的字节数。
                 - 如果查询失败或会话无效，返回 0（表示从头开始或会话已失效）。
        """
        # 构建 Content-Range 头。如果知道总大小，提供它更准确。
        content_range_header = f"bytes */{total_file_size}" if total_file_size is not None else "bytes */*"
        headers = {"Content-Range": content_range_header}
        if mine_type is not None:
            headers["Content-Type"] = mine_type

        # 发送一个空的 PUT 请求来查询已上传字节数
        # timeout 应该根据网络情况和预期响应时间设置
        response = await self._request("PUT", url, headers=headers)

        if response.status == 200:
            # GCS 响应 200 OK 表示整个文件已经完整上传。
            # 此时，如果知道文件总大小，可以直接返回它。
            # 如果不知道，通过 headers 获取文件大小，通常为 'x-goog-stored-content-length'
            if total_file_size:
                print(f"查询当前已上传文件大小：{total_file_size} bytes")
                return total_file_size
            else:
                content_length = response.headers.get("x-goog-stored-content-length")
                print(f"查询当前已上传文件大小：{content_length} bytes")
                if content_length:
                    return int(content_length)

        elif response.status == 308:
            # GCS 响应 308 Resume Incomplete，表示部分上传成功。
            content_length = response.headers.get("Content-Length")
            print(f"查询当前已上传文件大小：{content_length} bytes")
            if content_length is not None:
                return int(content_length)
            else:
                # 理论上 308 响应应该有 Content-Length 头，但作为健壮性处理
                print("查询当前已上传文件大小：0 bytes")
                return 0  # 没有 Content-Length 头，从头开始

        text = await response.text()
        raise Exception(f"Failed to check uploaded size: {response.status} - {text}")

    async def upload(
            self,
            url: str,
            content: Union[bytes, BinaryIO, Path],
            headers: Optional[Dict[str, str]] = None,
            progress_callback: Optional[Callable[[UploadProgress], None]] = None,
            total_size: Optional[int] = None,
            is_resume: bool = False,
    ) -> aiohttp.ClientResponse:
        """
        异步上传文件到指定URL
        
        Args:
            url: 上传URL
            content: 文件内容
            headers: 请求头
            progress_callback: 进度回调函数
            is_resume: 是否断点续传
        """
        headers = headers or {}

        # 获取文件大小（避免读取内容）
        final_total_size = total_size or await self._calculate_total_size(content)

        # 如果是断点续传，查询服务端 resume_from
        if is_resume:
            resume_from = await self.check_uploaded_size(url, final_total_size, mine_type=headers.get("Content-Type"))
        else:
            resume_from = 0

        # 生成 chunk 流（从 resume_from 开始）
        chunks = await self._generate_chunks(content, resume_from)

        #  设置断点续传头
        if is_resume:
            headers["Content-Range"] = f"bytes {resume_from}-{final_total_size - 1}/{final_total_size}"

        # 包装成带进度的流
        wrapped_chunks = self._wrap_chunks_with_progress(
            chunks, final_total_size, resume_from, time.time(), progress_callback
        )

        # 发起异步请求上传
        return await self._request(
            method="PUT",
            url=url,
            headers=headers,
            data=wrapped_chunks,
        )

    async def _request(
            self,
            method: str,
            url: str,
            headers: Optional[Dict[str, str]] = None,
            data: Optional[Union[bytes, str, asyncio.StreamReader, any]] = None,
    ) -> aiohttp.ClientResponse:
        """
        通用异步请求方法，带自动重试机制。

        Args:
            method (str): 请求方法，如 "POST", "PUT"
            url (str): 请求地址
            headers (dict): 请求头
            data: 请求体

        Returns:
            aiohttp.ClientResponse: 最终成功的响应对象（注意：需由调用方处理 resp.text() / resp.json()）
        """
        headers = headers or {}

        for attempt in range(self.total_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.request(method, url, headers=headers, data=data) as resp:
                        if resp.status < 400:
                            return resp
                        text = await resp.text()
                        raise RuntimeError(f"HTTP {resp.status}: {text}")
            except Exception as e:
                if attempt < self.total_retries - 1:
                    await asyncio.sleep(self.retry_delay_seconds)
                else:
                    raise RuntimeError(f"Request failed after {self.total_retries} attempts: {e}")

    async def _calculate_total_size(self, content: Union[bytes, Path, BinaryIO]) -> int:
        if isinstance(content, bytes):
            return len(content)
        elif isinstance(content, Path):
            return (await aiofiles.os.stat(str(content))).st_size
        elif hasattr(content, "seek") and hasattr(content, "tell"):
            current = content.tell()
            content.seek(0, 2)
            size = content.tell()
            content.seek(current)
            return size
        else:
            raise ValueError("Unsupported content type")

    async def _generate_chunks(self, content: Union[bytes, Path, BinaryIO], start: int) -> AsyncGenerator[bytes, None]:
        if isinstance(content, bytes):
            return self._bytes_to_chunks(content, start)
        elif isinstance(content, Path):
            return self._file_to_chunks_async(content, start)
        elif hasattr(content, "seek") and hasattr(content, "read"):
            await asyncio.get_event_loop().run_in_executor(None, content.seek, start)
            return self._stream_to_chunks(content)
        else:
            raise ValueError("Unsupported content type")

    async def _bytes_to_chunks(self, data: bytes, start: int = 0):
        for i in range(start, len(data), self.chunk_size):
            yield data[i:i + self.chunk_size]

    async def _file_to_chunks_async(self, file_path: Path, start: int = 0):
        async with aiofiles.open(file_path, 'rb') as f:
            await f.seek(start)
            while True:
                chunk = await f.read(self.chunk_size)
                if not chunk:
                    break
                yield chunk

    async def _stream_to_chunks(self, stream: BinaryIO):
        loop = asyncio.get_event_loop()
        while True:
            # 使用线程方式读取同步流内容
            chunk = await loop.run_in_executor(None, stream.read, self.chunk_size)
            if not chunk:
                break
            yield chunk

    async def _wrap_chunks_with_progress(
            self,
            chunks,
            total_size: int,
            uploaded_size: int,
            start_time: float,
            callback: Optional[Callable[[UploadProgress], None]] = None,
    ):
        async for chunk in chunks:
            yield chunk
            uploaded_size += len(chunk)

            if callback:
                elapsed = asyncio.get_event_loop().time() - start_time
                speed = uploaded_size / elapsed if elapsed > 0 else 0
                remaining = (total_size - uploaded_size) / speed if speed > 0 else 0
                progress = UploadProgress(
                    total_size=total_size,
                    uploaded_size=uploaded_size,
                    percentage=uploaded_size / total_size * 100,
                    speed=speed,
                    remaining_time=remaining
                )
                if asyncio.iscoroutinefunction(callback):
                    await callback(progress)
                else:
                    callback(progress)


def calculate_file_md5(content: Union[bytes, BinaryIO, Path], chunk_size: int = 8192) -> str:
    """计算文件MD5值"""
    md5 = hashlib.md5()

    if isinstance(content, bytes):
        md5.update(content)
    elif isinstance(content, Path):
        with open(content, 'rb') as f:
            while chunk := f.read(chunk_size):
                md5.update(chunk)
    else:
        # 文件对象
        pos = content.tell()
        content.seek(0)
        while chunk := content.read(chunk_size):
            md5.update(chunk)
        content.seek(pos)

    return md5.hexdigest()


# 尝试导入aiofiles（可选依赖）
try:
    import aiofiles
except ImportError:
    aiofiles = None
