"""
随访记录对象类 - TVisit
"""

from typing import Dict, Any, Optional
from datetime import datetime

from dateutil.relativedelta import relativedelta

from ..kit import StrKit


class TVisit:
    """随访记录对象类"""
    
    def __init__(self, data: Dict[str, Any]):
        """
        初始化随访记录对象
        :param data: 包含随访数据的字典
        """

        self.data = data
        
        # 基本信息
        self.visit_id = self._get_str('visit_id', '')
        self.date = self._get_date_str('visitDate', '')
        self.idcard = self._get_str('idcard').replace("Ⅹ", "X")
        self.name = self._get_str('name', '')
        self.sex = self._get_str('sex', '')
        self.age = self._get_int('age', 0)
        self.mobile = self._get_str('mobile', '')
        self.tag = self._get_str('tag', '')
        self.group_id = self._get_str('group_id', '')
        self.area_id = self._get_str('area_id', '')
        self.visitWay = self._get_str('visitWay', '家庭').replace('体检','家庭')
        # 症状和体征
        self.symptoms = self._get_str('symptoms', '无症状')
        self.sbp = self._get_int('lsbp', 0) if self._get_int('lsbp', 0)+self._get_int('ldbp', 0) > self._get_int('rsbp', 0)+self._get_int('rdbp', 0) else self._get_int('rsbp', 0)
        self.dbp = self._get_int('ldbp', 0) if self._get_int('lsbp', 0)+self._get_int('ldbp', 0) > self._get_int('rsbp', 0)+self._get_int('rdbp', 0)  else self._get_int('rdbp', 0)
        self.lsbp = self._get_int('lsbp', 0)
        self.ldbp = self._get_int('ldbp', 0)

        self.height = self._get_float('height', 0)
        self.weight = self._get_float('weight', 0)
        self.waistline = self._get_float('waistline', 0)
        self.bmi = self._get_str('bmi', '0')

        self.otherSigns = self._get_str('otherSigns', '无')
        self.heartRate = self._get_int('heartRate', 0)
        self.pulsation = self._get_str('pulsation', '触及正常').replace("无","触及正常")
        
        # 生活方式
        self.smoke = self._get_int('smoke', 0)  # 0-不吸烟, 1-吸烟
        self.drink = self._get_int('drink', 0)  # 0-不饮酒, 1-饮酒
        self.sportTimes = self._get_int('sportTimes', 0)  # 运动次数
        self.sportMinute = self._get_int('sportMinute', 0)  # 运动时间(分钟)
        
        # 心理和依从性
        self.psychology = self._get_str('psychology', '良好')  # 心理状态
        self.obeyDoctor = self._get_str('obeyDoctor', '良好')  # 遵医行为
        self.salt = self._get_str('salt', '轻')  # 摄盐情况
        self.food = self._get_int('food', 200)  # 主食量(克)
        
        # 检查指标
        self.fbs = self._get_float('fbs', 0)  # 空腹血糖
        self.pbs = self._get_float('pbs', 0)  # 餐后血糖
        self.hgb = self._get_float('hgb', 0)  # 血红蛋白
        
        # 用药依从性
        self.obeyMedicine_eh = self._get_str('obeyMedicine_eh', '规律')  # 高血压用药依从性
        self.obeyMedicine_dm = self._get_str('obeyMedicine_dm', '规律')  # 糖尿病用药依从性
        
        # 药物不良反应
        self.badEffect_eh = self._get_str('badEffect_eh', '无')  # 高血压药物不良反应
        self.badEffect_dm = self._get_str('badEffect_dm', '无')  # 糖尿病药物不良反应
        
        # 低血糖反应
        self.glycopenia = self._get_str('glycopenia', '无')

        # 用药情况
        self.takeMedicine = self._get_str('takeMedicine', '[]')  # 服用药物
        self.insulin = self._get_str('insulin', '[]')  # 胰岛素使用

        #备注
        self.note = self._get_str('note', '') if StrKit.isNotEmpty(self._get_str('note', ''))  else self._get_str('suggestion', '')

        # 治疗调整
        self.therapy_eh = self._get_str('therapy_eh', '无')  # 高血压治疗调整
        self.therapy_dm = self._get_str('therapy_dm', '无')  # 糖尿病治疗调整

        # 用药依从性原因
        self.obeyMedicine_reason_eh = self._get_str('obeyMedicine_reason_eh','其他=饮食调理，运动治疗')
        self.obeyMedicine_reason_dm = self._get_str('obeyMedicine_reason_dm', '其他=饮食调理，运动治疗')

    
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
                    '%Y-%m-%d %H:%M:%S',  # 2025-08-05 09:04:06
                    '%Y-%m-%d',           # 2025-08-05
                    '%Y/%m/%d %H:%M:%S',  # 2025/08/05 09:04:06
                    '%Y/%m/%d',           # 2025/08/05
                    '%Y.%m.%d %H:%M:%S',  # 2025.08.05 09:04:06
                    '%Y.%m.%d',           # 2025.08.05
                ]

                for fmt in date_formats:
                    try:
                        parsed_date = datetime.strptime(value, fmt)
                        # 如果原格式包含时间，保留时间；否则只返回日期
                        # if ' ' in value:
                        #     return parsed_date.strftime('%Y-%m-%d %H:%M:%S')
                        # else:
                        return parsed_date.strftime('%Y-%m-%d')
                    except ValueError:
                        continue

                # 如果所有格式都失败，返回原始值
                return str(value)

            except Exception:
                return str(value)

        # 如果是datetime对象
        elif hasattr(value, 'strftime'):
            return value.strftime('%Y-%m-%d %H:%M:%S')

        # 其他情况返回字符串形式
        else:
            return str(value) if value else default


    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.data.copy()
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"TVisit(visit_id={self.visit_id}, name={self.name}, visitDate={self.visitDate})"
    
    def __repr__(self) -> str:
        """对象表示"""
        return self.__str__()


    def get_next_visit_bp(self):
        """
        血压随访日期计算
        返回格式: YYYY-MM-DD
        逻辑说明：
            1. 65岁以下患者：血压≥140/90mmHg需14天内随访
            2. 65岁及以上患者：血压≥150/90mmHg需14天内随访
        3. 达标患者3个月后随访
        """

        # 血压判断阈值
        if self.age < 65:
            threshold = (140, 90)
        else:
            threshold = (150, 90)

        # 判断随访周期
        if self.sbp >= threshold[0] or self.dbp >= threshold[1]:
            delta = relativedelta(days=14)
        else:
            delta = relativedelta(months=3)

        # 将字符串日期转换为datetime对象进行计算
        visit_date = datetime.strptime(self.date, "%Y-%m-%d")
        next_visit_date = visit_date + delta
        return next_visit_date.strftime("%Y-%m-%d")

    def get_next_visit_dm(self):
        """
        糖尿病随访日期计算（空腹血糖优先）
        返回格式: YYYY-MM-DD
        判断标准：
        1. 空腹血糖≥7mmol/L → 14天内随访
        2. 随机血糖≥11.1mmol/L → 14天内随访
        3. 达标患者 → 3个月后随访
        """
        try:
            # 获取并转换数据
            visit_date = datetime.strptime(self.date, "%Y-%m-%d")
        except ValueError as e:
            print(f"糖尿病随访日期格式错误: {str(e)}")
            return ""
        except TypeError as e:
            print(f"输入日期类型错误: {str(e)}")
            return ""

        is_urgent = False

        # 优先判断空腹血糖
        if self.fbs >= 7.0:
            is_urgent = True
        # 空腹血糖不满足条件，判断随机血糖
        elif self.pbs >= 11.1:
            is_urgent = True
        # 都没有满足紧急情况，默认为达标患者，3个月后随访

        # 计算随访间隔
        delta = relativedelta(days=14) if is_urgent else relativedelta(months=3)
        visit_date = datetime.strptime(self.date, "%Y-%m-%d")
        return (visit_date + delta).strftime("%Y-%m-%d")

    def get_target_weight(self, days, max_loss=1.0, max_gain=0.5):
        """计算基于身高、当前体重和天数的目标体重"""
        try:
            # 参数类型转换与有效性校验
            height = self.height
            weight = self.weight
            day_count = min(max(int(days), 15), 120)  # 约束天数范围 15-120
        except (ValueError, TypeError) as e:
            print(f'参数类型错误: {e}')
            return "0.0"

        # 数值有效性检查 (确保正数)
        if any(v <= 0 for v in [height, weight, day_count]):
            print(f'无效数值参数: 身高={height}cm, 体重={weight}kg, 天数={days}')
            return "0.0"

        # 核心计算逻辑
        height_m = height / 100  # 厘米转米
        current_bmi = weight / (height_m ** 2)
        max_adjust = max_loss if day_count > 15 else max_gain  # 动态调整幅度

        # BMI超标处理
        if current_bmi > 24:
            # target_weight = 24 * (height_m ** 2)  # BMI24标准体重
            # adjustment = min(max_adjust, weight - target_weight)  # 允许最大减重量
            result = weight - max_adjust
        elif current_bmi < 18.5:
            target_weight = 18.5 * (height_m ** 2)  # BMI18.5标准体重
            adjustment = min(max_adjust, target_weight - weight)  # 允许最大增重量
            result = weight + adjustment
        else:
            result = weight  # 正常范围无需调整

        # 最低体重保护 (不低于30kg)
        return f"{max(result, 30):.1f}"

    def get_eval_bp(self):
        """优化血压评估逻辑"""

        if '高血压' not in self.tag:
            return ''
        if self.age < 65:
            threshold = (140, 90)
        else:
            threshold = (150, 90)
        return '控制满意' if (self.sbp <= threshold[0] and self.dbp <= threshold[1]) else '控制不满意'

    def get_eval_dm(self):
        """
        糖尿病控制评估（严格医学标准）
        判断规则:
            空腹血糖(fbs)优先判断:
                - 正常范围：3.9 < fbs < 7.0 → 控制满意
                - 异常情况：fbs ≤3.9 或 ≥7.0 → 控制不满意

            随机血糖(pbs)次优先判断:
                - 正常范围：3.9 ≤ pbs < 11.1 → 控制满意
                - 异常情况：pbs <3.9 或 ≥11.1 → 控制不满意

            无有效数据返回空字符串
        """
        # 优先处理空腹血糖

        if self.fbs > 0:  # 有效值判断
            if self.fbs < 3.9 or self.fbs > 7.0:
                return '控制不满意'

        # 空腹血糖无效时处理随机血糖
        if self.pbs > 0:  # 有效值判断
            if self.pbs < 3.9 or self.pbs > 11.1:
                return '控制不满意'

        # 无有效数据返回空
        return '控制满意'