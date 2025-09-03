"""浏览器配置示例

展示不同场景下的浏览器配置方案
"""

# 默认配置 - 使用Playwright（推荐）
DEFAULT_CONFIG = {
    "driver_type": "playwright",
    "browser_type": "chromium",
    "headless": True,
    "timeout": 30000,
    "viewport": {
        "width": 1920,
        "height": 1080
    }
}

# IE浏览器配置 - 使用Selenium
IE_CONFIG = {
    "driver_type": "selenium",
    "browser_type": "ie",
    "headless": False,  # IE不支持无头模式
    "timeout": 60,
    "driver_path": "drivers/IEDriverServer.exe",  # IE驱动路径
    "driver_options": {
        "ignoreProtectedModeSettings": True,
        "ignoreZoomSetting": True,
        "nativeEvents": False,
        "unexpectedAlertBehaviour": "accept",
        "elementScrollBehavior": 1,
        "requireWindowFocus": False
    }
}

# Chrome浏览器配置 - 使用Selenium
CHROME_SELENIUM_CONFIG = {
    "driver_type": "selenium",
    "browser_type": "chrome",
    "headless": True,
    "timeout": 30,
    "driver_path": "drivers/chromedriver.exe",  # Chrome驱动路径
    "driver_options": {
        "no-sandbox": None,
        "disable-dev-shm-usage": None,
        "disable-gpu": None,
        "window-size": "1920,1080"
    }
}

# Firefox浏览器配置 - 使用Selenium
FIREFOX_CONFIG = {
    "driver_type": "selenium",
    "browser_type": "firefox",
    "headless": True,
    "timeout": 30,
    "driver_path": "drivers/geckodriver.exe",  # Firefox驱动路径
    "driver_options": {
        "width": "1920",
        "height": "1080"
    }
}

# Edge浏览器配置 - 使用Selenium
EDGE_CONFIG = {
    "driver_type": "selenium",
    "browser_type": "edge",
    "headless": True,
    "timeout": 30,
    "driver_path": "drivers/msedgedriver.exe",  # Edge驱动路径
    "driver_options": {
        "no-sandbox": None,
        "disable-dev-shm-usage": None,
        "window-size": "1920,1080"
    }
}

# 开发环境配置
DEVELOPMENT_CONFIG = {
    "driver_type": "playwright",
    "browser_type": "chromium",
    "headless": False,  # 开发时显示浏览器
    "timeout": 60000,
    "slow_mo": 1000,  # 慢动作模式，便于调试
    "devtools": True   # 打开开发者工具
}

# 生产环境配置
PRODUCTION_CONFIG = {
    "driver_type": "playwright",
    "browser_type": "chromium",
    "headless": True,  # 生产环境无头模式
    "timeout": 30000,
    "viewport": {
        "width": 1920,
        "height": 1080
    },
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# 移动端模拟配置
MOBILE_CONFIG = {
    "driver_type": "playwright",
    "browser_type": "chromium",
    "headless": True,
    "timeout": 30000,
    "viewport": {
        "width": 375,
        "height": 667
    },
    "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
    "device_scale_factor": 2,
    "is_mobile": True,
    "has_touch": True
}

# 高性能配置（适用于批量处理）
HIGH_PERFORMANCE_CONFIG = {
    "driver_type": "playwright",
    "browser_type": "chromium",
    "headless": True,
    "timeout": 15000,
    "viewport": {
        "width": 1280,
        "height": 720
    },
    "args": [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-images",  # 禁用图片加载
        "--disable-javascript",  # 禁用JavaScript（如果不需要）
        "--disable-plugins",
        "--disable-extensions"
    ]
}

# 配置映射
CONFIG_MAP = {
    "default": DEFAULT_CONFIG,
    "ie": IE_CONFIG,
    "chrome_selenium": CHROME_SELENIUM_CONFIG,
    "firefox": FIREFOX_CONFIG,
    "edge": EDGE_CONFIG,
    "development": DEVELOPMENT_CONFIG,
    "production": PRODUCTION_CONFIG,
    "mobile": MOBILE_CONFIG,
    "high_performance": HIGH_PERFORMANCE_CONFIG
}


def get_config(config_name: str = "default"):
    """获取指定的配置
    
    Args:
        config_name: 配置名称
        
    Returns:
        dict: 配置字典
    """
    return CONFIG_MAP.get(config_name, DEFAULT_CONFIG)


def list_available_configs():
    """列出所有可用的配置
    
    Returns:
        list: 配置名称列表
    """
    return list(CONFIG_MAP.keys())


def print_config_info():
    """打印所有配置信息"""
    print("可用的浏览器配置:")
    print("=" * 50)
    
    for name, config in CONFIG_MAP.items():
        print(f"\n配置名称: {name}")
        print(f"驱动类型: {config['driver_type']}")
        print(f"浏览器类型: {config['browser_type']}")
        print(f"无头模式: {config.get('headless', 'N/A')}")
        print(f"超时时间: {config.get('timeout', 'N/A')}")
        
        if 'driver_path' in config:
            print(f"驱动路径: {config['driver_path']}")
        
        if 'viewport' in config:
            viewport = config['viewport']
            print(f"视口大小: {viewport['width']}x{viewport['height']}")
        
        print("-" * 30)


if __name__ == "__main__":
    print_config_info()