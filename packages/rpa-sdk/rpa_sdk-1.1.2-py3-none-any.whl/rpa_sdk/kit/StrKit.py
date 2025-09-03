# coding=utf-8
# cython: language_level=3
import re
import warnings
from _decimal import Decimal
from datetime import datetime, timedelta, date




def getDefault(val, defVal):
    if isinstance(val, (int, float,Decimal)):
        if val == 0:
            return defVal
        else:
            return val
    if isEmpty(val):
        return defVal
    return val


def getDateStr(val):
    """
    将多种日期类型统一转换为标准格式字符串 (YYYY-MM-DD)

    支持输入类型：
    - datetime.date / datetime.datetime 对象
    - 字符串格式（自动识别常见日期格式）

    返回：
    - 成功：标准格式字符串
    - 失败：保留原值并显示警告（生产环境可改为抛出异常）
    """
    # 处理日期对象
    if isinstance(val, (datetime, date)):
        return val.strftime("%Y-%m-%d")

    # 处理字符串类型
    if isinstance(val, str):
        # 预清洗字符串
        val = val.strip().replace('/', '-').replace('.', '-').replace('\\', '-')

        # 定义支持的日期格式（按优先级排序）
        formats = [
            "%Y-%m-%d",  # 标准格式
            "%Y%m%d",  # 紧凑格式
            "%Y-%m-%d %H:%M:%S",  # 含时间
            "%Y-%m-%d %H:%M",  # 含分钟
            "%Y-%m",  # 年月格式
            "%Y"  # 仅年份
        ]

        # 尝试解析日期
        for fmt in formats:
            try:
                dt = datetime.strptime(val, fmt)
                return dt.date().strftime("%Y-%m-%d")
            except ValueError:
                continue

        # 特殊处理不完整日期
        if len(val) == 6 and val.isdigit():
            try:  # 尝试解析为YYMMDD
                dt = datetime.strptime(val, "%y%m%d")
                return dt.strftime("%Y-%m-%d")
            except:
                pass

        # 解析失败处理
        warnings.warn(f"无法解析日期字符串: {val}", UserWarning)
        return val

    # 非日期类型直接返回
    return val


def getStr(val):
    if val is None:
        return ""
    elif isinstance(val, list):
        return str(val)
    elif isinstance(val, float) and val == int(val):
        return str(int(val))
    else:
        return str(val)


def extract_number_from_string(text):
    """
    从字符串中提取数字部分（支持整数和小数）

    :param text: 输入的字符串
    :return: 提取的数字部分（float 类型），如果未找到数字，返回 None
    """
    match = re.search(r'\d+(\.\d+)?', text)
    if match:
        return match.group()
    return None


def getFloat(value):

    ret = 0
    if value is None:
        ret = 0;
    elif isinstance(value, Decimal):  # 新增支持 Decimal
        ret = float(value)
    elif isinstance(value, float):
        return value
    elif isinstance(value, int):
        return float(value)
    elif isinstance(value, str):
        pattern = r'^[0-9.]+$'
        if re.match(pattern, value):
            ret = float(value)
    return ret


def getInt(value):
    ret = 0
    try:
        if value is None:
            ret = 0
        elif isinstance(value, Decimal):  # 新增支持 Decimal
            return int(value)
        elif isinstance(value, float):
            return int(value)
        elif isinstance(value, int):
            return value
        elif isinstance(value, str):
            pattern = r'^[0-9.]+$'
            if re.match(pattern, value):
                ret = int(float(value))
        return ret
    except Exception as e:
        return ret


def isEmpty(value):

    return value is None or value == ''


def isNotEmpty(value):
    return not isEmpty(value)


def remove_numbers(text):
    if text is None:
        return ""
    # 匹配类似"1、2、3、"的序号，并保留相邻两个标点中的第一个
    pattern = re.compile(r'\b\d+、(?:\s*\d+、)*\s*')
    modified_text = re.sub(pattern, '', text)

    # 将相邻的两个标点替换为一个
    modified_text = re.sub(r';+', ';', modified_text)
    return modified_text


