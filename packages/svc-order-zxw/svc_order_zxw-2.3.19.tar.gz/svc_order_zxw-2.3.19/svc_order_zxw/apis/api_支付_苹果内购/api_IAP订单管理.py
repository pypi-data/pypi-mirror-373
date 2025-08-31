"""
# File       : api_IAP订单管理.py
# Time       ：2025/7/28 14:34
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：需要前端登录的功能

print("1. 验证收据...")
        验证结果 = await 支付服务.验证收据_从应用收据(transactionReceipt2)
        print(f"验证结果: {验证结果.model_dump()}")
验证结果: {'商户订单号': '2000000973318333', '支付平台交易号': '2000000973318333', '原始交易号': '2000000971599396', '产品ID': 'vip001', '交易金额': 28.0, '交易状态': <OrderStatus.FINISHED: 'finished'>, '支付时间': '2025-07-31 09:44:27', '过期时间': '2025-07-31 09:49:27', '支付方式': <PaymentMethod.APPLE_PAY: 'apple_pay'>, '验证环境': 'Sandbox', '应用包ID': 'online.jingmu.fudaoyuan', '交易类型': 'Auto-Renewable Subscription', '交易原因': 'RENEWAL', '购买数量': 1, '货币代码': 'CNY', '原始价格': 28000, '店面代码': 'CHN', '应用交易ID': '704715577828757017', '是否试用期': None, '是否介绍性优惠期': None, '是否已退款': False, '退款时间': None, '退款原因': None, '备注': None}


订阅状态 = await 支付服务.获取订阅状态(transactionIdentifier2)
        print(f"订阅状态: ")
        print(f"环境: {订阅状态.环境}")
        print(f"最新收据: {订阅状态.最新收据}")
        print(f"最新交易信息: {订阅状态.最新交易信息}")
        print(f"待续费信息: {订阅状态.待续费信息}")
        print(f"是否有效订阅: {订阅状态.是否有效订阅}")
        print(f"订阅状态: {订阅状态.订阅状态}")
        print(f"过期时间: {订阅状态.过期时间}")
订阅状态:
环境: Sandbox
最新收据: None
最新交易信息: [SubscriptionTransactionInfo(transaction_id='2000000973318333', original_transaction_id='2000000971599396', product_id='vip001', bundle_id='online.jingmu.fudaoyuan', purchase_date='2025-07-31 09:44:27', purchase_date_ms='1753926267000', original_purchase_date='2025-07-29 11:44:06', original_purchase_date_ms='1753760646000', expires_date='2025-07-31 09:49:27', expires_date_ms='1753926567000', signed_date='2025-07-31 13:29:14', signed_date_ms='1753939754399', web_order_line_item_id='2000000107056054', subscription_group_identifier='21741812', quantity=1, type='Auto-Renewable Subscription', in_app_ownership_type='PURCHASED', transaction_reason='RENEWAL', environment='Sandbox', storefront='CHN', storefront_id='143465', price=28000, currency='CNY', app_transaction_id='704715577828757017', is_trial_period=None, is_in_intro_offer_period=None, is_upgraded=None, promotional_offer_id=None, offer_code_ref_name=None, cancellation_date=None, cancellation_date_ms=None, cancellation_reason=None, revocation_date=None, revocation_date_ms=None, revocation_reason=None)]
待续费信息: [PendingRenewalInfo(auto_renew_product_id='vip001', original_transaction_id='2000000971599396', product_id='vip001', auto_renew_status='0', is_in_billing_retry_period='False', price_consent_status=None, grace_period_expires_date=None, grace_period_expires_date_ms=None, promotional_offer_id=None, offer_code_ref_name=None, expiration_intent='1')]
是否有效订阅: False
订阅状态: expired
过期时间: 2025-07-31 09:49:27
"""
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from pydantic import BaseModel, Field

from svc_order_zxw.db import get_db
from svc_order_zxw.db.models import Payment, ProductType
from svc_order_zxw.异常代码 import 支付_异常代码
from svc_order_zxw.apis.schemas_payments import OrderStatus, PaymentMethod

