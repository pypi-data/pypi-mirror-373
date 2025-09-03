"""项目自定义元素操作实现

为当前项目定制的元素操作实现"""

import sys
sys.path.insert(0, '..')

from typing import List
from playwright.sync_api import Page
from rpa_sdk import WebElementOperations, ElementOperationsFactory


class ProjectElementOperations(WebElementOperations):
    """项目自定义元素操作实现
    
    继承 WebElementOperations 接口，实现项目特定的元素操作逻辑
    适用于中医体质辨识等业务场景
    """
    
    def __init__(self, page: Page):
        """初始化自定义元素操作类
        
        :param page: Playwright页面对象
        """
        self.page = page
        print(f"[ProjectElementOperations] 初始化完成，页面对象: {type(self.page)}")
        print(f"[ProjectElementOperations] 支持中医体质辨识等业务场景的元素操作")
    
    def single_choice(self, selector: str, labs: List[str], val: str) -> str:
        """自定义单选操作实现
        
        :param selector: 单选按钮组的选择器
        :param labs: 单选按钮的标签数组
        :param val: 需要选定的值
        :return: 被选中单选按钮的 value 属性值
        """
        print(f"[ProjectElementOperations] 执行单选操作: {val} in {labs}")
        
        # 参数校验
        if val not in labs:
            raise ValueError(f"值 '{val}' 不在选项列表 {labs} 中")
        
        # 获取目标选项的索引
        target_index = labs.index(val)
        
        try:
            # 定位所有单选按钮元素
            radio_buttons = self.page.locator(selector)
            actual_count = radio_buttons.count()
            
            if target_index >= actual_count:
                raise IndexError(f"选项索引 {target_index} 超出实际单选按钮数量 ({actual_count})")
            
            # 点击目标单选按钮
            target_radio = radio_buttons.nth(target_index)
            target_radio.click()
            
            # 获取并返回value属性
            value = target_radio.get_attribute('value') or str(target_index)
            print(f"[ProjectElementOperations] 单选操作成功，选中值: {value}")
            return value
            
        except Exception as e:
            print(f"[ProjectElementOperations] 单选操作失败: {e}")
            raise
    
    def get_selected_single_choice(self, selector: str, labs: List[str], val: str) -> str:
        """获取当前选中的单选值
        
        :param selector: 单选按钮组的选择器
        :param labs: 单选按钮的标签数组
        :param val: 参考值
        :return: 当前选中的值
        """
        print(f"[ProjectElementOperations] 获取单选选中值")
        
        try:
            # 查找选中的单选按钮
            selected_radio = self.page.locator(f"{selector}:checked")
            
            if selected_radio.count() == 0:
                print("[ProjectElementOperations] 没有选中的单选按钮")
                return ""
            
            # 获取选中按钮的value属性
            value = selected_radio.get_attribute('value') or ""
            print(f"[ProjectElementOperations] 当前选中值: {value}")
            return value
            
        except Exception as e:
            print(f"[ProjectElementOperations] 获取选中值失败: {e}")
            return ""
    
    def single_choice_with_other(self, selector: str, selector_other: str, labs: List[str], val: str) -> str:
        """带其他选项的单选操作
        
        :param selector: 单选按钮组的选择器
        :param selector_other: 其他选项输入框的选择器
        :param labs: 单选按钮的标签数组
        :param val: 需要选定的值（可包含=分隔的附加内容）
        :return: 操作结果
        """
        print(f"[ProjectElementOperations] 执行带其他选项的单选操作: {val}")
        
        try:
            # 检查是否包含其他选项的内容
            if '=' in val:
                option_val, other_content = val.split('=', 1)
                
                # 先选择对应的单选按钮
                if option_val in labs:
                    self.single_choice(selector, labs, option_val)
                    
                    # 如果是"其他"选项，填写输入框
                    if option_val == "其他" or option_val.lower() == "other":
                        other_input = self.page.locator(selector_other)
                        if other_input.count() > 0:
                            other_input.fill(other_content)
                            print(f"[ProjectElementOperations] 填写其他选项内容: {other_content}")
                
                return f"{option_val}={other_content}"
            else:
                # 普通单选操作
                return self.single_choice(selector, labs, val)
                
        except Exception as e:
            print(f"[ProjectElementOperations] 带其他选项的单选操作失败: {e}")
            raise
    
    def click_element(self, selector, timeout=10000):
        """点击元素
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
            
        Returns:
            bool: 操作是否成功
        """
        print(f"[ProjectElementOperations] 点击元素: {selector}")
        try:
            element = self.page.locator(selector)
            element.click(timeout=timeout)
            return True
        except Exception as e:
            print(f"[ProjectElementOperations] 点击元素失败: {e}")
            return False
    
    def input_text(self, selector, text, timeout=10000):
        """输入文本
        
        Args:
            selector: 元素选择器
            text: 要输入的文本
            timeout: 超时时间（毫秒）
            
        Returns:
            bool: 操作是否成功
        """
        print(f"[ProjectElementOperations] 输入文本到 {selector}: {text}")
        try:
            element = self.page.locator(selector)
            element.fill(text, timeout=timeout)
            return True
        except Exception as e:
            print(f"[ProjectElementOperations] 输入文本失败: {e}")
            return False
    
    def close_dialog(self, timeout=10000):
        """关闭对话框
        
        Args:
            timeout: 超时时间（毫秒）
            
        Returns:
            bool: 操作是否成功
        """
        print(f"[ProjectElementOperations] 关闭对话框")
        try:
            # 尝试常见的对话框关闭按钮选择器
            close_selectors = [
                ".modal .close",
                ".dialog .close",
                "[data-dismiss='modal']",
                ".ant-modal-close",
                ".el-dialog__close"
            ]
            
            for selector in close_selectors:
                close_btn = self.page.locator(selector)
                if close_btn.count() > 0:
                    close_btn.click(timeout=timeout)
                    return True
            
            # 如果没有找到关闭按钮，尝试按ESC键
            self.page.keyboard.press("Escape")
            return True
            
        except Exception as e:
            print(f"[ProjectElementOperations] 关闭对话框失败: {e}")
            return False
    
    def multiple_choice(self, selector, choice_value, timeout=10000):
        """多选操作
        
        Args:
            selector: 元素选择器
            choice_value: 选择值
            timeout: 超时时间（毫秒）
            
        Returns:
            bool: 操作是否成功
        """
        print(f"[ProjectElementOperations] 多选操作 {selector}: {choice_value}")
        try:
            checkboxes = self.page.locator(selector)
            if isinstance(choice_value, list):
                for value in choice_value:
                    checkbox = checkboxes.filter(has_text=value).first
                    if not checkbox.is_checked():
                        checkbox.click(timeout=timeout)
            else:
                checkbox = checkboxes.filter(has_text=choice_value).first
                if not checkbox.is_checked():
                    checkbox.click(timeout=timeout)
            return True
        except Exception as e:
            print(f"[ProjectElementOperations] 多选操作失败: {e}")
            return False
    
    def multiple_choice_with_other(self, selector, choice_value, other_text="", timeout=10000):
        """带其他选项的多选操作
        
        Args:
            selector: 元素选择器
            choice_value: 选择值
            other_text: 其他选项文本
            timeout: 超时时间（毫秒）
            
        Returns:
            bool: 操作是否成功
        """
        print(f"[ProjectElementOperations] 带其他选项的多选操作 {selector}: {choice_value}, 其他: {other_text}")
        try:
            # 先执行普通多选操作
            result = self.multiple_choice(selector, choice_value, timeout)
            
            # 如果有其他选项文本，填写到其他选项输入框
            if other_text and ("其他" in str(choice_value) or "other" in str(choice_value).lower()):
                other_input = self.page.locator(f"{selector}_other").or_(self.page.locator(".other-input"))
                if other_input.count() > 0:
                    other_input.fill(other_text, timeout=timeout)
            
            return result
        except Exception as e:
            print(f"[ProjectElementOperations] 带其他选项的多选操作失败: {e}")
            return False
    
    def set_combobox(self, selector, value, timeout=10000):
        """设置下拉框
        
        Args:
            selector: 元素选择器
            value: 设置值
            timeout: 超时时间（毫秒）
            
        Returns:
            bool: 操作是否成功
        """
        print(f"[ProjectElementOperations] 设置下拉框 {selector}: {value}")
        try:
            combobox = self.page.locator(selector)
            combobox.click(timeout=timeout)
            
            # 等待下拉选项出现并选择
            option = self.page.locator(f"option[value='{value}']")
            if option.count() == 0:
                option = self.page.locator(f"li:has-text('{value}')")
            
            if option.count() > 0:
                option.click(timeout=timeout)
                return True
            else:
                # 如果是可编辑的下拉框，直接输入值
                combobox.fill(value, timeout=timeout)
                return True
                
        except Exception as e:
            print(f"[ProjectElementOperations] 设置下拉框失败: {e}")
            return False
    
    def set_combobox_with_icon(self, selector, value, timeout=10000):
        """设置带图标的下拉框
        
        Args:
            selector: 元素选择器
            value: 设置值
            timeout: 超时时间（毫秒）
            
        Returns:
            bool: 操作是否成功
        """
        print(f"[ProjectElementOperations] 设置带图标的下拉框 {selector}: {value}")
        try:
            # 先点击下拉框或其图标
            combobox = self.page.locator(selector)
            icon = combobox.locator(".icon, .arrow, .dropdown-icon").first
            
            if icon.count() > 0:
                icon.click(timeout=timeout)
            else:
                combobox.click(timeout=timeout)
            
            # 选择选项
            return self.set_combobox(selector, value, timeout)
            
        except Exception as e:
            print(f"[ProjectElementOperations] 设置带图标的下拉框失败: {e}")
            return False
    
    def wait_for_input_has_value(self, selector, timeout=10000):
        """等待输入框有值
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
            
        Returns:
            bool: 操作是否成功
        """
        print(f"[ProjectElementOperations] 等待输入框有值: {selector}")
        try:
            element = self.page.locator(selector)
            element.wait_for(state="visible", timeout=timeout)
            
            # 等待输入框有值
            def has_value():
                value = element.input_value()
                return value is not None and value.strip() != ""
            
            # 轮询检查是否有值
            import time
            start_time = time.time()
            while time.time() - start_time < timeout / 1000:
                if has_value():
                    return True
                time.sleep(0.1)
            
            return False
            
        except Exception as e:
            print(f"[ProjectElementOperations] 等待输入框有值失败: {e}")
            return False
    
    def wait_load(self, timeout=10000):
        """等待页面加载
        
        Args:
            timeout: 超时时间（毫秒）
            
        Returns:
            bool: 操作是否成功
        """
        print(f"[ProjectElementOperations] 等待页面加载")
        try:
            # 等待页面加载完成
            self.page.wait_for_load_state("networkidle", timeout=timeout)
            
            # 等待常见的加载指示器消失
            loading_selectors = [
                ".loading",
                ".spinner",
                ".ant-spin",
                ".el-loading-mask",
                "[data-loading='true']"
            ]
            
            for selector in loading_selectors:
                loading_element = self.page.locator(selector)
                if loading_element.count() > 0:
                    loading_element.wait_for(state="hidden", timeout=timeout)
            
            return True
            
        except Exception as e:
            print(f"[ProjectElementOperations] 等待页面加载失败: {e}")
            return False


