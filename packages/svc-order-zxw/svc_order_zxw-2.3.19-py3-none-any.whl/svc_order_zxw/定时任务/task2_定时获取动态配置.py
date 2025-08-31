"""
# File       : task2_定时获取动态配置.py
# Time       ：2025/8/19 15:04
# Author     ：xuewei zhang
# Email      ：shuihuyangguang@gmail.com
# version    ：python 3.12
# Description：
定时获取动态配置
"""
import json
from pathlib import Path
from app_tools_zxw.Funcs.fastapi_logger import setup_logger

logger = setup_logger(__name__)

# 动态配置: 实际值在 dynamic_config.json中配置
DYNAMIC_CONFIG = {"enable_iOS_IAP": True}  # 默认配置


class TASK2_定时获取动态配置:
    interval_minutes = 2  # 执行周期(分钟)

    @staticmethod
    async def run(db=None):
        global DYNAMIC_CONFIG

        try:
            config_file = Path("configs/dynamic_config.json")
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    DYNAMIC_CONFIG = json.load(f)
                logger.info(f"配置更新成功: {DYNAMIC_CONFIG}")
            else:
                raise FileNotFoundError(f"配置文件不存在: {config_file}")
        except Exception as e:
            logger.error(f"读取配置文件失败: {e}")
        return DYNAMIC_CONFIG