from svc_order_zxw.apis.func_创建订单 import 创建新订单和支付单
from svc_order_zxw.apis.func_更新订单 import func_更新订单

from app_tools_zxw.SDK_苹果应用服务.sdk_支付验证 import 苹果内购支付服务_官方库, SubscriptionStatus
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW
from app_tools_zxw.Funcs.fastapi_logger import setup_logger
from svc_order_zxw.interface.interface_苹果内购_优惠券 import get_IAP优惠卷, Model促销优惠签名结果

from svc_order_zxw.config import ApplePayConfig

logger = setup_logger(__name__)
router = APIRouter(prefix="/apple_pay", tags=["苹果内购"])

apple支付服务 = 苹果内购支付服务_官方库(**{
    "私钥文件路径": ApplePayConfig.私钥文件路径,
    "密钥ID": ApplePayConfig.密钥ID,
    "发行者ID": ApplePayConfig.发行者ID,
    "应用包ID": ApplePayConfig.应用包ID,
    "是否沙盒环境": ApplePayConfig.是否沙盒环境,
    "苹果ID": ApplePayConfig.苹果ID
})


class RequestModel_验证收据(BaseModel):
    order_number: str
    payment_price: float
    quantity: int = Field(default=1)
    transactionIdentifier: str | None = None
    transactionReceipt: str | None = None


class ResponseModel_IPA_支付信息(BaseModel):
    order_number: str
    payment_status: str  # 理论上是OrderStatus类型, 在schemas_payments中
    payment_price: float
    quantity: int
    order_id: int
    subscription_expire_date: datetime | None
    transaction_id: str | None
    original_transaction_id: str | None
    payment_method: PaymentMethod


async def step1_验证收据_并更新订单(
        request: RequestModel_验证收据,
        db: AsyncSession = Depends(get_db)
):
    # 0. 如果未传入transactionIdentifier和receipt, 则创建新订单就返回
    验证结果 = None
    if request.transactionReceipt and request.transactionIdentifier:
        验证结果 = await apple支付服务.验证特定交易(request.transactionIdentifier)
        logger.info(f"苹果支付收据验证结果: {验证结果.model_dump()}")

    # 1. 更新订单
    new_order, new_payment = await func_更新订单(
        db=db,
        order_number=request.order_number,
        payment_price=request.payment_price,
        quantity=request.quantity,
        payment_status=验证结果.交易状态 if 验证结果 else OrderStatus.PENDING,
        transactionReceipt=request.transactionReceipt,
        transactionIdentifier=request.transactionIdentifier,
        original_transaction_id=验证结果.原始交易号 if 验证结果 else None,
        subscription_expire_date=datetime.strptime(
            验证结果.过期时间,
            "%Y-%m-%d %H:%M:%S") if 验证结果 and 验证结果.过期时间 else None,
    )
    logger.info(f"Payment更新成功...")
    return ResponseModel_IPA_支付信息(
        order_number=new_payment.order.order_number,
        payment_status=new_payment.payment_status.value,
        payment_price=new_payment.payment_price,
        quantity=new_payment.order.quantity,
        order_id=new_payment.order.id,
        transaction_id=new_payment.apple_transaction_id,
        original_transaction_id=new_payment.order.original_transaction_id,
        subscription_expire_date=new_payment.order.subscription_expire_date,
        payment_method=new_payment.payment_method,
    )


class RequestModel_IPA_恢复购买(BaseModel):
    user_id: int
    product_id: int
    transactionReceipt: str
    transactionIdentifier: str
    apple_product_id: str


