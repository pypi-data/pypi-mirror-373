"""
RPA客户端主入口文件
这个文件不是SDK的一部分，而是使用SDK的示例入口文件
"""

import sys
import os
import signal
import argparse
from typing import Dict, Any

# 添加父目录到Python路径，以便导入rpa_sdk
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rpa_sdk.rpa_client import RPAClient
from rpa_sdk.kit.Utils import Logger
from operations_registry import initialize_operations


def custom_login_function(page, username, password):
    """
    自定义登录函数
    根据具体网站的登录页面结构来实现
    """
    try:
        # 示例：根据实际网站修改选择器
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')
        
        # 等待登录成功的标志元素出现
        page.wait_for_selector('.user-dashboard', timeout=10000)
        return True
    except Exception as e:
        Logger.error(f"登录失败: {e}")
        return False


def get_rpa_config():
    """
    获取RPA配置
    在这里定义默认的URL、登录函数和浏览器驱动配置
    """
    # 基础配置
    config = {
        "default_url": "https://your-target-website.com/login",
        "default_login_func": custom_login_function
    }
    
    # 浏览器驱动配置 - 可以根据需要修改这些配置
    # 方案1: 使用 Playwright (推荐)
    browser_config = {
        "driver_type": "playwright",  # 可选: playwright, selenium
        "browser_type": "chromium",   # 可选: chromium, chrome, firefox, safari, ie, edge
        "headless": False,             # 是否启用无头模式
        # "driver_path": "",          # 可选: 指定驱动程序路径
    }
    
    # 方案2: 使用 Selenium IE (如需要IE浏览器支持，取消注释下面的配置)
    # browser_config = {
    #     "driver_type": "selenium",     # 使用selenium驱动
    #     "browser_type": "ie",          # 使用IE浏览器
    #     "headless": False,             # IE不支持无头模式
    #     # "driver_path": "path/to/IEDriverServer.exe",  # IE驱动程序路径
    # }
    
    # 如果使用IE浏览器，应用推荐配置
    if browser_config.get('browser_type') == 'ie':
        from rpa_sdk.manager import BrowserFactory
        ie_config = BrowserFactory.get_recommended_config_for_ie()
        # 合并IE推荐配置，但保留用户指定的参数
        for key, value in ie_config.items():
            if key not in browser_config:
                browser_config[key] = value
        browser_config['headless'] = False  # IE不支持无头模式
    
    # 合并浏览器配置到主配置
    config.update(browser_config)
    
    return config


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='RPA客户端')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--log-file', default='rpa.log', help='日志文件路径')
    parser.add_argument('--url', help='覆盖默认URL')
    
    args = parser.parse_args()

    # 创建RPA客户端实例
    client = None

    try:
        # 设置日志
        Logger.setup(debug_mode=args.debug, log_file=args.log_file)

        Logger.info("=" * 50)
        Logger.info("RPA客户端启动", extra_data={"debug_mode": args.debug, "log_file": args.log_file})
        Logger.info("=" * 50)
        
        # 初始化项目自定义元素操作（在创建RPAClient之前）
        Logger.info("初始化项目元素操作...")
        default_operations = initialize_operations()
        Logger.info(f"默认元素操作实现: {default_operations}")
        Logger.info("项目元素操作注册完成\n")

        # 获取配置（包含浏览器驱动配置）
        config = get_rpa_config()
        
        # 如果命令行指定了URL，则覆盖默认配置
        if args.url:
            config["default_url"] = args.url
            Logger.info(f"使用命令行指定的URL: {args.url}")
        
        # 输出当前配置信息
        Logger.info(f"驱动类型: {config.get('driver_type', 'playwright')}")
        Logger.info(f"浏览器类型: {config.get('browser_type', '自动选择')}")
        if config.get('driver_path'):
            Logger.info(f"驱动路径: {config['driver_path']}")
        Logger.info(f"无头模式: {config.get('headless', '自动选择')}")

        # 创建并启动RPA客户端
        client = RPAClient(config=config)

        # 设置信号处理器
        import signal
        def signal_handler(sig, frame):
            Logger.info("收到终止信号，正在停止客户端...")
            if client:
                client.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)  # 处理Ctrl+C
        signal.signal(signal.SIGTERM, signal_handler)  # 处理终止信号

        # 启动客户端（阻塞直到客户端停止）
        client.start()

    except KeyboardInterrupt:
        Logger.info("\n程序被用户中断")
        if client:
            client.stop()
    except Exception as e:
        Logger.error("程序异常退出", exception=e)
        if client:
            client.stop()
        sys.exit(1)
    finally:
        Logger.info("RPA客户端已退出")

if __name__ == "__main__":
    main()
