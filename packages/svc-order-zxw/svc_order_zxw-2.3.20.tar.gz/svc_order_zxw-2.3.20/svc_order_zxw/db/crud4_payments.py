from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select, delete
from svc_order_zxw.db.models import Payment, PaymentMethod, OrderStatus, Order, Product
from typing import List, Optional
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW
from svc_order_zxw.异常代码 import 其他_异常代码, 支付_异常代码
from app_tools_zxw.Funcs.fastapi_logger import setup_logger

logger = setup_logger(__name__)


class PYD_PaymentBase(BaseModel):
    payment_method: PaymentMethod
    payment_price: float
    payment_status: OrderStatus
    callback_url: Optional[str] = None
    payment_url: Optional[str] = None
    
    # 苹果内购特有字段
    apple_receipt: Optional[str] = None
    apple_transaction_id: Optional[str] = None
    apple_original_transaction_id: Optional[str] = None
    apple_environment: Optional[str] = None
    apple_expires_date: Optional[datetime] = None
    apple_auto_renew_status: Optional[bool] = None
    apple_offer_identifier: Optional[str] = None
    apple_offer_type: Optional[str] = None


class PYD_PaymentCreate(PYD_PaymentBase):
    order_id: int


class PYD_OrderResponse(BaseModel):
    id: int
    order_number: str
    user_id: str
    total_price: float
    quantity: int
    created_at: datetime
    updated_at: datetime
    product_id: int
    # 苹果内购订阅相关字段
    original_transaction_id: Optional[str] = None
    subscription_expire_date: Optional[datetime] = None
    auto_renew_status: Optional[bool] = None


class PYD_ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    app_id: int


class PYD_ApplicationResponse(BaseModel):
    id: int
    name: str


class PYD_PaymentResponse(PYD_PaymentBase):
    id: int
    order_id: int
    created_at: datetime
    updated_at: datetime
    order: Optional[PYD_OrderResponse] = None
    product: Optional[PYD_ProductResponse] = None
    application: Optional[PYD_ApplicationResponse] = None

    class Config:
        from_attributes = True


class PYD_PaymentUpdate(BaseModel):
    payment_method: Optional[PaymentMethod] = None
    payment_price: Optional[float] = None
    payment_status: Optional[OrderStatus] = None
    callback_url: Optional[str] = None
    payment_url: Optional[str] = None
    
    # 苹果内购特有字段
    apple_receipt: Optional[str] = None
    apple_transaction_id: Optional[str] = None
    apple_original_transaction_id: Optional[str] = None
    apple_environment: Optional[str] = None
    apple_expires_date: Optional[datetime] = None
    apple_auto_renew_status: Optional[bool] = None
    apple_offer_identifier: Optional[str] = None
    apple_offer_type: Optional[str] = None


async def create_payment(
        db: AsyncSession,
        payment: PYD_PaymentCreate,
        include_order: bool = False) -> PYD_PaymentResponse:
    try:
        new_payment = Payment(**payment.model_dump())
        db.add(new_payment)
        await db.commit()
        
        # 如果需要预加载关系，重新查询
        if include_order and new_payment:
            query = select(Payment).options(
                joinedload(Payment.order).joinedload(Order.product).joinedload(Product.app)
            ).where(Payment.id == new_payment.id)
            result = await db.execute(query)
            new_payment = result.scalar_one()
        else:
            query = select(Payment).where(Payment.id == new_payment.id)
            result = await db.execute(query)
            new_payment = result.scalar_one()

        payment_dict = {
            "id": new_payment.id,
            "order_id": new_payment.order_id,
            "payment_method": new_payment.payment_method,
            "payment_price": new_payment.payment_price,
            "payment_status": new_payment.payment_status,
            "callback_url": new_payment.callback_url,
            "payment_url": new_payment.payment_url,
            "created_at": new_payment.created_at,
            "updated_at": new_payment.updated_at,
            # 苹果内购字段
            "apple_receipt": new_payment.apple_receipt,
            "apple_transaction_id": new_payment.apple_transaction_id,
            "apple_original_transaction_id": new_payment.apple_original_transaction_id,
            "apple_environment": new_payment.apple_environment,
            "apple_expires_date": new_payment.apple_expires_date,
            "apple_auto_renew_status": new_payment.apple_auto_renew_status,
            "apple_offer_identifier": new_payment.apple_offer_identifier,
            "apple_offer_type": new_payment.apple_offer_type,
        }

        if include_order and new_payment.order:
            payment_dict["order"] = PYD_OrderResponse(
                id=new_payment.order.id,
                order_number=new_payment.order.order_number,
                user_id=new_payment.order.user_id,
                total_price=new_payment.order.total_price,
                quantity=new_payment.order.quantity,
                created_at=new_payment.order.created_at,
                updated_at=new_payment.order.updated_at,
                product_id=new_payment.order.product_id
            )

        return PYD_PaymentResponse(**payment_dict)
    except Exception as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(其他_异常代码.新增数据失败, f"创建支付记录失败: {str(e)}")


