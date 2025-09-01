"""
# File       : api_商品管理.py
# Time       ：2024/10/8 上午5:42
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from svc_order_zxw.db import get_db
from svc_order_zxw.db.crud1_applications import (
    PYD_ApplicationCreate,
    PYD_ApplicationResponse,
    PYD_ApplicationUpdate,
    create_application,
    get_application,
    update_application,
    delete_application,
    list_applications)
from svc_order_zxw.db.crud2_products import (
    PYD_ProductCreate, PYD_ProductUpdate,
    PYD_ProductResponse,
    create_product, get_product,
    update_product, delete_product, get_products)
from svc_order_zxw.db.crud3_orders import (
    PYD_OrderCreate, PYD_OrderUpdate,
    PYD_OrderFilter, PYD_OrderResponse,
    create_order, get_order,
    update_order, delete_order, list_orders)
from svc_order_zxw.db.crud4_payments import (
    PYD_PaymentCreate, PYD_PaymentUpdate,
    PYD_PaymentResponse,
    create_payment, get_payment,
    update_payment, delete_payment, list_payments)

from app_tools_zxw.Funcs.生成订单号 import 生成订单号
from svc_order_zxw import config

router = APIRouter(prefix="", tags=["商品管理"])


# 应用相关路由
async def 创建应用(application: PYD_ApplicationCreate, db: AsyncSession = Depends(get_db)):
    return await create_application(db, application)


async def 获取应用(application_id: int, db: AsyncSession = Depends(get_db)):
    return await get_application(db, application_id, include_products=True)


async def 更新应用(application_id: int, application: PYD_ApplicationUpdate, db: AsyncSession = Depends(get_db)):
    return await update_application(db, application_id, application)


async def 删除应用(application_id: int, db: AsyncSession = Depends(get_db)):
    return await delete_application(db, application_id)


async def 获取所有应用(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await list_applications(db, skip=skip, limit=limit, include_products=True)


# 产品相关路由
async def 创建产品(product: PYD_ProductCreate, db: AsyncSession = Depends(get_db)):
    return await create_product(db, product)


async def 获取产品(product_id: int, db: AsyncSession = Depends(get_db)):
    return await get_product(db, product_id)


async def 更新产品(product_id: int, product: PYD_ProductUpdate, db: AsyncSession = Depends(get_db)):
    return await update_product(db, product_id, product)


async def 删除产品(product_id: int, db: AsyncSession = Depends(get_db)):
    return await delete_product(db, product_id)


async def 获取所有产品(is_apple_product: bool = False, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await get_products(db, is_apple_product=is_apple_product, skip=skip, limit=limit)


# 订单相关路由
async def 创建订单(order: PYD_OrderCreate, db: AsyncSession = Depends(get_db)):
    order.order_number = 生成订单号()
    return await create_order(db, order, include_product=True, include_application=True)


async def 获取订单(order_id: int, db: AsyncSession = Depends(get_db)):
    return await get_order(db, order_id, include_product=True, include_application=True, include_payment=True)


async def 更新订单(order_id: int, order: PYD_OrderUpdate, db: AsyncSession = Depends(get_db)):
    return await update_order(db, order_id, order)


async def 删除订单(order_id: int, db: AsyncSession = Depends(get_db)):
    return await delete_order(db, order_id)


async def 获取所有订单(
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[str] = None,
        product_id: Optional[int] = None,
        application_id: Optional[int] = None,
        db: AsyncSession = Depends(get_db)
):
    filter = PYD_OrderFilter(user_id=user_id, product_id=product_id, application_id=application_id)
    return await list_orders(db, filter, skip=skip, limit=limit, include_product=True, include_application=True,
                             include_payment=True)


# 支付相关路由
async def 创建支付(payment: PYD_PaymentCreate, db: AsyncSession = Depends(get_db)):
    return await create_payment(db, payment, include_order=True)


async def 获取支付(payment_id: int, db: AsyncSession = Depends(get_db)):
    return await get_payment(db, payment_id=payment_id, include_order=True)


async def 更新支付(payment_id: int, payment: PYD_PaymentUpdate, db: AsyncSession = Depends(get_db)):
    return await update_payment(db, payment_id, payment)


async def 删除支付(payment_id: int, db: AsyncSession = Depends(get_db)):
    return await delete_payment(db, payment_id)


async def 获取所有支付(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await list_payments(db, skip=skip, limit=limit, include_order=True)


# 使用 router.add_api_route() 添加路由
if config.DEV_MODE:
    # 应用相关路由
    router.add_api_route("/applications", 创建应用, methods=["POST"], response_model=PYD_ApplicationResponse)
    router.add_api_route("/applications/{application_id}", 获取应用, methods=["GET"],
                         response_model=Optional[PYD_ApplicationResponse])
    router.add_api_route("/applications/{application_id}", 更新应用, methods=["PUT"],
                         response_model=PYD_ApplicationResponse)
    router.add_api_route("/applications/{application_id}", 删除应用, methods=["DELETE"])
    router.add_api_route("/applications", 获取所有应用, methods=["GET"], response_model=List[PYD_ApplicationResponse])

    # 产品相关路由
    router.add_api_route("/products", 创建产品, methods=["POST"], response_model=PYD_ProductResponse)
    router.add_api_route("/products/{product_id}", 获取产品, methods=["GET"],
                         response_model=Optional[PYD_ProductResponse])
    router.add_api_route("/products/{product_id}", 更新产品, methods=["PUT"], response_model=PYD_ProductResponse)
    router.add_api_route("/products/{product_id}", 删除产品, methods=["DELETE"])
    router.add_api_route("/products", 获取所有产品, methods=["GET"], response_model=List[PYD_ProductResponse])

    # 订单相关路由
    router.add_api_route("/orders", 创建订单, methods=["POST"], response_model=PYD_OrderResponse)
    router.add_api_route("/orders/{order_id}", 获取订单, methods=["GET"], response_model=Optional[PYD_OrderResponse])
    router.add_api_route("/orders/{order_id}", 更新订单, methods=["PUT"], response_model=PYD_OrderResponse)
    router.add_api_route("/orders/{order_id}", 删除订单, methods=["DELETE"])
    router.add_api_route("/orders", 获取所有订单, methods=["GET"], response_model=List[PYD_OrderResponse])

    # 支付相关路由
    router.add_api_route("/payments", 创建支付, methods=["POST"], response_model=PYD_PaymentResponse)
    router.add_api_route("/payments/{payment_id}", 获取支付, methods=["GET"],
                         response_model=Optional[PYD_PaymentResponse])
    router.add_api_route("/payments/{payment_id}", 更新支付, methods=["PUT"], response_model=PYD_PaymentResponse)
    router.add_api_route("/payments/{payment_id}", 删除支付, methods=["DELETE"])
    router.add_api_route("/payments", 获取所有支付, methods=["GET"], response_model=List[PYD_PaymentResponse])
