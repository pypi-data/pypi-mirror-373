import asyncio
import logging
import mimetypes
import os
import re
from typing import Optional, Dict
from urllib.parse import unquote, urlparse, quote
from aiohttp import (
    web,
    TCPConnector,
    ClientSession,
    ClientTimeout,
    ClientError,
)
from . import constants
from .utils import SafeMemory, get_base_url

logger = logging.getLogger("Mflow")


class LinkInfo:
    """存储和管理远程链接信息的类"""

    def __init__(self, url: str, headers: Optional[Dict[str, str]] = None):
        self.original_url: str = url  # 原始URL
        self.redirect_url: str = url  # 重定向后的URL
        # 如果未提供自定义请求头, 则使用默认的User-Agent
        self.headers: Dict[str, str] = headers or {"User-Agent": constants.USER_AGENT}
        self.support_range: bool = False  # 是否支持范围请求
        self.filesize: Optional[int] = None  # 文件大小
        self.filename: Optional[str] = None  # 文件名
        self.minetype: str = "application/octet-stream"  # MIME类型
        self.clients_queue: asyncio.Queue = asyncio.Queue()  # aiohttp客户端队列
        self.cache: SafeMemory = SafeMemory()  # 内存缓存
        logger.debug(f"LinkInfo for {url} initialized")

    def _create_client(self) -> ClientSession:
        """创建一个新的aiohttp客户端"""
        return ClientSession(
            connector=TCPConnector(limit=1, keepalive_timeout=600),
            timeout=ClientTimeout(total=constants.TIMEOUT),
            headers=self.headers,
            max_field_size=1<<16,  # 64KB
            max_line_size=1<<12,   # 4KB
        )

    async def init_clients(self, num_clients: int):
        """初始化指定数量的客户端到队列中"""
        # 清空现有队列
        while not self.clients_queue.empty():
            try:
                client = self.clients_queue.get_nowait()
                await client.close()
            except asyncio.QueueEmpty:
                break
        # 创建新客户端
        for _ in range(num_clients):
            self.clients_queue.put_nowait(self._create_client())

    async def close(self):
        """关闭所有客户端并清理资源"""
        logger.debug(f"Closing LinkInfo for {self.original_url}")
        while not self.clients_queue.empty():
            try:
                client = self.clients_queue.get_nowait()
                await client.close()
            except asyncio.QueueEmpty:
                break
        logger.debug(f"LinkInfo for {self.original_url} closed")

    async def get_client(self) -> ClientSession:
        """获取一个健康的客户端会话, 若取出的是已关闭的则自动替换"""
        client = await self.clients_queue.get()
        if getattr(client, 'closed', False):
            try:
                await client.close()
            except Exception:
                pass
            client = self._create_client()
        return client

    async def return_client(self, client: ClientSession):
        """归还客户端到队列, 若已关闭则替换为新的会话后再放回"""
        if getattr(client, 'closed', False):
            try:
                await client.close()
            except Exception:
                pass
            client = self._create_client()
        await self.clients_queue.put(client)


async def update_info(info: LinkInfo, request_id: str) -> Optional[web.Response]:
    """
    更新链接信息, 包括处理重定向、获取文件大小、文件名和类型。

    :param info: LinkInfo对象
    :param request_id: 请求ID, 用于日志记录
    :return: 如果发生错误, 返回aiohttp.Response错误对象, 否则返回None
    """
    sess = info._create_client()
    try:
        current_url = info.original_url
        try:
            logger.debug(
                f"[{request_id}] Checking resource info: {str(get_base_url(current_url))}"
            )
            # 1. 处理重定向
            resp = await sess.head(current_url, allow_redirects=False)
            depth = 0
            while resp.status in (301, 302, 303, 307, 308) and depth < constants.MAX_REDIRECTS:
                loc = resp.headers.get("Location")
                if not loc:
                    logger.warning(f"[{request_id}] Redirect without Location header")
                    return web.HTTPBadGateway(reason="Invalid redirect")
                current_url = loc
                resp = await sess.head(current_url, allow_redirects=False)
                depth += 1

            if info.redirect_url != current_url:
                info.redirect_url = current_url
                logger.info(
                    f"[{request_id}] Redirected to {str(get_base_url(current_url))}"
                )

            # 2. 检查是否支持范围请求并获取文件信息
            headers = {"Range": "bytes=0-"}
            async with sess.get(info.redirect_url, headers=headers) as r2:
                info.support_range = r2.status == 206 and "Content-Range" in r2.headers
                info.filesize = int(r2.headers.get("Content-Length", "0")) or None
                logger.info(
                    f"[{request_id}] Range support: {info.support_range}, Size: {info.filesize}"
                )

                # 3. 解析文件名
                cd = r2.headers.get("content-disposition", "")
                filename = None
                if cd:
                    # 优先解析 filename* (RFC 5987)
                    if m := re.search(
                        r"filename\*\s*=\s*(UTF-8|utf-8)?''?([^;]+)", cd, re.IGNORECASE
                    ):
                        filename = unquote(m.group(2))
                    # 其次解析 filename (RFC 2616)
                    elif m := re.search(r'filename\s*=\s*"([^"]+)"', cd, re.IGNORECASE):
                        filename = m.group(1)

                # 如果响应头中没有文件名, 则从URL路径中提取
                if not filename:
                    parsed = urlparse(info.redirect_url)
                    filename = unquote(parsed.path.rsplit("/", 1)[-1] or "download")

                # 4. 补充文件扩展名
                base, ext = os.path.splitext(filename)
                if not ext:
                    ct = r2.headers.get("content-type", "").split(";")[0].strip()
                    if guessed_ext := mimetypes.guess_extension(ct):
                        filename += guessed_ext

                # 5. 清理文件名中的非法字符
                filename = re.sub(r'[\x00<>:"/\\|?*]', "_", filename).strip()

                # 6. 更新MIME类型
                mime_type, _ = mimetypes.guess_type(filename)
                content_type_header = r2.headers.get("content-type", "application/octet-stream")
                if content_type_header != "application/octet-stream":
                    info.minetype = content_type_header
                elif mime_type:
                    info.minetype = mime_type

                info.filename = filename[:255]  # 限制文件名最大长度

                logger.info(f"[{request_id}] Filename resolved: {info.filename}")
            return None

        except ClientError as e:
            logger.warning(f"[{request_id}] ClientError during info update: {e}")
            return web.HTTPBadGateway(reason="Upstream error")
        except Exception as e:
            logger.error(f"[{request_id}] Unexpected error during info update: {e}", exc_info=True)
            return web.HTTPInternalServerError()
    finally:
        await sess.close()
