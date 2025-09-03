"""浏览器工厂类

根据配置创建合适的浏览器管理器实例
"""

from typing import Optional, Dict, Any
from .base_browser_manager import BaseBrowserManager, DriverType, BrowserType
from .playwright_browser_manager import PlaywrightBrowserManager
from .selenium_browser_manager import SeleniumBrowserManager
from ..kit.Utils import Logger


class BrowserFactory:
    """浏览器工厂类"""
    
    @staticmethod
    def create_browser_manager(
        driver_type: DriverType = DriverType.PLAYWRIGHT,
        message_sender=None
    ) -> Optional[BaseBrowserManager]:
        """创建浏览器管理器
        
        Args:
            driver_type: 驱动类型
            message_sender: 消息发送器
            
        Returns:
            BaseBrowserManager: 浏览器管理器实例
        """
        try:
            if driver_type == DriverType.PLAYWRIGHT:
                Logger.info("创建Playwright浏览器管理器")
                return PlaywrightBrowserManager(message_sender)
            elif driver_type == DriverType.SELENIUM:
                Logger.info("创建Selenium浏览器管理器")
                return SeleniumBrowserManager(message_sender)
            else:
                Logger.error(f"不支持的驱动类型: {driver_type}")
                return None
        except Exception as e:
            Logger.error(f"创建浏览器管理器失败: {e}")
            return None
    
    @staticmethod
    def create_browser_manager_from_config(
        config: Dict[str, Any],
        message_sender=None
    ) -> Optional[BaseBrowserManager]:
        """从配置创建浏览器管理器
        
        Args:
            config: 配置字典，包含driver_type等信息
            message_sender: 消息发送器
            
        Returns:
            BaseBrowserManager: 浏览器管理器实例
        """
        driver_type_str = config.get('driver_type', 'playwright')
        
        try:
            if driver_type_str.lower() == 'playwright':
                driver_type = DriverType.PLAYWRIGHT
            elif driver_type_str.lower() == 'selenium':
                driver_type = DriverType.SELENIUM
            else:
                Logger.warning(f"未知的驱动类型 '{driver_type_str}'，使用默认的Playwright")
                driver_type = DriverType.PLAYWRIGHT
            
            return BrowserFactory.create_browser_manager(driver_type, message_sender)
        except Exception as e:
            Logger.error(f"从配置创建浏览器管理器失败: {e}")
            return None
    
    @staticmethod
    def get_supported_drivers():
        """获取支持的驱动类型列表
        
        Returns:
            List[str]: 支持的驱动类型列表
        """
        return [driver.value for driver in DriverType]
    
    @staticmethod
    def get_supported_browsers_for_driver(driver_type: DriverType):
        """获取指定驱动支持的浏览器类型
        
        Args:
            driver_type: 驱动类型
            
        Returns:
            List[str]: 支持的浏览器类型列表
        """
        if driver_type == DriverType.PLAYWRIGHT:
            return [BrowserType.CHROMIUM.value, BrowserType.CHROME.value, 
                   BrowserType.FIREFOX.value, BrowserType.SAFARI.value]
        elif driver_type == DriverType.SELENIUM:
            return [BrowserType.IE.value, BrowserType.CHROME.value, 
                   BrowserType.FIREFOX.value, BrowserType.EDGE.value]
        else:
            return []
    
    @staticmethod
    def is_driver_available(driver_type: DriverType) -> bool:
        """检查指定驱动是否可用
        
        Args:
            driver_type: 驱动类型
            
        Returns:
            bool: 驱动是否可用
        """
        try:
            if driver_type == DriverType.PLAYWRIGHT:
                from playwright.sync_api import sync_playwright
                return True
            elif driver_type == DriverType.SELENIUM:
                from selenium import webdriver
                return True
            else:
                return False
        except ImportError:
            return False
    
    @staticmethod
    def get_recommended_config_for_ie():
        """获取IE浏览器的推荐配置
        
        Returns:
            Dict[str, Any]: IE浏览器推荐配置
        """
        return {
            'driver_type': 'selenium',
            'browser_type': 'ie',
            'headless': False,  # IE不支持无头模式
            'driver_options': {
                'ignoreProtectedModeSettings': True,
                'ignoreZoomSetting': True,
                'nativeEvents': False,
                'unexpectedAlertBehaviour': 'accept',
                'elementScrollBehavior': 1
            }
        }
    
    @staticmethod
    def get_default_config():
        """获取默认配置
        
        Returns:
            Dict[str, Any]: 默认配置
        """
        return {
            'driver_type': 'playwright',
            'browser_type': 'chromium',
            'headless': True
        }