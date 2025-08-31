import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import delete
from svc_order_zxw.db.models_活动表 import Base, Model用户, Model支付转换权限
from svc_order_zxw.db.models import Order
from svc_order_zxw.db.crud活动表2_支付转换权限 import create_支付转换权限, get_支付转换权限, update_支付转换权限, \
    delete_支付转换权限, list_支付转换权限
from svc_order_zxw.异常代码 import 支付转换权限_异常代码, 其他_异常代码, 用户_异常代码, 订单_异常代码
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW

# 使用 SQLite 本地文件作为测试数据库
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_database.db"


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


# 测试创建支付转换权限
def test_create_支付转换权限(db_session):
    async def create_test_data():
        # 创建测试用户
        user = Model用户(id=1)
        db_session.add(user)
        await db_session.commit()

        # 创建测试订单
        order = Order(order_number="TEST001", total_price=100.0, quantity=1)  # 添加 total_price
        db_session.add(order)
        await db_session.commit()

        # 创建支付转换权限
        result = await create_支付转换权限(db_session, user_id=1, isCharged=True, order_number="TEST001")
        return result

    result = asyncio.run(create_test_data())
    assert result.user_id == 1
    assert result.isCharged == True
    assert result.order_number == "TEST001"


# 测试获取支���转换权限
def test_get_支付转换权限(db_session):
    async def get_test_data():
        result = await get_支付转换权限(db_session, 支付转换权限_id=1, include_user=True, include_order=True)
        return result

    result = asyncio.run(get_test_data())
    assert result is not None
    assert result.id == 1
    assert result.user is not None
    assert result.order is not None


# 测试更新支付转换权限
def test_update_支付转换权限(db_session):
    async def update_test_data():
        result = await update_支付转换权限(db_session, 支付转换权限_id=1, isCharged=False)
        return result

    result = asyncio.run(update_test_data())
    assert result.isCharged == False


# 测试删除支付转换权限
def test_delete_支付转换权限(db_session):
    async def delete_test_data():
        result = await delete_支付转换权限(db_session, 支付转换权限_id=1)
        return result

    result = asyncio.run(delete_test_data())
    assert result == True


# 测试列出支付转换权限
def test_list_支付转换权限(db_session):
    async def list_test_data():
        # 检查用户是否已存在，如果不存在则创建
        user = await db_session.get(Model用户, 1)
        if not user:
            user = Model用户(id=1)
            db_session.add(user)
            await db_session.commit()

        # 创建测试订单
        order1 = Order(order_number="TEST002", total_price=100.0, quantity=1)
        order2 = Order(order_number="TEST003", total_price=200.0, quantity=2)
        db_session.add(order1)
        db_session.add(order2)
        await db_session.commit()

        # 创建多个支付转换权限
        await create_支付转换权限(db_session, user_id=1, isCharged=True, order_number="TEST002")
        await create_支付转换权限(db_session, user_id=1, isCharged=False, order_number="TEST003")

        result = await list_支付转换权限(db_session, user_id=1)
        return result

    result = asyncio.run(list_test_data())
    assert len(result) == 2


# 测试异常情况
def test_create_支付转换权限_user_not_exist(db_session):
    async def create_test_data():
        with pytest.raises(HTTPException_AppToolsSZXW) as exc_info:
            await create_支付转换权限(db_session, user_id=999, isCharged=True)
        return exc_info

    exc_info = asyncio.run(create_test_data())
    assert exc_info.value.detail["error_code"] == 用户_异常代码.用户不存在


def test_create_支付转换权限_order_not_exist(db_session):
    async def create_test_data():
        with pytest.raises(HTTPException_AppToolsSZXW) as exc_info:
            await create_支付转换权限(db_session, user_id=1, isCharged=True, order_number="NONEXISTENT")
        return exc_info

    exc_info = asyncio.run(create_test_data())
    assert exc_info.value.detail["error_code"] == 订单_异常代码.订单号不存在


