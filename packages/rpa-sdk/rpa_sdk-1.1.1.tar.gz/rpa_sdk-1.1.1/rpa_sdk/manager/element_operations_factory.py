"""元素操作工厂类

提供元素操作实现的创建和管理功能
"""
from typing import Type, Dict, Optional
from .element_operations_interface import WebElementOperations
from ..element.operations_gzby import GzbyElementOperations
from ..element.operations_gzzc import GzzcElementOperations
from ..element.operations_bjyd import BjydElementOperations
from ..element.operations_gzhz import GzhzElementOperations


class ElementOperationsFactory:
    """元素操作工厂类
    
    负责管理和创建不同的元素操作实现，支持用户注册自定义实现
    """
    
    _implementations: Dict[str, Type[WebElementOperations]] = {}
    _default_implementation = "default"
    
    @classmethod
    def register_implementation(cls, name: str, implementation: Type[WebElementOperations]):
        """注册元素操作实现
        
        :param name: 实现名称
        :param implementation: 实现类
        """
        if not issubclass(implementation, WebElementOperations):
            raise ValueError(f"实现类 {implementation.__name__} 必须继承自 WebElementOperations")
        
        cls._implementations[name] = implementation
    
    @classmethod
    def get_implementation(cls, name: str = None) -> Type[WebElementOperations]:
        """获取元素操作实现
        
        :param name: 实现名称，如果为None则返回默认实现
        :return: 实现类
        """
        if name is None:
            name = cls._default_implementation
        
        if name not in cls._implementations:
            raise ValueError(f"未找到名为 '{name}' 的元素操作实现")
        
        return cls._implementations[name]
    
    @classmethod
    def create_instance(cls, name: str = None, **kwargs) -> WebElementOperations:
        """创建元素操作实例
        
        :param name: 实现名称
        :param kwargs: 构造参数
        :return: 元素操作实例
        """
        implementation_class = cls.get_implementation(name)
        return implementation_class(**kwargs)
    
    @classmethod
    def set_default_implementation(cls, name: str):
        """设置默认实现
        
        :param name: 实现名称
        """
        if name not in cls._implementations:
            raise ValueError(f"未找到名为 '{name}' 的元素操作实现")
        
        cls._default_implementation = name
    
    @classmethod
    def list_implementations(cls) -> Dict[str, Type[WebElementOperations]]:
        """列出所有已注册的实现
        
        :return: 实现字典
        """
        return cls._implementations.copy()
    
    @classmethod
    def unregister_implementation(cls, name: str):
        """注销实现
        
        :param name: 实现名称
        """
        if name == cls._default_implementation:
            raise ValueError(f"不能注销默认实现 '{name}'")
        
        if name in cls._implementations:
            del cls._implementations[name]


# 注册系统特定实现（使用gzby作为默认实现）
ElementOperationsFactory.register_implementation("default", GzbyElementOperations)

# 注册其他系统特定实现
ElementOperationsFactory.register_implementation("gzby", GzbyElementOperations)
ElementOperationsFactory.register_implementation("gzzc", GzzcElementOperations)
ElementOperationsFactory.register_implementation("bjyd", BjydElementOperations)
ElementOperationsFactory.register_implementation("gzhz", GzhzElementOperations)