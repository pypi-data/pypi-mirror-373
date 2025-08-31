"""
设置测试根目录为 项目根目录
否则报错:找不到pem文件
"""
import asyncio
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from svc_order_zxw.db.models import Base
from svc_order_zxw.db.crud1_applications import (
    create_application,
    get_application,
    update_application,
    delete_application,
    list_applications,
    PYD_ApplicationCreate,
    PYD_ApplicationUpdate,
)

# 使用 SQLite 本地文件作为测试数据库
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_applications_database.db"


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


def test_create_application(db_session):
    app_create = PYD_ApplicationCreate(name="测试应用")
    created_app = asyncio.run(create_application(db_session, app_create))
    assert created_app.name == "测试应用"
    assert created_app.id is not None


def test_get_application(db_session):
    app_create = PYD_ApplicationCreate(name="获取测试应用")
    created_app = asyncio.run(create_application(db_session, app_create))

    retrieved_app = asyncio.run(get_application(db_session, created_app.id))
    assert retrieved_app.id == created_app.id
    assert retrieved_app.name == "获取测试应用"


def test_update_application(db_session):
    app_create = PYD_ApplicationCreate(name="更新前应用")
    created_app = asyncio.run(create_application(db_session, app_create))

    app_update = PYD_ApplicationUpdate(name="更新后应用")
    updated_app = asyncio.run(update_application(db_session, created_app.id, app_update))
    assert updated_app.id == created_app.id
    assert updated_app.name == "更新后应用"


def test_delete_application(db_session):
    app_create = PYD_ApplicationCreate(name="待删除应用")
    created_app = asyncio.run(create_application(db_session, app_create))

    delete_result = asyncio.run(delete_application(db_session, created_app.id))
    assert delete_result is True

    with pytest.raises(Exception):  # 假设删除不存在的应用会抛出异常
        asyncio.run(delete_application(db_session, created_app.id))


def test_list_applications(db_session):
    # 创建多个应用
    app_names = ["列表应用1", "列表应用2", "列表应用3"]
    for name in app_names:
        asyncio.run(create_application(db_session, PYD_ApplicationCreate(name=name)))

    # 获取应用列表
    applications = asyncio.run(list_applications(db_session))
    assert len(applications) >= len(app_names)
    assert all(app.name in app_names for app in applications[-len(app_names):])