async def get_payment(
        db: AsyncSession,
        payment_id: Optional[int] = None,
        order_number: Optional[str] = None,
        apple_transaction_id: Optional[str] = None,
        include_order: bool = False) -> Optional[PYD_PaymentResponse]:
    if payment_id is None and order_number is None and apple_transaction_id is None:
        raise HTTPException_AppToolsSZXW(其他_异常代码.未知错误, "必须提供payment_id、order_number或apple_transaction_id之一")

    query = select(Payment).options(
        joinedload(Payment.order).joinedload(Order.product).joinedload(Product.app)
    )

    if payment_id:
        query = query.where(Payment.id == payment_id)
    elif order_number:
        query = query.join(Order).where(Order.order_number == order_number)
    elif apple_transaction_id:
        query = query.where(Payment.apple_transaction_id == apple_transaction_id)

    # 按创建时间倒序排列，获取最新的一条记录
    query = query.order_by(Payment.created_at.desc())
    result = await db.execute(query)
    payment = result.unique().scalars().first()

    if not payment:
        return None
        # error_message = f"未找到支付记录: {'payment_id=' + str(payment_id) if payment_id else 'order_number=' + order_number}"
        # raise HTTPException_AppToolsSZXW(ErrorCode.支付记录未找到, error_message)

    payment_dict = {
        "id": payment.id,
        "order_id": payment.order_id,
        "payment_method": payment.payment_method,
        "payment_price": payment.payment_price,
        "payment_status": payment.payment_status,
        "callback_url": payment.callback_url,
        "payment_url": payment.payment_url,
        "created_at": payment.created_at,
        "updated_at": payment.updated_at,
        # 苹果内购字段
        "apple_receipt": payment.apple_receipt,
        "apple_transaction_id": payment.apple_transaction_id,
        "apple_original_transaction_id": payment.apple_original_transaction_id,
        "apple_environment": payment.apple_environment,
        "apple_expires_date": payment.apple_expires_date,
        "apple_auto_renew_status": payment.apple_auto_renew_status,
        "apple_offer_identifier": payment.apple_offer_identifier,
        "apple_offer_type": payment.apple_offer_type,
    }

    if include_order and payment.order:
        payment_dict["order"] = PYD_OrderResponse(
            id=payment.order.id,
            order_number=payment.order.order_number,
            user_id=payment.order.user_id,
            total_price=payment.order.total_price,
            quantity=payment.order.quantity,
            created_at=payment.order.created_at,
            updated_at=payment.order.updated_at,
            product_id=payment.order.product_id
        )
        payment_dict["product"] = PYD_ProductResponse(
            id=payment.order.product.id,
            name=payment.order.product.name,
            price=payment.order.product.price,
            app_id=payment.order.product.app_id
        )
        payment_dict["application"] = PYD_ApplicationResponse(
            id=payment.order.product.app.id,
            name=payment.order.product.app.name
        )

    return PYD_PaymentResponse(**payment_dict)


