"""
下载助手模块

提供HTTP下载、流式下载、进度监控等功能
"""
import time
import asyncio
from urllib.parse import urlparse

import aiohttp
import requests
from pathlib import Path
from typing import Union, Optional, Callable
from dataclasses import dataclass


@dataclass
class DownloadProgress:
    """下载进度信息"""
    total_size: int
    downloaded_size: int
    percentage: float
    speed: float  # bytes per second
    remaining_time: float  # seconds

    @property
    def is_completed(self) -> bool:
        return self.downloaded_size >= self.total_size if self.total_size > 0 else False


class HttpDownloader:
    """HTTP下载器，支持同步下载"""

    def __init__(self, chunk_size: int = 1024 * 1024, total_retries: int = 3, retry_delay_seconds: int = 5):  # 默认1MB分片
        self.chunk_size = chunk_size
        self.total_retries = total_retries
        self.retry_delay_seconds = retry_delay_seconds

    def download(
            self,
            url: str,
            save_path: Optional[Union[str, Path]] = None,
            chunk_size: Optional[int] = None,
            headers: Optional[dict] = None,
            progress_callback: Optional[Callable[[DownloadProgress], None]] = None,
            timeout: Optional[int] = None
    ) -> Union[bytes, Path]:
        """
        从URL下载文件
        
        Args:
            url: 下载URL
            save_path: 保存路径（如果为None，返回字节数据）
            chunk_size: 分块大小
            headers: 请求头
            progress_callback: 进度回调函数
            timeout: 超时时间（秒）
            
        Returns:
            下载的内容（字节）或保存的文件路径
        """
        headers = headers or {}
        chunk_size = chunk_size or self.chunk_size
        save_path = Path(save_path) if save_path else None

        # 校验扩展名一致性（若提供）
        parsed_url = urlparse(url)
        url_suffix = Path(parsed_url.path).suffix.lower()
        if save_path and save_path.suffix and save_path.suffix.lower() != url_suffix:
            raise ValueError(
                f"File extension mismatch: download_url ends with '{url_suffix}', but save_path ends with '{save_path.suffix.lower()}'")

        for attempt in range(self.total_retries):
            try:
                resume_from = 0
                if save_path:
                    temp_path = save_path.with_suffix(save_path.suffix + ".part")
                    if temp_path.exists():
                        resume_from = temp_path.stat().st_size
                        headers["Range"] = f"bytes={resume_from}-"

                # 发送请求
                response = requests.get(url, headers=headers, stream=True, timeout=timeout)
                response.raise_for_status()

                content_length = int(response.headers.get('content-length', 0))
                total_size = content_length + resume_from if save_path else content_length

                if save_path is None:
                    return self._download_to_memory(response, total_size, chunk_size, progress_callback, resume_from)
                else:
                    return self._download_to_file(response, save_path, total_size, chunk_size, progress_callback,
                                                  resume_from)
            except Exception as e:
                if attempt == self.total_retries - 1:
                    raise
                time.sleep(self.retry_delay_seconds)

    def _download_to_memory(
            self,
            response: requests.Response,
            total_size: int,
            chunk_size: int,
            progress_callback: Optional[Callable[[DownloadProgress], None]],
            resume_from: int = 0
    ) -> bytes:
        """下载到内存"""
        chunks = []
        downloaded_size = resume_from
        start_time = time.time()

        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                chunks.append(chunk)
                downloaded_size += len(chunk)

                if progress_callback:
                    self._report_progress(
                        downloaded_size, total_size, start_time, progress_callback
                    )

        return b''.join(chunks)

    def _download_to_file(
            self,
            response: requests.Response,
            save_path: Path,
            total_size: int,
            chunk_size: int,
            progress_callback: Optional[Callable[[DownloadProgress], None]],
            resume_from: int = 0
    ) -> Path:
        """下载到文件"""
        # 创建目录
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # 临时保存为 .part 文件
        temp_path = save_path.with_suffix(save_path.suffix + ".part")

        downloaded_size = resume_from
        start_time = time.time()

        mode = 'ab' if resume_from > 0 else 'wb'

        with open(temp_path, mode) as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    if progress_callback:
                        self._report_progress(downloaded_size, total_size, start_time, progress_callback)

        if save_path.exists():
            save_path.unlink()
        temp_path.rename(save_path)
        return save_path

    def _report_progress(
            self,
            downloaded_size: int,
            total_size: int,
            start_time: float,
            callback: Callable[[DownloadProgress], None]
    ):
        """报告下载进度"""
        elapsed = time.time() - start_time
        speed = downloaded_size / elapsed if elapsed > 0 else 0
        percentage = (downloaded_size / total_size * 100) if total_size > 0 else 0
        remaining = (total_size - downloaded_size) / speed if speed > 0 else 0

        progress = DownloadProgress(
            total_size=total_size,
            downloaded_size=downloaded_size,
            percentage=percentage,
            speed=speed,
            remaining_time=remaining
        )
        callback(progress)


