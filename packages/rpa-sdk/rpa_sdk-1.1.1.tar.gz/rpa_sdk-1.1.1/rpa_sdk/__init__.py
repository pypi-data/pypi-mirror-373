"""RPA SDK - 机器人流程自动化软件开发工具包

这是一个用于构建RPA应用程序的Python SDK，提供了浏览器自动化、
WebSocket通信、数据库操作等功能。
"""

__version__ = "1.1.0"
__author__ = "AITMC"
__email__ = "support@aitmc.com"
__description__ = "RPA SDK - 机器人流程自动化软件开发工具包"

# 导入主要类
from .rpa_client import RPAClient
from .manager.playwright_browser_manager import PlaywrightBrowserManager
from .manager.websocket_manager import WebSocketClient
from .manager.database_manager import DatabaseManager
from .kit.Utils import Logger, format_message, format_result

# 导入元素操作相关类
from .manager.element_operations_interface import WebElementOperations
from .manager.element_operations_factory import ElementOperationsFactory
from .manager.base_handler import BaseHandler

# 导入数据模型
from .data import TVisit, TPhysical, TArchive

# 定义公开的API
__all__ = [
    'RPAClient',
    'PlaywrightBrowserManager', 
    'WebSocketClient',
    'DatabaseManager',
    'Logger',
    'format_message',
    'format_result',
    'WebElementOperations',
    'ElementOperationsFactory',
    'BaseHandler',
    'TVisit',
    'TPhysical', 
    'TArchive'
]