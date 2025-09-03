"""Selenium浏览器管理器

基于Selenium WebDriver的浏览器管理器，支持IE等传统浏览器
"""

from typing import Optional, Dict, Any
import time

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.ie.service import Service as IEService
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from selenium.webdriver.edge.service import Service as EdgeService
    from selenium.webdriver.ie.options import Options as IEOptions
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.edge.options import Options as EdgeOptions
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False
    webdriver = None
    By = None
    WebDriverWait = None
    EC = None

from .base_browser_manager import BaseBrowserManager, DriverType, BrowserType
from ..kit.Utils import Logger
from ..kit.enums import MessageType


class SeleniumBrowserManager(BaseBrowserManager):
    """Selenium浏览器管理器"""
    
    def __init__(self, message_sender=None):
        super().__init__(DriverType.SELENIUM, message_sender)
        self.driver: Optional[webdriver.Remote] = None
        self.wait: Optional[WebDriverWait] = None
        
        # 检查 Selenium 是否可用
        if not HAS_SELENIUM:
            Logger.error("Selenium 未安装，请运行: pip install selenium")
    
    def initialize(self, 
                  headless: bool = True, 
                  url: str = None,
                  browser_type: BrowserType = BrowserType.IE,
                  driver_path: str = None,
                  **kwargs) -> bool:
        """初始化浏览器
        
        Args:
            headless: 是否无头模式（IE不支持）
            url: 初始URL
            browser_type: 浏览器类型
            driver_path: 驱动程序路径
            **kwargs: 其他配置参数
            
        Returns:
            bool: 初始化是否成功
        """
        if not HAS_SELENIUM:
            Logger.error("Selenium 未安装，无法初始化浏览器")
            return False
        
        try:
            Logger.info(f"初始化Selenium浏览器 (类型={browser_type.value}, headless={headless})")
            
            # 根据浏览器类型创建驱动
            if browser_type == BrowserType.IE:
                self.driver = self._create_ie_driver(driver_path, **kwargs)
            elif browser_type == BrowserType.CHROME:
                self.driver = self._create_chrome_driver(headless, driver_path, **kwargs)
            elif browser_type == BrowserType.FIREFOX:
                self.driver = self._create_firefox_driver(headless, driver_path, **kwargs)
            elif browser_type == BrowserType.EDGE:
                self.driver = self._create_edge_driver(headless, driver_path, **kwargs)
            else:
                Logger.error(f"不支持的浏览器类型: {browser_type.value}")
                return False
            
            # 设置等待对象
            self.wait = WebDriverWait(self.driver, 30)
            
            # 最大化窗口（IE需要）
            if browser_type == BrowserType.IE:
                self.driver.maximize_window()
            
            # 导航到目标页面（如果提供了URL）
            if url:
                Logger.info(f"导航到: {url}")
                self.driver.get(url)
                
                # 等待页面加载
                time.sleep(2)
            
            self.is_initialized = True
            Logger.info("Selenium浏览器初始化成功")
            
            # 发送成功消息
            if self.message_sender:
                self.message_sender(
                    MessageType.INFO,
                    "Selenium浏览器初始化成功",
                    {"url": url, "browser_type": browser_type.value, "headless": headless}
                )
            
            return True
            
        except Exception as e:
            Logger.error(f"Selenium浏览器初始化失败: {e}")
            self.cleanup()
            
            # 发送失败消息
            if self.message_sender:
                self.message_sender(
                    MessageType.ERROR,
                    f"Selenium浏览器初始化失败: {str(e)}",
                    {"error": str(e)}
                )
            
            return False
    
    def _create_ie_driver(self, driver_path: str = None, **kwargs) -> webdriver.Ie:
        """创建IE驱动"""
        options = IEOptions()
        
        # IE特殊配置
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--ignore-certificate-errors-spki-list')
        
        # 设置IE特定的能力
        options.set_capability('ignoreProtectedModeSettings', True)
        options.set_capability('ignoreZoomSetting', True)
        options.set_capability('nativeEvents', False)
        options.set_capability('unexpectedAlertBehaviour', 'accept')
        options.set_capability('elementScrollBehavior', 1)
        
        # 应用自定义配置
        for key, value in kwargs.items():
            if hasattr(options, 'add_argument'):
                options.add_argument(f'--{key}={value}')
        
        if driver_path:
            service = IEService(executable_path=driver_path)
            return webdriver.Ie(service=service, options=options)
        else:
            return webdriver.Ie(options=options)
    
    def _create_chrome_driver(self, headless: bool, driver_path: str = None, **kwargs) -> webdriver.Chrome:
        """创建Chrome驱动"""
        options = ChromeOptions()
        
        if headless:
            options.add_argument('--headless')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        # 应用自定义配置
        for key, value in kwargs.items():
            options.add_argument(f'--{key}={value}')
        
        if driver_path:
            service = ChromeService(executable_path=driver_path)
            return webdriver.Chrome(service=service, options=options)
        else:
            return webdriver.Chrome(options=options)
    
    def _create_firefox_driver(self, headless: bool, driver_path: str = None, **kwargs) -> webdriver.Firefox:
        """创建Firefox驱动"""
        options = FirefoxOptions()
        
        if headless:
            options.add_argument('--headless')
        
        # 应用自定义配置
        for key, value in kwargs.items():
            options.add_argument(f'--{key}={value}')
        
        if driver_path:
            service = FirefoxService(executable_path=driver_path)
            return webdriver.Firefox(service=service, options=options)
        else:
            return webdriver.Firefox(options=options)
    
    def _create_edge_driver(self, headless: bool, driver_path: str = None, **kwargs) -> webdriver.Edge:
        """创建Edge驱动"""
        options = EdgeOptions()
        
        if headless:
            options.add_argument('--headless')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # 应用自定义配置
        for key, value in kwargs.items():
            options.add_argument(f'--{key}={value}')
        
        if driver_path:
            service = EdgeService(executable_path=driver_path)
            return webdriver.Edge(service=service, options=options)
        else:
            return webdriver.Edge(options=options)
    
    def navigate_to(self, url: str) -> bool:
        """导航到指定URL"""
        if not self.is_initialized or not self.driver:
            Logger.error("浏览器未初始化，无法导航")
            return False
        
        try:
            Logger.info(f"导航到: {url}")
            self.driver.get(url)
            time.sleep(2)  # 等待页面加载
            return True
        except Exception as e:
            Logger.error(f"导航失败: {e}")
            return False
    
    def get_page(self):
        """获取WebDriver对象"""
        return self.driver
    
    def cleanup(self):
        """清理资源"""
        try:
            if self.driver:
                Logger.info("关闭Selenium浏览器")
                self.driver.quit()
                self.driver = None
                self.wait = None
            
            self.is_initialized = False
            Logger.info("Selenium浏览器资源清理完成")
            
        except Exception as e:
            Logger.error(f"清理Selenium浏览器资源时出错: {e}")
    
    def is_browser_running(self) -> bool:
        """检查浏览器是否运行中"""
        if not self.driver:
            return False
        
        try:
            # 尝试获取当前URL来检查浏览器是否还活着
            self.driver.current_url
            return True
        except Exception:
            return False
    
    def find_element(self, by: str, value: str, timeout: int = 10):
        """查找元素
        
        Args:
            by: 定位方式（如 By.ID, By.XPATH 等）
            value: 定位值
            timeout: 超时时间
            
        Returns:
            WebElement 或 None
        """
        if not self.is_initialized or not self.driver:
            Logger.error("浏览器未初始化，无法查找元素")
            return None
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, value)))
            return element
        except Exception as e:
            Logger.error(f"查找元素失败 ({by}={value}): {e}")
            return None
    
    def find_elements(self, by: str, value: str):
        """查找多个元素
        
        Args:
            by: 定位方式
            value: 定位值
            
        Returns:
            WebElement列表
        """
        if not self.is_initialized or not self.driver:
            Logger.error("浏览器未初始化，无法查找元素")
            return []
        
        try:
            elements = self.driver.find_elements(by, value)
            return elements
        except Exception as e:
            Logger.error(f"查找元素失败 ({by}={value}): {e}")
            return []