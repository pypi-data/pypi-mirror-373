"""
# File       : crud_促销活动.py
# Time       ：2024/10/11 上午13:30
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：促销活动表的异步CRUD操作
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import joinedload
from svc_order_zxw.db.models_活动表 import Model促销活动, Product
from typing import List, Optional
from pydantic import BaseModel
from datetime import date
from enum import Enum
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW
from svc_order_zxw.异常代码 import 促销活动_异常代码, 其他_异常代码


class DiscountType(str, Enum):
    金额 = '金额'
    折扣 = '折扣'
    优惠券 = '优惠券'


class PYD_ProductResponse(BaseModel):
    id: int
    name: str
    price: float

    class Config:
        from_attributes = True


class PYD_PromotionResponse(BaseModel):
    id: int
    name: str
    threshold: float
    discount_type: DiscountType
    discount_value: float
    start_date: date
    end_date: date
    is_active: bool
    product_id: int
    product: Optional[PYD_ProductResponse] = None

    class Config:
        from_attributes = True


class PYD_CreatePromotion(BaseModel):
    name: str
    threshold: float
    discount_type: DiscountType
    discount_value: float
    start_date: date
    end_date: date
    is_active: bool
    product_id: int


async def create_promotion(
        db: AsyncSession,
        promotion_data: PYD_CreatePromotion
) -> PYD_PromotionResponse:
    try:
        new_promotion = Model促销活动(**promotion_data.dict())
        db.add(new_promotion)
        await db.commit()
        await db.refresh(new_promotion)
        return PYD_PromotionResponse.from_orm(new_promotion)
    except Exception as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(其他_异常代码.新增数据失败, f"创建促销活动失败: {str(e)}")


async def get_promotion(
        db: AsyncSession,
        promotion_id: int,
        include_product: bool = False
) -> Optional[PYD_PromotionResponse]:
    query = select(Model促销活动).where(Model促销活动.id == promotion_id)
    if include_product:
        query = query.options(joinedload(Model促销活动.product))

    result = await db.execute(query)
    promotion = result.unique().scalar_one_or_none()

    if not promotion:
        return None

    promotion_dict = PYD_PromotionResponse.from_orm(promotion).dict()

    if include_product and promotion.product:
        promotion_dict["product"] = PYD_ProductResponse(
            id=promotion.product.id,
            name=promotion.product.name,
            price=promotion.product.price
        )

    return PYD_PromotionResponse(**promotion_dict)


class PYD_UpdatePromotion(BaseModel):
    name: Optional[str] = None
    threshold: Optional[float] = None
    discount_type: Optional[DiscountType] = None
    discount_value: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None
    product_id: Optional[int] = None


async def update_promotion(
        db: AsyncSession,
        promotion_id: int,
        update_data: PYD_UpdatePromotion
) -> Optional[PYD_PromotionResponse]:
    try:
        update_dict = update_data.dict(exclude_unset=True)

        query = update(Model促销活动).where(Model促销活动.id == promotion_id).values(**update_dict)
        result = await db.execute(query)
        await db.commit()

        if result.rowcount == 0:
            return None

        return await get_promotion(db, promotion_id)
    except Exception as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(其他_异常代码.更新数据失败, f"更新促销活动失败: {str(e)}")


async def delete_promotion(db: AsyncSession, promotion_id: int) -> bool:
    query = delete(Model促销活动).where(Model促销活动.id == promotion_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0


class PYD_PromotionFilter(BaseModel):
    product_id: int | None = None
    is_active: Optional[bool] = None


async def list_promotions(
        db: AsyncSession,
        filter: PYD_PromotionFilter,
        skip: int = 0,
        limit: int = 100,
        include_product: bool = False
) -> List[PYD_PromotionResponse]:
    query = select(Model促销活动)

    if filter.product_id:
        query = query.filter(Model促销活动.product_id == filter.product_id)
    if filter.is_active is not None:
        query = query.filter(Model促销活动.is_active == filter.is_active)
    if include_product:
        query = query.options(joinedload(Model促销活动.product))

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    promotions = result.unique().scalars().all()

    return [
        PYD_PromotionResponse(
            id=promotion.id,
            name=promotion.name,
            threshold=promotion.threshold,
            discount_type=promotion.discount_type,
            discount_value=promotion.discount_value,
            start_date=promotion.start_date,
            end_date=promotion.end_date,
            is_active=promotion.is_active,
            product_id=promotion.product_id,
            product=PYD_ProductResponse(
                id=promotion.product.id,
                name=promotion.product.name,
                price=promotion.product.price
            ) if include_product and promotion.product else None
        )
        for promotion in promotions
    ]
