"""
# File       : main.py
# Time       ：2024/8/25 08:18
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter

# from svc_order_zxw.apis.api_支付_微信 import api_二维码 as api_支付_微信_二维码
from svc_order_zxw.apis.api_支付_支付宝 import api_app与url方式 as api_支付_支付宝_url
from svc_order_zxw.apis import api_商品管理
from svc_order_zxw.apis import api_商品查询_低权限
from svc_order_zxw.apis.api_支付_苹果内购 import api_IAP订单管理
from svc_order_zxw.apis.api_支付_苹果内购 import api_开启IAP
from svc_order_zxw.db import Base, engine
from svc_order_zxw.定时任务 import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动: 在 FastAPI 应用启动时创建表结构
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("svc-order-zxw : All tables created if not existing.")

    print("🚀 启动svc_order_zxw定时任务...")
    await start_scheduler()  # 启动业务定时任务（商品表更新等）

    # 使用Yield，控制程序回到FastAPI服务
    yield

    await stop_scheduler()
    # 关闭逻辑: close connections, etc.
    await engine.dispose()


router = APIRouter(lifespan=lifespan)

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

#
# @app.exception_handler(Exception)
# async def global_exception_handler(request, exc):
#     logger.error(f"Unhandled exception: {exc}")
#     return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# Register API routers
# router.include_router(api_支付_微信_二维码.router)
router.include_router(api_支付_支付宝_url.router)
router.include_router(api_商品管理.router)
router.include_router(api_商品查询_低权限.router)
router.include_router(api_IAP订单管理.router)
router.include_router(api_开启IAP.router)
