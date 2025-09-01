from fastapi import APIRouter
from svc_order_zxw.定时任务 import task2_定时获取动态配置
from app_tools_zxw.Funcs.fastapi_logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/apple_pay", tags=["苹果内购"])


@router.get("/config/enable_ios_iap", summary="获取是否开启苹果内购")
async def get_IAP_config():
    """直接从缓存读取配置，无IO操作"""
    # 动态获取最新配置值
    current_config = task2_定时获取动态配置.DYNAMIC_CONFIG
    logger.info(f"{current_config=}")
    return current_config.get("enable_iOS_IAP", True)
