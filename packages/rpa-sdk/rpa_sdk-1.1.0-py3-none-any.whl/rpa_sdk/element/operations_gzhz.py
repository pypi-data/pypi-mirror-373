"""默认元素操作实现

提供标准的页面元素操作实现，适用于谷歌浏览器
"""
from typing import List
from playwright.sync_api import Page, expect
from ..manager.element_operations_interface import WebElementOperations


class GzhzElementOperations(WebElementOperations):
    """默认元素操作实现类
    
    实现了 WebElementOperations 接口的所有方法，
    提供标准的页面元素操作功能，专门针对谷歌浏览器优化。
    """
    
    def __init__(self, page: Page):
        """初始化元素操作类
        
        :param page: Playwright页面对象
        """
        self.page = page
    
    def single_choice(self, selector: str, labs: List[str], val: str) -> bool:
        """单选操作
        
        :param selector: 单选按钮组的选择器
        :param labs: 单选按钮的标签数组
        :param val: 需要选定的值
        :return: 操作是否成功
        """
        # 参数验证
        if not val or not labs:
            return False
        
        # 查找目标值在标签列表中的索引
        try:
            index = labs.index(val)
        except ValueError:
            return False
        
        # 定位单选组元素
        try:
            radio_group = self.page.locator(selector)
            if not radio_group.count():
                return False
            
            # 获取所有单选按钮
            radios = radio_group.locator('input[type="radio"]')
            radio_count = radios.count()
            
            # 验证索引范围
            if index >= radio_count:
                return False
            
            # 点击目标单选按钮
            target_radio = radios.nth(index)
            target_radio.click()
            
            return True
            
        except Exception as e:
             return False
    
    def wait_for_input_has_value(self, selector: str, timeout: int = 5000) -> bool:
        """等待输入框有值
        
        :param selector: 选择器
        :param timeout: 超时时间
        :return: 操作是否成功
        """
        try:
            # 等待输入框存在并且有值
            self.page.wait_for_function(
                f"document.querySelector('{selector}') && document.querySelector('{selector}').value !== ''",
                timeout=timeout
            )
            return True
        except Exception as e:
            print(f"等待输入框有值失败: {e}")
            return False

    
    def get_selected_single_choice(self, selector: str, labs: List[str], val: str) -> str:
        """获取被选中的单选按钮的值
        
        :param selector: 单选组的选择器
        :param labs: 选项标签列表
        :param val: 当前值（可能未使用）
        :return: 被选中单选按钮的 value 属性值
        """
        try:
            # 定位单选组元素
            radio_group = self.page.locator(selector)
            if not radio_group.count():
                return ""
            
            # 查找被选中的单选按钮
            checked_radio = radio_group.locator('input[type="radio"]:checked')
            if not checked_radio.count():
                return ""
            
            # 获取选中单选按钮的索引
            all_radios = radio_group.locator('input[type="radio"]')
            radio_count = all_radios.count()
            
            for i in range(radio_count):
                radio = all_radios.nth(i)
                if radio.is_checked():
                    # 返回对应标签列表中的值
                    if i < len(labs):
                        return labs[i]
                    break
            return ""
            
        except Exception as e:
            return ""
    
    def single_choice_with_other(self, selector: str, selector_other: str, labs: List[str], val: str) -> bool:
        """带其他选项的单选操作
        
        :param selector: 单选按钮组的选择器
        :param selector_other: 其他选项输入框的选择器
        :param labs: 单选按钮的标签数组
        :param val: 需要选定的值（可包含=分隔的附加内容）
        :return: 操作是否成功
        """
        if not val:
             return False
        
        # 解析输入值，格式可能是 "选项" 或 "其他:具体内容"
        other_value = None
        choice_value = val
        
        if ":" in val:
            parts = val.split(":", 1)
            choice_value = parts[0]
            other_value = parts[1] if len(parts) > 1 else ""
        
        # 验证选项是否在标签列表中
        if choice_value not in labs:
            return False
        
        # 执行基础单选操作
        self.single_choice(selector, labs, choice_value)
        
        # 如果有其他选项内容，填写到其他选项输入框
        if other_value is not None:
            try:
                other_input = self.page.locator(selector_other)
                if other_input.count():
                    other_input.fill(other_value)
                else:
                    return False
            except Exception as e:
                return False
        
        return True
    
    def multiple_choice(self, selector: str, labs: List[str], vals: str) -> bool:
        """多选操作
        
        :param selector: 多选框组的选择器
        :param labs: 多选框的标签数组
        :param vals: 要选中的值的字符串（逗号分隔）
        :return: 操作是否成功
        """
        if not vals or not labs:
            return False
        
        try:
            # 定位多选组元素
            checkbox_group = self.page.locator(selector)
            if not checkbox_group.count():
                return False
            
            # 分割输入值
            selected_values = [v.strip() for v in vals.split(",") if v.strip()]
            if not selected_values:
                return False
            
            # 获取所有复选框
            checkboxes = checkbox_group.locator('input[type="checkbox"]')
            checkbox_count = checkboxes.count()
            
            if checkbox_count != len(labs):
                return False
            
            # 遍历所有复选框，根据标签决定是否选中
            for i in range(checkbox_count):
                checkbox = checkboxes.nth(i)
                label = labs[i]
                
                should_be_checked = label in selected_values
                is_currently_checked = checkbox.is_checked()
                
                # 如果当前状态与期望状态不符，则点击切换
                if should_be_checked != is_currently_checked:
                    checkbox.click()
            
            return True
            
        except Exception as e:
            return False
    
    def multiple_choice_with_other(self, selector: str, selector_other: str, labs: List[str], vals: str) -> bool:
        """带其他选项的多选操作
        
        :param selector: 多选框组的选择器
        :param selector_other: 其他选项输入框的选择器
        :param labs: 多选框的标签数组
        :param vals: 要选中的值的字符串（多个值用逗号分隔，其他选项格式：其他:内容）
        :return: 操作是否成功
        """
        if not vals:
            return False
        
        # 解析输入值，分离标准选项和键值对
        standard_selections = []
        other_inputs = {}
        
        for item in vals.split(","):
            item = item.strip()
            if ":" in item:
                # 键值对格式：标签:值
                key, value = item.split(":", 1)
                key = key.strip()
                value = value.strip()
                if key in labs:
                    standard_selections.append(key)
                    other_inputs[key] = value
            else:
                # 普通选项
                if item in labs:
                    standard_selections.append(item)
        
        # 执行基础多选操作
        if standard_selections:
            base_vals = ",".join(standard_selections)
            self.multiple_choice(selector, labs, base_vals)
        
        # 处理其他选项的输入
        for label, value in other_inputs.items():
            try:
                # 查找对应的输入框
                other_input = self.page.locator(selector_other)
                if other_input.count():
                    other_input.fill(value)
                else:
                    return False
            except Exception as e:
                return False
        
        return True
    
    def set_combobox(self, selector: str, val: str, fuzzy_match: bool = False) -> bool:
        """设置下拉框值
        
        :param selector: 下拉框的选择器
        :param val: 要设置的值
        :param fuzzy_match: 是否启用模糊匹配
        :return: 操作是否成功
        """
        if not val:
            return False
        
        try:
            # 定位下拉框元素
            combobox = self.page.locator(selector)
            if not combobox.count():
                 return False
            
            # 尝试显示下拉选项（重试机制）
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    combobox.click()
                    self.page.wait_for_timeout(500)  # 等待下拉选项显示
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                         return False
                    self.page.wait_for_timeout(1000)
            
            # 查找匹配的选项
            option_found = False
            
            # 策略1: 精确匹配
            exact_option = self.page.locator(f'option[value="{val}"], li:has-text("{val}"), div:has-text("{val}")')
            if exact_option.count() > 0:
                exact_option.first.click()
                option_found = True
            
            # 策略2: 模糊匹配（如果启用）
            if not option_found and fuzzy_match:
                fuzzy_option = self.page.locator(f'option:has-text("{val}"), li:has-text("{val}"), div:has-text("{val}")')
                if fuzzy_option.count() > 0:
                    fuzzy_option.first.click()
                    option_found = True
            
            # 策略3: 包含匹配
            if not option_found:
                contains_option = self.page.locator('option, li, div').filter(has_text=val)
                if contains_option.count() > 0:
                    contains_option.first.click()
                    option_found = True
            
            # 策略4: 开始匹配
            if not option_found:
                all_options = self.page.locator('option, li, div')
                for i in range(all_options.count()):
                    option = all_options.nth(i)
                    option_text = option.text_content() or ""
                    if option_text.strip().startswith(val):
                        option.click()
                        option_found = True
                        break
            
            if not option_found:
                return False
            
            return True
            
        except Exception as e:
            return False
    
    def set_combobox_with_icon(self, selector: str, val: str, fuzzy_match: bool = False) -> bool:
        """通过图标设置下拉框值
        
        :param selector: 下拉框的选择器
        :param val: 要选择的值
        :param fuzzy_match: 是否进行模糊匹配
        :return: 操作是否成功
        """
        if not val:
            return False
        
        try:
            # 定位下拉框元素
            combobox = self.page.locator(selector)
            if not combobox.count():
                return False
            
            # 尝试显示下拉选项（重试机制）
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    combobox.click()
                    self.page.wait_for_timeout(500)  # 等待下拉选项显示
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        return False
                    self.page.wait_for_timeout(1000)
            
            # 查找匹配的选项（考虑图标元素）
            option_found = False
            
            # 策略1: 精确匹配（包含图标的选项）
            exact_selectors = [
                f'option[value="{val}"]',
                f'li:has-text("{val}")',
                f'div:has-text("{val}")',
                f'span:has-text("{val}")',
                f'[data-value="{val}"]'
            ]
            
            for sel in exact_selectors:
                exact_option = self.page.locator(sel)
                if exact_option.count() > 0:
                    exact_option.first.click()
                    option_found = True
                    break
            
            # 策略2: 模糊匹配（如果启用）
            if not option_found and fuzzy_match:
                fuzzy_selectors = [
                    f'option:has-text("{val}")',
                    f'li:has-text("{val}")',
                    f'div:has-text("{val}")',
                    f'span:has-text("{val}")'
                ]
                
                for sel in fuzzy_selectors:
                    fuzzy_option = self.page.locator(sel)
                    if fuzzy_option.count() > 0:
                        fuzzy_option.first.click()
                        option_found = True
                        break
            
            # 策略3: 包含匹配
            if not option_found:
                contains_option = self.page.locator('option, li, div, span').filter(has_text=val)
                if contains_option.count() > 0:
                    contains_option.first.click()
                    option_found = True
            
            # 策略4: 开始匹配
            if not option_found:
                all_options = self.page.locator('option, li, div, span')
                for i in range(all_options.count()):
                    option = all_options.nth(i)
                    option_text = option.text_content() or ""
                    if option_text.strip().startswith(val):
                        option.click()
                        option_found = True
                        break
            
            if not option_found:
                return False
            
            return True
            
        except Exception as e:
            return False
    
    def wait_load(self, msg: str = None) -> bool:
        """等待页面加载完成
        
        :param msg: 等待消息（可选）
        :return: 操作是否成功
        """
        try:
            # 策略1: 等待网络空闲
            try:
                self.page.wait_for_load_state('networkidle', timeout=10000)
            except Exception:
                pass  # 继续尝试其他策略
            
            # 策略2: 等待DOM内容加载完成
            try:
                self.page.wait_for_load_state('domcontentloaded', timeout=5000)
            except Exception:
                pass
            
            # 策略3: 等待页面完全加载
            try:
                self.page.wait_for_load_state('load', timeout=5000)
            except Exception:
                pass
            
            # 策略4: 检查并等待常见的加载指示器消失
            loading_selectors = [
                '.loading',
                '.spinner',
                '.loader',
                '[data-loading="true"]',
                '.ant-spin',
                '.el-loading-mask'
            ]
            
            for selector in loading_selectors:
                try:
                    loading_element = self.page.locator(selector)
                    if loading_element.count() > 0:
                        loading_element.wait_for(state='detached', timeout=10000)
                except Exception:
                    continue  # 继续检查下一个加载指示器
            
            # 策略5: 最终等待，确保页面稳定
            self.page.wait_for_timeout(1000)
            
            return True
            
        except Exception as e:
            return False
    
    def close_dialog(self, btn_text: str = "确定", msg: str = None) -> bool:
        """关闭对话框
        
        :param btn_text: 按钮文本，默认为"确定"
        :param msg: 期望的对话框消息（可选）
        :return: 是否成功关闭
        """
        try:
            # 查找对话框元素
            dialog_selectors = [
                '.modal',
                '.dialog',
                '.ant-modal',
                '.el-dialog',
                '[role="dialog"]',
                '.popup',
                '.overlay'
            ]
            
            dialog = None
            for selector in dialog_selectors:
                dialog_element = self.page.locator(selector)
                if dialog_element.count() > 0 and dialog_element.is_visible():
                    dialog = dialog_element.first
                    break
            
            if not dialog:
                return False  # 没有找到对话框
            
            # 如果指定了消息，验证对话框内容
            if msg:
                dialog_text = dialog.text_content() or ""
                if msg not in dialog_text:
                    return False  # 对话框消息不匹配
            
            # 查找并点击指定的按钮
            button_selectors = [
                f'button:has-text("{btn_text}")',
                f'input[type="button"][value="{btn_text}"]',
                f'a:has-text("{btn_text}")',
                f'.btn:has-text("{btn_text}")',
                f'[data-action="{btn_text.lower()}"]'
            ]
            
            button_found = False
            for btn_selector in button_selectors:
                button = dialog.locator(btn_selector)
                if button.count() > 0 and button.is_visible():
                    button.click()
                    button_found = True
                    break
            
            if not button_found:
                return False  # 没有找到指定的按钮
            
            # 等待对话框消失
            try:
                dialog.wait_for(state='detached', timeout=5000)
            except Exception:
                pass  # 对话框可能已经消失
            
            return True
            
        except Exception:
            return False
    
    def wait_for_input_has_value(self, selector: str, timeout: int = 5000) -> bool:
        """等待输入框有值
        
        :param selector: 输入框的选择器
        :param timeout: 超时时间（毫秒）
        :return: 是否在超时前输入框有了值
        """
        try:
            # 首先确保输入框存在且可见
            input_element = self.page.locator(selector)
            if not input_element.count():
                return False
            
            # 等待元素可见
            input_element.wait_for(state='visible', timeout=timeout)
            
            # 轮询检查输入框是否有值
            start_time = self.page.evaluate('Date.now()')
            
            while True:
                current_time = self.page.evaluate('Date.now()')
                if current_time - start_time > timeout:
                    return False  # 超时
                
                # 检查输入框的值
                try:
                    # 尝试多种方式获取输入框的值
                    value = input_element.input_value()
                    if value and value.strip():
                        return True
                except Exception:
                    # 如果input_value()失败，尝试其他方式
                    try:
                        value = input_element.text_content()
                        if value and value.strip():
                            return True
                    except Exception:
                        try:
                            value = input_element.get_attribute('value')
                            if value and value.strip():
                                return True
                        except Exception:
                            pass
                
                # 短暂等待后再次检查
                self.page.wait_for_timeout(100)
            
        except Exception:
            return False