"""
# File       : task1_定时更新商品.py
# Time       ：2025/6/26 15:04
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：启动时必须首先执行一次
定时更新apple商品信息
"""
from sqlalchemy.ext.asyncio import AsyncSession

from svc_order_zxw.db.get_db import get_db as get_db_order
from svc_order_zxw.db.crud1_applications import (
    get_application,
    create_application, PYD_ApplicationCreate,
)
from svc_order_zxw.db.crud2_products import (
    create_product, update_product, PYD_ProductCreate, PYD_ProductUpdate,
    PYD_ProductResponse, get_product, ProductType)
from svc_order_zxw.config import ApplePayConfig

from app_tools_zxw.Funcs.fastapi_logger import setup_logger

logger = setup_logger(__name__)


class TASK1_更新苹果内购商品表:
    interval_minutes = 2  # 执行周期(分钟)
    get_db = get_db_order

    @staticmethod
    async def run(db: AsyncSession):
        ...
        # logger.info("[svc_order_zxw task1]定时任务已启动")
        # for product_name, product_info in ApplePayConfig.products.items():
        #     # 1. 创建app - 查询app name , 如果没有则创建
        #     app_name = product_info.get("app_name", "default")
        #     app = await get_application(db, app_name, include_products=True)
        #     if app is None:
        #         new_app = PYD_ApplicationCreate(
        #             name=app_name,
        #             description=product_info.get("description", "苹果内购商品管理")
        #         )
        #         app = await create_application(db, new_app)

        #     # 2. 创建商品 - 如果有则更新价格
        #     all_products: list[PYD_ProductResponse] = app.products
        #     created = "已创建支付产品，app name = " + app_name + " : ["
        #     existing_product = next((product for product in all_products if product.name == product_name), None)
        #     if existing_product is None:
        #         new_product = PYD_ProductCreate(
        #             name=product_name,
        #             app_id=app.id,
        #             price=product_info["price"],
        #             apple_product_id=product_name,
        #             product_type=product_info["type"],
        #             subscription_duration=f"{product_info.get('duration', -1)} {product_info.get('duration_type', 'day')}"
        #         )
        #         product = await create_product(db, new_product)
        #         created += f"{product.name}, "
        #     elif existing_product.price != product_info["price"]:
        #         # 产品已存在,则更新价格
        #         update_data = PYD_ProductUpdate(
        #             name=product_name,
        #             price=product_info["price"]
        #         )
        #         updated_product = await update_product(db, existing_product.id, update_data)
        #         logger.info(f"[TASK1_更新商品表] 已更新商品: {product_name}, 价格: {product_info.get('price', 0)}")
