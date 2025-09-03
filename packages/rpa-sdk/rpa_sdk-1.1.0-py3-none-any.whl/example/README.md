# RPA SDK 使用示例

这个目录包含了使用 rpa_sdk 的完整示例，展示了如何在外部项目中使用和扩展 RPA SDK 的功能。

## 项目架构

本示例项目展示了如何在实际项目中组织代码，实现自定义元素操作和业务逻辑的分离：

```
example/
├── operations_registry.py      # 元素操作注册中心
├── custom_element_operations.py # 项目自定义元素操作实现
├── rpa_main.py               # RPA 客户端入口（集成元素操作注册）
├── browser_config_example.py  # 浏览器配置示例
├── script/                   # 任务处理器目录
│   └── script_tcmd.py        # 业务任务处理器
└── README.md                 # 本文档
```

## 📁 文件说明

### `operations_registry.py`
元素操作注册中心，负责：
- 注册项目自定义元素操作
- 提供默认元素操作名称
- 集中管理元素操作的初始化

### `custom_element_operations.py`
项目自定义元素操作实现，展示如何：
- 继承 `BaseElementOperations` 基类
- 实现针对中医体质辨识的元素操作逻辑
- 提供项目特定的元素查找和操作方法

### `script/script_tcmd.py`
中医体质辨识任务处理器，展示如何：
- 继承 `BaseHandler` 基类
- 自动使用项目自定义元素操作
- 实现具体的业务逻辑和页面操作
- 处理体检数据和用户交互
- 被RPAClient自动发现和注册



### `rpa_main.py`
RPA 客户端入口文件，集成了自定义元素操作注册，展示了：
- 在启动时自动注册项目自定义元素操作
- 如何配置和启动 RPA 客户端
- 支持 Playwright 和 Selenium 两种浏览器驱动
- 自定义登录函数的实现
- 命令行参数处理
- 信号处理和优雅退出

### `browser_config_example.py`
浏览器配置示例文件，提供了：
- 多种浏览器配置方案（Playwright、Selenium）
- 不同环境的配置模板（开发、生产、移动端）
- 高性能配置选项
- 配置获取和管理工具函数

## 🚀 快速开始

### 1. 运行 RPA 客户端（推荐）

```bash
# 运行 RPA 客户端（自动注册自定义元素操作）
python rpa_main.py

# 启用调试模式
python rpa_main.py --debug

# 指定自定义URL
python rpa_main.py --url "https://your-website.com"

# 自定义日志文件
python rpa_main.py --log-file "custom.log"
```

### 2. 运行其他示例

### 3. 测试自定义元素操作

```bash
# 运行自定义元素操作演示
python custom_element_operations.py
```

### 4. 查看浏览器配置选项

```bash
# 查看所有可用的浏览器配置
python browser_config_example.py
```

## 🏗️ 项目架构优势

### 1. 关注点分离
- **元素操作层**：`custom_element_operations.py` 专注于元素查找和操作
- **业务逻辑层**：`script_tcmd.py` 专注于业务流程和数据处理
- **注册管理层**：`operations_registry.py` 负责组件注册和配置

### 2. 依赖注入
- 任务处理器通过构造函数接收元素操作实现
- 支持运行时切换不同的元素操作实现
- 便于单元测试和模拟测试

### 3. 扩展性
- 可以轻松添加新的元素操作实现
- 支持多种业务场景的处理器
- 配置驱动的组件选择

### 4. 学习业务处理器实现

**script_tcmd.py** 展示了完整的业务处理器实现：
- 继承 `BaseHandler` 基类
- 自动注入项目元素操作
- 实现具体的业务逻辑
- 处理页面加载和数据录入
- 与 Web 元素进行交互

## 🔧 配置说明

### 浏览器配置

#### 在 rpa_main.py 中使用配置

你可以选择两种浏览器配置方案：

**方案1: Playwright (推荐)**
```python
browser_config = {
    "driver_type": "playwright",
    "browser_type": "chromium",  # chromium, chrome, firefox, safari, ie, edge
    "headless": False,
}
```

**方案2: Selenium IE**
```python
browser_config = {
    "driver_type": "selenium",
    "browser_type": "ie",
    "headless": False,
    # "driver_path": "path/to/IEDriverServer.exe",
}
```

#### 使用预定义配置

`browser_config_example.py` 提供了多种预定义配置：

```python
from browser_config_example import get_config

# 使用默认配置
config = get_config("default")

# 使用开发环境配置
config = get_config("development")

# 使用生产环境配置
config = get_config("production")

# 使用移动端配置
config = get_config("mobile")

# 使用高性能配置
config = get_config("high_performance")
```

### 自定义登录函数

根据你的目标网站修改 `custom_login_function`：

```python
def custom_login_function(page, username, password):
    # 根据实际网站的登录页面结构修改选择器
    page.fill('input[name="username"]', username)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    
    # 等待登录成功的标志元素
    page.wait_for_selector('.user-dashboard', timeout=10000)
    return True
```

## 🎯 扩展元素操作

### 创建自定义实现

1. **继承接口**：
```python
from rpa_sdk import WebElementOperations

class MyCustomOperations(WebElementOperations):
    def __init__(self, page):
        self.page = page
    
    def single_choice(self, selector, labs, val):
        # 实现你的自定义逻辑
        pass
```

2. **注册实现**：
```python
from rpa_sdk import ElementOperationsFactory

ElementOperationsFactory.register_implementation(
    "my_custom", 
    MyCustomOperations
)
```

3. **使用自定义实现**：
```python
# 创建实例
custom_ops = ElementOperationsFactory.create_instance(
    "my_custom", 
    page=playwright_page
)

# 使用自定义操作
result = custom_ops.single_choice(".radio-group", ["选项1", "选项2"], "选项1")
```

## 📋 接口方法说明

`WebElementOperations` 接口包含以下主要方法：

- `single_choice(selector, labs, val)` - 单选操作
- `get_selected_single_choice(selector, labs, val)` - 获取选中值
- `single_choice_with_other(selector, selector_other, labs, val)` - 带其他选项的单选

更多方法请参考接口定义文件。

## 🛠️ 开发建议

1. **错误处理**：在自定义实现中添加适当的异常处理
2. **日志记录**：使用 `Logger` 记录操作日志
3. **测试验证**：为自定义实现创建测试用例
4. **文档注释**：为自定义方法添加详细的文档字符串

## 📞 支持

如果在使用过程中遇到问题，请参考：
- RPA SDK 主要文档
- 接口定义文件
- 现有实现示例

---

**注意**：这些示例文件展示了如何在外部项目中使用 rpa_sdk，实际使用时请根据你的具体需求进行调整。