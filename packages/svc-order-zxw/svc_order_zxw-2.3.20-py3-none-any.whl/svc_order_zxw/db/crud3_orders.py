"""
# File       : crud3_orders.py
# Time       ：2024/10/7 06:26
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：订单管理的CRUD操作模块
"""
from pydantic import BaseModel, Field
from datetime import datetime
from svc_order_zxw.apis.schemas_payments import OrderStatus, PaymentMethod
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from svc_order_zxw.db.models import Order, Product, ProductType
from typing import List, Optional, Union
from sqlalchemy.orm import joinedload

from app_tools_zxw.Funcs.生成订单号 import 生成订单号
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW
from svc_order_zxw.异常代码 import 订单_异常代码, 其他_异常代码


class PYD_OrderBase(BaseModel):
    """订单基础模型"""
    user_id: str
    total_price: float
    quantity: int = Field(default=1)
    # 苹果内购订阅相关字段
    original_transaction_id: Optional[str] = Field(None, description="苹果原始交易ID，订阅续费时保持不变")
    subscription_expire_date: Optional[datetime] = Field(None, description="订阅过期时间，仅订阅型商品使用")
    auto_renew_status: Optional[bool] = Field(None, description="是否自动续费，仅订阅型商品使用")


class PYD_OrderCreate(PYD_OrderBase):
    """创建订单请求模型"""
    order_number: str = 生成订单号()
    product_id: int


class PYD_OrderUpdate(BaseModel):
    """更新订单请求模型"""
    total_price: Optional[float] = None
    quantity: Optional[int] = None
    # 苹果内购订阅相关字段
    original_transaction_id: Optional[str] = None
    subscription_expire_date: Optional[datetime] = None
    auto_renew_status: Optional[bool] = None


class PYD_ProductResponse(BaseModel):
    """产品响应模型"""
    id: int
    name: str
    price: float
    app_id: int
    # 苹果内购特有字段
    apple_product_id: Optional[list[str]] = Field(None, description="苹果商店产品ID")
    product_type: Optional[ProductType] = Field(None, description="商品类型")
    subscription_duration: Optional[str] = Field(None, description="订阅周期")


class PYD_ApplicationResponse(BaseModel):
    """应用响应模型"""
    id: int
    name: str


class PYD_PaymentResponse(BaseModel):
    """支付响应模型"""
    id: int
    payment_price: float
    payment_method: PaymentMethod
    payment_status: OrderStatus
    callback_url: Optional[str]
    payment_url: Optional[str]
    created_at: datetime
    updated_at: datetime


class PYD_OrderResponse(PYD_OrderBase):
    """订单响应模型"""
    id: int
    order_number: str
    created_at: datetime
    updated_at: datetime
    product_id: int
    product: Optional[PYD_ProductResponse] = None
    application: Optional[PYD_ApplicationResponse] = None
    payment: Optional[PYD_PaymentResponse] = None

    class Config:
        from_attributes = True


class PYD_OrderFilter(BaseModel):
    """订单过滤器模型"""
    user_id: Optional[str] = None
    product_id: Optional[int] = None
    application_id: Optional[int] = None
    # 新增过滤条件
    original_transaction_id: Optional[str] = None
    product_type: Optional[ProductType] = None


