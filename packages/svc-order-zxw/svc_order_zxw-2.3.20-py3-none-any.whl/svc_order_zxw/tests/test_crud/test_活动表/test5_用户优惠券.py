import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from svc_order_zxw.db.models_活动表 import Base, Model用户, Model优惠券, Model用户优惠券
from svc_order_zxw.db.crud活动表5_用户优惠券 import (
    create_用户优惠券, get_用户优惠券, update_用户优惠券, delete_用户优惠券, list_用户优惠券,
    PYD_用户优惠券Response, PYD_用户优惠券DetailResponse
)
from datetime import datetime, timedelta
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW
import random

# 使用 SQLite 本地文件作为测试数据库
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_database_user_coupons.db"


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    yield engine
    asyncio.run(engine.dispose())


@pytest.fixture(scope="module")
def session_factory(engine):
    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_db())

    yield sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def drop_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    asyncio.run(drop_db())


@pytest.fixture
def db_session(session_factory):
    session = session_factory()
    yield session
    asyncio.run(session.close())


@pytest.fixture
def sample_data(db_session):
    async def create_sample_data():
        user = Model用户()
        coupon_code = f"TEST{random.randint(1, 1000000):06d}"  # 生成随机唯一优惠券代码
        coupon = Model优惠券(code=coupon_code, discount_value=10.0,
                             expiration_date=datetime.now() + timedelta(days=30))
        db_session.add(user)
        db_session.add(coupon)
        await db_session.commit()
        await db_session.refresh(coupon)
        await db_session.refresh(user)
        return user, coupon

    return asyncio.run(create_sample_data())


def test_创建用户优惠券(db_session, sample_data):
    user, coupon = sample_data

    async def create_test_user_coupon():
        return await create_用户优惠券(db_session, user.id, coupon.id)

    result = asyncio.run(create_test_user_coupon())
    assert isinstance(result, PYD_用户优惠券Response)
    assert result.user_id == user.id
    assert result.coupon_id == coupon.id
    assert result.is_used == False


def test_获取用户优惠券(db_session, sample_data):
    user, coupon = sample_data

    async def get_test_user_coupon():
        user_coupon = await create_用户优惠券(db_session, user.id, coupon.id)
        return await get_用户优惠券(db_session, user_coupon.id, include_user=True, include_coupon=True)

    result = asyncio.run(get_test_user_coupon())
    assert isinstance(result, PYD_用户优惠券DetailResponse)
    assert result.user_id == user.id
    assert result.coupon_id == coupon.id
    assert result.user is not None
    assert result.coupon is not None


def test_获取用户优惠券_不包含用户和优惠券(db_session, sample_data):
    user, coupon = sample_data

    async def get_test_user_coupon():
        user_coupon = await create_用户优惠券(db_session, user.id, coupon.id)
        return await get_用户优惠券(db_session, user_coupon.id, include_user=False, include_coupon=False)

    result = asyncio.run(get_test_user_coupon())
    assert isinstance(result, PYD_用户优惠券DetailResponse)
    assert result.user_id == user.id
    assert result.coupon_id == coupon.id
    assert result.user is None
    assert result.coupon is None


def test_获取用户优惠券_仅包含用户(db_session, sample_data):
    user, coupon = sample_data

    async def get_test_user_coupon():
        user_coupon = await create_用户优惠券(db_session, user.id, coupon.id)
        return await get_用户优惠券(db_session, user_coupon.id, include_user=True, include_coupon=False)

    result = asyncio.run(get_test_user_coupon())
    assert isinstance(result, PYD_用户优惠券DetailResponse)
    assert result.user_id == user.id
    assert result.coupon_id == coupon.id
    assert result.user is not None
    assert result.coupon is None