async def step2_恢复购买(request: RequestModel_IPA_恢复购买, db: AsyncSession = Depends(get_db)):
    """
    Apple IAP 恢复购买
    1. 如果是订阅型商品，transactionIdentifier是原始交易号
    2. 如果是非订阅型商品，transactionIdentifier是应用收据
    """
    # 0) 根据apple_product_id查询ApplePayConfig中定义的商品类型
    product_type = ApplePayConfig.products[request.apple_product_id]["type"]

    # 1) 查询订单
    query = select(Payment).where(Payment.apple_transaction_id == request.transactionIdentifier).options(
        joinedload(Payment.order))
    existing_payment = await db.execute(query)
    existing_payment = existing_payment.scalar_one_or_none()

    # 2) 分别验证收据:订阅型/消耗性
    if product_type in [ProductType.AUTO_RENEWABLE.value, ProductType.NON_RENEWABLE.value]:
        # 1 订阅型商品
        订阅状态: SubscriptionStatus = await apple支付服务.获取订阅状态(request.transactionIdentifier)
        logger.info(
            f"恢复购买 - 订阅状态: {订阅状态.订阅状态}, 有效订阅: {订阅状态.是否有效订阅}, 最新交易信息: {订阅状态.最新交易信息}")
        if not 订阅状态.最新交易信息:
            raise HTTPException_AppToolsSZXW(
                error_code=支付_异常代码.支付记录不存在.value,
                detail="未找到交易信息",
                http_status_code=404
            )
        最新交易 = 订阅状态.最新交易信息[0]
        current_status = OrderStatus.FINISHED if 订阅状态.是否有效订阅 else OrderStatus.CANCELLED
        order_info = {
            "payment_price": 最新交易.price / 100,
            "payment_status": current_status,
            "transactionIdentifier": request.transactionIdentifier,
            "transactionReceipt": request.transactionReceipt,
            "original_transaction_id": 最新交易.original_transaction_id,
            "subscription_expire_date": datetime.strptime(最新交易.expires_date, "%Y-%m-%d %H:%M:%S"),
            "apple_environment": ApplePayConfig.是否沙盒环境,
        }
    else:
        # 2. 验证非订阅型商品
        最新交易 = await apple支付服务.验证特定交易(request.transactionIdentifier)
        logger.info(f"恢复购买 - 验证结果: {最新交易.model_dump()}")
        order_info = {
            "payment_price": 最新交易.交易金额 / 100,
            "payment_status": 最新交易.交易状态,
            "transactionIdentifier": request.transactionIdentifier,
            "transactionReceipt": request.transactionReceipt,
            "original_transaction_id": 最新交易.原始交易号,
            "subscription_expire_date": None,
            "apple_environment": ApplePayConfig.是否沙盒环境,
        }

    # 3) 创建订单或更新订单
    if existing_payment:
        new_order, new_payment = await func_更新订单(
            db=db,
            order_number=existing_payment.order.order_number,
            payment_price=order_info["payment_price"],
            payment_status=order_info["payment_status"],
            transactionIdentifier=order_info["transactionIdentifier"],
            transactionReceipt=order_info["transactionReceipt"],
            original_transaction_id=order_info["original_transaction_id"],
            subscription_expire_date=order_info["subscription_expire_date"],
        )
    else:
        new_order, new_payment = await 创建新订单和支付单(
            db_payment=db,
            user_id=request.user_id,
            product_id=request.product_id,
            payment_price=order_info["payment_price"],
            payment_method=PaymentMethod.APPLE_PAY,
            quantity=order_info["quantity"],
            payment_status=order_info["payment_status"],
            apple_transaction_id=order_info["transactionIdentifier"],
            apple_receipt=order_info["transactionReceipt"],
            apple_original_transaction_id=order_info["original_transaction_id"],
            apple_expires_date=order_info["subscription_expire_date"],
            apple_environment=order_info["apple_environment"],
        )

    logger.info(f"恢复购买成功")

    return ResponseModel_IPA_支付信息(
        order_number=new_order.order_number,
        payment_status=new_payment.payment_status.value,
        payment_price=new_payment.payment_price,
        quantity=new_payment.order.quantity,
        order_id=new_payment.order.id,
        transaction_id=new_payment.apple_transaction_id,
        original_transaction_id=new_payment.order.original_transaction_id,
        subscription_expire_date=new_payment.order.subscription_expire_date,
        payment_method=new_payment.payment_method,
    )


router.add_api_route("/valid_order", step1_验证收据_并更新订单, methods=["POST"])
router.add_api_route("/restore_subscription", step2_恢复购买, methods=["POST"])
router.add_api_route("/promotion/create", get_IAP优惠卷, methods=["POST"], response_model=Model促销优惠签名结果)
