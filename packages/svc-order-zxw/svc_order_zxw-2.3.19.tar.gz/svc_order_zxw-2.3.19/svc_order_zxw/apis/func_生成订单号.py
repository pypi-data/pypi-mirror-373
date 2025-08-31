"""
# File       : func_生成订单号.py
# Time       ：2025/7/28 14:47
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from uuid import uuid4
import hashlib


def 生成订单号() -> str:
    原始订单号 = str(uuid4())  # 或者其他生成逻辑
    return hashlib.md5(原始订单号.encode('utf-8')).hexdigest()
