"""
WebSocket客户端
负责与服务端的WebSocket通信
"""

import json
import threading
import time
from typing import Callable, Dict, Any, Optional

try:
    import websocket
    HAS_WEBSOCKET = True
except ImportError:
    HAS_WEBSOCKET = False
    websocket = None

from ..kit.Utils import format_message, Logger, format_result
from ..kit.enums import MessageType

class WebSocketClient:
    """WebSocket客户端"""
    
    def __init__(self, url: str = None, message_handler: Optional[Callable] = None):
        self.websocket_thread = None
        if not HAS_WEBSOCKET:
            Logger.warning("websocket 模块未安装，WebSocket功能将被禁用")

        self.ws = None
        self.url = 'ws://127.0.0.1:8765'
        self.message_handler = message_handler
        self.is_connected = False
        self.reconnect_interval = 1  # 重连间隔（秒）
        self.max_reconnect_attempts = 3
        self.reconnect_count = 0
        self._stop_event = threading.Event()

    def send_result(self, key_id: str, rpa_type: str, rpa_state: int, rpa_note: str):
        """发送RPA任务执行结果"""
        if not HAS_WEBSOCKET or not self.ws or not self.is_connected:
            Logger.warning(f"WebSocket未连接，无法发送结果: {key_id}")
            return

        try:
            self.ws.send(format_result(key_id, rpa_type, rpa_state, rpa_note))
        except Exception as e:
            Logger.error(f"发送结果失败: {e}")

    def send_message(self, action, message: str, data: Dict[str, Any] = None):
        """发送消息"""
        if not HAS_WEBSOCKET or not self.ws or not self.is_connected:
            Logger.warning(f"WebSocket未连接，无法发送消息: {message}")
            return

        try:
            # 处理 MessageType 枚举或字符串
            if hasattr(action, 'value'):
                action_value = action.value
            else:
                action_value = str(action)

            self.ws.send(format_message(action_value, message, data))
        except Exception as e:
            Logger.error(f"发送消息失败: {e}")
    
    def on_message(self, ws, message):
        """处理接收到的WebSocket消息"""
        try:
            data = json.loads(message)
            command = data['command']
            payload = data['payload']
            records = payload['records'] if 'records' in payload else ''
            Logger.debug(f"收到消息: {command} {records}")
            print(command,records)
            if self.message_handler:
                # 在新线程中处理消息，避免阻塞WebSocket
                threading.Thread(
                    target=self.message_handler,
                    args=(data,),
                    daemon=True
                ).start()
            else:
                Logger.warning("未设置消息处理器")
                
        except json.JSONDecodeError:
            Logger.error("接收到无效的JSON消息")
        except Exception as e:
            Logger.error(f"处理消息时出错: {e}")
    
    def on_error(self, ws, error):
        """WebSocket错误处理"""
        Logger.error(f"WebSocket错误: {error}")
        self.is_connected = False
    
    def on_close(self, ws, close_status_code, close_msg):
        """WebSocket连接关闭处理"""
        Logger.info(f"WebSocket连接已关闭: {close_status_code} - {close_msg}")
        self.is_connected = False
        
        # 如果不是主动停止，则尝试重连
        if not self._stop_event.is_set() and self.reconnect_count < self.max_reconnect_attempts:
            self._schedule_reconnect()
    
    def on_open(self, ws):
        """WebSocket连接建立处理"""
        Logger.info("WebSocket连接已建立")
        self.is_connected = True
        self.reconnect_count = 0  # 重置重连计数

        # 发送客户端就绪消息
        try:
            self.send_message(MessageType.INFO,"RPA客户端已连接，等待指令...")
        except Exception as e:
            Logger.error(f"发送就绪消息失败: {e}")
    
    def _schedule_reconnect(self):
        """安排重连"""
        self.reconnect_count += 1
        Logger.info(f"将在 {self.reconnect_interval} 秒后尝试第 {self.reconnect_count} 次重连")
        
        def reconnect():
            if not self._stop_event.wait(self.reconnect_interval):
                Logger.info(f"尝试重连 ({self.reconnect_count}/{self.max_reconnect_attempts})")
                self.connect()
        
        threading.Thread(target=reconnect, daemon=True).start()
    
    def connect(self):
        """连接到WebSocket服务器"""
        if not HAS_WEBSOCKET:
            Logger.warning("websocket 模块未安装，无法连接到WebSocket服务器")
            return

        try:
            Logger.info(f"正在连接到WebSocket服务器: {self.url}")

            # 创建WebSocket连接
            self.ws = websocket.WebSocketApp(
                self.url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )

            # 启动WebSocket连接（阻塞运行）
            self.ws.run_forever()
            
        except Exception as e:
            Logger.error(f"WebSocket连接失败: {e}")
            self.is_connected = False
            
            # 如果连接失败且未达到最大重连次数，则重连
            if not self._stop_event.is_set() and self.reconnect_count < self.max_reconnect_attempts:
                self._schedule_reconnect()
    
    def start(self):
        """启动WebSocket客户端"""
        if not HAS_WEBSOCKET:
            Logger.warning("websocket 模块未安装，无法启动WebSocket客户端")
            return

        Logger.info("启动WebSocket客户端...")
        self._stop_event.clear()

        # 在独立线程中启动WebSocket连接，避免阻塞主线程
        self.websocket_thread = threading.Thread(target=self.connect, daemon=True)
        self.websocket_thread.start()

        # 不要使用简单的time.sleep，而是等待连接建立或超时
        return self.wait_for_connection(timeout=10)
    
    def stop(self):
        """停止WebSocket客户端"""
        Logger.info("正在停止WebSocket客户端...")
        self._stop_event.set()
        
        if self.ws:
            self.ws.close()
        
        self.is_connected = False
        Logger.info("WebSocket客户端已停止")
    
    def wait_for_connection(self, timeout: int = 30) -> bool:
        """等待连接建立"""
        start_time = time.time()
        while not self.is_connected and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        return self.is_connected
