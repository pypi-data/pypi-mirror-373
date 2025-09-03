"""
档案记录对象类 - TArchive
"""

from typing import Dict, Any, Optional
from datetime import datetime


class TArchive:
    """档案记录对象类"""
    
    def __init__(self, data: Dict[str, Any]):
        """
        初始化档案记录对象
        :param data: 包含档案数据的字典
        """
        self.data = data

        self.area_id = self._get_str('area_id', '')
        # 基本信息
        self.createDate = self._get_date_str('createDate', '')
        self.name = self._get_str('name', '')
        self.nation = self._get_str('nation', '汉族')
        self.nation = f"{self.nation}族" if not '族' in self.nation else self.nation
        self.sex = self._get_str('sex', '')
        self.birthday = self._get_date_str('birthday', '')
        self.idcard = self._get_str('idcard').replace("Ⅹ", "X")
        self.tag = self._get_str('tag', '')
        self.card_type = self._get_str('card_type', '居民身份证')
        self.mobile = self._get_str('mobile', '')
        self.phone = self._get_str('phone', '')
        
        # 地址信息
        self.card_address = self._get_str('card_address', '')
        self.live_address = self._get_str('live_address', '')
        self.region = self._get_str('region', '')
        self.workplace = self._get_str('workplace', '无')
        self.reside = self._get_str('reside', '户籍')
        
        # 联系人信息
        self.linker = self._get_str('linker', '')
        self.linkerTel = self._get_str('linkerTel', '')
        
        # 血型信息
        self.blood = self._get_str('blood', '不详')
        self.blood_rh = self._get_str('blood_rh', '不详')
        
        # 个人信息
        self.education = self._get_str('education', '不详')
        self.profession = self._get_str('profession', '无职业').replace('农、林、牧、渔、水利专业生产人员', '农、林、牧、渔业生产及辅助人员')
        self.marry = self._get_str('marry', '未说明的婚姻状况')
        self.payment = self._get_str('payment', '其他')
        
        # 过敏史
        self.history_allergy = self._get_str('history_allergy', '无')
        
        # 暴露史
        self.history_expose = self._get_str('history_expose', '无')
        
        # 家族史
        self.history_family_father = self._get_str('history_family_father', '无')
        self.history_family_mother = self._get_str('history_family_mother', '无')
        self.history_family_brother = self._get_str('history_family_brother', '无')
        self.history_family_child = self._get_str('history_family_child', '无')
        
        # 遗传病史
        self.history_genetic = self._get_str('history_genetic', '无')
        
        # 残疾情况
        self.disability = self._get_str('disability', '无残疾')
        
        # 居住环境
        self.kitchen = self._get_str('kitchen', '油烟机')
        self.fuel = self._get_str('fuel', '液化气')
        self.water = self._get_str('water', '自来水')
        self.toilet = self._get_str('toilet', '卫生厕所')
        self.corral = self._get_str('corral', '无')
        
        # 既往史
        self.history_past_disease = self._get_str('history_past_disease', '[]')
        self.history_past_operation = self._get_str('history_past_operation', '[]')
        self.history_past_trauma = self._get_str('history_past_trauma', '[]')
        self.history_past_blood = self._get_str('history_past_blood', '[]')

        self.tracker = self._get_str('tracker', '').replace('农、林、牧、渔、水利专业生产人员', '农、林、牧、渔业生产及辅助人员')
        self.created = self._get_date_str('created', '')
        self.updated = self._get_date_str('updated', '')
    
    def _get_str(self, key: str, default: str = "") -> str:
        """获取字符串值"""
        value = self.data.get(key, default)
        if value is None or value == "":
            return default
        return str(value)
    
    def _get_int(self, key: str, default: int = 0) -> int:
        """获取整数值"""
        try:
            value = self.data.get(key, default)
            if value is None or value == "":
                return default
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def _get_float(self, key: str, default: float = 0.0) -> float:
        """获取浮点数值"""
        try:
            value = self.data.get(key, default)
            if value is None or value == "":
                return default
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def _get_bool(self, key: str, default: bool = False) -> bool:
        """获取布尔值"""
        value = self.data.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', '是')
        return bool(value) if value is not None else default

    def _get_date_str(self, key: str, default: str = "") -> str:
        """获取日期字符串，转换为标准格式 YYYY-MM-DD"""
        from datetime import datetime

        value = self.data.get(key, default)

        if not value or value == "":
            return default

        # 如果已经是字符串，尝试解析并格式化
        if isinstance(value, str):
            try:
                # 尝试解析各种可能的日期格式
                date_formats = [
                    '%Y-%m-%d %H:%M:%S',  # 2024-11-05 00:00:00
                    '%Y-%m-%d',           # 2024-11-05
                    '%Y/%m/%d',           # 2024/11/05
                    '%Y.%m.%d',           # 2024.11.05
                    '%m/%d/%Y',           # 11/05/2024
                    '%d/%m/%Y',           # 05/11/2024
                ]

                for fmt in date_formats:
                    try:
                        parsed_date = datetime.strptime(value, fmt)
                        return parsed_date.strftime('%Y-%m-%d')
                    except ValueError:
                        continue

                # 如果所有格式都失败，返回原始值
                return str(value)

            except Exception:
                return str(value)

        # 如果是datetime对象
        elif hasattr(value, 'strftime'):
            return value.strftime('%Y-%m-%d')

        # 其他情况返回字符串形式
        else:
            return str(value) if value else default

    def get_age(self) -> int:
        """根据生日计算年龄"""
        if not self.birthday:
            return 0
        
        try:
            birth_date = datetime.strptime(self.birthday, '%Y-%m-%d')
            today = datetime.now()
            age = today.year - birth_date.year
            
            # 如果今年的生日还没到，年龄减1
            if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
                age -= 1
                
            return max(0, age)
        except:
            return 0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.data.copy()
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"TArchive(id={self.archive_id}, name={self.name}, idcard={self.idcard})"
    
    def __repr__(self) -> str:
        """对象表示"""
        return self.__str__()
