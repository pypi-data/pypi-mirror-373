"""元素操作接口定义

定义了页面元素操作的抽象接口，允许用户自定义实现
"""
from abc import ABC, abstractmethod
from typing import List


class WebElementOperations(ABC):
    """元素操作抽象接口
    
    定义了所有页面元素操作的标准接口，用户可以继承此接口
    实现自定义的元素操作逻辑
    """
    
    @abstractmethod
    def single_choice(self, selector: str, labs: List[str], val: str) -> str:
        """单选操作
        
        :param selector: 单选按钮组的选择器
        :param labs: 单选按钮的标签数组
        :param val: 需要选定的值
        :return: 被选中单选按钮的 value 属性值
        """
        pass
    
    @abstractmethod
    def get_selected_single_choice(self, selector: str, labs: List[str], val: str) -> str:
        """获取单选选中值
        
        :param selector: 单选按钮组的选择器
        :param labs: 单选按钮的标签数组
        :param val: 参考值
        :return: 当前选中的值
        """
        pass
    
    @abstractmethod
    def single_choice_with_other(self, selector: str, selector_other: str, labs: List[str], val: str) -> str:
        """带其他选项的单选操作
        
        :param selector: 单选按钮组的选择器
        :param selector_other: 其他选项输入框的选择器
        :param labs: 单选按钮的标签数组
        :param val: 需要选定的值（可包含=分隔的附加内容）
        :return: 操作结果
        """
        pass
    
    @abstractmethod
    def multiple_choice(self, selector: str, labs: List[str], vals: str):
        """多选操作
        
        :param selector: 多选框组的选择器
        :param labs: 多选框的标签数组
        :param vals: 要选中的值的字符串（逗号分隔）
        """
        pass
    
    @abstractmethod
    def multiple_choice_with_other(self, selector: str, selector_other: str, labs: List[str], vals: str):
        """带其他选项的多选操作
        
        :param selector: 多选框组的选择器
        :param selector_other: 其他选项输入框的选择器
        :param labs: 多选框的标签数组
        :param vals: 要选中的值的字符串
        """
        pass
    
    @abstractmethod
    def set_combobox(self, selector: str, val: str, fuzzy_match: bool = False):
        """设置下拉框值
        
        :param selector: 下拉框的选择器
        :param val: 要选择的值
        :param fuzzy_match: 是否进行模糊匹配
        """
        pass
    
    @abstractmethod
    def set_combobox_with_icon(self, selector: str, val: str, fuzzy_match: bool = False):
        """通过图标设置下拉框值
        
        :param selector: 下拉框的选择器
        :param val: 要选择的值
        :param fuzzy_match: 是否进行模糊匹配
        """
        pass
    
    @abstractmethod
    def wait_load(self, msg: str = None):
        """等待加载完成
        
        :param msg: 可选的加载消息
        """
        pass
    
    @abstractmethod
    def close_dialog(self, btn_text: str = "确定", msg: str = None) -> bool:
        """关闭对话框
        
        :param btn_text: 按钮文本
        :param msg: 可选的消息文本
        :return: 是否成功关闭
        """
        pass
    
    @abstractmethod
    def wait_for_input_has_value(self, selector: str, timeout: int = 5000) -> bool:
        """等待输入框有值
        
        :param selector: 输入框选择器
        :param timeout: 超时时间（毫秒）
        :return: 是否成功等到值
        """
        pass
    