"""
# File       : crud2_products.py
# Time       ：2024/10/7 05:35
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：Product表的异步CRUD操作
"""
from typing import List, Optional
from pydantic import BaseModel, validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError

from svc_order_zxw.db.models import Product, Application, ProductType
from svc_order_zxw.异常代码 import (
    商品_异常代码, 其他_异常代码
)
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW


class PYD_ProductCreate(BaseModel):
    name: str
    app_id: int
    price: float
    # 苹果内购相关字段
    apple_product_id: Optional[List[str]] = None
    product_type: Optional[ProductType] = None
    subscription_duration: Optional[str] = None

    @validator('apple_product_id')
    def validate_apple_product_id(cls, v):
        if v is not None:
            if not isinstance(v, list):
                raise ValueError('apple_product_id must be a list')
            if not all(isinstance(item, str) for item in v):
                raise ValueError('all items in apple_product_id must be strings')
            if len(v) == 0:
                raise ValueError('apple_product_id list cannot be empty')
        return v


class PYD_ProductUpdate(BaseModel):
    name: Optional[str] = None
    app_id: Optional[int] = None
    price: Optional[float] = None
    # 苹果内购相关字段
    apple_product_id: Optional[List[str]] = None
    product_type: Optional[ProductType] = None
    subscription_duration: Optional[str] = None

    @validator('apple_product_id')
    def validate_apple_product_id(cls, v):
        if v is not None:
            if not isinstance(v, list):
                raise ValueError('apple_product_id must be a list')
            if not all(isinstance(item, str) for item in v):
                raise ValueError('all items in apple_product_id must be strings')
            if len(v) == 0:
                raise ValueError('apple_product_id list cannot be empty')
        return v


class PYD_ProductResponse(BaseModel):
    id: int
    name: str
    app_name: str
    price: float
    # 苹果内购相关字段
    apple_product_id: Optional[List[str]] = None
    product_type: Optional[ProductType] = None
    subscription_duration: Optional[str] = None

    class Config:
        from_attributes = True


async def create_product(db: AsyncSession, product: PYD_ProductCreate) -> PYD_ProductResponse:
    try:
        # 检查应用是否存在
        app = await db.execute(select(Application).filter(Application.id == product.app_id))
        if not app.scalar_one_or_none():
            raise HTTPException_AppToolsSZXW(商品_异常代码.商品不存在, "指定的应用不存在", 404)

        db_product = Product(**product.model_dump())
        db.add(db_product)
        await db.commit()
        await db.refresh(db_product)

        # 获应用名称
        app_name = (await db.execute(select(Application.name).filter(Application.id == db_product.app_id))).scalar_one()

        return PYD_ProductResponse(
            id=db_product.id,
            name=db_product.name,
            app_name=app_name,
            price=db_product.price,
            apple_product_id=db_product.apple_product_id,
            product_type=db_product.product_type,
            subscription_duration=db_product.subscription_duration
        )
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(其他_异常代码.未知错误, f"创建商品时发生错误: {str(e)}", 500)


async def get_product(db: AsyncSession, product_id: int) -> Optional[PYD_ProductResponse]:
    try:
        result = await db.execute(
            select(Product, Application.name.label("app_name"))
            .join(Application)
            .filter(Product.id == product_id)
        )
        row = result.one_or_none()
        if not row:
            return None
            # raise HTTPException_AppToolsSZXW(ErrorCode.产品未找到, "产品未找到", 404)
        product, app_name = row
        return PYD_ProductResponse(
            id=product.id,
            name=product.name,
            app_name=app_name,
            price=product.price,
            apple_product_id=product.apple_product_id,
            product_type=product.product_type,
            subscription_duration=product.subscription_duration
        )
    except SQLAlchemyError as e:
        raise HTTPException_AppToolsSZXW(其他_异常代码.未知错误, f"获取商品时发生错误: {str(e)}", 500)


async def get_product_by_apple_id(db: AsyncSession, apple_product_id: str) -> Optional[PYD_ProductResponse]:
    """根据苹果产品ID查询商品"""
    try:
        # 使用JSON查询来查找包含特定apple_product_id的商品
        # 注意：这里的语法可能因数据库而异，以下是通用的JSON查询方式
        result = await db.execute(
            select(Product, Application.name.label("app_name"))
            .join(Application)
            .filter(Product.apple_product_id.op('JSON_CONTAINS')(f'"{apple_product_id}"'))
        )
        row = result.first()
        if not row:
            return None
        
        product, app_name = row
        return PYD_ProductResponse(
            id=product.id,
            name=product.name,
            app_name=app_name,
            price=product.price,
            apple_product_id=product.apple_product_id,
            product_type=product.product_type,
            subscription_duration=product.subscription_duration
        )
    except SQLAlchemyError as e:
        raise HTTPException_AppToolsSZXW(其他_异常代码.未知错误, f"查询苹果产品时发生错误: {str(e)}", 500)


async def get_products(db: AsyncSession, app_name: str = None, is_apple_product: bool = False, skip: int = 0,
                       limit: int = 100) -> List[PYD_ProductResponse]:
    # 获取所有产品
    query = (
        select(Product, Application.name.label("app_name"))
        .join(Application)
        .filter(Product.apple_product_id.isnot(None) if is_apple_product else Product.apple_product_id.is_(None))
    )

    if app_name:
        query = query.filter(Application.name == app_name)

    result = await db.execute(query.offset(skip).limit(limit))

    products = result.all()
    return [PYD_ProductResponse(
        id=product.id,
        name=product.name,
        app_name=app_name,
        price=product.price,
        apple_product_id=product.apple_product_id,
        product_type=product.product_type,
        subscription_duration=product.subscription_duration
    ) for product, app_name in products]


async def update_product(db: AsyncSession,
                         product_id: int,
                         product_update: PYD_ProductUpdate) -> Optional[PYD_ProductResponse]:
    try:
        result = await db.execute(select(Product).filter(Product.id == product_id))
        db_product = result.scalar_one_or_none()
        if not db_product:
            raise HTTPException_AppToolsSZXW(商品_异常代码.商品不存在, "商品不存在", 404)

        update_data = product_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)

        await db.commit()
        await db.refresh(db_product)

        # 获取应用名称
        app_result = await db.execute(select(Application.name).filter(Application.id == db_product.app_id))
        app_name = app_result.scalar_one_or_none()
        if not app_name:
            raise HTTPException_AppToolsSZXW(商品_异常代码.商品不存在, "商品关联的应用不存在", 404)

        return PYD_ProductResponse(
            id=db_product.id,
            name=db_product.name,
            app_name=app_name,
            price=db_product.price,
            apple_product_id=db_product.apple_product_id,
            product_type=db_product.product_type,
            subscription_duration=db_product.subscription_duration
        )
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(其他_异常代码.未知错误, f"更新商品时发生错误: {str(e)}", 500)


async def delete_product(db: AsyncSession, product_id: int) -> bool:
    try:
        result = await db.execute(select(Product).filter(Product.id == product_id))
        db_product = result.scalar_one_or_none()
        if not db_product:
            raise HTTPException_AppToolsSZXW(
                商品_异常代码.商品不存在,
                "商品未找到",
                404)

        await db.delete(db_product)
        await db.commit()
        return True
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(
            其他_异常代码.未知错误,
            f"删除商品时发生错误: {str(e)}",
            500)
