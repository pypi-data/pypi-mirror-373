"""
浏览器管理器 - 同步模式
负责管理浏览器实例的生命周期
"""

from typing import Optional

try:
    from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext, Playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    sync_playwright = None
    Page = None
    Browser = None
    BrowserContext = None
    Playwright = None

from .base_browser_manager import BaseBrowserManager, DriverType, BrowserType
from ..kit.Utils import get_screen_size, Logger
from ..kit.enums import MessageType
# 移除对不存在模块的依赖


class PlaywrightBrowserManager(BaseBrowserManager):
    """Playwright浏览器管理器 - 同步模式"""
    
    def __init__(self, message_sender=None):
        super().__init__(DriverType.PLAYWRIGHT, message_sender)
        
        # Playwright 相关
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        # 检查 Playwright 是否可用
        if not HAS_PLAYWRIGHT:
            Logger.error("Playwright 未安装，请运行: pip install playwright && playwright install")
    
    def initialize(self, 
                  headless: bool = True, 
                  url: str = None,
                  browser_type: BrowserType = BrowserType.CHROMIUM,
                  **kwargs) -> bool:
        """初始化浏览器"""
        if not HAS_PLAYWRIGHT:
            Logger.error("Playwright 未安装，无法初始化浏览器")
            return False
        
        try:
            Logger.info(f"初始化浏览器 (headless={headless})")
            
            # 启动 Playwright
            self.playwright = sync_playwright().start()
            
            # 获取屏幕尺寸
            width, height = get_screen_size()
            
            # 启动浏览器
            self.browser = self.playwright.chromium.launch(
                headless=headless,
                args=['--no-sandbox', '--disable-dev-shm-usage'] if headless else []
            )
            
            # 创建浏览器上下文
            self.context = self.browser.new_context(
                viewport={'width': width, 'height': height - 170}
            )
            
            # 创建页面
            self.page = self.context.new_page()
            
            # 设置超时（增加到60秒）
            self.page.set_default_timeout(60000)
            
            # 导航到目标页面（如果提供了URL）
            if url:
                Logger.info(f"导航到: {url}")
                self.page.goto(url, timeout=60000)
                
                # 等待页面加载（增加到60秒）
                self.page.wait_for_load_state("networkidle", timeout=60000)
            
            self.is_initialized = True
            Logger.info("浏览器初始化成功")
            
            # 发送成功消息
            if self.message_sender:
                self.message_sender(
                    MessageType.INFO,
                    "浏览器初始化成功",
                    {"url": url, "headless": headless}
                )
            
            return True
            
        except Exception as e:
            Logger.error(f"浏览器初始化失败: {e}")
            self.cleanup()
            
            # 发送失败消息
            if self.message_sender:
                self.message_sender(
                    MessageType.ERROR,
                    f"浏览器初始化失败: {str(e)}",
                    {"error": str(e)}
                )
            
            return False
    
    def login(self, username: str, password: str, login_func=None) -> bool:
        """登录系统"""
        if not self.is_initialized or not self.page:
            Logger.error("浏览器未初始化，无法登录")
            return False
        
        if not login_func:
            Logger.error("未提供登录函数")
            return False
        
        try:
            Logger.info(f"开始登录: {username}")
            
            # 使用传入的登录函数
            success = login_func(self.page, username, password)
            
            if success:
                Logger.info("登录成功")
                
                # 发送成功消息
                if self.message_sender:
                    self.message_sender(
                        MessageType.INFO,
                        "登录成功",
                        {"username": username}
                    )
                
                return True
            else:
                Logger.error("❌ 登录失败")
                
                # 发送失败消息
                if self.message_sender:
                    self.message_sender(
                        MessageType.ERROR,
                        "登录失败",
                        {"username": username}
                    )
                
                return False
                
        except Exception as e:
            Logger.error(f"登录过程中出现异常: {e}")
            
            # 发送异常消息
            if self.message_sender:
                self.message_sender(
                    MessageType.ERROR,
                    f"登录异常: {str(e)}",
                    {"username": username, "error": str(e)}
                )
            
            return False
    
    def navigate_to(self, url: str) -> bool:
        """导航到指定URL"""
        if not self.is_initialized or not self.page:
            Logger.error("浏览器未初始化，无法导航")
            return False
        
        try:
            Logger.info(f"导航到: {url}")
            self.page.goto(url)
            self.page.wait_for_load_state("networkidle", timeout=30000)
            Logger.info("导航成功")
            return True
            
        except Exception as e:
            Logger.error(f"导航失败: {e}")
            return False
    
    def cleanup(self):
        """清理浏览器资源"""
        Logger.info("开始清理浏览器资源...")

        try:
            # 关闭页面
            if self.page:
                try:
                    self.page.close()
                    Logger.debug("页面已关闭")
                except Exception as e:
                    Logger.warning(f"关闭页面时出现异常: {e}")
                finally:
                    self.page = None

            # 关闭上下文
            if self.context:
                try:
                    self.context.close()
                    Logger.debug("浏览器上下文已关闭")
                except Exception as e:
                    Logger.warning(f"关闭浏览器上下文时出现异常: {e}")
                finally:
                    self.context = None

            # 关闭浏览器
            if self.browser:
                try:
                    self.browser.close()
                    Logger.debug("浏览器已关闭")
                except Exception as e:
                    Logger.warning(f"关闭浏览器时出现异常: {e}")
                finally:
                    self.browser = None

            # 停止 Playwright
            if self.playwright:
                try:
                    self.playwright.stop()
                    Logger.debug("Playwright 已停止")
                except Exception as e:
                    Logger.warning(f"停止 Playwright 时出现异常: {e}")
                finally:
                    self.playwright = None

            self.is_initialized = False
            Logger.info("浏览器资源清理完成")

        except Exception as e:
            Logger.error(f"清理浏览器资源时出现异常: {e}")
            # 强制重置状态
            self.page = None
            self.context = None
            self.browser = None
            self.playwright = None
            self.is_initialized = False
    
    def force_close(self):
        """强制关闭浏览器（用于任务中止）"""
        Logger.info("强制关闭浏览器...")

        try:
            # 尝试安全关闭
            if self.page:
                try:
                    # 先尝试关闭页面
                    self.page.close()
                    Logger.info("页面已关闭")
                except Exception as e:
                    Logger.warning(f"关闭页面时出现异常: {e}")
                finally:
                    self.page = None

            if self.context:
                try:
                    # 关闭上下文
                    self.context.close()
                    Logger.info("浏览器上下文已关闭")
                except Exception as e:
                    Logger.warning(f"关闭浏览器上下文时出现异常: {e}")
                finally:
                    self.context = None

            if self.browser:
                try:
                    # 关闭浏览器
                    self.browser.close()
                    Logger.info("浏览器已关闭")
                except Exception as e:
                    Logger.warning(f"关闭浏览器时出现异常: {e}")
                finally:
                    self.browser = None

            # 强制重置状态
            self.is_initialized = False
            Logger.info("✅ 浏览器强制关闭完成")

        except Exception as e:
            Logger.error(f"强制关闭浏览器时出现异常: {e}")
            # 强制重置所有状态
            self.page = None
            self.context = None
            self.browser = None
            self.is_initialized = False
            Logger.info("✅ 浏览器状态已强制重置")
    
    def get_page(self):
        """获取页面对象
        
        Returns:
            Playwright Page对象
        """
        return self.page
    
    def is_browser_running(self) -> bool:
        """检查浏览器是否正在运行"""
        return self.is_initialized and self.page is not None
      
    # 上下文管理器支持
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
