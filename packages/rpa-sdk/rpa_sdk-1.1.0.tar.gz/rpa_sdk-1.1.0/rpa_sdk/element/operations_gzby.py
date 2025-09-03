"""默认元素操作实现

提供标准的页面元素操作实现，适用于谷歌浏览器
"""
from typing import List
from playwright.sync_api import Page, expect
from ..manager.element_operations_interface import WebElementOperations


class GzbyElementOperations(WebElementOperations):
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
        
        根据选项值 val 在 labs 中的索引位置，选择对应的单选按钮并返回其 value 属性
        :param selector: 单选按钮组的 CSS xpath 选择器
        :param labs: 单选按钮的标签数组，如 ['男', '女', '未知']
        :param val: 需要选定的值，必须在 labs 中存在
        :return: 操作是否成功
        :raises ValueError: 当 val 不在 labs 中时抛出
        :raises IndexError: 当索引超出实际单选按钮数量时抛出
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
        # if not target_radio.is_checked():
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
        ret = ""
        lst_radio = self.page.locator(selector)
        # 遍历所有的单选按钮
        for i in range(lst_radio.count()):
            radio = lst_radio.nth(i)
            if radio.is_checked():
                ret = radio.get_attribute('value')  # 获取单选按钮的 value 属性
                break
        return ret
    
    def single_choice_with_other(self, selector: str, selector_other: str, labs: List[str], val: str) -> bool:
        """带其他选项的单选操作
        
        根据选项值 val，在 labs 中查找对应索引并选择单选按钮。
        如果 val 包含 '='，例如 '有=高血压'，则：
            - 先选择等号前的部分（如 '有'）
            - 再通过 selector_other 填写等号后的部分（如 '高血压'）

        :param selector: 单选按钮组的 CSS 选择器
        :param selector_other: 输入框的选择器，用于填写等号后内容（当 val 包含 '=' 时）
        :param labs: 单选按钮的标签数组，如 ['男', '女', '未知']
        :param val: 需要选定的值，可以是普通字符串或形如 '有=高血压'
        :return: 操作是否成功
        :raises ValueError: 当 val 不在 labs 中且不包含 = 时抛出
        :raises IndexError: 当索引超出实际单选按钮数量时抛出
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
        
        多选操作，传入选择器、keys 和要选中的值的字符串
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
        
        带有"其他"选项的多选操作，支持需要额外填写的值
        :param selector: 多选框组选择器
        :param selector_other: 其他选项的输入框选择器
        :param labs: 多选框标签列表
        :param vals: 选中值字符串（支持 key=value 格式处理其他选项）
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
        '''
        下拉组件设置
        尝试点击下拉框图标展开选项，如果2秒内下拉列表未显示则重试。

        :param selector: 下拉框的选择器（定位下拉框本身）
        :param val: 要选择的值
        :param fuzzy_match: 是否进行模糊匹配（True 表示模糊匹配，False 表示精确匹配）
        :return: 操作是否成功
        '''
        try:
            max_retries = 3  # 设置最大重试次数
            retry_count = 0  # 当前重试次数
            dropdown_visible = False  # 标志，表示下拉列表是否已成功显示
            dropdown_selector = ".x-layer.x-combo-list[style*='visibility: visible']"  # 下拉列表的CSS选择器

            # 循环尝试，直到下拉列表显示或达到最大重试次数
            while not dropdown_visible and retry_count < max_retries:
                # 点击下拉框旁边的图标展开选项
                # selector/../img 是一个XPath或类似的选择器，表示选择器元素的父级下的img标签
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
                            # 对于 [4] 这种情况，确保匹配的是 [4] 而不是包含4的其他数字
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
            # 捕获并打印整个过程中可能发生的任何错误
            print(f"在 set_combobox 方法中发生错误: {e}")
            # 打印当前可用的选项以便调试
            try:
                options = self.page.locator(f"{dropdown_selector} div.x-combo-list-item").all_text_contents()
                print(f"当前可用选项: {options}")
            except:
                print("无法获取当前可用选项")
            return False
    
    def set_combobox_with_icon(self, selector: str, val: str, fuzzy_match: bool = False) -> bool:
        """通过图标设置下拉框值
        
        :param selector: 下拉框的选择器
        :param val: 要选择的值
        :param fuzzy_match: 是否进行模糊匹配
        :return: 操作是否成功
        """
        # 点击展开按钮（XPath 版）
        self.page.click(f"{selector}/following-sibling::img[1]")

        # 等待下拉列表可见（使用 CSS 类名匹配）
        dropdown = self.page.locator(".x-layer.x-combo-list:visible")
        dropdown.wait_for(state="attached", timeout=5000)

        # 构造文本匹配规则
        val_escaped = val.replace('"', r'\"')
        text_matcher = f'"{val_escaped}" i' if fuzzy_match else f'"{val_escaped}"'

        # 定位目标项并点击
        option_locator = dropdown.locator(f"li span:text-matches({text_matcher})")
        option_locator.scroll_into_view_if_needed()
        option_locator.click()

        # 关闭下拉
        dropdown.wait_for(state="hidden", timeout=2000)
        self.page.keyboard.press("Escape")
        return True
    
    def wait_load(self, msg: str = None):
        """等待加载框出现并消失
        
        :param msg: 可选的加载消息
        :return: 操作是否成功
        """
        # 构建加载框的选择器
        loading_selector = "div.x-mask-loading"
        if msg is not None:
            loading_selector = f"div.x-mask-loading:has-text('{msg}')"

        try:
            # 等待加载框出现（3秒）
            self.page.wait_for_selector(
                loading_selector,
                state="visible",
                timeout=3000
            )
            # 等待加载框消失（30秒）
            self.page.wait_for_selector(
                loading_selector,  # 使用相同的选择器来等待它消失
                state="detached",
                timeout=30000
            )
        except Exception as e:
            print(e)
            return False
        return True
    
    def close_dialog(self, btn_text: str = "确定", msg: str = None) -> bool:
        """
        关闭对话框。
        """
        dialog_locator_str = "//div[@class=' x-window x-window-plain x-window-dlg' and contains(@style,'visibility: visible;')]"

        try:
            # 使用 expect.to_be_visible() 来等待对话框出现
            # 它会在超时时间内重试查找，直到元素可见或超时
            # 如果不期望对话框出现，或者想快速失败，可以设置较短的超时
            dialog_element = self.page.locator(dialog_locator_str)
            expect(dialog_element).to_be_visible(timeout=1000)  # 例如，最多等待2秒，如果对话框没出现就直接抛出异常

            # 如果到这里，说明对话框已经可见
            if msg:
                tip_locator_str = f"{dialog_locator_str}//span[contains(text(),'{msg}')]"
                # 同样使用 expect 来确保提示文本存在于对话框内
                tip_element = self.page.locator(tip_locator_str)
                expect(tip_element).to_be_visible(timeout=1000)  # 假设提示文本会很快出现

                button_locator_str = f"{dialog_locator_str}//button[text()='{btn_text}']"
                button_element = self.page.locator(button_locator_str)
                # 点击按钮，Playwright会自动等待按钮可点击
                button_element.click(timeout=1000)  # click也有超时参数
            else:
                button_locator_str = f"{dialog_locator_str}//button[contains(text(),'{btn_text}')]"
                button_element = self.page.locator(button_locator_str)
                button_element.click(timeout=1000)

            # 等待对话框消失（可选，但推荐，确保操作完成）
            expect(dialog_element).to_be_hidden(timeout=2000)
            return True

        except Exception as e:
            # 如果在任何expect或click操作中超时，都会捕获到异常
            # print(f"关闭对话框失败或超时: {e}") # 可以打印日志
            return False
    
    def wait_for_input_has_value(self, selector: str, timeout: int = 5000) -> bool:
        """等待输入框有值
        
        等待元素出现并显示值
        :param selector: 输入框选择器
        :param timeout: 超时时间（毫秒）
        :return: 是否成功等到值
        """
        # 等待元素出现
        self.page.wait_for_selector(selector, timeout=timeout)

        # 判断是否是XPath选择器
        is_xpath = selector.startswith("//") or selector.startswith("(//")

        # 根据选择器类型构建不同的JS代码
        if is_xpath:
            # 对 selector 中的单引号进行转义，避免 JS 语法错误
            escaped_selector = selector.replace("'", "\\'")
            js_code = """
            () => {{
                const xpath = '{}';
                const result = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                const el = result.singleNodeValue;
                return el && el.value && el.value.trim() !== '';
            }}
            """.format(escaped_selector)

        else:
            escaped_selector = selector.replace("\\", "\\\\").replace("'", "\\'")
            js_code = """
            () => {{
                const el = document.querySelector('{}');
                return el && el.value && el.value.trim() !== '';
            }}
            """.format(escaped_selector)

        # 等待函数返回true（即input有值）
        try:
            self.page.wait_for_function(js_code, timeout=timeout)
            return True
        except Exception as e:
            print(f"等待输入框 {selector} 有值超时: {e}")
            return False
    