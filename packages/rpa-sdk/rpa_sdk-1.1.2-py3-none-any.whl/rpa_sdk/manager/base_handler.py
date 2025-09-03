"""
任务处理器基类
"""
import re
from abc import ABC, abstractmethod
from typing import Dict, Any, List

from ..kit.enums import MessageType
from ..kit.Utils import Logger


from .element_operations_interface import WebElementOperations
from .element_operations_factory import ElementOperationsFactory

class BaseHandler(ABC):
    """任务处理器基类"""
    TASK_NAME = None  # 子类必须重写
    FIELD_NAME = None
    def __init__(self, records: List, browser_manager, check_mode, db_manager, message_sender=None, result_sender=None, element_operations_impl=None):
        self.browser_manager = browser_manager
        self.message_sender = message_sender
        self.result_sender = result_sender
        self.db_manager = db_manager
        self.page = browser_manager.page if browser_manager else None
        self.check_mode = check_mode
        self.start_time = None
        self.total_records = 0
        self.processed_records = 0
        self.result = []
        
        # 初始化元素操作器
        if element_operations_impl:
            self.element_ops = ElementOperationsFactory.create_instance(element_operations_impl, page=self.page)
        else:
            self.element_ops = ElementOperationsFactory.create_instance(page=self.page)

        self.load_page()
        self.execute(records)


    @classmethod
    def get_task_name(cls) -> str:
        if cls.TASK_NAME is None:
            raise NotImplementedError(f"{cls.__name__} 必须定义 TASK_NAME")
        return cls.TASK_NAME

    @abstractmethod
    def load_page(self)-> bool:
        """加载任务数据的抽象方法，子类需要实现"""
        pass
    
    
    def _navigate_to_page(self, page_name: str) -> bool:
        """导航到指定页面"""
        try:
            # 发送导航开始消息
            if self.message_sender:
                self.message_sender(
                    MessageType.INFO,
                    f"导航到{page_name}"
                )

            success = self.load_page()

            if success:
                # 发送导航成功消息
                if self.message_sender:
                    self.message_sender(
                        MessageType.INFO,
                        f"成功导航到{page_name}"
                    )
                return True
            else:
                # 发送导航失败消息
                if self.message_sender:
                    self.message_sender(
                        MessageType.ERROR,
                        f"导航到{page_name}失败"
                    )
                return False

        except Exception as e:
            # 发送导航异常消息
            if self.message_sender:
                self.message_sender(
                    MessageType.ERROR,
                    f"导航到{page_name}异常",
                    {"status": "failed", "page": page_name, "error": str(e)}
                )
            return False
        

    def execute(self, records: List ):
        """
        执行任务的抽象方法
        Args:
            records:  Dict[str, Any] - 需要处理的记录列表
        """
        # 检查中止标志
        if self._check_abort_flag():
            Logger.info("任务在开始前被中止")
            return

        self._navigate_to_page(self.TASK_NAME)

        # 再次检查中止标志
        if self._check_abort_flag():
            Logger.info("任务在导航后被中止")
            self._cleanup_on_abort()
            return

        total = len(records)
        for index, record in enumerate(records):
            # 每条记录处理前检查中止标志
            if self._check_abort_flag():
                Logger.info(f"任务在处理第 {index+1}/{total} 条记录前被中止")
                self._cleanup_on_abort()
                return
            Logger.info(f"开始处理第 {index+1}/{total} 条记录,{record['idcard']},{record['name']}")
            self.message_sender(MessageType.INFO, f"开始处理第 {index+1}/{total} 条记录,{record['idcard']},{record['name']}")
            self.result = []
            ret = self.process_single_record(record, index, total)
            if ret:
                self.result_sender(record[self.FIELD_NAME], self.TASK_NAME, 1, ','.join(self.result))
            else:
                self.result_sender(record[self.FIELD_NAME], self.TASK_NAME, 0, ','.join(self.result))

        self.message_sender(MessageType.INFO, f"处理完成")

        # 任务完成后清理浏览器资源
        self._cleanup_after_completion()

    def _check_abort_flag(self):
        """检查任务是否应该中止"""
        try:
            if hasattr(self, 'task_abort_flag') and callable(self.task_abort_flag):
                return self.task_abort_flag()
            return False
        except:
            return False

    def _cleanup_on_abort(self):
        """任务中止时的清理操作"""
        try:
            Logger.info("任务被中止，开始清理浏览器资源...")

            # 在任务线程中安全地清理浏览器
            if hasattr(self, 'browser_manager') and self.browser_manager:
                self.browser_manager.cleanup()
                Logger.info("浏览器资源清理完成")

            # 发送中止完成消息
            if hasattr(self, 'message_sender') and self.message_sender:
                self.message_sender(MessageType.COMPLETED, "任务已中止，浏览器已关闭")

        except Exception as e:
            Logger.error("任务中止清理时出现异常", exception=e)
            if hasattr(self, 'message_sender') and self.message_sender:
                self.message_sender(MessageType.ERROR, f"任务中止清理异常: {str(e)}")

    def _cleanup_after_completion(self):
        """任务完成后的清理操作"""
        try:
            Logger.info("任务完成，开始清理浏览器资源...")

            # 在任务线程中安全地清理浏览器
            if hasattr(self, 'browser_manager') and self.browser_manager:
                self.browser_manager.cleanup()
                Logger.info("任务完成后浏览器资源清理完成")

            # 发送清理完成消息
            if hasattr(self, 'message_sender') and self.message_sender:
                self.message_sender(MessageType.INFO, "任务完成，浏览器已关闭")

        except Exception as e:
            Logger.error("任务完成后清理时出现异常", exception=e)
            if hasattr(self, 'message_sender') and self.message_sender:
                self.message_sender(MessageType.ERROR, f"任务完成后清理异常: {str(e)}")
    
    @abstractmethod
    def process_single_record(self, record: Dict[str, Any], index: int, total: int) -> bool:
        """
        处理单条记录的抽象方法

        Args:
            record: 单条记录数据
            index: 当前记录的索引（从0开始）
            total: 总记录数

        Returns:
            bool: 处理是否成功
        """
        pass
    
    # 元素操作方法的便捷访问（保持向后兼容性）
    def single_choice(self, selector: str, labs: List[str], val: str) -> bool:
        """单选操作"""
        return self.element_ops.single_choice(selector, labs, val)
    
    def single_choice_with_other(self, selector: str, selector_other: str, labs: List[str], val: str) -> bool:
        """带其他选项的单选操作"""
        return self.element_ops.single_choice_with_other(selector, selector_other, labs, val)
        
    def get_selected_single_choice(self, selector: str, labs: List[str], val: str) -> str:
        """获取单选选中值"""
        return self.element_ops.get_selected_single_choice(selector, labs, val)
    

    def multiple_choice(self, selector: str, labs: List[str], vals: str) -> bool:
        """多选操作"""
        return self.element_ops.multiple_choice(selector, labs, vals)
    
    def multiple_choice_with_other(self, selector: str, selector_other: str, labs: List[str], vals: str) -> bool:
        """带其他选项的多选操作"""
        return self.element_ops.multiple_choice_with_other(selector, selector_other, labs, vals)
    
    def set_combobox(self, selector: str, val: str, fuzzy_match: bool = False) -> bool:
        """设置下拉框值"""
        return self.element_ops.set_combobox(selector, val, fuzzy_match)
    
    def set_combobox_with_icon(self, selector: str, val: str, fuzzy_match: bool = False) -> bool:
        """通过图标设置下拉框值"""
        return self.element_ops.set_combobox_with_icon(selector, val, fuzzy_match)
    
    def wait_load(self, msg: str = None):
        """等待加载完成"""
        return self.element_ops.wait_load(msg)
    
    def close_dialog(self, btn_text: str = "确定", msg: str = None) -> bool:
        """关闭对话框"""
        return self.element_ops.close_dialog(btn_text, msg)
    
    def wait_for_input_has_value(self, selector: str, timeout: int = 5000) -> bool:
        """等待输入框有值"""
        return self.element_ops.wait_for_input_has_value(selector, timeout)
    

