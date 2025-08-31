"""
# File       : crud活动表4_优惠券.py
# Time       ：2024/10/11 下午2:29
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload
from svc_order_zxw.db.models_活动表 import Model优惠券, Model促销活动
from typing import List, Optional
from pydantic import BaseModel
from datetime import date
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW
from svc_order_zxw.异常代码 import 优惠券_异常代码, 其他_异常代码


class PYD_促销活动Response(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class PYD_优惠券Response(BaseModel):
    id: int
    code: str
    discount_value: float
    expiration_date: date
    promotion_id: int
    promotion: Optional[PYD_促销活动Response] = None

    class Config:
        from_attributes = True


async def create_coupon(
        db: AsyncSession,
        code: str,
        discount_value: float,
        expiration_date: date,
        promotion_id: int
) -> PYD_优惠券Response:
    try:
        new_coupon = Model优惠券(
            code=code,
            discount_value=discount_value,
            expiration_date=expiration_date,
            promotion_id=promotion_id
        )
        db.add(new_coupon)
        await db.commit()
        await db.refresh(new_coupon)

        return PYD_优惠券Response(
            id=new_coupon.id,
            code=new_coupon.code,
            discount_value=new_coupon.discount_value,
            expiration_date=new_coupon.expiration_date,
            promotion_id=new_coupon.promotion_id
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(其他_异常代码.新增数据失败, f"创建优惠券失败: {str(e)}")


async def get_coupon(
        db: AsyncSession,
        coupon_id: int,
        include_promotion: bool = False
) -> Optional[PYD_优惠券Response]:
    query = select(Model优惠券).where(Model优惠券.id == coupon_id)

    if include_promotion:
        query = query.options(joinedload(Model优惠券.promotion))

    result = await db.execute(query)
    coupon = result.unique().scalar_one_or_none()

    if not coupon:
        return None

    coupon_dict = {
        "id": coupon.id,
        "code": coupon.code,
        "discount_value": coupon.discount_value,
        "expiration_date": coupon.expiration_date,
        "promotion_id": coupon.promotion_id
    }

    if include_promotion and coupon.promotion:
        coupon_dict["promotion"] = PYD_促销活动Response(
            id=coupon.promotion.id,
            name=coupon.promotion.name
        )

    return PYD_优惠券Response(**coupon_dict)


async def update_coupon(
        db: AsyncSession,
        coupon_id: int,
        code: Optional[str] = None,
        discount_value: Optional[float] = None,
        expiration_date: Optional[date] = None,
        promotion_id: Optional[int] = None
) -> Optional[PYD_优惠券Response]:
    try:
        query = select(Model优惠券).where(Model优惠券.id == coupon_id)
        result = await db.execute(query)
        coupon = result.scalar_one_or_none()

        if not coupon:
            raise HTTPException_AppToolsSZXW(优惠券_异常代码.优惠券不存在, f"未找到要更新的优惠券: {coupon_id}")

        if code is not None:
            coupon.code = code
        if discount_value is not None:
            coupon.discount_value = discount_value
        if expiration_date is not None:
            coupon.expiration_date = expiration_date
        if promotion_id is not None:
            coupon.promotion_id = promotion_id

        await db.commit()
        await db.refresh(coupon)

        return PYD_优惠券Response(
            id=coupon.id,
            code=coupon.code,
            discount_value=coupon.discount_value,
            expiration_date=coupon.expiration_date,
            promotion_id=coupon.promotion_id
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(其他_异常代码.更新数据失败, f"更新优惠券失败: {str(e)}")


async def delete_coupon(db: AsyncSession, coupon_id: int) -> bool:
    try:
        query = delete(Model优惠券).where(Model优惠券.id == coupon_id)
        result = await db.execute(query)
        await db.commit()
        if result.rowcount == 0:
            raise HTTPException_AppToolsSZXW(优惠券_异常代码.优惠券不存在, f"未找到要删除的优惠券: {coupon_id}")
        return True
    except Exception as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(其他_异常代码.删除数据失败, f"删除优惠券失败: {str(e)}")


class PYD_优惠券Filter(BaseModel):
    promotion_id: Optional[int] = None
    expiration_date_before: Optional[date] = None
    expiration_date_after: Optional[date] = None


async def list_coupons(
        db: AsyncSession,
        filter: PYD_优惠券Filter,
        skip: int = 0,
        limit: int = 100,
        include_promotion: bool = False
) -> List[PYD_优惠券Response]:
    query = select(Model优惠券)

    if include_promotion:
        query = query.options(joinedload(Model优惠券.promotion))

    if filter.promotion_id:
        query = query.where(Model优惠券.promotion_id == filter.promotion_id)
    if filter.expiration_date_before:
        query = query.where(Model优惠券.expiration_date <= filter.expiration_date_before)
    if filter.expiration_date_after:
        query = query.where(Model优惠券.expiration_date >= filter.expiration_date_after)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    coupons = result.unique().scalars().all()

    coupon_responses = []
    for coupon in coupons:
        coupon_dict = {
            "id": coupon.id,
            "code": coupon.code,
            "discount_value": coupon.discount_value,
            "expiration_date": coupon.expiration_date,
            "promotion_id": coupon.promotion_id,
        }

        if include_promotion and coupon.promotion:
            coupon_dict["promotion"] = PYD_促销活动Response(
                id=coupon.promotion.id,
                name=coupon.promotion.name
            )

        coupon_responses.append(PYD_优惠券Response(**coupon_dict))

    return coupon_responses
