from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import joinedload
from svc_order_zxw.db.models_活动表 import Model用户优惠券, Model用户, Model优惠券
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW
from svc_order_zxw.异常代码 import 用户优惠券_异常代码, 其他_异常代码, 用户_异常代码, 优惠券_异常代码


class PYD_用户优惠券Response(BaseModel):
    id: int
    is_used: bool
    user_id: int
    coupon_id: int

    class Config:
        from_attributes = True


class PYD_用户Response(BaseModel):
    id: int


class PYD_优惠券Response(BaseModel):
    id: int
    code: str
    discount_value: float
    expiration_date: datetime


class PYD_用户优惠券DetailResponse(PYD_用户优惠券Response):
    user: Optional[PYD_用户Response] = None
    coupon: Optional[PYD_优惠券Response] = None


async def create_用户优惠券(db: AsyncSession, user_id: int, coupon_id: int) -> PYD_用户优惠券Response:
    try:
        # 检查用户是否存在
        query = select(Model用户).where(Model用户.id == user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException_AppToolsSZXW(用户_异常代码.用户不存在, f"用户不存在: {user_id}")

        # 检查优惠券是否存在
        query = select(Model优惠券).where(Model优惠券.id == coupon_id)
        result = await db.execute(query)
        coupon = result.scalar_one_or_none()
        if not coupon:
            raise HTTPException_AppToolsSZXW(优惠券_异常代码.优惠券不存在, f"优惠券不存在: {coupon_id}")

        new_用户优惠券 = Model用户优惠券(user_id=user_id, coupon_id=coupon_id, is_used=False)
        db.add(new_用户优惠券)
        await db.commit()
        await db.refresh(new_用户优惠券)
        return PYD_用户优惠券Response(
            id=new_用户优惠券.id,
            is_used=new_用户优惠券.is_used,
            user_id=new_用户优惠券.user_id,
            coupon_id=new_用户优惠券.coupon_id
        )
    except HTTPException_AppToolsSZXW:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(其他_异常代码.新增数据失败, f"创建用户优惠券失败: {str(e)}")


async def get_用户优惠券(
        db: AsyncSession,
        用户优惠券_id: int,
        include_user: bool = False,
        include_coupon: bool = False) -> Optional[PYD_用户优惠券DetailResponse]:
    query = select(Model用户优惠券).where(Model用户优惠券.id == 用户优惠券_id)

    if include_user:
        query = query.options(joinedload(Model用户优惠券.user))
    if include_coupon:
        query = query.options(joinedload(Model用户优惠券.coupon))

    result = await db.execute(query)
    用户优惠券 = result.unique().scalar_one_or_none()

    if not 用户优惠券:
        return None

    response_dict = {
        "id": 用户优惠券.id,
        "is_used": 用户优惠券.is_used,
        "user_id": 用户优惠券.user_id,
        "coupon_id": 用户优惠券.coupon_id
    }

    if include_user and 用户优惠券.user:
        response_dict["user"] = PYD_用户Response(
            id=用户优惠券.user.id
        )

    if include_coupon and 用户优惠券.coupon:
        response_dict["coupon"] = PYD_优惠券Response(
            id=用户优惠券.coupon.id,
            code=用户优惠券.coupon.code,
            discount_value=用户优惠券.coupon.discount_value,
            expiration_date=用户优惠券.coupon.expiration_date
        )

    return PYD_用户优惠券DetailResponse(**response_dict)


async def update_用户优惠券(db: AsyncSession, 用户优惠券_id: int, is_used: bool) -> Optional[PYD_用户优惠券Response]:
    try:
        query = select(Model用户优惠券).where(Model用户优惠券.id == 用户优惠券_id)
        result = await db.execute(query)
        用户优惠券 = result.scalar_one_or_none()

        if not 用户优惠券:
            raise HTTPException_AppToolsSZXW(用户优惠券_异常代码.用户优惠券不存在,
                                             f"未找到要更新的用户优惠券: {用户优惠券_id}")

        用户优惠券.is_used = is_used

        await db.commit()
        await db.refresh(用户优惠券)

        return PYD_用户优惠券Response(
            id=用户优惠券.id,
            is_used=用户优惠券.is_used,
            user_id=用户优惠券.user_id,
            coupon_id=用户优惠券.coupon_id
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(其他_异常代码.更新数据失败, f"更新用户优惠券失败: {str(e)}")


async def delete_用户优惠券(db: AsyncSession, 用户优惠券_id: int) -> bool:
    try:
        query = delete(Model用户优惠券).where(Model用户优惠券.id == 用户优惠券_id)
        result = await db.execute(query)
        await db.commit()
        return result.rowcount > 0
    except Exception as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(其他_异常代码.删除数据失败, f"删除用户优惠券失败: {str(e)}")


async def list_用户优惠券(
        db: AsyncSession,
        user_id: Optional[int] = None,
        skip: int = 0, limit: int = 100) -> List[PYD_用户优惠券Response]:
    query = select(Model用户优惠券)

    if user_id:
        query = query.where(Model用户优惠券.user_id == user_id)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    用户优惠券_list = result.scalars().all()

    return [PYD_用户优惠券Response(
        id=用户优惠券.id,
        is_used=用户优惠券.is_used,
        user_id=用户优惠券.user_id,
        coupon_id=用户优惠券.coupon_id
    ) for 用户优惠券 in 用户优惠券_list]
