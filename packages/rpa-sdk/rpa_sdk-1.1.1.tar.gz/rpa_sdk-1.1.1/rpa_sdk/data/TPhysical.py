"""
体检记录对象类 - TPhysical
"""

from typing import Dict, Any, Optional
from datetime import datetime


class TPhysical:
    """体检记录对象类"""
    
    def __init__(self, data: Dict[str, Any]):
        """
        初始化体检记录对象
        :param data: 包含体检数据的字典
        """
        self.data = data
        
        # 基本信息
        self.physical_id = self._get_str('physical_id', '')
        self.date = self._get_date_str('checkDate', '')
        self.idcard = self._get_str('idcard').replace("Ⅹ", "X")
        self.name = self._get_str('name', '')
        self.sex = self._get_str('sex', '')
        self.age = self._get_int('age', 0)
        self.mobile = self._get_str('mobile', '')
        self.tag = self._get_str('tag', '')
        self.group_id = self._get_str('group_id', '')
        self.area_id = self._get_str('area_id', '')
        
        # 症状和健康状态
        self.symptom = self._get_str('symptom', '无症状')
        self.healthStatus = self._get_str('healthStatus', '满意')
        self.selfCare = self._get_str('selfCare', '{"result":"可自理","values":[0,0,0,0,0]}')
        self.cognitive = self._get_str('cognitive', '正常')
        self.cognitiveZF = self._get_int('cognitiveZF', 0)
        self.emotion = self._get_str('emotion', '正常')
        self.emotionZF = self._get_int('emotionZF', 0)
        
        # 生命体征
        self.temperature = self._get_str('temperature', '36.5')
        self.pulse = self._get_int('pulse', 0)
        self.breathe = self._get_int('breathe', 20)
        self.lsbp = self._get_int('LSBP', 0)
        self.ldbp = self._get_int('LDBP', 0)
        self.rsbp = self._get_int('RSBP', 0)
        self.rdbp = self._get_int('RDBP', 0)
        self.height = self._get_float('height', 0)
        self.weight = self._get_float('weight', 0)
        self.waistline = self._get_float('waistline', 0)
        self.bmi = self._get_float('bmi', 0)
        
        # 生活方式
        self.sportFreq = self._get_str('sportFreq', '不锻炼')
        self.sportMinute = self._get_int('sportMinute', 30)
        self.sportYear = self._get_int('sportYear', 1)
        self.sportMode = self._get_str('sportMode', '散步')
        self.foodStyle = self._get_str('foodStyle', '荤素均衡')
        self.smoke = self._get_str('smoke', '从不吸烟')
        self.smokeNum = self._get_int('smokeNum', 0)
        self.smokeStart = self._get_int('smokeStart', 0)
        self.smokeStop = self._get_int('smokeStop', 0)
        self.drink = self._get_str('drink', '从不')
        self.drinkNum = self._get_float('drinkNum', 0)
        self.drinkHas = self._get_str('drinkHas', '')
        self.drinkStart = self._get_int('drinkStart', 0)
        self.drinkStop = self._get_int('drinkStop', 0)
        self.isDrink = self._get_str('isDrink', '')
        self.drinkCate = self._get_str('drinkCate', '')
        
        # 职业病危害因素
        self.occupational = self._get_str('occupational', '无')
        self.jobs = self._get_str('jobs', '')
        self.workTime = self._get_int('workTime', 0)
        self.dust = self._get_str('dust', '')
        self.dustPro = self._get_str('dustPro', '无')
        self.ray = self._get_str('ray', '')
        self.rayPro = self._get_str('rayPro', '无')
        self.physical = self._get_str('physical', '')
        self.physicalPro = self._get_str('physicalPro', '无')
        self.chemicals = self._get_str('chemicals', '')
        self.chemicalsPro = self._get_str('chemicalsPro', '无')
        self.otherToxic = self._get_str('otherToxic', '')
        self.otherToxicPro = self._get_str('otherToxicPro', '无')
        
        # 脏器查体
        self.lip = self._get_str('lip', '红润')
        self.denture = self._get_str('denture', '正常')
        self.pharyngeal = self._get_str('pharyngeal', '无充血')
        self.leftEye = self._get_str('leftEye', '')
        self.rightEye = self._get_str('rightEye', '')
        self.recLeftEye = self._get_str('recLeftEye', '')
        self.recRightEye = self._get_str('recRightEye', '')
        self.hearing = self._get_str('hearing', '听见')
        self.motion = self._get_str('motion', '正常')
        self.fundus = self._get_str('fundus', '正常')
        self.skin = self._get_str('skin', '正常')
        self.sclera = self._get_str('sclera', '正常')
        self.lymphnodes = self._get_str('lymphnodes', '未触及')
        self.barrelChest = self._get_str('barrelChest', '否')
        self.breathSound = self._get_str('breathSound', '正常')
        self.rales = self._get_str('rales', '无').replace("正常","无")
        self.heartRate = self._get_int('heartRate', 0)
        self.rhythm = self._get_str('rhythm', '齐')
        self.heartMurmur = self._get_str('heartMurmur', '无')
        self.abdominAltend = self._get_str('abdominAltend', '无')
        self.adbominAlmass = self._get_str('adbominAlmass', '无')
        self.liverBig = self._get_str('liverBig', '无')
        self.splenomegaly = self._get_str('splenomegaly', '无')
        self.dullness = self._get_str('dullness', '无')
        self.edema = self._get_str('edema', '无')
        self.footPulse = self._get_str('footPulse', '触及双侧对称')
        self.dre = self._get_str('dre', '')
        self.breast = self._get_str('breast', '')
        self.vulva = self._get_str('vulva', '')
        self.vaginal = self._get_str('vaginal', '')
        self.cervix = self._get_str('cervix', '')
        self.palace = self._get_str('palace', '')
        self.attachment = self._get_str('attachment', '')
        self.tjother = self._get_str('tjother', '')
        
        # 血常规
        self.hgb = self._get_str('hgb', '')
        self.wbc = self._get_str('wbc', '')
        self.rbc = self._get_str('rbc', '')
        self.plt = self._get_str('plt', '')
        self.brtOther = self._get_str('brtOther', '')
        self.brtEval = self._get_str('brtEval', '')
        
        # 尿常规
        self.pro = self._get_str('pro', '')
        self.glu = self._get_str('glu', '')
        self.ket = self._get_str('ket', '')
        self.oc = self._get_str('oc', '')
        self.urtOther = self._get_str('urtOther', '')
        self.urtEval = self._get_str('urtEval', '')
        
        # 血糖
        self.fbs = self._get_str('fbs', '')
        self.hba1c = self._get_str('hba1c', '')
        self.hba1cEval = self._get_str('hba1cEval', '')
        # 肝功能
        self.alt = self._get_str('alt', '')
        self.ast = self._get_str('ast', '')
        self.alb = self._get_str('alb', '')
        self.tbil = self._get_str('tbil', '')
        self.dbil = self._get_str('dbil', '')
        self.liverEval = self._get_str('liverEval', '')
        
        # 肾功能
        self.crea = self._get_str('crea', '')
        self.ua = self._get_str('ua', '')
        self.bun = self._get_str('bun', '')
        self.kal = self._get_str('kal', '')
        self.nat = self._get_str('nat', '')
        self.kidneyEval = self._get_str('kidneyEval', '')
        
        # 血脂
        self.chol = self._get_str('chol', '')
        self.tg = self._get_str('tg', '')
        self.ldl = self._get_str('ldl', '')
        self.hdl = self._get_str('hdl', '')
        self.lipidEval = self._get_str('lipidEval', '')
        
        # 健康评估
        self.cerebrovascularDisease = self._get_str('cerebrovascularDisease', '未发现')
        self.kidneyDisease = self._get_str('kidneyDisease', '未发现')
        self.heartDisease = self._get_str('heartDisease', '未发现')
        self.vascularDisease = self._get_str('vascularDisease', '未发现')
        self.eyeDiseases = self._get_str('eyeDiseases', '未发现')
        self.neurologicalDiseases = self._get_str('neurologicalDiseases', '未发现')
        self.otherDiseasesone = self._get_str('otherDiseasesone', '')
        
        # 住院史和家族史
        self.diseaseHospital = self._get_str('diseaseHospital', '[]')
        self.diseaseFamily = self._get_str('diseaseFamily', '[]')

        # 用药情况
        self.takeMedicine = self._get_str('takeMedicine', '[]')

        self.tcmd_values = self._get_str('tcmd_values', '[]')
        
        # 心电图和B超
        self.ecg = self._get_str('ecg', '')
        self.ecg_src = self._get_str('ecg_src', '')
        self.bscan = self._get_str('bscan', '')
        self.bscan_src = self._get_str('bscan_src', '')
        self.dr = self._get_str('dr', '')
        self.dr_src = self._get_str('dr_src', '')

    
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
                    '%Y-%m-%d %H:%M:%S',  # 2025-06-30 00:00:00
                    '%Y-%m-%d',           # 2025-06-30
                    '%Y/%m/%d',           # 2025/06/30
                    '%Y.%m.%d',           # 2025.06.30
                    '%m/%d/%Y',           # 06/30/2025
                    '%d/%m/%Y',           # 30/06/2025
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

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.data.copy()
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"TPhysical(physical_id={self.physical_id}, name={self.name}, checkDate={self.date})"
    
    def __repr__(self) -> str:
        """对象表示"""
        return self.__str__()
