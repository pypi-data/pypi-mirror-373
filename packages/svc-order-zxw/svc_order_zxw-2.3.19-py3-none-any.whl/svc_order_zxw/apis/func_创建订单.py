from fastapi import Depends
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from svc_order_zxw.db import get_db
from svc_order_zxw.db.crud2_products import get_product
from svc_order_zxw.db.crud3_orders import (
    create_order,
    PYD_OrderCreate,
    PYD_OrderResponse,
)
from svc_order_zxw.db.crud4_payments import (
    create_payment,
    PYD_PaymentCreate,
    PYD_PaymentResponse,
)
from svc_order_zxw.异常代码 import 商品_异常代码
from svc_order_zxw.apis.schemas_payments import OrderStatus, PaymentMethod
from svc_order_zxw.apis.func_生成订单号 import 生成订单号
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW
from app_tools_zxw.Funcs.fastapi_logger import setup_logger

logger = setup_logger(__name__)


# class Model创建订单返回值(BaseModel):
#     user_id: int
#     product_id: int
#     order_number: str

#     total_price: float  # 原始价格
#     payment_price: float  # 实际支付金额
#     quantity: int
#     status: str


async def 创建新订单和支付单(
        user_id: int,
        product_id: int,
        payment_price: float,
        payment_method: PaymentMethod,
        db_payment: AsyncSession = Depends(get_db),
        # 非必填字段
        quantity: int = 1,
        payment_status: OrderStatus = OrderStatus.PENDING,
        callback_url: str | None = None,
        payment_url: str | None = None,
        # 苹果内购特有字段
        apple_transaction_id: str | None = None,
        apple_receipt: str | None = None,
        apple_original_transaction_id: str | None = None,
        apple_expires_date: datetime | None = None,
        apple_auto_renew_status: bool | None = None,
        apple_offer_identifier: str | None = None,
        apple_offer_type: str | None = None,
        apple_environment: str | None = None,
) -> tuple[PYD_OrderResponse, PYD_PaymentResponse]:
    """
    创建新订单_并创建支付单
    :param user_id: 用户ID
    :param product_id: 商品ID
    :param payment_price: 支付金额
    :param payment_method: 支付方式
    :param payment_status: 支付状态
    :param quantity: 购买数量
    :param callback_url: 回调URL
    :param payment_url: 支付URL
    :param db_payment: 数据库会话
    :param apple_transaction_id: 苹果交易ID
    :param apple_receipt: 苹果收据
    :param apple_original_transaction_id: 苹果原始交易ID
    :param apple_expires_date: 苹果订阅过期时间
    :param apple_auto_renew_status: 苹果自动续费状态
    :param apple_offer_identifier: 苹果促销优惠标识符
    :param apple_offer_type: 苹果促销优惠类型
    :param apple_environment: 苹果支付环境 sandbox/production
    """
    # 验证产品是否存在
    product = await get_product(db_payment, product_id)
    if not product:
        raise HTTPException_AppToolsSZXW(
            error_code=商品_异常代码.商品不存在.value,
            detail="商品不存在",
            http_status_code=404
        )

    # 创建新订单
    new_order = await create_order(db_payment, PYD_OrderCreate(
        order_number=生成订单号(),
        user_id=str(user_id),
        total_price=product.price * quantity,
        quantity=quantity,
        product_id=product_id,
        # 苹果内购相关字段
        original_transaction_id=apple_original_transaction_id,
        subscription_expire_date=apple_expires_date,
        auto_renew_status=apple_auto_renew_status,
    ))

    # 创建支付单
    new_payment = await create_payment(db_payment, PYD_PaymentCreate(
        order_id=new_order.id,
        payment_price=payment_price,
        payment_method=payment_method,
        payment_status=payment_status,
        callback_url=callback_url,
        payment_url=payment_url,
        # 苹果内购特有字段
        apple_receipt=apple_receipt,
        apple_transaction_id=apple_transaction_id,
        apple_original_transaction_id=apple_original_transaction_id,
        apple_environment=apple_environment,
        apple_expires_date=apple_expires_date,
        apple_auto_renew_status=apple_auto_renew_status,
        apple_offer_identifier=apple_offer_identifier,
        apple_offer_type=apple_offer_type,
    ))

    return new_order, new_payment

    # return Model创建订单返回值(
    #     order_number=new_order.order_number,
    #     user_id=new_order.user_id,
    #     product_id=new_order.product_id,
    #     total_price=new_order.total_price,
    #     payment_price=new_payment.payment_price,
    #     quantity=new_order.quantity,
    #     status=new_payment.payment_status.value
    # )