class AsyncHttpDownloader:
    """异步HTTP下载器"""

    def __init__(self, chunk_size: int = 1024 * 1024, total_retries: int = 3, retry_delay_seconds: int = 5):  # 默认1MB分片
        self.chunk_size = chunk_size
        self.total_retries = total_retries
        self.retry_delay_seconds = retry_delay_seconds

    async def download(
            self,
            url: str,
            save_path: Optional[Union[str, Path]] = None,
            chunk_size: Optional[int] = None,
            headers: Optional[dict] = None,
            progress_callback: Optional[Callable[[DownloadProgress], None]] = None,
            timeout: Optional[int] = None
    ) -> Union[bytes, Path]:
        """
        异步从URL下载文件
        
        Args:
            url: 下载URL
            save_path: 保存路径（如果为None，返回字节数据）
            chunk_size: 分块大小
            headers: 请求头
            progress_callback: 进度回调函数
            timeout: 超时时间（秒）
            
        Returns:
            下载的内容（字节）或保存的文件路径
        """
        headers = headers or {}
        save_path = Path(save_path) if save_path else None
        chunk_size = chunk_size or self.chunk_size

        # 校验扩展名一致性（若提供）
        parsed_url = urlparse(url)
        url_suffix = Path(parsed_url.path).suffix.lower()
        if save_path and save_path.suffix and save_path.suffix.lower() != url_suffix:
            raise ValueError(
                f"File extension mismatch: download_url ends with '{url_suffix}', but save_path ends with '{save_path.suffix.lower()}'")

        for attempt in range(self.total_retries):
            try:
                resume_from = 0
                if save_path:
                    temp_path = save_path.with_suffix(save_path.suffix + ".part")
                    if temp_path.exists():
                        resume_from = temp_path.stat().st_size
                        headers["Range"] = f"bytes={resume_from}-"

                timeout_config = aiohttp.ClientTimeout(total=timeout) if timeout else None

                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers, timeout=timeout_config) as response:
                        if response.status not in (200, 206):
                            raise Exception(f"Unexpected status: {response.status}")

                        total_size = int(response.headers.get("content-length", 0)) + resume_from

                        if save_path is None:
                            return await self._download_to_memory(response, total_size, chunk_size, progress_callback,
                                                                  resume_from)
                        else:
                            return await self._download_to_file(response, save_path, total_size, chunk_size,
                                                                progress_callback, resume_from)
            except Exception as e:
                if attempt == self.total_retries - 1:
                    raise
                await asyncio.sleep(self.retry_delay_seconds)

    async def _download_to_memory(
            self,
            response: aiohttp.ClientResponse,
            total_size: int,
            chunk_size: Optional[int],
            progress_callback: Optional[Callable[[DownloadProgress], None]],
            resume_from: int = 0
    ) -> bytes:
        """异步下载到内存"""
        chunks = []
        downloaded_size = resume_from
        start_time = asyncio.get_event_loop().time()

        async for chunk in response.content.iter_chunked(chunk_size):
            chunks.append(chunk)
            downloaded_size += len(chunk)

            if progress_callback:
                await self._report_progress(
                    downloaded_size, total_size, start_time, progress_callback
                )

        return b''.join(chunks)

    async def _download_to_file(
            self,
            response: aiohttp.ClientResponse,
            save_path: Path,
            total_size: int,
            chunk_size: Optional[int],
            progress_callback: Optional[Callable[[DownloadProgress], None]],
            resume_from: int = 0
    ) -> Path:
        """异步下载到文件"""
        # 创建目录
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # 临时保存为 .part 文件
        temp_path = save_path.with_suffix(save_path.suffix + ".part")

        downloaded_size = 0
        start_time = time.time()

        mode = 'ab' if resume_from > 0 else 'wb'

        if aiofiles:
            # 使用异步文件IO
            async with aiofiles.open(temp_path, mode) as f:
                async for chunk in response.content.iter_chunked(chunk_size):
                    await f.write(chunk)
                    downloaded_size += len(chunk)

                    if progress_callback:
                        await self._report_progress(
                            downloaded_size, total_size, start_time, progress_callback
                        )
        else:
            # 回退到同步文件IO
            with open(temp_path, mode) as f:
                async for chunk in response.content.iter_chunked(chunk_size):
                    f.write(chunk)
                    downloaded_size += len(chunk)

                    if progress_callback:
                        await self._report_progress(
                            downloaded_size, total_size, start_time, progress_callback
                        )
        if save_path.exists():
            save_path.unlink()
        temp_path.rename(save_path)
        return save_path

    async def _report_progress(
            self,
            downloaded_size: int,
            total_size: int,
            start_time: float,
            callback: Callable[[DownloadProgress], None]
    ):
        """报告下载进度"""
        elapsed = asyncio.get_event_loop().time() - start_time
        speed = downloaded_size / elapsed if elapsed > 0 else 0
        percentage = (downloaded_size / total_size * 100) if total_size > 0 else 0
        remaining = (total_size - downloaded_size) / speed if speed > 0 else 0

        progress = DownloadProgress(
            total_size=total_size,
            downloaded_size=downloaded_size,
            percentage=percentage,
            speed=speed,
            remaining_time=remaining
        )

        if asyncio.iscoroutinefunction(callback):
            await callback(progress)
        else:
            callback(progress)


# 尝试导入aiofiles（可选依赖）
try:
    import aiofiles
except ImportError:
    aiofiles = None