async def update_payment(
        db: AsyncSession,
        payment_id: int,
        payment_update: PYD_PaymentUpdate,
        include_order: bool = False) -> Optional[PYD_PaymentResponse]:
    # 步骤1: 构建查询和获取支付记录
    try:
        if include_order:
            query = select(Payment).options(
                joinedload(Payment.order).joinedload(Order.product).joinedload(Product.app)
            ).where(Payment.id == payment_id)
        else:
            query = select(Payment).where(Payment.id == payment_id)

        result = await db.execute(query)
        payment = result.scalar_one_or_none()

        if not payment:
            raise HTTPException_AppToolsSZXW(支付_异常代码.支付单号不存在, f"未找到要更新的支付记录: {payment_id}")
            
    except HTTPException_AppToolsSZXW:
        # 重新抛出业务异常
        raise
    except Exception as e:
        logger.error(f"查询支付记录失败 (payment_id={payment_id}): {str(e)}")
        raise HTTPException_AppToolsSZXW(其他_异常代码.查询数据失败, f"查询支付记录失败: {str(e)}")

    # 步骤2: 更新支付记录字段
    try:
        for field, value in payment_update.model_dump(exclude_unset=True).items():
            setattr(payment, field, value)
    except Exception as e:
        logger.error(f"设置支付记录字段失败 (payment_id={payment_id}): {str(e)}")
        raise HTTPException_AppToolsSZXW(其他_异常代码.更新数据失败, f"设置支付记录字段失败: {str(e)}")

    # 步骤3: 提交数据库事务
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(f"提交数据库事务失败 (payment_id={payment_id}): {str(e)}")
        raise HTTPException_AppToolsSZXW(其他_异常代码.更新数据失败, f"提交数据库事务失败: {str(e)}")

    # 步骤4: 重新获取更新后的支付记录
    try:
        # 如果需要预加载关系，重新查询
        if include_order:
            logger.info(f"获取支付记录以及关联数据 (payment_id={payment_id})")
            query = select(Payment).options(
                joinedload(Payment.order).joinedload(Order.product).joinedload(Product.app)
            ).where(Payment.id == payment_id)
            result = await db.execute(query)
            payment = result.scalar_one()
        else:
            query = select(Payment).where(Payment.id == payment_id)
            result = await db.execute(query)
            payment = result.scalar_one()
    except Exception as e:
        logger.error(f"重新获取支付记录失败 (payment_id={payment_id}): {str(e)}")
        raise HTTPException_AppToolsSZXW(其他_异常代码.查询数据失败, f"重新获取支付记录失败: {str(e)}")

    # 步骤5: 构建基础支付字典
    try:
        # 创建一个字典来存储支付信息
        payment_dict = {
            "id": payment.id,
            "order_id": payment.order_id,
            "payment_method": payment.payment_method,
            "payment_price": payment.payment_price,
            "payment_status": payment.payment_status,
            "callback_url": payment.callback_url,
            "payment_url": payment.payment_url,
            "created_at": payment.created_at,
            "updated_at": payment.updated_at,
            # 苹果内购字段
            "apple_receipt": payment.apple_receipt,
            "apple_transaction_id": payment.apple_transaction_id,
            "apple_original_transaction_id": payment.apple_original_transaction_id,
            "apple_environment": payment.apple_environment,
            "apple_expires_date": payment.apple_expires_date,
            "apple_auto_renew_status": payment.apple_auto_renew_status,
            "apple_offer_identifier": payment.apple_offer_identifier,
            "apple_offer_type": payment.apple_offer_type,
        }
    except Exception as e:
        logger.error(f"构建基础支付字典失败 (payment_id={payment_id}): {str(e)}")
        raise HTTPException_AppToolsSZXW(9999, f"构建基础支付字典失败: {str(e)}")

    # 步骤6: 构建关联数据（订单、产品、应用）
    if include_order and payment.order:
        try:
            payment_dict["order"] = PYD_OrderResponse(
                id=payment.order.id,
                order_number=payment.order.order_number,
                user_id=payment.order.user_id,
                total_price=payment.order.total_price,
                quantity=payment.order.quantity,
                created_at=payment.order.created_at,
                updated_at=payment.order.updated_at,
                product_id=payment.order.product_id
            )
        except Exception as e:
            logger.error(f"构建订单响应数据失败 (payment_id={payment_id}): {str(e)}")
            raise HTTPException_AppToolsSZXW(其他_异常代码.数据处理失败, f"构建订单响应数据失败: {str(e)}")

        try:
            payment_dict["product"] = PYD_ProductResponse(
                id=payment.order.product.id,
                name=payment.order.product.name,
                price=payment.order.product.price,
                app_id=payment.order.product.app_id
            )
        except Exception as e:
            logger.error(f"构建产品响应数据失败 (payment_id={payment_id}): {str(e)}")
            raise HTTPException_AppToolsSZXW(其他_异常代码.数据处理失败, f"构建产品响应数据失败: {str(e)}")

        try:
            payment_dict["application"] = PYD_ApplicationResponse(
                id=payment.order.product.app.id,
                name=payment.order.product.app.name
            )
        except Exception as e:
            logger.error(f"构建应用响应数据失败 (payment_id={payment_id}): {str(e)}")
            raise HTTPException_AppToolsSZXW(其他_异常代码.数据处理失败, f"构建应用响应数据失败: {str(e)}")

    # 步骤7: 创建并返回响应对象
    try:
        # 使用字典创建 PYD_PaymentResponse 对象
        return PYD_PaymentResponse(**payment_dict)
    except Exception as e:
        logger.error(f"创建支付响应对象失败 (payment_id={payment_id}): {str(e)}")
        raise HTTPException_AppToolsSZXW(其他_异常代码.数据处理失败, f"创建支付响应对象失败: {str(e)}")


