# cython: language_level=3
# coding=utf-8
from datetime import datetime

import psutil
import wmi
import configparser
import hashlib

import requests
from .DialogKit import showMessageBox


def get_mac_address():
    interfaces = psutil.net_if_addrs()
    for interface, addrs in interfaces.items():
        stats = psutil.net_if_stats()[interface]
        if stats.isup:
            for addr in addrs:
                if addr.family == psutil.AF_LINK:
                    return addr.address.replace("-","")
    return ''
def getDeviceSn():
    c = wmi.WMI()
    # 获取 CPU ID
    cpu_id = ''
    for cpu in c.Win32_Processor():
        cpu_id =cpu.ProcessorId.strip()
    board_id=''
    for board_id in c.Win32_BaseBoard():
        board_id=board_id.SerialNumber.strip()
    # 合并计算机名、CPU ID 和主板ID
    combined_info = f"{cpu_id}{board_id}{get_mac_address()}"
    # 使用哈希函数生成机器码
    machine_code = hashlib.md5(combined_info.encode()).hexdigest()
    return machine_code


def check():
    try:
        config = configparser.ConfigParser()
        config.read('config.ini',encoding='utf-8')
        code = config.get('organ', 'code')
        name = config.get('organ', 'name')
        response = requests.get(f"http://service.aitmc.cn/auth?code={code}&name={name}&sn={getDeviceSn()}")
        if response.status_code == 200:
            data = response.json()
            if data['state'] == 'ok':
                return True
            else:
                showMessageBox(data['msg'])
                return False
        else:
            showMessageBox("请联系服务商,联系电话：1569249550 \n设备码：" + getDeviceSn())
            return False
    except Exception as e:
        showMessageBox("配置文件不存在")
        return False



if "__main__" == __name__:
    getDeviceSn()