# 测试获取支付转换权限 - 不包含用户和订单信息
def test_get_支付转换权限_no_includes(db_session):
    async def get_test_data():
        result = await get_支付转换权限(db_session, 支付转换权限_id=1)
        return result

    result = asyncio.run(get_test_data())
    print(result)
    assert result is not None
    assert result.id == 1
    assert result.user is None
    assert result.order is None


# 测试获取支付转换权限 - 仅包含用户信息
def test_get_支付转换权限_include_user_only(db_session):
    async def get_test_data():
        result = await get_支付转换权限(db_session, 支付转换权限_id=1, include_user=True)
        return result

    result = asyncio.run(get_test_data())
    assert result is not None
    assert result.id == 1
    assert result.user is not None
    assert result.order is None


# 测试获取支付转换权限 - 仅包含订单信息
def test_get_支付转换权限_include_order_only(db_session):
    async def get_test_data():
        result = await get_支付转换权限(db_session, 支付转换权限_id=1, include_order=True)
        return result

    result = asyncio.run(get_test_data())
    assert result is not None
    assert result.id == 1
    assert result.user is None
    assert result.order is not None


# 测试获取不存在的支付转换权限
def test_get_nonexistent_支付转换权限(db_session):
    async def get_test_data():
        result = await get_支付转换权限(db_session, 支付转换权限_id=9999)
        return result

    result = asyncio.run(get_test_data())
    assert result is None


# 测试更新支付转换权限 - 更新isCharged
def test_update_支付转换权限_isCharged(db_session):
    async def update_test_data():
        result = await update_支付转换权限(db_session, 支付转换权限_id=1, isCharged=False)
        return result

    result = asyncio.run(update_test_data())
    assert result.isCharged == False


# 测试更新支付转换权限 - 更新order_number
def test_update_支付转换权限_order_number(db_session):
    async def update_test_data():
        # 首先创建一个新的订单
        new_order = Order(order_number="TEST004", total_price=300.0, quantity=3)
        db_session.add(new_order)
        await db_session.commit()

        result = await update_支付转换权限(db_session, 支付转换权限_id=1, order_number="TEST004")
        return result

    result = asyncio.run(update_test_data())
    assert result.order_number == "TEST004"


# 测试更新不存在的支付转换权限
def test_update_nonexistent_支付转换权限(db_session):
    async def update_test_data():
        with pytest.raises(HTTPException_AppToolsSZXW) as exc_info:
            await update_支付转换权限(db_session, 支付转换权限_id=9999, isCharged=True)
        return exc_info

    exc_info = asyncio.run(update_test_data())
    assert exc_info.value.detail["error_code"] == 支付转换权限_异常代码.支付转换权限不存在


# 测试更新支付转换权限 - 使用不存在的订单号
def test_update_支付转换权限_nonexistent_order(db_session):
    async def update_test_data():
        with pytest.raises(HTTPException_AppToolsSZXW) as exc_info:
            await update_支付转换权限(db_session, 支付转换权限_id=1, order_number="NONEXISTENT")
        return exc_info

    exc_info = asyncio.run(update_test_data())
    assert exc_info.value.detail["error_code"] == 订单_异常代码.订单号不存在


# 测试删除不存在的支付转换权限
def test_delete_nonexistent_支付转换权限(db_session):
    async def delete_test_data():
        with pytest.raises(HTTPException_AppToolsSZXW) as exc_info:
            await delete_支付转换权限(db_session, 支付转换权限_id=9999)
        return exc_info

    exc_info = asyncio.run(delete_test_data())
    assert exc_info.value.detail["error_code"] == 支付转换权限_异常代码.支付转换权限不存在


# 测试列出支付转换权限 - 空列表
def test_list_empty_支付转换权限(db_session):
    async def list_test_data():
        # 首先删除所有现有的支付转换权限
        await db_session.execute(delete(Model支付转换权限))
        await db_session.commit()

        result = await list_支付转换权限(db_session, user_id=1)
        return result

    result = asyncio.run(list_test_data())
    assert len(result) == 0
