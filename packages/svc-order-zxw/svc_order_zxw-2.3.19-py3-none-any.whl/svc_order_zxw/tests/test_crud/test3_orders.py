import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from svc_order_zxw.db.models import Base, Product, Application, Order, Payment
from svc_order_zxw.db.crud3_orders import (
    create_order,
    get_order,
    update_order,
    delete_order,
    list_orders,
    PYD_OrderCreate,
    PYD_OrderUpdate,
    PYD_OrderFilter
)
from svc_order_zxw.apis.schemas_payments import OrderStatus, PaymentMethod
import uuid

# 使用 SQLite 本地文件作为测试数据库
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_database_orders.db"


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
async def sample_data(db_session):
    # 获取当前最大的应用 ID
    result = await db_session.execute(text("SELECT MAX(id) FROM applications"))
    max_id = result.scalar() or 0

    app_name = f"测试应用_{max_id + 1}"
    app = Application(name=app_name)
    db_session.add(app)
    await db_session.commit()

    product = Product(name="测试产品", price=100.0, app_id=app.id)
    db_session.add(product)
    await db_session.commit()

    return app, product


def generate_unique_order_number():
    return f"ORDER-{uuid.uuid4().hex[:8].upper()}"


def test_create_order(db_session, sample_data):
    _, product = asyncio.run(sample_data)
    order_create = PYD_OrderCreate(
        user_id="test_user",
        total_price=100.0,
        quantity=1,
        order_number=generate_unique_order_number(),
        product_id=product.id
    )

    order = asyncio.run(create_order(db_session, order_create))

    assert order.user_id == "test_user"
    assert order.total_price == 100.0
    assert order.quantity == 1
    assert order.order_number.startswith("ORDER-")
    assert order.product_id == product.id


def test_get_order(db_session):
    order = asyncio.run(get_order(db_session, 1))

    assert order is not None
    assert order.id == 1
    assert order.user_id == "test_user"


def test_update_order(db_session):
    order_update = PYD_OrderUpdate(total_price=150.0, quantity=2)
    updated_order = asyncio.run(update_order(db_session, 1, order_update))

    assert updated_order.total_price == 150.0
    assert updated_order.quantity == 2


def test_list_orders(db_session):
    filter = PYD_OrderFilter(user_id="test_user")
    orders = asyncio.run(list_orders(db_session, filter))

    assert len(orders) > 0
    assert orders[0].user_id == "test_user"


def test_delete_order(db_session):
    result = asyncio.run(delete_order(db_session, 1))
    assert result is True

    with pytest.raises(Exception):
        asyncio.run(delete_order(db_session, 1))


def test_create_order_with_relations(db_session, sample_data):
    _, product = asyncio.run(sample_data)
    order_create = PYD_OrderCreate(
        user_id="test_user",
        total_price=100.0,
        quantity=1,
        order_number=generate_unique_order_number(),
        product_id=product.id
    )

    order = asyncio.run(create_order(db_session, order_create, include_product=True, include_application=True))

    assert order.user_id == "test_user"
    assert order.total_price == 100.0
    assert order.quantity == 1
    assert order.order_number.startswith("ORDER-")
    assert order.product_id == product.id
    assert order.product is not None
    assert order.product.name == "测试产品"
    assert order.application is not None
    assert order.application.name[:4] == "测试应用"


def test_get_order_with_relations(db_session):
    order = asyncio.run(get_order(db_session,
                                  1,
                                  include_product=True,
                                  include_application=True,
                                  include_payment=True))

    assert order is not None
    assert order.id == 1
    assert order.user_id == "test_user"
    assert order.product is not None
    assert order.product.name == "测试产品"
    assert order.application is not None
    assert order.application.name[:4] == "测试应用"
    assert order.payment is None  # 因为我们还没有创建支付信息


def test_list_orders_with_relations(db_session):
    filter = PYD_OrderFilter(user_id="test_user")
    orders = asyncio.run(list_orders(db_session, filter, include_product=True, include_application=True))

    assert len(orders) > 0
    assert orders[0].user_id == "test_user"
    assert orders[0].product is not None
    assert orders[0].product.name == "测试产品"
    assert orders[0].application is not None
    assert orders[0].application.name[:4] == "测试应用"


def test_list_orders_with_include_application(db_session):
    filter = PYD_OrderFilter(user_id="test_user")
    orders = asyncio.run(list_orders(db_session,
                                     filter,
                                     include_application=True))

    assert len(orders) > 0
    assert orders[0].user_id == "test_user"
    assert orders[0].product is None
    assert orders[0].application is not None
    assert orders[0].application.name[:4] == "测试应用"
