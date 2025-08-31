"""
# File       : test_用户表.py
# Time       ：2024/10/11 上午10:11
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
import pytest
import pytest_asyncio
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from svc_order_zxw.db.models_活动表 import Base, Model用户, Model支付转换权限, Model用户优惠券
from svc_order_zxw.db.crud活动表1_用户 import (
    create_user, get_user, delete_user, list_users,
    PYD_支付转换权限Response, PYD_用户优惠券Response, PYD_用户Response
)
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW

# 使用 SQLite 本地文件作为测试数据库
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_database_user.db"


@pytest_asyncio.fixture(scope="module")
async def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="module")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="module")
async def session_factory(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(session_factory):
    async with session_factory() as session:
        yield session


async def create_user_with_relations(db_session, user_id):
    user = await create_user(db_session, user_id)

    # 创建关联的支付转换权限
    权限 = Model支付转换权限(user_id=user.id, isCharged=True)
    db_session.add(权限)

    # 创建关联的用户优惠券
    优惠券 = Model用户优惠券(user_id=user.id, is_used=False)
    db_session.add(优惠券)

    await db_session.commit()
    return user


@pytest.mark.asyncio
async def test_get_user_with_relations(db_session):
    user = await create_user_with_relations(db_session, 4)

    # 测试不包含关联数据
    result = await get_user(db_session, user.id)
    assert result.id == user.id
    assert result.支付转换权限 is None
    assert result.用户优惠券 is None

    # 测试包含支付转换权限
    result: PYD_用户Response = await get_user(db_session, user.id, include_支付转换权限=True)
    assert result.id == user.id
    assert len(result.支付转换权限) == 1
    assert result.支付转换权限[0].isCharged == True
    assert result.用户优惠券 is None

    # 测试包含用户优惠券
    result = await get_user(db_session, user.id, include_用户优惠券=True)
    assert result.id == user.id
    assert len(result.用户优惠券) == 1
    assert result.用户优惠券[0].is_used == False
    assert result.支付转换权限 is None

    # 测试同时包含支付转换权限和用户优惠券
    result = await get_user(db_session, user.id, include_支付转换权限=True, include_用户优惠券=True)
    assert result.id == user.id
    assert len(result.支付转换权限) == 1
    assert len(result.用户优惠券) == 1


@pytest.mark.asyncio
async def test_list_users_with_relations(db_session):
    # 创建多个用户及其关联数据
    await create_user_with_relations(db_session, 5)
    await create_user_with_relations(db_session, 6)

    # 测试不包含关联数据
    users = await list_users(db_session)
    assert len(users) >= 2
    assert users[0].支付转换权限 is None
    assert users[0].用户优惠券 is None

    # 测试包含支付转换权限
    users = await list_users(db_session, include_支付转换权限=True)
    assert len(users) >= 2
    assert len(users[0].支付转换权限) == 1
    assert users[0].用户优惠券 is None

    # 测试包含用户优惠券
    users = await list_users(db_session, include_用户优惠券=True)
    assert len(users) >= 2
    assert len(users[0].用户优惠券) == 1
    assert users[0].支付转换权限 is None

    # 测试同时包含支付转换权限和用户优惠券
    users = await list_users(db_session, include_支付转换权限=True, include_用户优惠券=True)
    assert len(users) >= 2
    assert len(users[0].支付转换权限) == 1
    assert len(users[0].用户优惠券) == 1


def test_create_user(db_session):
    user = asyncio.run(create_user(db_session, 1))
    assert user.id == 1


def test_get_user(db_session):
    user = asyncio.run(get_user(db_session, 1))
    assert user.id == 1


def test_delete_user(db_session):
    result = asyncio.run(delete_user(db_session, 1))
    assert result is True


def test_list_users(db_session):
    # 先创建几个用户
    asyncio.run(create_user(db_session, 2))
    asyncio.run(create_user(db_session, 3))

    users = asyncio.run(list_users(db_session))
    assert len(users) == 5


def test_user_not_found(db_session):
    result = asyncio.run(get_user(db_session, 999))
    assert result is None


def test_create_duplicate_user(db_session):
    with pytest.raises(HTTPException_AppToolsSZXW):
        asyncio.run(create_user(db_session, 2))  # 2已经存在


def test_delete_nonexistent_user(db_session):
    with pytest.raises(HTTPException_AppToolsSZXW):
        asyncio.run(delete_user(db_session, 999))
