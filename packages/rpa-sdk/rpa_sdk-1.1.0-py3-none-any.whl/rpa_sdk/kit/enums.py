#!/usr/bin/env python3
"""
RPA系统枚举定义
"""

from enum import Enum

class MessageType(Enum):
    """消息类型枚举"""
    COMPLETED = "COMPLETED" # 任务完成
    INFO = "info"           # 信息消息
    ERROR = "error"         # 错误消息
    WARNING = "warning"     # 警告消息
    SUCCESS = "success"     # 成功消息
    PROGRESS = "progress"   # 进度消息
    RESULT = "result"       # 结果消息
    STATUS = "status"       # 状态消息
    STEP = "step"          # 步骤消息


    

