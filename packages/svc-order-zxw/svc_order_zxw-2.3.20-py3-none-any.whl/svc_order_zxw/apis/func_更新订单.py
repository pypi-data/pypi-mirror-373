from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from svc_order_zxw.db.crud3_orders import PYD_OrderResponse, PYD_OrderUpdate, update_order
from svc_order_zxw.db.crud4_payments import PYD_PaymentResponse, PYD_PaymentUpdate, update_payment, get_payment
from svc_order_zxw.apis.schemas_payments import OrderStatus
from svc_order_zxw.异常代码 import 其他_异常代码, 支付_异常代码
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW
from app_tools_zxw.Funcs.fastapi_logger import setup_logger

logger = setup_logger(__name__)


async def func_更新订单(
        db: AsyncSession,
        order_number: str,
        payment_price: float | None = None,
        quantity: int | None = None,
        payment_status: OrderStatus | None = None,
        # 苹果内购特有字段
        original_transaction_id: str | None = None,
        subscription_expire_date: datetime | None = None,
        transactionReceipt: str | None = None,
        transactionIdentifier: str | None = None,
) -> tuple[PYD_OrderResponse, PYD_PaymentResponse]:
    # 0) 查询支付单是否存在
    existing_payment = await get_payment(db, order_number=order_number)
    if not existing_payment:
        raise HTTPException_AppToolsSZXW(
            error_code=支付_异常代码.支付单号不存在,
            detail="支付单号不存在",
            http_status_code=404
        )
    # 1) 更新订单（仅对非 None 字段进行更新）
    order_update_kwargs = {}
    if payment_price is not None:
        order_update_kwargs["total_price"] = payment_price
    if quantity is not None:
        order_update_kwargs["quantity"] = quantity
    if original_transaction_id is not None and existing_payment.apple_original_transaction_id is None:
        order_update_kwargs["original_transaction_id"] = original_transaction_id
    if subscription_expire_date is not None:
        order_update_kwargs["subscription_expire_date"] = subscription_expire_date

    # 更新订单与支付信息，并返回最新的支付响应（包含order）
    try:
        updated_order = await update_order(
            db,
            existing_payment.order_id,
            PYD_OrderUpdate(**order_update_kwargs)
        )
    except Exception as e:
        logger.exception(f"更新订单失败: {e}")
        raise HTTPException_AppToolsSZXW(
            error_code=其他_异常代码.更新数据失败,
            detail=f"更新订单失败: {e}",
            http_status_code=404
        )

    # 2) 更新支付记录（仅对非 None 字段进行更新），并携带order返回
    payment_update_kwargs = {}
    if payment_price is not None:
        payment_update_kwargs["payment_price"] = payment_price
    if payment_status is not None:
        payment_update_kwargs["payment_status"] = payment_status
    if transactionReceipt is not None and existing_payment.apple_receipt is None:
        payment_update_kwargs["apple_receipt"] = transactionReceipt
    if transactionIdentifier is not None and existing_payment.apple_transaction_id is None:
        payment_update_kwargs["apple_transaction_id"] = transactionIdentifier
    if original_transaction_id is not None and existing_payment.apple_original_transaction_id is None:
        payment_update_kwargs["apple_original_transaction_id"] = original_transaction_id
    if subscription_expire_date is not None:
        payment_update_kwargs["apple_expires_date"] = subscription_expire_date

    try:
        updated_payment: PYD_PaymentResponse = await update_payment(
            db,
            existing_payment.id,
            PYD_PaymentUpdate(**payment_update_kwargs),
            include_order=True
        )
        return updated_order, updated_payment
    except Exception as e:
        logger.exception(f"更新支付记录失败: {e}")
        raise HTTPException_AppToolsSZXW(
            error_code=其他_异常代码.更新数据失败,
            detail=f"更新支付记录失败: {e}",
            http_status_code=404
        )
