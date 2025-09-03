"""
RPA客户端工具函数
"""

import json
import time
import traceback
import inspect
import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import ctypes


def get_screen_size():
    """获取屏幕尺寸"""
    try:
        user32 = ctypes.windll.user32
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)
        return width, height
    except Exception:
        # 默认尺寸
        return 1920, 1080


def format_result(keyId:str,rpa_type:str,rpa_state:int,rpa_note:str) -> str:
    """格式化消息为JSON字符串"""

    payload = {
        "keyId": keyId,
        "rpa_type": rpa_type,
        "rpa_state": rpa_state,
        "rpa_note": rpa_note,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return json.dumps(payload, ensure_ascii=False)

def format_message(action: str, message: str = "", data: dict = None) -> str:
    """格式化消息为JSON字符串"""
    from datetime import datetime
    payload = {
        "action": action,
        "message": message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # 如果有额外数据，添加到payload中
    if data:
        payload["data"] = data

    return json.dumps(payload, ensure_ascii=False)

def safe_execute(func, *args, **kwargs):
    """安全执行函数，捕获异常"""
    try:
        return func(*args, **kwargs), None
    except Exception as e:
        error_info = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        Logger.error(f"执行函数 {func.__name__} 时发生异常", exception=e, extra_data={"args": args, "kwargs": kwargs})
        return None, error_info



class Logger:
    """增强的日志记录器"""

    _debug_mode = False
    _initialized = False

    @classmethod
    def setup(cls, debug_mode: bool = False, log_file: str = "rpa.log"):
        """设置日志配置"""
        cls._debug_mode = debug_mode

        if not cls._initialized:
            # 配置logging
            log_level = logging.DEBUG if debug_mode else logging.INFO

            # 创建格式化器
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            # 文件处理器
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            file_handler.setLevel(log_level)

            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(log_level)

            # 配置根日志器
            root_logger = logging.getLogger()
            root_logger.setLevel(log_level)
            root_logger.handlers.clear()  # 清除现有处理器
            root_logger.addHandler(file_handler)
            root_logger.addHandler(console_handler)

            cls._initialized = True

    @staticmethod
    def _get_caller_info():
        """获取调用者信息"""
        frame = inspect.currentframe()
        try:
            # 向上查找调用栈，跳过Logger类的方法
            caller_frame = frame.f_back.f_back
            if caller_frame:
                filename = caller_frame.f_code.co_filename.split('\\')[-1].split('/')[-1]
                line_number = caller_frame.f_lineno
                function_name = caller_frame.f_code.co_name
                return f"[{filename}:{line_number}] {function_name}()"
            return "[unknown]"
        except:
            return "[unknown]"
        finally:
            del frame

    @classmethod
    def info(cls, message: str, extra_data: Dict[str, Any] = None):
        """记录信息日志"""
        if cls._initialized:
            if extra_data:
                logging.info(f"{message} - 数据: {extra_data}")
            else:
                logging.info(message)
        else:
            caller_info = cls._get_caller_info()
            log_msg = f"[INFO] {time.strftime('%Y-%m-%d %H:%M:%S')} {caller_info} - {message}"
            if extra_data:
                log_msg += f" - 数据: {extra_data}"
            print(log_msg)

    @classmethod
    def warning(cls, message: str, extra_data: Dict[str, Any] = None):
        """记录警告日志"""
        if cls._initialized:
            if extra_data:
                logging.warning(f"{message} - 数据: {extra_data}")
            else:
                logging.warning(message)
        else:
            caller_info = cls._get_caller_info()
            log_msg = f"[WARNING] {time.strftime('%Y-%m-%d %H:%M:%S')} {caller_info} - {message}"
            if extra_data:
                log_msg += f" - 数据: {extra_data}"
            print(log_msg)

    @classmethod
    def error(cls, message: str, exception: Exception = None, extra_data: Dict[str, Any] = None):
        """记录错误日志"""
        if cls._initialized:
            log_message = message
            if exception:
                log_message += f" - 异常: {type(exception).__name__}: {str(exception)}"
            if extra_data:
                log_message += f" - 数据: {extra_data}"
            logging.error(log_message)

            # 记录堆栈跟踪
            if exception:
                logging.error("堆栈跟踪:", exc_info=True)
        else:
            caller_info = cls._get_caller_info()
            log_msg = f"[ERROR] {time.strftime('%Y-%m-%d %H:%M:%S')} {caller_info} - {message}"
            if exception:
                log_msg += f" - 异常: {type(exception).__name__}: {str(exception)}"
            if extra_data:
                log_msg += f" - 数据: {extra_data}"
            print(log_msg)

            # 打印堆栈跟踪
            if exception:
                print("堆栈跟踪:")
                traceback.print_exc()

    @classmethod
    def debug(cls, message: str, extra_data: Dict[str, Any] = None):
        """记录调试日志"""
        if not cls._debug_mode:
            return

        if cls._initialized:
            if extra_data:
                logging.debug(f"{message} - 数据: {extra_data}")
            else:
                logging.debug(message)
        else:
            caller_info = cls._get_caller_info()
            log_msg = f"[DEBUG] {time.strftime('%Y-%m-%d %H:%M:%S')} {caller_info} - {message}"
            if extra_data:
                log_msg += f" - 数据: {extra_data}"
            print(log_msg)

    @classmethod
    def exception(cls, message: str, extra_data: Dict[str, Any] = None):
        """记录异常日志（自动捕获当前异常）"""
        if cls._initialized:
            log_message = message
            if extra_data:
                log_message += f" - 数据: {extra_data}"
            logging.exception(log_message)
        else:
            caller_info = cls._get_caller_info()
            log_msg = f"[EXCEPTION] {time.strftime('%Y-%m-%d %H:%M:%S')} {caller_info} - {message}"
            if extra_data:
                log_msg += f" - 数据: {extra_data}"
            print(log_msg)
            traceback.print_exc()