async def create_order(
        db: AsyncSession,
        order: PYD_OrderCreate,
        include_product: bool = False,
        include_application: bool = False,
        include_payment: bool = False) -> PYD_OrderResponse:
    """
    创建新订单

    功能说明：
    - 创建一个新的订单记录
    - 支持同时加载关联的产品、应用和支付信息
    - 自动生成订单号
    - 事务安全，失败时会回滚
    - 支持苹果内购订阅相关字段

    参数说明：
    - db: AsyncSession - 数据库异步会话对象
    - order: PYD_OrderCreate - 订单创建数据（包含用户ID、总价、数量、产品ID等）
    - include_product: bool - 是否在响应中包含关联的产品信息，默认False
    - include_application: bool - 是否在响应中包含关联的应用信息，默认False
    - include_payment: bool - 是否在响应中包含关联的支付信息，默认False

    返回值：
    - PYD_OrderResponse - 创建成功的订单详细信息

    异常：
    - HTTPException_AppToolsSZXW - 创建失败时抛出，包含错误代码和详细信息

    使用示例：
    ```python
    order_data = PYD_OrderCreate(
        user_id="user123",
        total_price=99.99,
        quantity=2,
        product_id=1,
        original_transaction_id="1000000123456789"
    )
    new_order = await create_order(db, order_data, include_product=True)
    ```
    """
    try:
        new_order = Order(**order.model_dump())
        db.add(new_order)
        await db.commit()
        await db.refresh(new_order)

        if include_product:
            await db.refresh(new_order, attribute_names=['product'])
        if include_application:
            # 修改这里：分两步刷新 product 和 app
            await db.refresh(new_order, attribute_names=['product'])
            if new_order.product:
                await db.refresh(new_order.product, attribute_names=['app'])
        if include_payment:
            await db.refresh(new_order, attribute_names=['payment'])

        order_dict = {
            "id": new_order.id,
            "user_id": new_order.user_id,
            "total_price": new_order.total_price,
            "quantity": new_order.quantity,
            "order_number": new_order.order_number,
            "created_at": new_order.created_at,
            "updated_at": new_order.updated_at,
            "product_id": new_order.product_id,
            # 苹果内购订阅相关字段
            "original_transaction_id": new_order.original_transaction_id,
            "subscription_expire_date": new_order.subscription_expire_date,
            "auto_renew_status": new_order.auto_renew_status,
        }

        if include_product and new_order.product:
            order_dict["product"] = PYD_ProductResponse(
                id=new_order.product.id,
                name=new_order.product.name,
                price=new_order.product.price,
                app_id=new_order.product.app_id,
                apple_product_id=new_order.product.apple_product_id,
                product_type=new_order.product.product_type,
                subscription_duration=new_order.product.subscription_duration
            )

        if include_application and new_order.product and new_order.product.app:
            order_dict["application"] = PYD_ApplicationResponse(
                id=new_order.product.app.id,
                name=new_order.product.app.name
            )

        if include_payment and new_order.payment:
            order_dict["payment"] = PYD_PaymentResponse(
                id=new_order.payment.id,
                payment_price=new_order.payment.payment_price,
                payment_method=new_order.payment.payment_method,
                payment_status=new_order.payment.payment_status,
                callback_url=new_order.payment.callback_url,
                payment_url=new_order.payment.payment_url,
                created_at=new_order.payment.created_at,
                updated_at=new_order.payment.updated_at
            )

        return PYD_OrderResponse(**order_dict)
    except Exception as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(其他_异常代码.新增数据失败, f"创建订单失败: {str(e)}")


