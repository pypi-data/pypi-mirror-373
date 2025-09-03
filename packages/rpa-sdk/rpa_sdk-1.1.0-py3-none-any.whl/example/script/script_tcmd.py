"""
体检任务处理器
"""
import json
from datetime import datetime
from typing import Dict, Any

from rpa_sdk.data import TPhysical
from rpa_sdk.kit import StrKit, DialogKit
from rpa_sdk.manager.base_handler import BaseHandler
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from operations_registry import get_project_operations_name



class TcmdHandler(BaseHandler):
    TASK_NAME = "中医"  # 子类必须重写
    FIELD_NAME = "physical_id"

    """体检任务处理器"""

    def __init__(self, records, browser_manager, check_mode, db_manager, message_sender=None, result_sender=None, element_operations_impl=None):
        # 如果没有指定元素操作实现，使用项目默认实现
        if element_operations_impl is None:
            element_operations_impl = get_project_operations_name()
        
        print(f"[TcmdHandler] 使用元素操作实现: {element_operations_impl}")
        
        # 检查是否为演示模式（browser_manager为None）
        if browser_manager is None:
            print("[TcmdHandler] 演示模式：跳过浏览器相关初始化")
            # 设置基本属性但不调用父类初始化
            self.records = records
            self.check_mode = check_mode
            self.db_manager = db_manager
            self.message_sender = message_sender
            self.result_sender = result_sender
            self.element_operations_impl = element_operations_impl
            self.browser_manager = None
            self.page = None
            self.element_ops = None
            return
        
        # 正常模式：调用父类初始化
        super().__init__(records, browser_manager, check_mode, db_manager, message_sender, result_sender, element_operations_impl)

    div_parent = "//div[@class='x-tab-panel-body x-tab-panel-body-noborder x-tab-panel-body-top']/div[not(contains(@class,'x-hide-display'))]"
    div_toolbar = "//button[@class=' x-btn-text query']/ancestor::td[@class='x-toolbar-left']"
    def load_page(self)->bool:
        if self.page is None:
            print("[TcmdHandler] 演示模式：跳过页面加载")
            return True
        
        self.page.wait_for_timeout(1000)
        self.close_dialog("取消")
        self.page.click("//ul[@id='_topTab']//a[text()='健康管理']/..")
        if self.page.query_selector("//li[@id='HR']//a[text()='健康档案' and contains(@class,'up')]"):
            self.page.click("//li[@id='HR']//a[text()='健康档案' and contains(@class,'up')]")
        self.page.click("//ul[@id='HR_module']//a[@title='个人健康档案管理']")
        self.page.wait_for_timeout(1000)
        self.wait_load()
        self.set_combobox(f"({self.div_toolbar}//input)[1]", "身份证号")
        return True


    def process_single_record(self, record: Dict[str, Any], index: int, total: int) -> bool:
        if self.page.is_visible("//a[@id='CLOSE']", timeout=3000):
            self.page.click("//a[@id='CLOSE']")

        physical = TPhysical(record)
        if not self.exists_archive(physical.idcard):
            self.result.append("无档案")
            return False
        self.page.click("//button[text()='查看(F3)']")
        self.page.wait_for_load_state('load')

        return self.set_tcmd(physical)

    def exists_archive(self, idcard):
        '''
        判断身份证号是否已经建档
        :param idcard:
        :return:
        '''
        cmb_selector ="//div[@class='x-panel-bbar x-panel-bbar-noborder']//td[@class='x-toolbar-cell'][15]//input"
        if self.page.locator(cmb_selector).input_value()!='正常':
            self.set_combobox(cmb_selector, "正常")
        self.page.wait_for_timeout(1000)
        self.page.locator(f"{self.div_toolbar}//input").nth(1).fill(idcard)
        self.page.locator(f"{self.div_toolbar}//input").nth(1).press("Enter")
        self.wait_load()
        if self.page.query_selector(f"//table[@class='x-grid3-row-table']//div[text()='{idcard}']"):
            return True

        self.set_combobox(cmb_selector,"已注销")
        self.wait_load()
        if self.page.query_selector(f"//table[@class='x-grid3-row-table']//div[text()='{idcard}']"):
            self.page.click("//button[text()='注销恢复(F7)']")
            self.page.wait_for_timeout(3000)
            dlg_xpath="//div[@class=' x-window x-window-plain x-resizable-pinned' and contains(@style,'visibility: visible;')]"
            if self.page.query_selector(f"{dlg_xpath}//div[@class='x-grid3-body']//tr"):
                self.page.click(f"{dlg_xpath}//tr[@class='x-grid3-hd-row']//div[@class='x-grid3-hd-inner x-grid3-hd-checker']")
                self.page.click(f"{dlg_xpath}//button[text()='恢复(F1)']")
                self.close_dialog()
                self.set_combobox(cmb_selector, "正常")
                self.wait_load()
                if self.page.query_selector(f"//table[@class='x-grid3-row-table']//div[text()='{idcard}']"):
                    return True

        self.set_combobox(cmb_selector,"暂停管理")
        self.wait_load()
        if self.page.query_selector(f"//table[@class='x-grid3-row-table']//div[text()='{idcard}']"):
            self.page.click("//button[text()='暂停管理恢复(F6)']")
            self.page.wait_for_timeout(1000)
            self.close_dialog()
            self.set_combobox(cmb_selector, "正常")
            self.wait_load()
            if self.page.query_selector(f"//table[@class='x-grid3-row-table']//div[text()='{idcard}']"):
                return True
        else:
            return False

    def set_tcmd(self, physical: TPhysical)->bool:
        if StrKit.isEmpty(physical.tcmd_values):
            self.result.append('没有数据')
            return False
        try:
            values = json.loads(physical.tcmd_values)
            self.page.click("//span[text()='中医体质辨识管理' and @class='x-tab-strip-text ']")
            self.wait_load()
            # 记录中没有体检记录
            xpath = f"//button[text()='删除(F1)']/ancestor::div[@class='x-panel-tbar x-panel-tbar-noborder']/..//div[contains(@class,'x-grid3-row')]//div[text()='{physical.date}']"
            if self.page.query_selector(xpath):
                self.page.click(f"{xpath}/ancestor::table/..")
            else:
                self.wait_for_input_has_value(f"{self.div_parent}//input[@name='reportDate']")
                reportDate = self.page.locator("//input[@name='reportDate']").input_value()
                today_date = datetime.now().strftime("%Y-%m-%d")
                while reportDate != today_date:
                    self.page.click(
                        f"{self.div_parent}//div[@class='x-panel-tbar x-panel-tbar-noborder']//button[text()='新增(F2)']")
                    self.page.wait_for_timeout(1000)
                    reportDate = self.page.locator("//input[@name='reportDate']").input_value()

            for i in range(0, 33):
                xpath = f"(//font[text()='问卷信息']//ancestor::fieldset//table//tr//input)[{i + 1}]"
                self.set_combobox(xpath, f"[{StrKit.getStr(values[i])}]")
            self.page.locator(f"{self.div_parent}//input[@name='reportDate']").fill(physical.date)
            self.page.click("//input[@name='reportUser']/../img")
            self.page.wait_for_selector("//div[@class='x-layer x-combo-list ' and contains(@style,'visibility: visible;')]",timeout=2000)
            self.page.click("//div[@class='x-layer x-combo-list ' and contains(@style,'visibility: visible;')]//span[text()='刘帅']")
            ret = DialogKit.showQuestion("确定保存数据？") if self.check_mode else True
            if ret:
                self.page.click(f"{self.div_parent}//button[text()='保存(F1)']")
                self.page.wait_for_timeout(1000)
                self.close_dialog()
                self.result.append('中医体质成功')
                return True
            else:
                self.result.append('中医体质失败')
                return False
        except Exception as e:
            print(e)
            self.result.append('中医体质失败')
            return False

