"""
RPA客户端主类
"""
import importlib
import inspect
import os
import threading
import traceback
from functools import partial

from .kit.enums import MessageType
from typing import Dict, Any, Callable, Optional

from .manager.base_handler import BaseHandler
from .manager.browser_factory import BrowserFactory
from .manager.base_browser_manager import BaseBrowserManager, DriverType, BrowserType

from .manager.websocket_manager import WebSocketClient

from .kit.Utils import Logger
from .manager.database_manager import get_db_manager, DatabaseManager



class RPAClient:
    # 任务脚本目录 - 在当前工作目录中查找
    SCRIPT_DIR = os.path.join(os.getcwd(), "script")

    def __init__(self, config: Dict[str, Any] = None):
        self.browser_manager: Optional[BaseBrowserManager] = None
        self.websocket_client: Optional[WebSocketClient] = None
        self.db_manager: Optional[DatabaseManager] = None

        self.is_running = False
        self.task_abort_flag = threading.Event()
        self.current_task_thread: Optional[threading.Thread] = None
        self.current_task: Optional[str] = None

        # 配置信息
        self.config = config or {}
        self.default_url = self.config.get("default_url")
        self.default_login_func = self.config.get("default_login_func")
        self.element_operations_impl = self.config.get("element_operations_impl", None)
        
        # 浏览器驱动配置
        self.driver_type = self._get_driver_type_from_config()
        self.browser_type = self._get_browser_type_from_config()

        self.task_handlers: Dict[str, Callable[[Dict[str, Any]], None]] = {}
        self._setup_task_handlers()
    
    def _get_driver_type_from_config(self) -> DriverType:
        """从配置中获取驱动类型"""
        driver_type_str = self.config.get('driver_type', 'playwright').lower()
        if driver_type_str == 'selenium':
            return DriverType.SELENIUM
        else:
            return DriverType.PLAYWRIGHT
    
    def _get_browser_type_from_config(self) -> BrowserType:
        """从配置中获取浏览器类型"""
        browser_type_str = self.config.get('browser_type', 'chromium').lower()
        try:
            return BrowserType(browser_type_str)
        except ValueError:
            Logger.warning(f"未知的浏览器类型 '{browser_type_str}'，使用默认的chromium")
            return BrowserType.CHROMIUM

    def _setup_task_handlers(self):
        """动态加载 script/ 目录下所有继承 BaseHandler 的类"""
        script_dir = os.path.abspath(self.SCRIPT_DIR)
        if not os.path.isdir(script_dir):
            Logger.warning(f"目录 '{script_dir}' 不存在，无法加载任务处理器。")
            return

        for filename in os.listdir(script_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                file_path = os.path.join(script_dir, filename)
                try:
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    if spec is None or spec.loader is None:
                        Logger.warning(f"无法加载模块: {file_path}")
                        continue
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, BaseHandler) and obj is not BaseHandler:
                            try:
                                task_name = obj.get_task_name() # ✅ 安全获取
                            except NotImplementedError:
                                continue

                            self.task_handlers[task_name] = lambda data, cls=obj: self._generic_task_handler(cls, data)
                            Logger.info(f"注册任务处理器: '{task_name}' -> {name}")

                except Exception as e:
                    Logger.error(f"加载模块 {module_name} 失败: {e}\n{traceback.format_exc()}")

        # 注册内置指令
        self.task_handlers["abort"] = self._handle_abort

    def _generic_task_handler(self, handler_class: type, data: Dict[str, Any]):
        """通用任务执行包装器"""
        try:
            if self.task_abort_flag.is_set():
                Logger.info(f"任务在开始前被中止")
                return

            self._safe_send_message(MessageType.INFO, f"开始执行任务")

            records = data.get("records", [])
            checkMode = data.get("checkMode", False)
            handler = handler_class(
                records=records,
                browser_manager=self.browser_manager,
                check_mode=checkMode,
                db_manager=self.db_manager,
                message_sender=self._safe_send_message,
                result_sender=self._safe_send_result,
                element_operations_impl=self.element_operations_impl
            )
            handler.task_abort_flag = self.task_abort_flag
            # 注意：BaseHandler.__init__中已经调用了execute(records)，所以这里不需要再次调用

            if not self.task_abort_flag.is_set():
                self._safe_send_message(MessageType.COMPLETED, f"任务执行完成")

        except Exception as e:
            error_msg = f"任务执行失败: {str(e)}"
            self._safe_send_message(MessageType.ERROR, error_msg)
            Logger.error(f"{error_msg}\n{traceback.format_exc()}")

        finally:
            self.is_running = False
            self.current_task = None

    def _safe_send_message(self, msg_type: MessageType, content: str, data: Any = None):
        """安全发送WebSocket消息"""
        if self.websocket_client:
            try:
                self.websocket_client.send_message(msg_type, content, data)
            except Exception as e:
                Logger.warning(f"发送消息失败: {e}")

    def _safe_send_result(self, key_id: str, rpa_type: str, rpa_state: str, rpa_note: str):
        """安全发送结果"""
        if self.websocket_client:
            try:
                self.websocket_client.send_result(key_id, rpa_type, rpa_state, rpa_note)
            except Exception as e:
                Logger.warning(f"发送结果失败: {e}")

    def initialize_browser(self, headless: bool = True, url: str = None) -> bool:
        """初始化浏览器（幂等）"""
        if self.browser_manager and self.browser_manager.is_initialized:
            return True

        try:
            # 使用浏览器工厂创建合适的浏览器管理器
            self.browser_manager = BrowserFactory.create_browser_manager(
                driver_type=self.driver_type,
                message_sender=self._safe_send_message
            )
            
            if not self.browser_manager:
                self._safe_send_message(MessageType.ERROR, f"无法创建{self.driver_type.value}浏览器管理器")
                return False
            
            # 获取驱动路径配置
            driver_path = self.config.get('driver_path')
            driver_options = self.config.get('driver_options', {})
            
            Logger.info(f"使用{self.driver_type.value}驱动初始化{self.browser_type.value}浏览器")
            
            return self.browser_manager.initialize(
                headless=headless, 
                url=url,
                browser_type=self.browser_type,
                driver_path=driver_path,
                **driver_options
            )
        except Exception as e:
            self._safe_send_message(MessageType.ERROR, "初始化浏览器失败")
            Logger.error(f"初始化浏览器失败: {e}")
            return False

    def login_system(self, username: str, password: str, login_func=None) -> bool:
        """登录系统（避免重复登录）"""
        if not self.browser_manager:
            self._safe_send_message(MessageType.ERROR, "浏览器未初始化")
            return False
        return self.browser_manager.login(username, password, login_func=login_func)

    def cleanup(self):
        """清理资源（幂等）"""
        try:
            if self.browser_manager:
                self.browser_manager.cleanup()
                self.browser_manager = None
            if self.db_manager:
                self.db_manager.close()
                self.db_manager = None
            Logger.info("资源清理完成")
        except Exception as e:
            Logger.error(f"清理资源失败: {e}")

    def _handle_abort(self, data: Dict[str, Any]):
        """处理中止指令"""
        try:
            Logger.info("收到中止指令")
            self._safe_send_message(MessageType.INFO, "正在中止当前任务...")

            self.task_abort_flag.set()

            if self.current_task_thread and self.current_task_thread.is_alive():
                Logger.info("等待任务线程退出...")
                self.current_task_thread.join(timeout=5.0)

            self.cleanup()

            self.is_running = False
            self.current_task = None
            self.current_task_thread = None
            self.task_abort_flag.clear()

            self._safe_send_message(MessageType.COMPLETED, "任务已中止，资源已释放")
            Logger.info("任务中止完成")

        except Exception as e:
            Logger.error(f"处理中止指令失败: {e}")
            self._safe_send_message(MessageType.ERROR, f"中止失败: {str(e)}")

    def _handle_websocket_message(self, data: Dict[str, Any]):
        """处理WebSocket消息"""
        try:
            command = data.get("command", "").strip()
            payload = data.get("payload", {})

            if not command:
                self._safe_send_message(MessageType.WARNING, "缺少 command 字段")
                return

            self._safe_send_message(MessageType.INFO, f"收到指令: {command}")

            handler = self.task_handlers.get(command)
            if not handler:
                self._safe_send_message(MessageType.WARNING, f"未知指令: {command}")
                return

            if command == "abort":
                handler(payload)
            elif not self.is_running:
                self.is_running = True
                self.task_abort_flag.clear()
                self.current_task = command

                self.current_task_thread = threading.Thread(
                    target=self._execute_task,
                    args=(command, payload),
                    daemon=True
                )
                self.current_task_thread.start()
            else:
                self._safe_send_message(MessageType.WARNING, "当前有任务正在执行，请稍后再试")

        except Exception as e:
            Logger.error(f"处理消息异常: {e}")
            self._safe_send_message(MessageType.ERROR, f"处理消息失败: {str(e)}")

    def _execute_task(self, command: str, payload: Dict[str, Any]):
        """执行任务的线程函数"""
        try:
            if self.task_abort_flag.is_set():
                Logger.info("任务被中止（执行前）")
                return

            # 初始化数据库（可选）
            db_config = payload.get("db_config")
            if db_config and not self.db_manager:
                self.db_manager = get_db_manager()
                if not self.db_manager.is_initialized():
                    if self.db_manager.initialize(db_config):
                        Logger.info("数据库初始化成功")
                    else:
                        Logger.warning("数据库初始化失败")
                        self._safe_send_message(MessageType.ERROR, "数据库连接失败")
                        return

            if self.task_abort_flag.is_set():
                self.cleanup()
                return

            # 初始化浏览器
            if not self.browser_manager or not self.browser_manager.is_initialized:
                headless = payload.get("headless", True)
                # 使用配置中的默认URL，如果payload中有URL则优先使用payload中的
                url = payload.get("url") or self.default_url
                Logger.info("初始化浏览器...")
                if not self.initialize_browser(headless, url=url):
                    self._safe_send_message(MessageType.ERROR, "浏览器初始化失败")
                    return

            if self.task_abort_flag.is_set():
                self.cleanup()
                return

            # 登录系统
            username = payload.get("username", "").strip()
            password = payload.get("password", "").strip()
            if username and password:
                # 使用配置中的默认登录函数，如果payload中有则优先使用payload中的
                login_func = payload.get("login_func") or self.default_login_func
                Logger.info("登录系统...")
                if not self.login_system(username, password, login_func=login_func):
                    self._safe_send_message(MessageType.ERROR, "登录失败")
                    self.cleanup()
                    return

            if self.task_abort_flag.is_set():
                self.cleanup()
                return

            # 执行任务
            handler = self.task_handlers.get(command)
            if handler:
                handler(payload)
            else:
                self._safe_send_message(MessageType.ERROR, f"未找到指令处理器: {command}")

        except Exception as e:
            Logger.error(f"任务执行异常: {traceback.format_exc()}")
            self._safe_send_message(MessageType.ERROR, f"任务异常: {str(e)}")
        finally:
            self.is_running = False
            self.current_task = None
            self.cleanup()

    def start(self) -> bool:
        """启动客户端"""
        try:
            Logger.info("启动 RPA 客户端...")
            self.websocket_client = WebSocketClient(message_handler=self._handle_websocket_message)
            if not self.websocket_client.start():
                Logger.error("WebSocket连接失败")
                return False

            self._stop_event = threading.Event()
            Logger.info("RPA客户端已启动，等待任务...")
            self._stop_event.wait()  # 阻塞直到 stop()
            return True

        except KeyboardInterrupt:
            Logger.info("收到中断信号")
            self.stop()
            return False
        except Exception as e:
            Logger.error(f"启动失败: {e}")
            self.stop()
            return False

    def stop(self):
        """停止客户端"""
        try:
            Logger.info("停止 RPA 客户端...")
            if hasattr(self, '_stop_event'):
                self._stop_event.set()
            self.cleanup()
            if self.websocket_client:
                self.websocket_client.stop()
                self.websocket_client = None
            Logger.info("RPA客户端已停止")
        except Exception as e:
            Logger.error(f"停止失败: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


# --- 使用示例（可选）---
if __name__ == "__main__":
    with RPAClient() as client:
        client.start()