async def get_order(
        db: AsyncSession,
        order_identifier: Union[int, str],
        include_product: bool = False,
        include_application: bool = False,
        include_payment: bool = False) -> Optional[PYD_OrderResponse]:
    """
    获取指定订单的详细信息

    功能说明：
    - 根据订单ID或订单号查询订单
    - 支持同时加载关联的产品、应用和支付信息
    - 使用 joinedload 优化查询性能
    - 找不到订单时返回 None
    - 支持苹果内购订阅相关字段

    参数说明：
    - db: AsyncSession - 数据库异步会话对象
    - order_identifier: Union[int, str] - 订单标识符，可以是订单ID（整数）或订单号（字符串）
    - include_product: bool - 是否包含关联的产品信息，默认False
    - include_application: bool - 是否包含关联的应用信息，默认False
    - include_payment: bool - 是否包含关联的支付信息，默认False

    返回值：
    - Optional[PYD_OrderResponse] - 如果找到订单，返回订单响应对象；否则返回None

    使用示例：
    ```python
    # 根据订单ID查询
    order = await get_order(db, 123, include_product=True)

    # 根据订单号查询
    order = await get_order(db, "ORDER20241007001", include_application=True)
    ```
    """

    query = select(Order)

    if include_product:
        query = query.options(joinedload(Order.product))
    if include_application:
        query = query.options(joinedload(Order.product).joinedload(Product.app))
    if include_payment:
        query = query.options(joinedload(Order.payment))

    if isinstance(order_identifier, int):
        query = query.where(Order.id == order_identifier)
    else:
        query = query.where(Order.order_number == order_identifier)

    result = await db.execute(query)
    order = result.unique().scalar_one_or_none()

    if not order:
        return None
        # raise HTTPException_AppToolsSZXW(订单_异常代码.订单号不存在, f"未找到订单: {order_identifier}")

    # 创建包含所有字段的订单字典
    order_dict = {
        "id": order.id,
        "user_id": order.user_id,
        "total_price": order.total_price,
        "quantity": order.quantity,
        "order_number": order.order_number,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
        "product_id": order.product_id,
        # 苹果内购订阅相关字段
        "original_transaction_id": order.original_transaction_id,
        "subscription_expire_date": order.subscription_expire_date,
        "auto_renew_status": order.auto_renew_status,
    }

    # 如果包含产品信息，添加到字典中
    if include_product and order.product:
        order_dict["product"] = PYD_ProductResponse(
            id=order.product.id,
            name=order.product.name,
            price=order.product.price,
            app_id=order.product.app_id,
            apple_product_id=order.product.apple_product_id,
            product_type=order.product.product_type,
            subscription_duration=order.product.subscription_duration
        )

    # 如果包含应用信息，添加到字典中
    if include_application and order.product and order.product.app:
        order_dict["application"] = PYD_ApplicationResponse(
            id=order.product.app.id,
            name=order.product.app.name
        )

    # 如果包含支付信息，添加到字典中
    if include_payment and order.payment:
        order_dict["payment"] = PYD_PaymentResponse(
            id=order.payment.id,
            payment_price=order.payment.payment_price,
            payment_method=order.payment.payment_method,
            payment_status=order.payment.payment_status,
            callback_url=order.payment.callback_url,
            payment_url=order.payment.payment_url,
            created_at=order.payment.created_at,
            updated_at=order.payment.updated_at
        )

    return PYD_OrderResponse(**order_dict)


async def update_order(
        db: AsyncSession,
        order_id: int,
        order_update: PYD_OrderUpdate) -> Optional[PYD_OrderResponse]:
    """
    更新指定订单的信息

    功能说明：
    - 根据订单ID更新订单信息
    - 只更新提供的字段，未提供的字段保持不变
    - 事务安全，失败时会回滚
    - 支持更新苹果内购订阅相关字段

    参数说明：
    - db: AsyncSession - 数据库异步会话对象
    - order_id: int - 要更新的订单ID
    - order_update: PYD_OrderUpdate - 更新数据（可包含总价、数量、订阅信息等）

    返回值：
    - Optional[PYD_OrderResponse] - 更新成功的订单信息

    异常：
    - HTTPException_AppToolsSZXW - 订单不存在或更新失败时抛出

    使用示例：
    ```python
    update_data = PYD_OrderUpdate(
        total_price=199.99,
        quantity=3,
        subscription_expire_date=datetime(2024, 12, 31),
        auto_renew_status=True
    )
    updated_order = await update_order(db, 123, update_data)
    ```
    """
    try:
        # 首先获取现有订单
        query = select(Order).where(Order.id == order_id)
        result = await db.execute(query)
        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException_AppToolsSZXW(订单_异常代码.订单号不存在, f"未找到要更新的订单: {order_id}")

        # 更新订单
        for field, value in order_update.dict(exclude_unset=True).items():
            setattr(order, field, value)

        await db.commit()
        await db.refresh(order)

        # 手动创建 PYD_OrderResponse 对象
        order_response = PYD_OrderResponse(
            id=order.id,
            user_id=order.user_id,
            total_price=order.total_price,
            quantity=order.quantity,
            order_number=order.order_number,
            created_at=order.created_at,
            updated_at=order.updated_at,
            product_id=order.product_id,
            # 苹果内购订阅相关字段
            original_transaction_id=order.original_transaction_id,
            subscription_expire_date=order.subscription_expire_date,
            auto_renew_status=order.auto_renew_status
        )

        return order_response
    except Exception as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(其他_异常代码.更新数据失败, f"更新订单失败: {str(e)}")


