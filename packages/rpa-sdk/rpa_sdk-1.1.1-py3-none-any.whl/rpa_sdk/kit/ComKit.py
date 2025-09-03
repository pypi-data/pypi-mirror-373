import json
import random
import re
from ast import literal_eval

from . import StrKit
from datetime import datetime, date


def new_temperature():
    # 生成一个在 35.5 到 37.0 之间的随机浮点数，并保留一位小数
    temperature = round(random.uniform(35.5, 37.0), 1)
    return str(temperature)


def new_breathe():
    # 生成一个在 18 到 20 之间的随机整数
    rate = random.randint(18, 20)
    return str(rate)

def get_bmi(height,weight):

    if height == 0 or weight == 0:
        return 0
    bmi = weight / (height ** 2)
    return round(bmi, 2)

def get_leftBP(leftVal, rightVal):
    # 如果某侧值有效（大于1），则直接返回,否则基于另一侧值加上一个随机偏移量（±3）生成
    val = random.randint(-3, 3)
    if StrKit.getInt(leftVal) > 1:
        return leftVal
    else:
        return StrKit.getInt(rightVal) - val


def get_rightBP(leftVal, rightVal):
    # 如果某侧值有效（大于1），则直接返回,否则基于另一侧值加上一个随机偏移量（±3）生成
    val = random.randint(-3, 3)
    if StrKit.getInt(rightVal) > 1:
        return rightVal
    else:
        return StrKit.getInt(leftVal) - val


def get_self_care(val):
    """
    解析自理能力字符串。

    :param val: JSON 格式字符串，例如: {"result":"可自理","values":[0,0,0,0,0]}
    :return: (result, values) 元组；若解析失败则返回 ("", [])
    """
    try:
        data = json.loads(val)

        result = data.get('result', '')
        values = data.get('values', [])

        # 类型检查，避免非预期类型
        if not isinstance(result, str):
            result = str(result)

        if not isinstance(values, list) or not all(isinstance(v, int) for v in values):
            values = []

        return result, values

    except (json.JSONDecodeError, TypeError):
        # 捕获 JSON 解析错误或类型错误
        return "可自理", [0, 0, 0, 0, 0]


def get_denture_state(val):
    if val==None or val.strip() == "正常" or val.strip()=="{}" or val.strip()=="[]":
        return "正常"

    try:
        teeth_dict = json.loads(val)
    except json.JSONDecodeError:
        try:
            teeth_dict = literal_eval(val)
        except:
            return "正常"
    # 检测值是否包含数字
    abnormal_keys = [
        key for key, value in teeth_dict.items()
        if re.search(r'\d', str(value))  # 转为字符串并检查数字
    ]
    return ",".join(abnormal_keys) if abnormal_keys else "正常"


def get_denture_info(result: str, key: str) -> tuple:
    teeth_dict = {}

    result = result.strip()

    try:
        # 尝试用 json.loads 解析标准 JSON 字符串
        teeth_dict = json.loads(result)
    except json.JSONDecodeError:
        try:
            # 尝试用 literal_eval 解析类似 Python 字典的字符串
            teeth_dict = literal_eval(result)
        except:
            pass  # 都失败则返回空字典

    value = teeth_dict.get(key, [])

    # 确保 value 是字符串或可迭代对象
    if isinstance(value, str):
        parts = value.split(',')
    elif isinstance(value, (list, tuple)):
        parts = [str(item) if item is not None else '' for item in value]
    else:
        parts = []

    # 截取前4个元素并补全到4个
    parts = parts[:4]
    parts += [''] * (4 - len(parts))

    return tuple(parts)

def parse_medical_item(item_str):
    """
    解析医学数据项，支持数值和符号型值，如：
    - "血小板压积:0.29 %(↑)"
    - "抗坏血酸:± mmol/l(±)"
    返回: (name, value, unit, hint) 或 None
    """
    item_str = item_str.strip()
    # 正则表达式修正：兼容符号型value
    pattern = r'^([^:]+):\s*([^\(\s]+)\s*([^\s\(]*)\s*\(([^)]+)\)$'
    match = re.match(pattern, item_str)
    if match:
        name = match.group(1).strip()
        if '尿隐血' in name:
            pass
        value = match.group(2).strip()
        unit = match.group(3).strip()
        hint = match.group(4).strip()
        return (name, value, unit, hint)
    else:
        return None

def get_medical_other(val):
    ret = []
    items = StrKit.getStr(val).split(";")
    for item in items:
        name, value, unit, hint = parse_medical_item(item)
        ret.append(f"{name}:{value} {unit}")
    if len(ret) > 0:
        return "；".join(ret)
    return ""


def days_diff(date1, date2):
    """
    计算两个日期之间的绝对天数差
	        支持类型: datetime对象、date对象、字符串（自动解析常见格式）

    参数:
	            date1: 第一个日期（datetime/date/str）
	            date2: 第二个日期（datetime/date/str）

    返回:
        int: 相差天数的绝对值
    """
    # 支持的日期格式列表（按解析优先级排序）
    DATE_FORMATS = [
        "%Y-%m-%d",  # ISO格式 2023-10-01
        "%Y/%m/%d",  # 2023/10/01
        "%d-%m-%Y",  # 欧洲格式 01-10-2023
        "%d/%m/%Y",  # 01/10/2023
        "%m-%d-%Y",  # 美国格式 10-01-2023
        "%m/%d/%Y",  # 10/01/2023
        "%Y%m%d"  # 紧凑格式 20231001
    ]

    def _parse_date(d):
        """统一解析多种日期格式为datetime对象"""
        if isinstance(d, datetime):
            return d
        if isinstance(d, date):
            return datetime(d.year, d.month, d.day)
        if isinstance(d, str):
            # 尝试所有支持的格式
            for fmt in DATE_FORMATS:
                try:
                    return datetime.strptime(d, fmt)
                except ValueError:
                    continue
            raise ValueError(f"无法识别的日期格式: {d}")
        raise TypeError("不支持的日期类型，必须是date/datetime/str")

    try:
        # 解析两个日期
        d1 = _parse_date(date1)
        d2 = _parse_date(date2)

        # 计算绝对差值
        return abs((d2 - d1).days)

    except (ValueError, TypeError) as e:
        print(f"日期计算错误: {str(e)}")
        return 0  # 或根据需求抛出异常

if __name__ == '__main__':
    pass
    # val = '湖南省永州市江永县江镇荷叶塘区委会1组'
    # print(parse_chinese_address(val))
    # val = '湖北省恩施土家族苗族自治州巴东县渡河镇野马洞村三组9号'
    # print(parse_chinese_address(val))
