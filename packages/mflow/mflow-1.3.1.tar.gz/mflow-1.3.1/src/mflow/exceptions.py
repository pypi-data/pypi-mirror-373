
class IncompleteChunkError(Exception):
    """块下载不完整时抛出"""
    pass


class LowSpeedError(Exception):
    """下载速度过低时抛出"""
    pass


class IncompleteResponseError(Exception):
    """响应不完整时抛出"""
    pass