async def delete_order(db: AsyncSession, order_id: int) -> bool:
    """
    删除指定的订单

    功能说明：
    - 根据订单ID删除订单记录
    - 物理删除（从数据库中完全移除）
    - 事务安全，失败时会回滚

    参数说明：
    - db: AsyncSession - 数据库异步会话对象
    - order_id: int - 要删除的订单ID

    返回值：
    - bool - 删除成功返回True

    异常：
    - HTTPException_AppToolsSZXW - 订单不存在或删除失败时抛出

    使用示例：
    ```python
    success = await delete_order(db, 123)
    if success:
        print("订单删除成功")
    ```
    """
    try:
        query = delete(Order).where(Order.id == order_id)
        result = await db.execute(query)
        await db.commit()
        if result.rowcount == 0:
            raise HTTPException_AppToolsSZXW(订单_异常代码.订单号不存在, f"未找到要删除的订单: {order_id}")
        return True
    except Exception as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(其他_异常代码.删除数据失败, f"删除订单失败: {str(e)}")


async def list_orders(
        db: AsyncSession,
        filter: PYD_OrderFilter,
        skip: int = 0,
        limit: int = 100,
        include_product: bool = False,
        include_application: bool = False,
        include_payment: bool = False) -> List[PYD_OrderResponse]:
    """
    获取订单列表（支持过滤和分页）

    功能说明：
    - 根据过滤条件获取订单列表
    - 支持按用户ID、产品ID、应用ID、原始交易ID、商品类型进行过滤
    - 支持分页查询
    - 支持同时加载关联的产品、应用和支付信息
    - 使用 joinedload 优化查询性能
    - 支持苹果内购订阅相关字段

    参数说明：
    - db: AsyncSession - 数据库异步会话对象
    - filter: PYD_OrderFilter - 过滤条件（用户ID、产品ID、应用ID、原始交易ID、商品类型）
    - skip: int - 跳过的记录数（分页用），默认0
    - limit: int - 返回的最大记录数（分页用），默认100
    - include_product: bool - 是否包含关联的产品信息，默认False
    - include_application: bool - 是否包含关联的应用信息，默认False
    - include_payment: bool - 是否包含关联的支付信息，默认False

    返回值：
    - List[PYD_OrderResponse] - 符合条件的订单列表

    使用示例：
    ```python
    # 获取用户的所有订单
    filter_data = PYD_OrderFilter(user_id="user123")
    orders = await list_orders(db, filter_data, include_product=True)

    # 获取特定原始交易ID的所有订阅续费订单
    filter_data = PYD_OrderFilter(original_transaction_id="1000000123456789")
    orders = await list_orders(db, filter_data, include_product=True)

    # 获取特定商品类型的订单
    filter_data = PYD_OrderFilter(product_type=ProductType.AUTO_RENEWABLE)
    orders = await list_orders(db, filter_data, include_application=True)
    ```
    """
    query = select(Order)

    if include_product:
        query = query.options(joinedload(Order.product))
    if include_application:
        query = query.options(joinedload(Order.product).joinedload(Product.app))
    if include_payment:
        query = query.options(joinedload(Order.payment))

    if filter.user_id:
        query = query.where(Order.user_id == filter.user_id)
    if filter.product_id:
        query = query.where(Order.product_id == filter.product_id)
    if filter.application_id:
        query = query.join(Product).where(Product.app_id == filter.application_id)
    if filter.original_transaction_id:
        query = query.where(Order.original_transaction_id == filter.original_transaction_id)
    if filter.product_type:
        query = query.join(Product).where(Product.product_type == filter.product_type)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    orders = result.unique().scalars().all()

    order_responses = []
    for order in orders:
        order_dict = {
            "id": order.id,
            "user_id": order.user_id,
            "total_price": order.total_price,
            "quantity": order.quantity,
            "order_number": order.order_number,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "product_id": order.product_id,
            # 苹果内购订阅相关字段
            "original_transaction_id": order.original_transaction_id,
            "subscription_expire_date": order.subscription_expire_date,
            "auto_renew_status": order.auto_renew_status,
        }

        if include_product and order.product:
            order_dict["product"] = PYD_ProductResponse(
                id=order.product.id,
                name=order.product.name,
                price=order.product.price,
                app_id=order.product.app_id,
                apple_product_id=order.product.apple_product_id,
                product_type=order.product.product_type,
                subscription_duration=order.product.subscription_duration
            )

        if include_application and order.product and order.product.app:
            order_dict["application"] = PYD_ApplicationResponse(
                id=order.product.app.id,
                name=order.product.app.name
            )

        if include_payment and order.payment:
            order_dict["payment"] = PYD_PaymentResponse(
                id=order.payment.id,
                payment_price=order.payment.payment_price,
                payment_method=order.payment.payment_method,
                payment_status=order.payment.payment_status,
                callback_url=order.payment.callback_url,
                payment_url=order.payment.payment_url,
                created_at=order.payment.created_at,
                updated_at=order.payment.updated_at
            )

        order_responses.append(PYD_OrderResponse(**order_dict))

    return order_responses


