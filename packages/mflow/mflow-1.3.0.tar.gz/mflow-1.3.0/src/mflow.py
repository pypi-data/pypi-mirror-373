from aiohttp import web
from mflow.app import init_app
from mflow.config import init_var
from mflow import constants

def main():
    """主函数, 用于通过setuptools等工具启动应用"""
    if init_var():
        app = init_app()
        web.run_app(
            app, 
            host="0.0.0.0", 
            port=constants.PORT, 
            access_log=None, 
            print=None
        )

if __name__ == "__main__":
    """直接执行此脚本时, 应用于调试"""
    if init_var():
        # --- 在此覆盖配置用于调试 ---
        constants.LOG_LEVEL = "DEBUG"
        constants.MAX_WORKERS = 3
        constants.MAX_STREAK = 3
        constants.CHUNK_SIZE = 20 << 20   # 20 MB
        constants.MIN_SPEED = 2 << 20     # 2 MB/S
        constants.RENEW_ON = True
        # --------------------------
        
        app = init_app()
        web.run_app(
            app, 
            host="0.0.0.0", 
            port=constants.PORT, 
            access_log=None, 
            print=None
        )