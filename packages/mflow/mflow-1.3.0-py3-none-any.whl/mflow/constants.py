# 版本号
VERSION = "1.3.0"
# 用户代理
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
)
# 默认块大小: 1 MB
CHUNK_SIZE = 1 << 20
# 默认并行下载数
MAX_WORKERS = 4
# 最大重定向次数
MAX_REDIRECTS = 3
# 每个块最大重试次数
MAX_RETRIES = 5
# 缓存大小上限: 1 GB
MAX_CACHE_ON_SIZE = 1 << 30
# 是否启用缓存
CACHE_ON = False
# 失败后是否等待
WAIT_ON = False
# 失败后是否重建连接
RENEW_ON = False
# 触发低速错误的连续次数
MAX_STREAK = 5
# 默认日志级别
LOG_LEVEL = "INFO"
# 默认端口
PORT = 80
# 默认超时时间
TIMEOUT = None
# 最低速度, 单位: Bytes/s
MIN_SPEED = 0.0
