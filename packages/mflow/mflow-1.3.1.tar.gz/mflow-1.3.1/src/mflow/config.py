import argparse
from . import constants

def init_var():
    """
    解析命令行参数并更新全局配置变量。
    :return: 如果解析成功返回True, 否则返回False。
    """
    parser = argparse.ArgumentParser(
        description="Multi Flow - Concurrent Streaming Proxy"
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="Mflow v" + constants.VERSION,
        help="显示程序版本号并退出",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=constants.PORT,
        help=f"监听端口 (默认: {constants.PORT})",
    )
    parser.add_argument(
        "-r",
        "--retry",
        type=int,
        default=constants.MAX_RETRIES,
        help=f"每个块的最大重试次数 (默认: {constants.MAX_RETRIES})",
    )
    parser.add_argument(
        "-c",
        "--connections",
        type=int,
        default=constants.MAX_WORKERS,
        help=f"每个流的并发连接数 (默认: {constants.MAX_WORKERS})",
    )
    parser.add_argument(
        "-s",
        "--chunk-size",
        type=str,
        default=f"{constants.CHUNK_SIZE // 1024 // 1024}M",
        help="并行下载的块大小 (例如 1M, 512K) (默认: 1M)",
    )
    parser.add_argument(
        "--log-level",
        default=constants.LOG_LEVEL,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help=f"设置日志级别 (默认: {constants.LOG_LEVEL})",
    )
    parser.add_argument(
        "--cache",
        action="store_true",
        help="为流媒体启用内存缓存 (默认: 关闭)",
    )
    parser.add_argument(
        "--min-speed",
        type=str,
        default="0",
        help="连接的最低速度 (例如 100K, 0.5M)。如果速度持续低于此值将触发重试 (默认: 0, 关闭)",
    )
    args = parser.parse_args()

    # --- 解析块大小 ---
    size_str: str = args.chunk_size.upper()
    try:
        if size_str.endswith("K"):
            chunk_size = int(size_str[:-1]) * 1024
        elif size_str.endswith("M"):
            chunk_size = int(size_str[:-1]) * 1024 * 1024
        else:
            chunk_size = int(size_str)
    except ValueError:
        parser.error(f"无效的块大小格式: {args.chunk_size}。请使用数字, K, 或 M。")
        return False

    # --- 解析最低速度 ---
    speed_str: str = args.min_speed.upper()
    try:
        if speed_str.endswith("K"):
            min_speed = float(speed_str[:-1]) * 1024
        elif speed_str.endswith("M"):
            min_speed = float(speed_str[:-1]) * 1024 * 1024
        else:
            min_speed = float(speed_str)
    except ValueError:
        parser.error(f"无效的最低速度格式: {args.min_speed}。请使用数字, K, 或 M。")
        return False

    # --- 更新全局常量 ---
    constants.PORT = int(args.port)
    constants.CHUNK_SIZE = int(chunk_size)
    constants.MAX_WORKERS = int(args.connections)
    constants.MAX_RETRIES = int(args.retry)
    constants.LOG_LEVEL = str(args.log_level)
    constants.CACHE_ON = bool(args.cache)
    constants.MIN_SPEED = float(min_speed)

    return True