def test_获取用户优惠券_仅包含优惠券(db_session, sample_data):
    user, coupon = sample_data

    async def get_test_user_coupon():
        user_coupon = await create_用户优惠券(db_session, user.id, coupon.id)
        return await get_用户优惠券(db_session, user_coupon.id, include_user=False, include_coupon=True)

    result = asyncio.run(get_test_user_coupon())
    assert isinstance(result, PYD_用户优惠券DetailResponse)
    assert result.user_id == user.id
    assert result.coupon_id == coupon.id
    assert result.user is None
    assert result.coupon is not None


def test_更新用户优惠券(db_session, sample_data):
    user, coupon = sample_data

    async def update_test_user_coupon():
        user_coupon = await create_用户优惠券(db_session, user.id, coupon.id)
        return await update_用户优惠券(db_session, user_coupon.id, is_used=True)

    result = asyncio.run(update_test_user_coupon())
    assert isinstance(result, PYD_用户优惠券Response)
    assert result.is_used == True


def test_删除用户优惠券(db_session, sample_data):
    user, coupon = sample_data

    async def delete_test_user_coupon():
        user_coupon = await create_用户优惠券(db_session, user.id, coupon.id)
        return await delete_用户优惠券(db_session, user_coupon.id)

    result = asyncio.run(delete_test_user_coupon())
    assert result == True


def test_列出用户优惠券(db_session, sample_data):
    user, coupon = sample_data

    async def list_test_user_coupons():
        await create_用户优惠券(db_session, user.id, coupon.id)
        await create_用户优惠券(db_session, user.id, coupon.id)
        return await list_用户优惠券(db_session, user_id=user.id)

    results = asyncio.run(list_test_user_coupons())
    assert len(results) == 2
    for result in results:
        assert isinstance(result, PYD_用户优惠券Response)
        assert result.user_id == user.id


def test_列出用户优惠券_带用户ID(db_session, sample_data):
    user, coupon = sample_data

    async def list_test_user_coupons():
        await create_用户优惠券(db_session, user.id, coupon.id)
        await create_用户优惠券(db_session, user.id, coupon.id)
        return await list_用户优惠券(db_session, user_id=user.id)

    results = asyncio.run(list_test_user_coupons())
    assert len(results) == 2
    for result in results:
        assert isinstance(result, PYD_用户优惠券Response)
        assert result.user_id == user.id


def test_列出用户优惠券_不带用户ID(db_session, sample_data):
    user, coupon = sample_data

    async def list_test_user_coupons():
        await create_用户优惠券(db_session, user.id, coupon.id)
        await create_用户优惠券(db_session, user.id, coupon.id)
        return await list_用户优惠券(db_session)

    results = asyncio.run(list_test_user_coupons())
    assert len(results) >= 2
    for result in results:
        assert isinstance(result, PYD_用户优惠券Response)


def test_创建用户优惠券_用户不存在(db_session):
    async def create_test_user_coupon_invalid_user():
        with pytest.raises(HTTPException_AppToolsSZXW):
            await create_用户优惠券(db_session, 999, 1)

    asyncio.run(create_test_user_coupon_invalid_user())


def test_创建用户优惠券_优惠券不存在(db_session, sample_data):
    user, _ = sample_data

    async def create_test_user_coupon_invalid_coupon():
        with pytest.raises(HTTPException_AppToolsSZXW):
            await create_用户优惠券(db_session, user.id, 999)

    asyncio.run(create_test_user_coupon_invalid_coupon())


def test_获取不存在的用户优惠券(db_session):
    async def get_nonexistent_user_coupon():
        result = await get_用户优惠券(db_session, 999)
        assert result is None

    asyncio.run(get_nonexistent_user_coupon())


def test_更新不存在的用户优惠券(db_session):
    async def update_nonexistent_user_coupon():
        with pytest.raises(HTTPException_AppToolsSZXW):
            await update_用户优惠券(db_session, 999, is_used=True)

    asyncio.run(update_nonexistent_user_coupon())


def test_删除不存在的用户优惠券(db_session):
    async def delete_nonexistent_user_coupon():
        result = await delete_用户优惠券(db_session, 999)
        assert result == False

    asyncio.run(delete_nonexistent_user_coupon())
