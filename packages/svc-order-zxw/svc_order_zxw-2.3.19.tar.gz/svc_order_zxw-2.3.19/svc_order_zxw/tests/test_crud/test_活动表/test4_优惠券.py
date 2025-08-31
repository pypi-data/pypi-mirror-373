"""
# File       : test4_优惠券.py
# Time       ：2024/10/11 下午2:40
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from svc_order_zxw.db.models_活动表 import Base, Model优惠券, Model促销活动
from svc_order_zxw.db.crud活动表4_优惠券 import (
    create_coupon, get_coupon, update_coupon, delete_coupon, list_coupons,
    PYD_优惠券Response, PYD_优惠券Filter
)
from datetime import date, timedelta
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW
from svc_order_zxw.异常代码 import 优惠券_异常代码

# 使用 SQLite 本地文件作为测试数据库
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_database_coupons.db"


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
def sample_promotion(db_session):
    async def _test_():
        promotion = Model促销活动(name="测试促销活动", threshold=100.0, discount_type="金额", discount_value=10.0,
                                  start_date=date.today(), end_date=date.today() + timedelta(days=7), is_active=True)
        db_session.add(promotion)
        await db_session.commit()
        await db_session.refresh(promotion)
        return promotion

    return asyncio.run(_test_())


def test_创建优惠券(db_session, sample_promotion):
    async def create_test_coupon():
        coupon = await create_coupon(
            db_session,
            code="TEST001",
            discount_value=50.0,
            expiration_date=date.today() + timedelta(days=30),
            promotion_id=sample_promotion.id
        )
        return coupon

    result = asyncio.run(create_test_coupon())
    assert isinstance(result, PYD_优惠券Response)
    assert result.code == "TEST001"
    assert result.discount_value == 50.0


def test_获取优惠券(db_session):
    async def get_test_coupon():
        coupon = await get_coupon(db_session, coupon_id=1, include_promotion=True)
        return coupon

    result = asyncio.run(get_test_coupon())
    assert isinstance(result, PYD_优惠券Response)
    assert result.id == 1
    assert result.promotion is not None


def test_获取优惠券_不包含促销活动(db_session):
    async def get_test_coupon():
        coupon = await get_coupon(db_session, coupon_id=1, include_promotion=False)
        return coupon

    result = asyncio.run(get_test_coupon())
    assert isinstance(result, PYD_优惠券Response)
    assert result.id == 1
    assert result.promotion is None


def test_更新优惠券(db_session):
    async def update_test_coupon():
        updated_coupon = await update_coupon(
            db_session,
            coupon_id=1,
            discount_value=60.0,
            expiration_date=date.today() + timedelta(days=60)
        )
        return updated_coupon

    result = asyncio.run(update_test_coupon())
    assert isinstance(result, PYD_优惠券Response)
    assert result.discount_value == 60.0


def test_删除优惠券(db_session):
    async def delete_test_coupon():
        result = await delete_coupon(db_session, coupon_id=1)
        return result

    assert asyncio.run(delete_test_coupon()) is True


def test_列出优惠券(db_session, sample_promotion):
    async def create_and_list_coupons():
        # 创建多个优惠券
        for i in range(3):
            await create_coupon(
                db_session,
                code=f"TEST{i + 1:03d}",
                discount_value=10.0 * (i + 1),
                expiration_date=date.today() + timedelta(days=30 * (i + 1)),
                promotion_id=sample_promotion.id
            )

        # 列出优惠券
        filter = PYD_优惠券Filter(promotion_id=sample_promotion.id)
        coupons = await list_coupons(db_session, filter, include_promotion=True)
        return coupons

    results = asyncio.run(create_and_list_coupons())
    assert len(results) == 3
    for coupon in results:
        assert isinstance(coupon, PYD_优惠券Response)
        assert coupon.promotion is not None


def test_列出优惠券_不包含促销活动(db_session, sample_promotion):
    async def create_and_list_coupons():
        # 创建多个优惠券
        for i in range(3):
            await create_coupon(
                db_session,
                code=f"TEST{i + 4:03d}",
                discount_value=10.0 * (i + 1),
                expiration_date=date.today() + timedelta(days=30 * (i + 1)),
                promotion_id=sample_promotion.id
            )

        # 列出优惠券，不包含促销活动
        filter = PYD_优惠券Filter(promotion_id=sample_promotion.id)
        coupons = await list_coupons(db_session, filter, include_promotion=False)
        return coupons

    results = asyncio.run(create_and_list_coupons())
    assert len(results) == 3
    for coupon in results:
        assert isinstance(coupon, PYD_优惠券Response)
        assert coupon.promotion is None


def test_获取不存在的优惠券(db_session):
    async def get_nonexistent_coupon():
        coupon = await get_coupon(db_session, coupon_id=9999, include_promotion=True)
        return coupon

    result = asyncio.run(get_nonexistent_coupon())
    assert result is None


def test_更新不存在的优惠券(db_session):
    async def update_nonexistent_coupon():
        try:
            await update_coupon(
                db_session,
                coupon_id=9999,
                discount_value=100.0
            )
        except HTTPException_AppToolsSZXW as e:
            return e

    result = asyncio.run(update_nonexistent_coupon())
    assert isinstance(result, HTTPException_AppToolsSZXW)
    print("result = ", result)
    # assert result.detail["error_code"] == 优惠券_异常代码.优惠券不存在


def test_删除不存在的优惠券(db_session):
    async def delete_nonexistent_coupon():
        try:
            await delete_coupon(db_session, coupon_id=9999)
        except HTTPException_AppToolsSZXW as e:
            return e

    result = asyncio.run(delete_nonexistent_coupon())
    assert isinstance(result, HTTPException_AppToolsSZXW)
    # assert result.detail["error_code"] == 优惠券_异常代码.优惠券不存在


def test_列出优惠券_过滤条件(db_session, sample_promotion):
    async def create_and_list_coupons():
        # 创建多个优惠券
        for i in range(5):
            await create_coupon(
                db_session,
                code=f"TEST{i + 7:03d}",
                discount_value=10.0 * (i + 1),
                expiration_date=date.today() + timedelta(days=30 * (i + 1)),
                promotion_id=sample_promotion.id
            )

        # 使用过滤条件列出优惠券
        filter = PYD_优惠券Filter(
            promotion_id=sample_promotion.id,
            expiration_date_before=date.today() + timedelta(days=60),
            expiration_date_after=date.today()
        )
        coupons = await list_coupons(db_session, filter, include_promotion=True)
        return coupons

    results = asyncio.run(create_and_list_coupons())
    assert len(results) == 2  # 只有两个优惠券满足过滤条件
    for coupon in results:
        assert isinstance(coupon, PYD_优惠券Response)
        assert coupon.promotion is not None
        assert coupon.expiration_date > date.today()
        assert coupon.expiration_date <= date.today() + timedelta(days=60)
