"""
# File       : crud_支付转换权限.py
# Time       ：2024/10/12 上午8:30
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：支付转换权限的CRUD操作
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import joinedload
from svc_order_zxw.db.models_活动表 import Model支付转换权限, Model用户
from svc_order_zxw.db.models import Order
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW
from svc_order_zxw.异常代码 import 支付转换权限_异常代码, 其他_异常代码, 用户_异常代码, 订单_异常代码


class PYD_支付转换权限Response(BaseModel):
    id: int
    isCharged: bool
    created_at: datetime
    updated_at: datetime
    user_id: int
    order_number: Optional[str] = None

    class Config:
        from_attributes = True


class PYD_用户Response(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime


class PYD_订单Response(BaseModel):
    order_number: str


class PYD_支付转换权限DetailResponse(PYD_支付转换权限Response):
    user: Optional[PYD_用户Response] = None
    order: Optional[PYD_订单Response] = None


async def create_支付转换权限(db: AsyncSession, user_id: int, isCharged: bool,
                              order_number: Optional[str] = None) -> PYD_支付转换权限Response:
    try:
        # 检查用户是否存在
        query = select(Model用户).where(Model用户.id == user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException_AppToolsSZXW(用户_异常代码.用户不存在, f"用户不存在: {user_id}")

        # 如果提供了订单号，检查订单是否存在
        if order_number:
            order = await db.execute(select(Order).where(Order.order_number == order_number))
            if not order.scalar_one_or_none():
                raise HTTPException_AppToolsSZXW(订单_异常代码.订单号不存在, f"订单不存在: {order_number}")

        new_支付转换权限 = Model支付转换权限(user_id=user_id, isCharged=isCharged, order_number=order_number)
        db.add(new_支付转换权限)
        await db.commit()
        await db.refresh(new_支付转换权限)
        return PYD_支付转换权限Response(
            id=new_支付转换权限.id,
            isCharged=new_支付转换权限.isCharged,
            created_at=new_支付转换权限.created_at,
            updated_at=new_支付转换权限.updated_at,
            user_id=new_支付转换权限.user_id,
            order_number=new_支付转换权限.order_number
        )
    except HTTPException_AppToolsSZXW:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(其他_异常代码.新增数据失败, f"创建支付转换权限失败: {str(e)}")


async def get_支付转换权限(
        db: AsyncSession,
        支付转换权限_id: int | None = None,
        order_number: str | None = None,
        include_user: bool = False,
        include_order: bool = False) -> Optional[PYD_支付转换权限DetailResponse]:

    if 支付转换权限_id is None and order_number is None:
        raise HTTPException_AppToolsSZXW(其他_异常代码.数据不存在,
                                         "支付转换权限_id,order_number 至少一个有值.",
                                         400)

    if 支付转换权限_id is not None:
        query = select(Model支付转换权限).where(Model支付转换权限.id == 支付转换权限_id)
    else:
        query = select(Model支付转换权限).where(Model支付转换权限.order_number == order_number)

    if include_user:
        query = query.options(joinedload(Model支付转换权限.user))
    if include_order:
        query = query.options(joinedload(Model支付转换权限.order))

    result = await db.execute(query)
    支付转换权限 = result.unique().scalar_one_or_none()

    if not 支付转换权限:
        return None

    response_dict = {
        "id": 支付转换权限.id,
        "isCharged": 支付转换权限.isCharged,
        "created_at": 支付转换权限.created_at,
        "updated_at": 支付转换权限.updated_at,
        "user_id": 支付转换权限.user_id,
        "order_number": 支付转换权限.order_number
    }

    if include_user and 支付转换权限.user:
        response_dict["user"] = PYD_用户Response(
            id=支付转换权限.user.id,
            created_at=支付转换权限.user.created_at,
            updated_at=支付转换权限.user.updated_at
        )

    if include_order and 支付转换权限.order:
        response_dict["order"] = PYD_订单Response(
            order_number=支付转换权限.order.order_number
        )

    return PYD_支付转换权限DetailResponse(**response_dict)


async def update_支付转换权限(
        db: AsyncSession,
        支付转换权限_id: int,
        isCharged: Optional[bool] = None,
        order_number: Optional[str] = None) -> Optional[PYD_支付转换权限Response]:
    try:
        update_data = {}
        if isCharged is not None:
            update_data["isCharged"] = isCharged
        if order_number is not None:
            # 检查订单是否存在
            order = await db.execute(select(Order).where(Order.order_number == order_number))
            if not order.scalar_one_or_none():
                raise HTTPException_AppToolsSZXW(订单_异常代码.订单号不存在, f"订单不存在: {order_number}")
            update_data["order_number"] = order_number

        if not update_data:
            raise HTTPException_AppToolsSZXW(其他_异常代码.更新数据失败, "没有提供要更新的数据")

        query = select(Model支付转换权限).where(Model支付转换权限.id == 支付转换权限_id)
        result = await db.execute(query)
        支付转换权限 = result.scalar_one_or_none()

        if not 支付转换权限:
            raise HTTPException_AppToolsSZXW(支付转换权限_异常代码.支付转换权限不存在,
                                             f"未找到要更新的支付转换权限: {支付转换权限_id}")

        for key, value in update_data.items():
            setattr(支付转换权限, key, value)

        await db.commit()
        await db.refresh(支付转换权限)

        return PYD_支付转换权限Response(
            id=支付转换权限.id,
            isCharged=支付转换权限.isCharged,
            created_at=支付转换权限.created_at,
            updated_at=支付转换权限.updated_at,
            user_id=支付转换权限.user_id,
            order_number=支付转换权限.order_number
        )
    except HTTPException_AppToolsSZXW:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(其他_异常代码.更新数据失败, f"更新支付转换权限失败: {str(e)}")


async def delete_支付转换权限(db: AsyncSession, 支付转换权限_id: int) -> bool:
    try:
        query = delete(Model支付转换权限).where(Model支付转换权限.id == 支付转换权限_id)
        result = await db.execute(query)
        await db.commit()
        if result.rowcount == 0:
            raise HTTPException_AppToolsSZXW(支付转换权限_异常代码.支付转换权限不存在,
                                             f"未找到要删除的支付转换权限: {支付转换权限_id}")
        return True
    except HTTPException_AppToolsSZXW:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(其他_异常代码.删除数据失败, f"删除支付转换权限失败: {str(e)}")


async def list_支付转换权限(
        db: AsyncSession,
        user_id: int,
        skip: int = 0, limit: int = 100) -> List[PYD_支付转换权限Response]:
    query = select(Model支付转换权限)

    if user_id:
        query = query.where(Model支付转换权限.user_id == user_id)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    支付转换权限_list = result.scalars().all()

    return [PYD_支付转换权限Response.from_orm(支付转换权限) for 支付转换权限 in 支付转换权限_list]
