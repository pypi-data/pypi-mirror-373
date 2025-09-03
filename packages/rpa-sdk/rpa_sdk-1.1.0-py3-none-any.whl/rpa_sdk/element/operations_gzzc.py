"""默认元素操作实现

提供标准的页面元素操作实现，适用于谷歌浏览器
"""
from typing import List
from playwright.sync_api import Page, expect
from ..manager.element_operations_interface import WebElementOperations


class GzzcElementOperations(WebElementOperations):
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
        # 参数校验：确保 val 存在于选项列表
        if val not in labs:
            raise ValueError(f"值 '{val}' 不在选项列表 {labs} 中，请检查参数有效性")

        # 获取目标选项的索引
        target_index = labs.index(val)

        # 定位所有单选按钮元素
        radio_buttons = self.page.locator(selector)
        actual_count = radio_buttons.count()

        # 索引有效性检查
        if target_index >= actual_count:
            raise IndexError(
                f"选项索引 {target_index} 超出实际单选按钮数量 ({actual_count})，"
                f"请检查选择器 {selector} 是否匹配正确元素"
            )

        # 获取目标单选按钮元素
        target_radio = radio_buttons.nth(target_index)

        # 确保元素可见并操作（附加等待策略）
        target_radio.wait_for(state="visible")
        target_radio.click()
        
        # 选中操作完成
        return True
    
    def get_selected_single_choice(self, selector: str, labs: List[str], val: str) -> str:
        """获取单选选中值
        
        :param selector: 单选按钮组的选择器
        :param labs: 单选按钮的标签数组
        :param val: 参考值
        :return: 当前选中的值
        """
        lst_radio = self.page.locator(selector)
        # 遍历所有的单选按钮
        for i in range(lst_radio.count()):
            radio = lst_radio.nth(i)
            if radio.is_checked():
                return radio.get_attribute('value') or ''  # 获取单选按钮的 value 属性
        return ''
    
    def single_choice_with_other(self, selector: str, selector_other: str, labs: List[str], val: str) -> bool:
        """带其他选项的单选操作
        
        :param selector: 单选按钮组的选择器
        :param selector_other: 其他选项输入框的选择器
        :param labs: 单选按钮的标签数组
        :param val: 需要选定的值（可包含=分隔的附加内容）
        :return: 操作是否成功
        """
        if '=' in val:
            label, input_val = val.split('=', 1)
        else:
            label, input_val = val, None

        # 参数校验：确保 label 存在于选项列表
        if label not in labs:
            raise ValueError(f"值 '{label}' 不在选项列表 {labs} 中，请检查参数有效性")

        # 复用 single_choice 方法完成单选操作
        self.single_choice(selector, labs, label)

        # 如果有输入需求，则处理输入框
        if input_val is not None:
            # 等待输入框可见并填写内容
            self.page.wait_for_selector(selector_other)
            self.page.fill(selector_other, input_val)
        
        return True
    
    def multiple_choice(self, selector: str, labs: List[str], vals: str) -> bool:
        """多选操作
        
        :param selector: 多选框组的选择器
        :param labs: 多选框的标签数组
        :param vals: 要选中的值的字符串（逗号分隔）
        :return: 操作是否成功
        """
        # 调用私有方法先取消所有选中状态，并获取映射字典
        lst_check = self.page.locator(selector)

        # 处理空值情况并拆分选中值
        selected_values = [v.strip() for v in vals.split(',')] if vals else []

        # 按labs顺序遍历多选框
        for index, lab in enumerate(labs):
            checkbox = lst_check.nth(index)  # 获取对应序号的多选框

            # 判断是否需要选中
            if lab in selected_values:
                while not checkbox.is_checked():
                    checkbox.check()
            else:
                while checkbox.is_checked():
                    checkbox.uncheck()
        
        return True
    
    def multiple_choice_with_other(self, selector: str, selector_other: str, labs: List[str], vals: str) -> bool:
        """带其他选项的多选操作
        
        :param selector: 多选框组的选择器
        :param selector_other: 其他选项输入框的选择器
        :param labs: 多选框的标签数组
        :param vals: 要选中的值的字符串
        :return: 操作是否成功
        """
        # 分离普通选项和需要特殊处理的键值对
        selected_values = []
        special_entries = {}

        for part in vals.split(','):
            part = part.strip()
            if '=' in part:
                key, value = part.split('=', 1)
                key = key.strip()
                special_entries[key] = value.strip()
            else:
                selected_values.append(part)

        # 合并需要选中的值（普通选项+特殊键）
        combined_vals = selected_values + list(special_entries.keys())

        # 执行基础多选操作
        self.multiple_choice(selector, labs, ','.join(combined_vals))

        # 处理特殊输入框
        for key, value in special_entries.items():
            if key in labs:
                index = labs.index(key)
                checkbox = self.page.locator(selector).nth(index)

                # 只有当选中的情况下才填写附加内容
                if checkbox.is_checked():
                    input_field = self.page.locator(selector_other)
                    input_field.fill(value)
        
        return True
    
    def set_combobox(self, selector: str, val: str, fuzzy_match: bool = False) -> bool:
        """设置下拉框值
        
        :param selector: 下拉框的选择器
        :param val: 要选择的值
        :param fuzzy_match: 是否进行模糊匹配
        :return: 操作是否成功
        """
        try:
            max_retries = 3  # 设置最大重试次数
            retry_count = 0  # 当前重试次数
            dropdown_visible = False  # 标志，表示下拉列表是否已成功显示
            dropdown_selector = ".x-layer.x-combo-list[style*='visibility: visible']"  # 下拉列表的CSS选择器

            # 循环尝试，直到下拉列表显示或达到最大重试次数
            while not dropdown_visible and retry_count < max_retries:
                # 点击下拉框旁边的图标展开选项
                self.page.click(f"{selector}/../img", force=True, timeout=3000)

                try:
                    # 等待下拉列表可见（使用 CSS 选择器），最长等待2秒
                    self.page.wait_for_selector(dropdown_selector, timeout=2000)
                    dropdown_visible = True  # 如果成功显示，设置标志为True
                except Exception as e:
                    # 如果在2秒内没有显示，则捕获异常并进行重试
                    print(f"下拉列表在2秒内未显示。正在重试... (尝试 {retry_count + 1}/{max_retries}) 错误: {e}")
                    retry_count += 1  # 增加重试计数
                    self.page.wait_for_timeout(500)  # 可选：在重试前等待0.5秒，给页面一个反应时间

            # 如果多次重试后下拉列表仍未显示，则抛出异常
            if not dropdown_visible:
                raise Exception("多次重试后下拉列表仍未显示。")

            # 尝试多种匹配策略来选择正确的选项
            item_selector = None

            # 首先尝试使用更精确的下拉列表选择器（选择最后一个可见的）
            precise_dropdown_selector = f"{dropdown_selector}:last-child"

            # 策略1: 精确匹配（优先级最高）
            try:
                exact_selector = f"{precise_dropdown_selector} div.x-combo-list-item:text-is('{val}')"
                if self.page.locator(exact_selector).count() > 0:
                    item_selector = exact_selector
                    print(f"使用精确匹配选择器: {item_selector}")
            except:
                # 如果精确选择器失败，回退到原始选择器
                try:
                    exact_selector = f"{dropdown_selector} div.x-combo-list-item:text-is('{val}')"
                    if self.page.locator(exact_selector).count() > 0:
                        item_selector = exact_selector
                        print(f"使用回退精确匹配选择器: {item_selector}")
                except:
                    pass

            # 策略2: 如果精确匹配失败且启用模糊匹配，尝试改进的模糊匹配
            if item_selector is None and fuzzy_match:
                try:
                    # 转义特殊字符，避免正则表达式问题
                    escaped_val = val.replace('[', r'\[').replace(']', r'\]').replace('(', r'\(').replace(')', r'\)')

                    # 优先匹配以目标值开头的选项（如 [4] 开头）
                    start_with_selector = f"{precise_dropdown_selector} div.x-combo-list-item:text-matches('^{escaped_val}', 'i')"
                    if self.page.locator(start_with_selector).count() > 0:
                        item_selector = start_with_selector
                        print(f"使用开头匹配选择器: {item_selector}")
                    else:
                        # 回退到原始选择器尝试开头匹配
                        start_with_selector = f"{dropdown_selector} div.x-combo-list-item:text-matches('^{escaped_val}', 'i')"
                        if self.page.locator(start_with_selector).count() > 0:
                            item_selector = start_with_selector
                            print(f"使用回退开头匹配选择器: {item_selector}")
                        else:
                            # 如果开头匹配失败，使用包含匹配（但要更精确）
                            if val.startswith('[') and val.endswith(']'):
                                # 对于 [数字] 格式，使用更精确的匹配
                                precise_pattern = escaped_val.replace(r'\[', r'\[').replace(r'\]', r'\]')
                                contains_selector = f"{dropdown_selector} div.x-combo-list-item:text-matches('{precise_pattern}', 'i')"
                            else:
                                contains_selector = f"{dropdown_selector} div.x-combo-list-item:text-matches('.*{escaped_val}.*', 'i')"

                            if self.page.locator(contains_selector).count() > 0:
                                item_selector = contains_selector
                                print(f"使用包含匹配选择器: {item_selector}")
                except Exception as e:
                    print(f"模糊匹配构造失败: {e}")

            # 策略3: 如果所有匹配都失败，回退到原始的模糊匹配
            if item_selector is None:
                if fuzzy_match:
                    item_selector = f"{dropdown_selector} div.x-combo-list-item:text-matches('.*{val}.*', 'i')"
                    print(f"使用回退模糊匹配选择器: {item_selector}")
                else:
                    item_selector = f"{dropdown_selector} div.x-combo-list-item:text-is('{val}')"
                    print(f"使用回退精确匹配选择器: {item_selector}")

            # 点击匹配的选项
            if item_selector:
                matched_count = self.page.locator(item_selector).count()
                print(f"找到 {matched_count} 个匹配的选项，选择第一个")

                # 如果找到多个匹配项，尝试选择最合适的一个
                if matched_count > 1:
                    print("警告: 找到多个匹配项，尝试选择最精确的匹配")
                    # 获取所有匹配项的文本，选择最精确的
                    all_matches = self.page.locator(item_selector).all_text_contents()
                    print(f"所有匹配项: {all_matches}")

                    # 寻找精确匹配
                    for i, match_text in enumerate(all_matches):
                        if match_text == val or (fuzzy_match and match_text.startswith(val)):
                            print(f"选择第 {i+1} 个匹配项: {match_text}")
                            self.page.locator(item_selector).nth(i).click()
                            return

                # 默认选择第一个匹配项
                self.page.click(item_selector)
                return True
            else:
                raise Exception(f"无法找到匹配值 '{val}' 的选项")

        except Exception as e:
            print(f"在 set_combobox 方法中发生错误: {e}")
            # 打印当前可用的选项以便调试
            try:
                options = self.page.locator(f"{dropdown_selector} div.x-combo-list-item").all_text_contents()
                print(f"当前可用选项: {options}")
            except:
                print("无法获取当前可用选项")
            return False
    
    def set_combobox_with_icon(self, selector: str, val: str, fuzzy_match: bool = False) -> bool:
        """设置带图标的下拉框值
        
        :param selector: 下拉框的选择器
        :param val: 要选择的值
        :param fuzzy_match: 是否进行模糊匹配
        :return: 操作是否成功
        """
        try:
            max_retries = 3
            retry_count = 0
            dropdown_visible = False
            dropdown_selector = ".x-layer.x-combo-list[style*='visibility: visible']"

            # 循环尝试，直到下拉列表显示或达到最大重试次数
            while not dropdown_visible and retry_count < max_retries:
                # 点击下拉框旁边的图标展开选项
                self.page.click(f"{selector}/../img", force=True, timeout=3000)

                try:
                    # 等待下拉列表可见
                    self.page.wait_for_selector(dropdown_selector, timeout=2000)
                    dropdown_visible = True
                except Exception as e:
                    print(f"下拉列表在2秒内未显示。正在重试... (尝试 {retry_count + 1}/{max_retries}) 错误: {e}")
                    retry_count += 1
                    self.page.wait_for_timeout(500)

            if not dropdown_visible:
                raise Exception("多次重试后下拉列表仍未显示。")

            # 尝试多种匹配策略来选择正确的选项
            item_selector = None
            precise_dropdown_selector = f"{dropdown_selector}:last-child"

            # 策略1: 精确匹配（优先级最高）
            try:
                exact_selector = f"{precise_dropdown_selector} div.x-combo-list-item:text-is('{val}')"
                if self.page.locator(exact_selector).count() > 0:
                    item_selector = exact_selector
                    print(f"使用精确匹配选择器: {item_selector}")
            except:
                try:
                    exact_selector = f"{dropdown_selector} div.x-combo-list-item:text-is('{val}')"
                    if self.page.locator(exact_selector).count() > 0:
                        item_selector = exact_selector
                        print(f"使用回退精确匹配选择器: {item_selector}")
                except:
                    pass

            # 策略2: 模糊匹配
            if item_selector is None and fuzzy_match:
                try:
                    escaped_val = val.replace('[', r'\[').replace(']', r'\]').replace('(', r'\(').replace(')', r'\)')
                    start_with_selector = f"{precise_dropdown_selector} div.x-combo-list-item:text-matches('^{escaped_val}', 'i')"
                    if self.page.locator(start_with_selector).count() > 0:
                        item_selector = start_with_selector
                        print(f"使用开头匹配选择器: {item_selector}")
                    else:
                        start_with_selector = f"{dropdown_selector} div.x-combo-list-item:text-matches('^{escaped_val}', 'i')"
                        if self.page.locator(start_with_selector).count() > 0:
                            item_selector = start_with_selector
                            print(f"使用回退开头匹配选择器: {item_selector}")
                        else:
                            if val.startswith('[') and val.endswith(']'):
                                precise_pattern = escaped_val.replace(r'\[', r'\[').replace(r'\]', r'\]')
                                contains_selector = f"{dropdown_selector} div.x-combo-list-item:text-matches('{precise_pattern}', 'i')"
                            else:
                                contains_selector = f"{dropdown_selector} div.x-combo-list-item:text-matches('.*{escaped_val}.*', 'i')"

                            if self.page.locator(contains_selector).count() > 0:
                                item_selector = contains_selector
                                print(f"使用包含匹配选择器: {item_selector}")
                except Exception as e:
                    print(f"模糊匹配构造失败: {e}")

            # 策略3: 回退匹配
            if item_selector is None:
                if fuzzy_match:
                    item_selector = f"{dropdown_selector} div.x-combo-list-item:text-matches('.*{val}.*', 'i')"
                    print(f"使用回退模糊匹配选择器: {item_selector}")
                else:
                    item_selector = f"{dropdown_selector} div.x-combo-list-item:text-is('{val}')"
                    print(f"使用回退精确匹配选择器: {item_selector}")

            # 点击匹配的选项
            if item_selector:
                matched_count = self.page.locator(item_selector).count()
                print(f"找到 {matched_count} 个匹配的选项，选择第一个")

                if matched_count > 1:
                    print("警告: 找到多个匹配项，尝试选择最精确的匹配")
                    all_matches = self.page.locator(item_selector).all_text_contents()
                    print(f"所有匹配项: {all_matches}")

                    for i, match_text in enumerate(all_matches):
                        if match_text == val or (fuzzy_match and match_text.startswith(val)):
                            print(f"选择第 {i+1} 个匹配项: {match_text}")
                            self.page.locator(item_selector).nth(i).click()
                            return

                self.page.click(item_selector)
                return True
            else:
                raise Exception(f"无法找到匹配值 '{val}' 的选项")

        except Exception as e:
            print(f"在 set_combobox_with_icon 方法中发生错误: {e}")
            # 打印当前可用的选项以便调试
            try:
                options = self.page.locator(f"{dropdown_selector} div.x-combo-list-item").all_text_contents()
                print(f"当前可用选项: {options}")
            except:
                print("无法获取当前可用选项")
            return False
    
    def wait_load(self, msg: str = None) -> bool:
        """等待页面加载完成
        
        :param msg: 等待消息
        :return: 操作是否成功
        """
        try:
            # 如果提供了消息，打印等待信息
            if msg:
                print(f"等待页面加载: {msg}")
            
            # 等待页面加载完成的多种策略
            
            # 策略1: 等待网络空闲状态
            try:
                self.page.wait_for_load_state('networkidle', timeout=30000)
                print("页面网络空闲状态达成")
            except Exception as e:
                print(f"等待网络空闲超时: {e}")
            
            # 策略2: 等待DOM内容加载完成
            try:
                self.page.wait_for_load_state('domcontentloaded', timeout=15000)
                print("DOM内容加载完成")
            except Exception as e:
                print(f"等待DOM加载超时: {e}")
            
            # 策略3: 等待页面完全加载
            try:
                self.page.wait_for_load_state('load', timeout=20000)
                print("页面完全加载完成")
            except Exception as e:
                print(f"等待页面加载超时: {e}")
            
            # 策略4: 检查是否存在加载指示器并等待其消失
            loading_selectors = [
                '.loading',
                '.spinner',
                '.x-mask-loading',
                '[class*="loading"]',
                '[class*="spinner"]'
            ]
            
            for selector in loading_selectors:
                try:
                    # 如果找到加载指示器，等待其消失
                    if self.page.locator(selector).count() > 0:
                        print(f"发现加载指示器: {selector}，等待其消失")
                        self.page.wait_for_selector(selector, state='detached', timeout=30000)
                        print(f"加载指示器已消失: {selector}")
                except Exception as e:
                    # 忽略单个选择器的错误，继续检查其他选择器
                    pass
            
            # 策略5: 额外等待确保页面稳定
            self.page.wait_for_timeout(1000)  # 等待1秒确保页面稳定
            
            print("页面加载等待完成")
            return True
            
        except Exception as e:
            print(f"wait_load方法执行出错: {e}")
            # 即使出错也不抛出异常，因为这是一个辅助方法
            # 让调用方继续执行后续操作
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
    
     
    def close_dialog(self, btn_text: str = "确定", msg: str = None) -> bool:
        """关闭对话框
        
        :param btn_text: 按钮文本
        :param msg: 对话框消息
        :return: 是否成功关闭
        """
        try:
            # 等待对话框出现
            dialog_selectors = [
                '.x-window',
                '.x-panel-window',
                '.x-window-dlg',
                '[class*="dialog"]',
                '[class*="modal"]'
            ]
            
            dialog_found = False
            dialog_selector = None
            
            # 查找对话框
            for selector in dialog_selectors:
                try:
                    if self.page.locator(selector).count() > 0:
                        # 检查对话框是否可见
                        if self.page.locator(selector).first.is_visible():
                            dialog_found = True
                            dialog_selector = selector
                            print(f"找到对话框: {selector}")
                            break
                except:
                    continue
            
            if not dialog_found:
                print("未找到可见的对话框")
                return False
            
            # 如果指定了消息，验证对话框内容
            if msg:
                try:
                    dialog_content = self.page.locator(dialog_selector).first.text_content()
                    if msg not in dialog_content:
                        print(f"对话框内容不匹配。期望包含: '{msg}', 实际内容: '{dialog_content}'")
                        return False
                    else:
                        print(f"对话框内容匹配: '{msg}'")
                except Exception as e:
                    print(f"验证对话框内容时出错: {e}")
            
            # 查找并点击按钮
            button_selectors = [
                f"{dialog_selector} button:text-is('{btn_text}')",
                f"{dialog_selector} .x-btn-text:text-is('{btn_text}')",
                f"{dialog_selector} input[value='{btn_text}']",
                f"{dialog_selector} [role='button']:text-is('{btn_text}')",
                f"button:text-is('{btn_text}')",
                f".x-btn-text:text-is('{btn_text}')"
            ]
            
            button_clicked = False
            
            for btn_selector in button_selectors:
                try:
                    if self.page.locator(btn_selector).count() > 0:
                        button = self.page.locator(btn_selector).first
                        if button.is_visible():
                            print(f"点击按钮: {btn_selector}")
                            button.click()
                            button_clicked = True
                            break
                except Exception as e:
                    print(f"尝试点击按钮 {btn_selector} 时出错: {e}")
                    continue
            
            if not button_clicked:
                print(f"未找到可点击的按钮: '{btn_text}'")
                return False
            
            # 等待对话框消失
            try:
                self.page.wait_for_selector(dialog_selector, state='detached', timeout=5000)
                print("对话框已成功关闭")
                return True
            except Exception as e:
                print(f"等待对话框关闭超时: {e}")
                # 检查对话框是否仍然可见
                if self.page.locator(dialog_selector).count() > 0 and self.page.locator(dialog_selector).first.is_visible():
                    print("对话框仍然可见")
                    return False
                else:
                    print("对话框已关闭（通过可见性检查）")
                    return True
                    
        except Exception as e:
            print(f"close_dialog方法执行出错: {e}")
            return False
    
    def wait_for_input_has_value(self, selector: str, timeout: int = 5000) -> bool:
        """等待输入框有值
        
        :param selector: 输入框选择器
        :param timeout: 超时时间（毫秒）
        :return: 是否有值
        """
        try:
            print(f"等待输入框 {selector} 有值，超时时间: {timeout}ms")
            
            # 首先确保输入框存在
            try:
                self.page.wait_for_selector(selector, timeout=timeout)
                print(f"输入框 {selector} 已找到")
            except Exception as e:
                print(f"输入框 {selector} 未找到: {e}")
                return False
            
            # 获取输入框元素
            input_element = self.page.locator(selector).first
            
            # 检查输入框是否可见
            if not input_element.is_visible():
                print(f"输入框 {selector} 不可见")
                return False
            
            # 等待输入框有值的策略
            start_time = self.page.evaluate("Date.now()")
            
            while True:
                try:
                    # 获取输入框的值
                    value = input_element.input_value()
                    
                    # 检查值是否非空（去除空白字符后）
                    if value and value.strip():
                        print(f"输入框 {selector} 已有值: '{value}'")
                        return True
                    
                    # 检查是否超时
                    current_time = self.page.evaluate("Date.now()")
                    if current_time - start_time > timeout:
                        print(f"等待输入框 {selector} 有值超时")
                        return False
                    
                    # 短暂等待后重试
                    self.page.wait_for_timeout(100)
                    
                except Exception as e:
                    print(f"检查输入框值时出错: {e}")
                    # 尝试其他方法获取值
                    try:
                        # 尝试使用 textContent
                        text_content = input_element.text_content()
                        if text_content and text_content.strip():
                            print(f"输入框 {selector} 通过textContent获取到值: '{text_content}'")
                            return True
                        
                        # 尝试使用 getAttribute('value')
                        attr_value = input_element.get_attribute('value')
                        if attr_value and attr_value.strip():
                            print(f"输入框 {selector} 通过getAttribute获取到值: '{attr_value}'")
                            return True
                            
                    except Exception as inner_e:
                        print(f"尝试其他方法获取输入框值失败: {inner_e}")
                    
                    # 检查是否超时
                    current_time = self.page.evaluate("Date.now()")
                    if current_time - start_time > timeout:
                        print(f"等待输入框 {selector} 有值超时")
                        return False
                    
                    # 短暂等待后重试
                    self.page.wait_for_timeout(100)
                    
        except Exception as e:
            print(f"wait_for_input_has_value方法执行出错: {e}")
            return False