import re
from datetime import datetime


def is_valid(id_card):
    """
    验证中国大陆身份证号码有效性
    参数：id_card - 身份证号码字符串
    返回：布尔值，True表示有效
    """
    # 基本格式校验
    if not re.match(r'^[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$', id_card):
        return False

    # 校验码计算
    factors = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    checksum_map = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']

    try:
        total = sum(int(id_card[i]) * factors[i] for i in range(17))
        checksum = checksum_map[total % 11]
        return id_card[-1].upper() == checksum
    except:
        return False
def get_gender(id_card):
    if len(id_card) != 18:
        return ''

    # 提取性别信息
    gender_digit = int(id_card[16])  # 第17位数字
    gender = '男' if gender_digit % 2 != 0 else '女'  # 奇数为男，偶数为女

    return gender


def get_age(id_card):
    if len(id_card) != 18:
        return ''

    # 提取出生年份
    birth_year = int(id_card[6:10])
    birth_month = int(id_card[10:12])
    birth_day = int(id_card[12:14])

    # 获取当前日期
    today = datetime.now()
    current_year = today.year
    current_month = today.month
    current_day = today.day

    # 计算年龄
    age = current_year - birth_year

    # 检查当前日期是否在生日之前
    # if (current_month < birth_month) or (current_month == birth_month and current_day < birth_day):
    #     age -= 1

    return age
