import logging
from aiohttp import web
from colorama import init as colorama_init

from . import constants
from .handler import MultiFlow
from .utils import ColoredFormatter

logger = logging.getLogger("Mflow")

def init_app():
    """
    初始化并返回 aiohttp 应用实例。
    """
    # 初始化 colorama 以在Windows上支持彩色日志
    colorama_init(autoreset=True)

    # 配置日志记录器
    handler = logging.StreamHandler()
    handler.setFormatter(
        ColoredFormatter(fmt="%(asctime)s [%(levelname).4s] %(message)s")
    )
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(constants.LOG_LEVEL)
    logger.info("Initializing application...")

    # 创建 MultiFlow 控制器和 aiohttp 应用
    mf_controller = MultiFlow()
    app = web.Application()
    app.router.add_get("/stream", mf_controller.handle_request)
    app.router.add_post("/jsonrpc", mf_controller.handle_jsonrpc)

    # 注册清理回调, 以在应用关闭时关闭连接
    app.on_cleanup.append(lambda _: mf_controller.close())

    logger.info(f"Server starting on 0.0.0.0:{constants.PORT}")
    return app