def get_current_year_str() -> str:
    """
    获取当前年份的字符串（格式：YYYY）
    示例：2023
    """
    return str(datetime.now().year)


def get_date(d):
    # 定义支持的日期格式（按解析优先级排序）
    DATE_FORMATS = [
        "%Y-%m-%d", "%Y/%m/%d",  # ISO 格式
        "%d-%m-%Y", "%d/%m/%Y",  # 欧洲格式
        "%m-%d-%Y", "%m/%d/%Y",  # 美国格式
        "%Y%m%d"  # 紧凑格式
    ]

    """统一解析日期为 datetime 对象"""
    if isinstance(d, datetime):
        return d
    if isinstance(d, str):
        for fmt in DATE_FORMATS:
            try:
                return datetime.strptime(d, fmt)
            except ValueError:
                continue
        raise ValueError(f"无法识别的日期格式: {d}")
    raise TypeError("不支持的日期类型，必须是 datetime 或 str")


def compare_dates(date1, date2):
    """
    比较两个日期的大小（支持日期对象和多种格式的字符串）

    参数:
        date1: 第一个日期 (datetime/date/str)
        date2: 第二个日期 (datetime/date/str)

    返回:
        int:
            -1 表示 date1 < date2
            0  表示 date1 == date2
            1  表示 date1 > date2
            None 表示无法比较

    示例:
        compare_dates("2023-10-01", "2023-09-30") -> 1
    """

    try:
        # 解析两个日期
        d1 = get_date(date1)
        d2 = get_date(date2)

        # 标准化为日期对象（去除时间部分）
        date1_normalized = d1.date()
        date2_normalized = d2.date()

        if date1_normalized < date2_normalized:
            return -1
        elif date1_normalized > date2_normalized:
            return 1
        else:
            return 0
    except Exception as e:
        print(f"日期比较错误: {str(e)}")
        return None


def parse_data(data):
    '''解析出数据中选中项目'''
    items = set()
    other_value = ''
    other_title = ''
    for val in str(data).split(","):
        if isEmpty(val):
            continue
        if '=' in val:
            parts = str(data).split('=')
            other_title = parts[0].strip()
            if len(parts) > 1:
                other_value = parts[1].strip()
            else:
                other = ''
        else:
            items.add(val)
    return items, other_title, other_value


def merge_data(items: set, other_title, other_value, out_value):
    '''合并选择的项目数据'''
    ret = ''
    if out_value in items:
        items.remove(out_value)
    if isNotEmpty(other_value):
        ret = ','.join(items)
        ret += '' if isEmpty(ret) else ','
        ret += other_title + '=' + other_value
        return ret
    else:
        return out_value

def remove_parentheses(text):
  """
  去除字符串中所有括号（包括全角和半角）及其内部的内容。
  Args:
    text: 输入的字符串。

  Returns:
    去除括号及其内部内容后的字符串。
  """
  # 匹配半角括号和全角括号及其内部的任意字符（非贪婪模式）
  pattern = r"\(.*?\)|（.*?）"
  return re.sub(pattern, "", text)


def get_items_other(labs, vals, other_key):
    """
    标准化处理带有"其他"选项的多选值，将已知选项和其他选项分别处理
    
    Args:
        labs (list): 已知的选项标签列表
        vals (str): 用逗号分隔的选择值字符串
        other_key (str): "其他"选项的键名
    
    Returns:
        str: 处理后的结果字符串，格式为"已知选项,其他选项=自定义值"
    
    Example:
        labs = ['选项1', '选项2']
        vals = '选项1,自定义值1,选项2,自定义值2'
        other_key = '其他'
        返回: '选项1,选项2,其他=自定义值1、自定义值2'
    """
    others = set()
    items = set()
    result = []
    for part in vals.split(','):
        if part in labs:
            items.add(part)
        else:
            if '' in part and len(part.split('=')) > 1:
                others.add(part.split('=')[1])
            else:
                others.add(part)
    if len(items) > 0:
        result.append(",".join(items))
    if len(others) > 0:
        result.append(f"{other_key}={'、'.join(others)}")
    return ",".join(result)