def register_custom_operations():
    """注册自定义元素操作实现
    
    这个函数展示了如何将自定义实现注册到ElementOperationsFactory中
    """
    print("[ProjectElementOperations] 注册项目自定义元素操作实现")
    
    # 注册自定义实现
    ElementOperationsFactory.register_implementation(
        "project", 
        ProjectElementOperations
    )
    
    # 列出所有已注册的实现
    implementations = ElementOperationsFactory.list_implementations()
    print(f"[ProjectElementOperations] 已注册的实现: {list(implementations.keys())}")
    
    print("[ProjectElementOperations] 项目自定义元素操作注册完成")


def demo_usage():
    """演示如何使用自定义元素操作
    
    这个函数展示了注册和使用自定义元素操作的完整流程
    """
    print("=" * 50)
    print("项目自定义元素操作演示")
    print("=" * 50)
    
    # 1. 注册项目自定义实现
    register_custom_operations()
    
    # 2. 演示工厂方法
    try:
        # 获取项目自定义实现类
        ProjectClass = ElementOperationsFactory.get_implementation("project")
        print(f"获取到项目实现类: {ProjectClass.__name__}")
        
        print("\n使用示例:")
        print("project_ops = ElementOperationsFactory.create_instance('project', page=playwright_page)")
        print("result = project_ops.single_choice('.radio-group', ['选项1', '选项2'], '选项1')")
        
    except Exception as e:
        print(f"演示过程中出现错误: {e}")
    
    print("\n=" * 50)
    print("演示完成")
    print("=" * 50)


if __name__ == "__main__":
    # 运行演示
    demo_usage()