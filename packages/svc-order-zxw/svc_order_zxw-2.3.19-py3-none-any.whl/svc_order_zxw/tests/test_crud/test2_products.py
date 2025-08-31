import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from svc_order_zxw.db.models import Base, Application
from svc_order_zxw.db.crud2_products import (
    create_product, get_product, get_products, update_product, delete_product,
    PYD_ProductCreate, PYD_ProductUpdate
)

import uuid

# 使用 SQLite 本地文件作为测试数据库
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_database_products.db"


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


@pytest.fixture(scope="function")
async def create_test_application(db_session):
    async with db_session as session:
        app = Application(name=f"测试应用_{uuid.uuid4().hex[:8]}")
        session.add(app)
        await session.commit()
        await session.refresh(app)
        return app


def test_create_product(db_session, create_test_application):
    app = asyncio.run(create_test_application)
    product_data = PYD_ProductCreate(name="测试产品", app_id=app.id, price=99.99)

    async def create_test_product():
        async with db_session as session:
            return await create_product(session, product_data)

    result = asyncio.run(create_test_product())
    assert result.name == "测试产品"
    assert result.app_name[:4] == "测试应用"
    assert result.price == 99.99


def test_get_product(db_session, create_test_application):
    app = asyncio.run(create_test_application)
    product_data = PYD_ProductCreate(name="获取测试产品", app_id=app.id, price=88.88)

    async def create_and_get_product():
        async with db_session as session:
            created_product = await create_product(session, product_data)
            return await get_product(session, created_product.id)

    result = asyncio.run(create_and_get_product())
    assert result.name == "获取测试产品"
    assert result.app_name[:4] == "测试应用"
    assert result.price == 88.88


def test_get_products(db_session, create_test_application):
    app = asyncio.run(create_test_application)
    product_data1 = PYD_ProductCreate(name="产品1", app_id=app.id, price=10.0)
    product_data2 = PYD_ProductCreate(name="产品2", app_id=app.id, price=20.0)

    async def create_and_get_products():
        async with db_session as session:
            await create_product(session, product_data1)
            await create_product(session, product_data2)
            return await get_products(session)

    results = asyncio.run(create_and_get_products())
    assert len(results) >= 2
    assert any(p.name == "产品1" for p in results)
    assert any(p.name == "产品2" for p in results)


def test_update_product(db_session, create_test_application):
    app = asyncio.run(create_test_application)
    product_data = PYD_ProductCreate(name="更新前产品", app_id=app.id, price=50.0)

    async def create_update_and_get_product():
        async with db_session as session:
            created_product = await create_product(session, product_data)
            update_data = PYD_ProductUpdate(name="更新后产品", price=60.0)
            await update_product(session, created_product.id, update_data)
            return await get_product(session, created_product.id)

    result = asyncio.run(create_update_and_get_product())
    assert result.name == "更新后产品"
    assert result.price == 60.0


def test_delete_product(db_session, create_test_application):
    app = asyncio.run(create_test_application)
    product_data = PYD_ProductCreate(name="待删除产品", app_id=app.id, price=30.0)
    created_product = asyncio.run(create_product(db_session, product_data))

    async def create_delete_and_check_product():
        async with db_session as session:
            await delete_product(session, created_product.id)
            return await get_product(session, created_product.id)

    asyncio.run(create_delete_and_check_product())
    with pytest.raises(Exception):  # 假设删除后获取产品会抛出异常
        asyncio.run(create_delete_and_check_product())
