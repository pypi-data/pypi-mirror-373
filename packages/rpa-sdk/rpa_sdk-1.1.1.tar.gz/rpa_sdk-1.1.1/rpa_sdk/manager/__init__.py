"""RPA SDK 管理器模块

包含浏览器管理、WebSocket通信、数据库操作等管理器类。
"""

from .playwright_browser_manager import PlaywrightBrowserManager
from .selenium_browser_manager import SeleniumBrowserManager
from .base_browser_manager import BaseBrowserManager, DriverType, BrowserType
from .browser_factory import BrowserFactory
from .websocket_manager import WebSocketClient
from .database_manager import DatabaseManager, get_db_manager
from .base_handler import BaseHandler
from .element_operations_interface import WebElementOperations
from .element_operations_factory import ElementOperationsFactory

__all__ = [
    'PlaywrightBrowserManager',
    'SeleniumBrowserManager',
    'BaseBrowserManager',
    'BrowserFactory',
    'DriverType',
    'BrowserType',
    'WebSocketClient', 
    'DatabaseManager',
    'get_db_manager',
    'BaseHandler',
    'WebElementOperations',
    'ElementOperationsFactory'
]