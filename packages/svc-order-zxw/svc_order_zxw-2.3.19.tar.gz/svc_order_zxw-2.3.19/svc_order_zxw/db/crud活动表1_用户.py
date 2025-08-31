"""
# File       : crud_用户.py
# Time       ：2024/10/12 07:30
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：Model用户表的异步CRUD操作
"""
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from svc_order_zxw.db.models_活动表 import Model用户, Model支付转换权限, Model用户优惠券
from typing import List, Optional
from sqlalchemy.orm import joinedload

from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW
from svc_order_zxw.异常代码 import 用户_异常代码, 其他_异常代码


class PYD_用户Response(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    支付转换权限: Optional[List["PYD_支付转换权限Response"]] = None
    用户优惠券: Optional[List["PYD_用户优惠券Response"]] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_relations(cls, user, include_支付转换权限: bool = False, include_用户优惠券: bool = False):
        user_dict = {
            "id": user.id,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }

        if include_支付转换权限 and user.支付转换权限:
            user_dict["支付转换权限"] = [PYD_支付转换权限Response(
                id=权限.id,
                isCharged=权限.isCharged,
                created_at=权限.created_at,
                updated_at=权限.updated_at
            ) for 权限 in user.支付转换权限]

        if include_用户优惠券 and user.用户优惠券:
            user_dict["用户优惠券"] = [PYD_用户优惠券Response(
                id=优惠券.id,
                is_used=优惠券.is_used
            ) for 优惠券 in user.用户优惠券]

        return cls(**user_dict)


class PYD_支付转换权限Response(BaseModel):
    id: int
    isCharged: bool
    created_at: datetime
    updated_at: datetime


class PYD_用户优惠券Response(BaseModel):
    id: int
    is_used: bool


async def create_user(db: AsyncSession, external_user_id: int) -> PYD_用户Response:
    try:
        new_user = Model用户(id=external_user_id)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return PYD_用户Response.from_orm_with_relations(new_user)
    except Exception as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(其他_异常代码.新增数据失败, f"创建用户失败: {str(e)}")


async def get_user(
        db: AsyncSession,
        user_id: int,
        include_支付转换权限: bool = False,
        include_用户优惠券: bool = False
) -> Optional[PYD_用户Response]:
    query = select(Model用户).where(Model用户.id == user_id)

    if include_支付转换权限:
        query = query.options(joinedload(Model用户.支付转换权限))
    if include_用户优惠券:
        query = query.options(joinedload(Model用户.用户优惠券))

    result = await db.execute(query)
    user = result.unique().scalar_one_or_none()

    if not user:
        return None

    return PYD_用户Response.from_orm_with_relations(user, include_支付转换权限, include_用户优惠券)


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    try:
        stmt = delete(Model用户).where(Model用户.id == user_id)
        result = await db.execute(stmt)
        await db.commit()
        if result.rowcount == 0:
            raise HTTPException_AppToolsSZXW(用户_异常代码.用户不存在, f"未找到要删除的用户: {user_id}")
        return True
    except Exception as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(其他_异常代码.删除数据失败, f"删除用户失败: {str(e)}")


async def list_users(db: AsyncSession,
                     skip: int = 0,
                     limit: int = 100,
                     include_支付转换权限: bool = False,
                     include_用户优惠券: bool = False) -> List[PYD_用户Response]:
    query = select(Model用户)

    if include_支付转换权限:
        query = query.options(joinedload(Model用户.支付转换权限))
    if include_用户优惠券:
        query = query.options(joinedload(Model用户.用户优惠券))

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.unique().scalars().all()

    return [PYD_用户Response.from_orm_with_relations(user, include_支付转换权限, include_用户优惠券) for user in users]
