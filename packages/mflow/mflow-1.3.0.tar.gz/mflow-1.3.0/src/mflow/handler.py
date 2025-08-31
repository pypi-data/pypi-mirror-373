import asyncio
import logging
import random
from typing import Dict, Set, Optional
from urllib.parse import quote

from aiohttp import web, ClientError

from . import constants
from .exceptions import IncompleteChunkError, LowSpeedError, IncompleteResponseError
from .link_info import LinkInfo, update_info
from .utils import AsyncSafeStore, get_base_url, parse_range

logger = logging.getLogger("Mflow")


class MultiFlow:
    """多线程流处理器, 管理所有下载请求"""

    def __init__(self):
        self.link_cache: Dict[str, LinkInfo] = {}  # 缓存LinkInfo对象
        self.request_counter: int = 0  # 请求计数器
        logger.info("MultiFlow controller initialized")

    async def close(self):
        """关闭所有链接, 清理资源"""
        logger.info(f"Closing {len(self.link_cache)} link connections")
        tasks = [info.close() for info in self.link_cache.values()]
        await asyncio.gather(*tasks)
        self.link_cache.clear()
        logger.info("All link connections closed")

    async def handle_jsonrpc(self, request: web.Request) -> web.Response:
        """处理Aria2 JSON-RPC请求"""
        self.request_counter += 1
        request_id = f"{self.request_counter % 100:02d}"
        data = {}
        
        try:
            data = await request.json()
            rpc_id = data.get("id")
            
            if data.get("method") != "aria2.addUri":
                raise ValueError("Only 'aria2.addUri' method is supported")

            params = data.get("params", [])
            if len(params) < 2:
                raise ValueError("Invalid params for aria2.addUri")

            urls = params[1]
            if not isinstance(urls, list) or not urls:
                raise ValueError("URL list is missing or empty in params")
            url = urls[0]

            options = params[2] if len(params) > 2 else {}
            header_list = options.get("header", [])
            
            headers = {}
            for header_str in header_list:
                if ":" in header_str:
                    key, value = header_str.split(":", 1)
                    headers[key.strip()] = value.strip()
            
            if "User-Agent" not in headers:
                from .constants import USER_AGENT
                headers["User-Agent"] = USER_AGENT

            logger.info(f"[{request_id}] JSON-RPC request for {get_base_url(url)}")

            info = LinkInfo(url, headers=headers)
            err_resp = await update_info(info, request_id)
            
            if err_resp:
                await info.close()
                raise ValueError(f"Failed to get link info: {err_resp.reason}")

            if not info.support_range:
                await info.close()
                raise ValueError("Upstream does not support range requests")

            await info.init_clients(constants.MAX_WORKERS)
            
            gid = str(self.request_counter)
            self.link_cache[gid] = info
            
            logger.info(f"[{request_id}] Successfully created download task with GID: {gid}")

            return web.json_response({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": gid
            })

        except Exception as e:
            logger.error(f"[{request_id}] JSON-RPC request failed: {e}", exc_info=True)
            return web.json_response({
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "error": {
                    "code": -1,
                    "message": str(e)
                }
            }, status=400)

    async def handle_request(self, request: web.Request) -> web.StreamResponse:
        """
        处理传入的流请求。

        :param request: aiohttp的Request对象
        :return: aiohttp的StreamResponse对象
        """
        # 1. 初始化请求
        self.request_counter += 1
        request_id = f"{self.request_counter % 100:02d}"

        gid = request.query.get("gid")
        url = request.query.get("url")

        if not gid and not url:
            return web.HTTPBadRequest(reason="Missing 'gid' or 'url' parameter")

        info: Optional[LinkInfo] = None

        # 优先使用 GID 获取 LinkInfo
        if gid:
            logger.info(f"[{request_id}] Incoming stream request for GID: {gid}")
            info = self.link_cache.get(gid)
            if not info:
                return web.HTTPNotFound(reason=f"GID not found: {gid}")
            logger.info(f"[{request_id}] GID cache hit: {info.filename}")
        
        # 如果没有 GID，则使用 URL (兼容旧版)
        elif url:
            logger.info(f"[{request_id}] Incoming stream request: {str(get_base_url(url))}")
            if url not in self.link_cache:
                logger.info(f"[{request_id}] Link cache miss, initializing LinkInfo")
                # 对于旧式 /stream?url=... 的请求，使用默认headers
                info = LinkInfo(url)
                err = await update_info(info, request_id)
                if err:
                    await info.close()
                    return err
                if info.support_range:
                    await info.init_clients(constants.MAX_WORKERS)
                    self.link_cache[url] = info
                else:
                    logger.error(f"[{request_id}] URL does not support range requests")
                    await info.close()
                    return web.HTTPForbidden(reason="Range requests not supported by upstream")
            else:
                info = self.link_cache[url]
                logger.info(f"[{request_id}] Link cache hit: {info.filename}")

        # 2. 解析Range头
        range_hdr = request.headers.get("Range", "")
        start, end = parse_range(range_hdr)
        logger.info(
            f"[{request_id}] Range header: {range_hdr or 'NONE'} -> {start}-{end or 'EOF'}"
        )

        if info.filesize is None:
            return web.HTTPBadGateway(reason="Content length is unknown")

        # 4. 计算并验证范围
        end = end or (info.filesize - 1)
        end = min(end, info.filesize - 1)
        if start < 0 or start > end or start >= info.filesize:
            return web.HTTPRequestRangeNotSatisfiable(
                headers={"Content-Range": f"bytes */{info.filesize}"}
            )

        # 5. 准备响应头
        total_len = end - start + 1
        headers = {
            "Content-Type": info.minetype,
            "Accept-Ranges": "bytes",
            "Content-Length": str(total_len),
        }
        if info.filename:
            headers["Content-Disposition"] = (
                f"inline; filename*=UTF-8''{quote(info.filename)}"
            )
        status = 206 if (start > 0 or end < info.filesize - 1) else 200
        if status == 206:
            headers["Content-Range"] = f"bytes {start}-{end}/{info.filesize}"

        # 6. 创建并准备流式响应
        resp = web.StreamResponse(status=status, headers=headers)
        await resp.prepare(request)
        logger.info(f"[{request_id}] Response prepared, starting stream...")

        # 7. 并行下载与流式传输
        next_chunk_start = start
        in_flight: Set[asyncio.Task] = set()
        chunk_id_counter = 1
        stream_chunk_id = AsyncSafeStore(1)
        should_update_info = True

        async def fetch_chunk(chunk_start: int, chunk_id: int):
            """获取并处理单个数据块"""
            nonlocal stream_chunk_id, should_update_info
            chunk_end = min(chunk_start + constants.CHUNK_SIZE - 1, end)
            current_pos = chunk_start
            buffer = bytearray()

            client = await info.get_client()
            try:
                # 7.1 尝试从缓存读取
                if constants.CACHE_ON:
                    try:
                        view = await info.cache.view(chunk_start, chunk_end + 1)
                        buffer += view
                        current_pos += len(view)
                        view.release()
                        should_update_info = False

                        while await stream_chunk_id.get() != chunk_id:
                            await asyncio.sleep(0.1)
                        
                        try:
                            await resp.write(buffer)
                            await stream_chunk_id.set(await stream_chunk_id.get() + 1)
                        except Exception as e:
                            raise IncompleteResponseError(f"Response write failed: {e}")

                        logger.debug(f"[{request_id}] Chunk({chunk_id}) {chunk_start}-{chunk_end} Cache hit")
                        return  # client 统一在 finally 中归还
                    except ValueError:
                        pass # 缓存未命中或不完整，继续执行下载逻辑
                    except (asyncio.CancelledError, IncompleteResponseError):
                        raise
                    except Exception as e:
                        logger.error(f"[{request_id}] Chunk({chunk_id}) cache read error: {e}")

                # 7.2 从上游服务器下载
                for attempt in range(1, constants.MAX_RETRIES + 1):
                    try:
                        range_header = f"bytes={current_pos}-{chunk_end}"
                        async with client.get(info.redirect_url, headers={"Range": range_header}) as r:
                            if r.status != 206:
                                raise IncompleteChunkError(f"bad response status {r.status}")
                            should_update_info = False

                            # 7.2.1 数据流生成器, 包含低速检测
                            async def data_generator():
                                low_speed_streak = 0
                                last_check_time = asyncio.get_event_loop().time()
                                bytes_this_second = 0
                                
                                while True:
                                    try:
                                        data = await asyncio.wait_for(r.content.readany(), timeout=1.0)
                                        if not data:
                                            break
                                        bytes_this_second += len(data)
                                        yield data
                                    except asyncio.TimeoutError:
                                        yield b''

                                    now = asyncio.get_event_loop().time()
                                    if now - last_check_time >= 1.0:
                                        speed = bytes_this_second / (now - last_check_time)
                                        if constants.MIN_SPEED > 0 and speed < constants.MIN_SPEED:
                                            low_speed_streak += 1
                                            logger.debug(f"[{request_id}] Chunk({chunk_id}) low speed detected: {speed/1024:.1f} KB/s streak {low_speed_streak}")
                                        else:
                                            low_speed_streak = 0

                                        if low_speed_streak >= constants.MAX_STREAK:
                                            raise LowSpeedError(f"Speed ({speed/1024:.1f} KB/s) < {constants.MIN_SPEED/1024:.1f} KB/s")
                                        
                                        last_check_time = now
                                        bytes_this_second = 0
                            
                            # 7.2.2 处理数据流
                            buffer_written = False
                            async for data in data_generator():
                                if await stream_chunk_id.get() != chunk_id:
                                    # 还未轮到当前 chunk 输出 -> 先缓冲
                                    buffer.extend(data)
                                    if data and constants.CACHE_ON:
                                        await info.cache.write(current_pos, data)
                                    if data:
                                        current_pos += len(data)
                                    # 适度让出事件循环，避免长时间占用
                                    await asyncio.sleep(0.1)
                                    continue

                                # 轮到当前 chunk 输出
                                try:
                                    if not buffer_written and buffer:
                                        await resp.write(buffer)
                                        buffer_written = True
                                    if data:
                                        await resp.write(data)
                                        if constants.CACHE_ON:
                                            await info.cache.write(current_pos, data)
                                        current_pos += len(data)
                                except Exception as e:
                                    raise IncompleteResponseError(f"Response write failed: {e}")

                            # 循环结束（下载完成）。若尚未轮到，阻塞等待顺序。
                            if await stream_chunk_id.get() != chunk_id:
                                while await stream_chunk_id.get() != chunk_id:
                                    await asyncio.sleep(0.1)
                                # 轮到后一次性写出剩余缓冲
                                try:
                                    if buffer and not buffer_written:
                                        await resp.write(buffer)
                                        buffer_written = True
                                except Exception as e:
                                    raise IncompleteResponseError(f"Response write failed (final flush): {e}")

                            # 推进顺序指针
                            if await stream_chunk_id.get() == chunk_id:
                                await stream_chunk_id.set(await stream_chunk_id.get() + 1)

                            if current_pos - 1 == chunk_end:
                                logger.debug(f"[{request_id}] Chunk({chunk_id}) range {chunk_start}-{chunk_end} OK")
                                return  # client 统一在 finally 中归还
                            else:
                                raise IncompleteChunkError(f"Incomplete data: expected {chunk_end}, got {current_pos - 1}")

                    except LowSpeedError as e:
                        logger.warning(f"[{request_id}] Chunk({chunk_id}) attempt {attempt}/{constants.MAX_RETRIES} failed: {e}.")
                        if constants.RENEW_ON:
                            logger.warning(f"[{request_id}] Chunk({chunk_id}) Renewing TCP connection.")
                            try:
                                await client.close()
                            except Exception:
                                pass
                            client = info._create_client()
                        if constants.WAIT_ON:
                            backoff = 0.8 * (2 ** (attempt - 1)) + random.uniform(0, 0.2)
                            logger.warning(f"[{request_id}] Retrying after {backoff:.2f}s")
                            await asyncio.sleep(backoff)
                    
                    except (ClientError, IncompleteChunkError, asyncio.TimeoutError) as e:
                        backoff = 0.5 * (2 ** (attempt - 1)) + random.uniform(0, 0.1)
                        logger.warning(f"[{request_id}] Chunk({chunk_id}) attempt {attempt}/{constants.MAX_RETRIES} failed: {e}. Retrying after {backoff:.2f}s")
                        await asyncio.sleep(backoff)

                    except (asyncio.CancelledError, IncompleteResponseError):
                        raise
                    except Exception as e:
                        logger.error(f"[{request_id}] Chunk({chunk_id}) unexpected error: {e}", exc_info=True)

                raise IncompleteChunkError(f"Chunk({chunk_id}) failed after {constants.MAX_RETRIES} attempts")

            finally:
                await info.return_client(client)

        async def cancel_all_tasks():
            """取消所有正在运行的下载任务"""
            for task in in_flight:
                task.cancel()
            await asyncio.gather(*in_flight, return_exceptions=True)

        # 8. 启动并管理下载任务
        try:
            while len(in_flight) < constants.MAX_WORKERS and next_chunk_start <= end:
                task = asyncio.create_task(fetch_chunk(next_chunk_start, chunk_id_counter))
                in_flight.add(task)
                next_chunk_start += constants.CHUNK_SIZE
                chunk_id_counter += 1

            while in_flight:
                done, _ = await asyncio.wait(in_flight, return_when=asyncio.FIRST_COMPLETED)
                for task in done:
                    in_flight.remove(task)
                    if exc := task.exception():
                        raise exc

                while len(in_flight) < constants.MAX_WORKERS and next_chunk_start <= end:
                    task = asyncio.create_task(fetch_chunk(next_chunk_start, chunk_id_counter))
                    in_flight.add(task)
                    next_chunk_start += constants.CHUNK_SIZE
                    chunk_id_counter += 1
            
            logger.info(f"[{request_id}] Streaming finished, sent {total_len} bytes")

        except (Exception, asyncio.CancelledError) as e:
            logger.error(f"[{request_id}] Streaming failed: {e}")
        
        finally:
            await cancel_all_tasks()
            logger.info(f"[{request_id}] Response stream ended")

            if should_update_info:
                logger.warning(f"[{request_id}] No data downloaded, forcing LinkInfo update")
                await update_info(info, request_id)

        return resp