# 新增：根据原始交易ID获取订单的便捷函数
async def get_orders_by_original_transaction_id(
        db: AsyncSession,
        original_transaction_id: str,
        include_product: bool = True,
        include_application: bool = False,
        include_payment: bool = True) -> List[PYD_OrderResponse]:
    """
    根据苹果原始交易ID获取所有相关订单（主要用于订阅续费场景）

    功能说明：
    - 根据苹果原始交易ID查询所有相关订单
    - 主要用于查询同一订阅的所有续费记录
    - 默认包含产品和支付信息

    参数说明：
    - db: AsyncSession - 数据库异步会话对象
    - original_transaction_id: str - 苹果原始交易ID
    - include_product: bool - 是否包含产品信息，默认True
    - include_application: bool - 是否包含应用信息，默认False
    - include_payment: bool - 是否包含支付信息，默认True

    返回值：
    - List[PYD_OrderResponse] - 相关订单列表，按创建时间倒序排列

    使用示例：
    ```python
    # 获取订阅的所有续费记录
    orders = await get_orders_by_original_transaction_id(db, "1000000123456789")
    ```
    """
    filter_data = PYD_OrderFilter(original_transaction_id=original_transaction_id)
    return await list_orders(
        db=db,
        filter=filter_data,
        include_product=include_product,
        include_application=include_application,
        include_payment=include_payment
    )


# 新增：根据商品类型获取订单的便捷函数
async def get_orders_by_product_type(
        db: AsyncSession,
        product_type: ProductType,
        user_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        include_product: bool = True,
        include_application: bool = False,
        include_payment: bool = False) -> List[PYD_OrderResponse]:
    """
    根据商品类型获取订单列表

    功能说明：
    - 根据商品类型（消耗型、非消耗型、订阅型等）查询订单
    - 可选择性地按用户ID进行进一步过滤
    - 支持分页查询

    参数说明：
    - db: AsyncSession - 数据库异步会话对象
    - product_type: ProductType - 商品类型
    - user_id: Optional[str] - 可选的用户ID过滤
    - skip: int - 跳过的记录数，默认0
    - limit: int - 返回的最大记录数，默认100
    - include_product: bool - 是否包含产品信息，默认True
    - include_application: bool - 是否包含应用信息，默认False
    - include_payment: bool - 是否包含支付信息，默认False

    返回值：
    - List[PYD_OrderResponse] - 符合条件的订单列表

    使用示例：
    ```python
    # 获取所有自动续费订阅订单
    orders = await get_orders_by_product_type(db, ProductType.AUTO_RENEWABLE)

    # 获取特定用户的消耗型商品订单
    orders = await get_orders_by_product_type(
        db, ProductType.CONSUMABLE, user_id="user123"
    )
    ```
    """
    filter_data = PYD_OrderFilter(product_type=product_type, user_id=user_id)
    return await list_orders(
        db=db,
        filter=filter_data,
        skip=skip,
        limit=limit,
        include_product=include_product,
        include_application=include_application,
        include_payment=include_payment
    )