async def delete_payment(db: AsyncSession, payment_id: int) -> bool:
    try:
        query = delete(Payment).where(Payment.id == payment_id)
        result = await db.execute(query)
        await db.commit()
        if result.rowcount == 0:
            raise HTTPException_AppToolsSZXW(支付_异常代码.支付单号不存在, f"未找到要删除的支付记录: {payment_id}")
        return True
    except Exception as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(其他_异常代码.删除数据失败, f"删除支付记录失败: {str(e)}")


async def list_payments(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        include_order: bool = False) -> List[PYD_PaymentResponse]:
    # 基本查询
    query = select(Payment)

    # 仅在需要外键数据时添加joinedload
    if include_order:
        query = query.options(
            joinedload(Payment.order).joinedload(Order.product).joinedload(Product.app)
        )

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    payments = result.unique().scalars().all()

    payment_responses = []
    for payment in payments:
        payment_dict = {
            "id": payment.id,
            "order_id": payment.order_id,
            "payment_method": payment.payment_method,
            "payment_price": payment.payment_price,
            "payment_status": payment.payment_status,
            "callback_url": payment.callback_url,
            "payment_url": payment.payment_url,
            "created_at": payment.created_at,
            "updated_at": payment.updated_at,
            # 苹果内购字段
            "apple_receipt": payment.apple_receipt,
            "apple_transaction_id": payment.apple_transaction_id,
            "apple_original_transaction_id": payment.apple_original_transaction_id,
            "apple_environment": payment.apple_environment,
            "apple_expires_date": payment.apple_expires_date,
            "apple_auto_renew_status": payment.apple_auto_renew_status,
            "apple_offer_identifier": payment.apple_offer_identifier,
            "apple_offer_type": payment.apple_offer_type,
        }

        if include_order and payment.order:
            payment_dict["order"] = PYD_OrderResponse(
                id=payment.order.id,
                order_number=payment.order.order_number,
                user_id=payment.order.user_id,
                total_price=payment.order.total_price,
                quantity=payment.order.quantity,
                created_at=payment.order.created_at,
                updated_at=payment.order.updated_at,
                product_id=payment.order.product_id
            )
            payment_dict["product"] = PYD_ProductResponse(
                id=payment.order.product.id,
                name=payment.order.product.name,
                price=payment.order.product.price,
                app_id=payment.order.product.app_id
            )
            payment_dict["application"] = PYD_ApplicationResponse(
                id=payment.order.product.app.id,
                name=payment.order.product.app.name
            )

        payment_responses.append(PYD_PaymentResponse(**payment_dict))

    return payment_responses
