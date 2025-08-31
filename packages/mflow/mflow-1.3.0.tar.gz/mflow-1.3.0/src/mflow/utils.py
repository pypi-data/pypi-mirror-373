import asyncio
import logging
import re
from typing import Optional, Tuple
from urllib.parse import urlparse, urlunparse
from bytesparse import Memory
from colorama import Fore, Style


class SafeMemory(Memory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lock = asyncio.Lock()

    async def view(self, *args, **kwargs):
        async with self._lock:
            return super().view(*args, **kwargs)

    async def write(self, *args, **kwargs):
        async with self._lock:
            return super().write(*args, **kwargs)


class ColoredFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.WHITE,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA,
    }

    def format(self, record):
        color = self.LEVEL_COLORS.get(record.levelno, "")
        msg = super().format(record)
        return f"{color}{msg}{Style.RESET_ALL}"


class AsyncSafeStore:
    def __init__(self, initial_value=None):
        self._value = initial_value
        self._lock = asyncio.Lock()

    async def get(self):
        """异步安全地读取当前值"""
        async with self._lock:
            return self._value

    async def set(self, new_value):
        """异步安全地写入新值"""
        async with self._lock:
            self._value = new_value


def get_base_url(url: str, have_path=True) -> str:
    """
    返回不包含参数(query)和锚点(fragment)的 URL 部分。
    """
    parts = urlparse(url)
    if have_path:
        return urlunparse((parts.scheme, parts.netloc, parts.path, "", "", ""))
    else:
        return urlunparse((parts.scheme, parts.netloc, "", "", "", ""))


def parse_range(header: str) -> Tuple[int, Optional[int]]:
    m = re.match(r"bytes=(\d+)-(\d+)?", header or "")
    if not m:
        return 0, None
    start = int(m.group(1))
    end = int(m.group(2)) if m.group(2) else None
    return start, end
