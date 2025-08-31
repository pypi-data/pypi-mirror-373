"""
# File       : crud1_applications.py
# Time       ：2024/10/7 12:04
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload
from typing import List, Optional
from pydantic import BaseModel
from svc_order_zxw.db.models import Application
from svc_order_zxw.db.crud2_products import PYD_ProductResponse

from svc_order_zxw.异常代码 import (
    其他_异常代码
)
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW


class PYD_ApplicationBase(BaseModel):
    name: str


class PYD_ApplicationCreate(PYD_ApplicationBase):
    pass


class PYD_ApplicationUpdate(PYD_ApplicationBase):
    pass


class PYD_ApplicationResponse(PYD_ApplicationBase):
    id: int
    products: Optional[List[PYD_ProductResponse]] = None

    class Config:
        from_attributes = True


async def create_application(db: AsyncSession, application: PYD_ApplicationCreate) -> PYD_ApplicationResponse:
    try:
        new_application = Application(**application.model_dump())
        db.add(new_application)
        await db.commit()
        await db.refresh(new_application)

        # 手动创建 PYD_ApplicationResponse 实例
        return PYD_ApplicationResponse(
            id=new_application.id,
            name=new_application.name,
            products=[]  # 新创建的应用还没有产品，所以使用空列表
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(其他_异常代码.新增数据失败, f"创建应用失败: {str(e)}")


async def get_application(
        db: AsyncSession,
        application_id_or_name: int | str,
        include_products: bool = False) -> Optional[PYD_ApplicationResponse]:
    query = select(Application)

    if include_products:
        query = query.options(joinedload(Application.products))

    if isinstance(application_id_or_name, int):
        query = query.where(Application.id == application_id_or_name)
    else:
        print("执行name查询,application_id_or_name = ",application_id_or_name)
        query = query.where(Application.name == application_id_or_name)

    result = await db.execute(query)
    application = result.unique().scalar_one_or_none()

    if not application:
        return None
        # raise HTTPException_AppToolsSZXW(ErrorCode.应用未找到, f"未找到应用: {application_id}")

    application_dict = {
        "id": application.id,
        "name": application.name,
    }

    if include_products and application.products:
        application_dict["products"] = [
            PYD_ProductResponse(
                id=product.id,
                name=product.name,
                app_name=application.name,
                price=product.price
            ) for product in application.products
        ]

    return PYD_ApplicationResponse(**application_dict)


async def update_application(
        db: AsyncSession,
        application_id: int,
        application_update: PYD_ApplicationUpdate) -> Optional[PYD_ApplicationResponse]:
    try:
        query = select(Application).where(Application.id == application_id)
        result = await db.execute(query)
        application = result.scalar_one_or_none()
        if not application:
            raise HTTPException_AppToolsSZXW(其他_异常代码.数据不存在, f"未找到要更新的应用: {application_id}")
        for field, value in application_update.model_dump(exclude_unset=True).items():
            setattr(application, field, value)
        await db.commit()
        await db.refresh(application)

        # 手动创建 PYD_ApplicationResponse 实例
        return PYD_ApplicationResponse(
            id=application.id,
            name=application.name,
            products=[]  # 如果需要包含产品，可能需要额外的查询
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(其他_异常代码.更新数据失败, f"更新应用失败: {str(e)}")


async def delete_application(db: AsyncSession, application_id: int) -> bool:
    try:
        query = delete(Application).where(Application.id == application_id)
        result = await db.execute(query)
        await db.commit()
        if result.rowcount == 0:
            raise HTTPException_AppToolsSZXW(其他_异常代码.数据不存在, f"未找到要删除的应用: {application_id}")
        return True
    except Exception as e:
        await db.rollback()
        raise HTTPException_AppToolsSZXW(其他_异常代码.删除数据失败, f"删除应用失败: {str(e)}")


async def list_applications(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        include_products: bool = False) -> List[PYD_ApplicationResponse]:
    query = select(Application)
    if include_products:
        query = query.options(joinedload(Application.products))
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    applications = result.unique().scalars().all()

    application_responses = []
    for application in applications:
        application_dict = {
            "id": application.id,
            "name": application.name,
        }

        if include_products and application.products:
            application_dict["products"] = [
                PYD_ProductResponse(
                    id=product.id,
                    name=product.name,
                    app_name=application.name,
                    price=product.price
                ) for product in application.products
            ]

        application_responses.append(PYD_ApplicationResponse(**application_dict))

    return application_responses
