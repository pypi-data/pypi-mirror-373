"""浏览器管理器基类

定义了浏览器管理器的抽象接口，支持多种驱动类型
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from enum import Enum


class DriverType(Enum):
    """驱动类型枚举"""
    PLAYWRIGHT = "playwright"
    SELENIUM = "selenium"


class BrowserType(Enum):
    """浏览器类型枚举"""
    CHROMIUM = "chromium"
    CHROME = "chrome"
    FIREFOX = "firefox"
    SAFARI = "safari"
    IE = "ie"
    EDGE = "edge"


class BaseBrowserManager(ABC):
    """浏览器管理器抽象基类"""
    
    def __init__(self, driver_type: DriverType, message_sender=None):
        self.driver_type = driver_type
        self.message_sender = message_sender
        self.is_initialized = False
        
    @abstractmethod
    def initialize(self, 
                  headless: bool = True, 
                  url: str = None,
                  browser_type: BrowserType = BrowserType.CHROMIUM,
                  **kwargs) -> bool:
        """初始化浏览器
        
        Args:
            headless: 是否无头模式
            url: 初始URL
            browser_type: 浏览器类型
            **kwargs: 其他配置参数
            
        Returns:
            bool: 初始化是否成功
        """
        pass
    
    @abstractmethod
    def navigate_to(self, url: str) -> bool:
        """导航到指定URL
        
        Args:
            url: 目标URL
            
        Returns:
            bool: 导航是否成功
        """
        pass
    
    @abstractmethod
    def get_page(self):
        """获取页面对象
        
        Returns:
            页面对象（Playwright Page 或 Selenium WebDriver）
        """
        pass
    
    @abstractmethod
    def cleanup(self):
        """清理资源"""
        pass
    
    @abstractmethod
    def is_browser_running(self) -> bool:
        """检查浏览器是否运行中
        
        Returns:
            bool: 浏览器是否运行中
        """
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()