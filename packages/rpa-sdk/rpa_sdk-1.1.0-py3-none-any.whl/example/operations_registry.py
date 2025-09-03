"""元素操作注册模块

负责注册项目中的自定义元素操作实现
"""

from rpa_sdk import ElementOperationsFactory
from custom_element_operations import ProjectElementOperations


def register_project_operations():
    """注册项目的自定义元素操作
    
    这个函数应该在应用启动时调用，用于注册项目特定的元素操作实现
    """
    print("[OperationsRegistry] 开始注册项目自定义元素操作...")
    
    # 注册项目自定义元素操作
    ElementOperationsFactory.register_implementation(
        "project",  # 注册名称
        ProjectElementOperations  # 实现类
    )
    
    # 可以注册多个不同的实现
    # ElementOperationsFactory.register_implementation(
    #     "project_mobile",  # 移动端专用实现
    #     ProjectMobileElementOperations
    # )
    
    print("[OperationsRegistry] 项目元素操作注册完成")
    
    # 显示已注册的实现
    implementations = ElementOperationsFactory.list_implementations()
    print(f"[OperationsRegistry] 当前已注册的实现: {list(implementations.keys())}")


def get_project_operations_name():
    """获取项目默认的元素操作实现名称
    
    Returns:
        str: 元素操作实现名称
    """
    return "project"


def initialize_operations():
    """初始化元素操作
    
    应用启动时调用此函数来完成元素操作的初始化
    """
    register_project_operations()
    return get_project_operations_name()