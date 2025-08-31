"""
# File       : api_支付_支付宝_二维码.py
# Time       ：2024/8/25 12:02
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, Callable, Awaitable

from svc_order_zxw.db import get_db
from svc_order_zxw.db.crud2_products import get_product
from svc_order_zxw.db.crud3_orders import (
    create_order,
    get_order,
    PYD_OrderCreate,
)
from svc_order_zxw.db.crud4_payments import (
    create_payment,
    get_payment,
    update_payment,
    PYD_PaymentUpdate,
    PYD_PaymentCreate,
)
from svc_order_zxw.apis.func_创建订单 import 创建新订单和支付单
from svc_order_zxw.异常代码 import 订单_异常代码, 商品_异常代码, 支付_异常代码, 其他_异常代码
from svc_order_zxw.config import AliPayConfig
from svc_order_zxw.apis.schemas_payments import OrderStatus, PaymentMethod

from app_tools_zxw.SDK_支付宝.支付服务_async import 支付服务, PaymentResult
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW
from app_tools_zxw.Funcs.fastapi_logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/alipay/pay_qr", tags=["支付宝支付"])

alipay_client = 支付服务(
    app_id=AliPayConfig.appid,
    key应用私钥=AliPayConfig.key应用私钥,
    key支付宝公钥=AliPayConfig.key支付宝公钥,
    回调路径_root=AliPayConfig.回调路径_root,
    回调路径_prefix=AliPayConfig.回调路径_prefix
)


class Model创建订单返回值(BaseModel):
    user_id: int
    product_id: int
    order_number: str

    total_price: float  # 原始价格
    payment_price: float  # 实际支付金额
    quantity: int
    status: str


返回_支付宝url_订单信息 = Model创建订单返回值  # 向后兼容


class 请求_支付宝url_创建订单(BaseModel):
    user_id: str
    product_id: int
    payment_price: float
    quantity: int = Field(default=1)


class 请求_支付宝url_发起支付(BaseModel):
    order_number: str
    callback_url: str


class 返回_支付宝url_支付信息(BaseModel):
    order_number: str
    payment_status: str  # 理论上是OrderStatus类型, 在schemas_payments中
    payment_price: float
    quantity: int
    order_id: int
    product_name: str
    app_name: str
    qr_uri: Optional[str] = None


async def 创建订单(request: 请求_支付宝url_创建订单, db: AsyncSession = Depends(get_db)):
    new_order, new_payment = await 创建新订单和支付单(
        user_id=int(request.user_id),
        product_id=request.product_id,
        payment_price=request.payment_price,
        payment_method=PaymentMethod.ALIPAY_QR,
        db_payment=db
    )

    return Model创建订单返回值(
        user_id=new_order.user_id,
        product_id=new_order.product_id,
        order_number=new_order.order_number,
        total_price=new_order.total_price,
        payment_price=new_payment.payment_price,
        quantity=new_order.quantity,
        status=new_payment.payment_status.value
    )


async def 发起支付(request: 请求_支付宝url_发起支付, db: AsyncSession = Depends(get_db)):
    # 查询订单
    order = await get_order(
        db,
        order_identifier=request.order_number,
        include_product=True)

    print("发起支付: order  = ", order)

    if not order:
        raise HTTPException_AppToolsSZXW(
            error_code=订单_异常代码.订单号不存在.value,
            detail="Order not found",
            http_status_code=404
        )

    # 查询支付记录
    payment = await get_payment(db, order_number=order.order_number)

    # 如果payment不存在, 创建新的支付记录
    if payment is None:
        payment = await create_payment(db, PYD_PaymentCreate(
            order_id=order.id,
            payment_method=PaymentMethod.ALIPAY_QR,
            payment_price=order.total_price,
            payment_status=OrderStatus.PENDING,
            callback_url=request.callback_url,
            payment_url="",  # 支付链接，在发起支付时由系统生成
        ))

    # 发起支付宝支付
    支付链接 = await alipay_client.发起二维码支付(
        商户订单号=order.order_number,
        价格=payment.payment_price,
        商品名称=order.product.name if order.product else "未知商品")

    # 更新现有支付记录
    payment = await update_payment(db, payment.id, PYD_PaymentUpdate(
        payment_status=OrderStatus.PENDING,
        callback_url=request.callback_url,
        payment_url=支付链接,
    ))

    return 返回_支付宝url_支付信息(
        order_number=order.order_number,
        payment_status=payment.payment_status.value,
        payment_price=payment.payment_price,
        quantity=order.quantity,
        order_id=payment.order_id,
        app_name=order.application.name if order.application else "None",
        product_name=order.product.name if order.product.name else "None",
        qr_uri=payment.payment_url
    )


async def 查询支付状态(order_number: str, db: AsyncSession = Depends(get_db)):
    # 查询支付记录
    payment = await get_payment(
        db,
        order_number=order_number,
        include_order=True)
    logger.info(f"payment 查询结果 = {payment}")
    if not payment:
        raise HTTPException_AppToolsSZXW(
            error_code=支付_异常代码.支付单号不存在.value,
            detail="Payment not found",
            http_status_code=404
        )

    if not payment.order:
        raise HTTPException_AppToolsSZXW(
            error_code=订单_异常代码.订单号不存在.value,
            detail="Order not found for this payment",
            http_status_code=404
        )

    # 检查支付状态
    payment_status = await alipay_client.查询订单(payment.order.order_number)

    if payment_status != payment.payment_status:
        print(f"支付状态更新：{payment.payment_status} -> {payment_status}")
        payment = await update_payment(
            db,
            payment.id,
            PYD_PaymentUpdate(
                payment_status=payment_status
            ),
            include_order=True
        )

    # 返回支付信息
    return 返回_支付宝url_支付信息(
        order_number=payment.order.order_number,
        payment_status=payment.payment_status.value,
        payment_price=payment.payment_price,
        quantity=payment.order.quantity,
        order_id=payment.order_id,
        app_name=payment.application.name if payment.application else "None",
        product_name=payment.product.name if payment.product.name else "None",
        qr_uri=payment.payment_url
    )


def 支付宝_注册支付回调(回调func_支付成功: Callable[[PaymentResult], Awaitable[None]]):
    """
        注册回调函数
        回调func_支付成功: 回调函数在判断支付成功后执行的外部函数，参数为PaymentResult对象，返回值为None.
    """
    alipay_client.注册回调接口_示例(router, 回调func_支付成功)


@router.post("/create_order/", response_model=返回_支付宝url_订单信息)
async def __创建订单__(request: 请求_支付宝url_创建订单, db: AsyncSession = Depends(get_db)):
    return await 创建订单(request, db)


@router.post("/pay/", response_model=返回_支付宝url_支付信息)
async def __发起支付__(request: 请求_支付宝url_发起支付, db: AsyncSession = Depends(get_db)):
    return await 发起支付(request, db)


@router.get("/payment_status/{transaction_id}", response_model=返回_支付宝url_支付信息)
async def __查询支付状态__(order_number: str, db: AsyncSession = Depends(get_db)):
    return await 查询支付状态(order_number, db)
