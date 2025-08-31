import pytest
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from svc_order_zxw.db.models import Base, Payment, Order, Product, Application
from svc_order_zxw.db.crud4_payments import (
    create_payment, get_payment, update_payment, delete_payment, list_payments
)
from svc_order_zxw.apis.schemas_payments import OrderStatus, PaymentMethod
from svc_order_zxw.db.crud4_payments import PYD_PaymentCreate, PYD_PaymentUpdate

# 使用 SQLite 本地文件作为测试数据库
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_database_payments.db"


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


import uuid


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

    random_order_number = str(uuid.uuid4())[:8]  # 使用UUID的前8个字符作为随机订单号
    order = Order(order_number=random_order_number,
                  user_id="user1",
                  total_price=100.0,
                  quantity=1,
                  product_id=product.id)
    db_session.add(order)
    await db_session.commit()

    return app, product, order


def test_create_payment(db_session, sample_data):
    _, _, order = asyncio.run(sample_data)
    payment_create = PYD_PaymentCreate(
        payment_method=PaymentMethod.ALIPAY_QR,
        payment_price=100.0,
        payment_status=OrderStatus.PENDING,
        order_id=order.id
    )

    payment = asyncio.run(create_payment(db_session, payment_create))

    assert payment.id is not None
    assert payment.payment_method == PaymentMethod.ALIPAY_QR
    assert payment.payment_price == 100.0
    assert payment.payment_status == OrderStatus.PENDING
    assert payment.order_id == order.id


def test_get_payment(db_session):
    payment = asyncio.run(get_payment(db_session, payment_id=1, include_order=True))

    assert payment is not None
    assert payment.id == 1
    assert payment.order is not None


def test_update_payment(db_session):
    payment_update = PYD_PaymentUpdate(payment_status=OrderStatus.PAID)
    updated_payment = asyncio.run(update_payment(db_session, payment_id=1, payment_update=payment_update))

    assert updated_payment is not None
    assert updated_payment.payment_status == OrderStatus.PAID


def test_delete_payment(db_session):
    result = asyncio.run(delete_payment(db_session, payment_id=1))
    assert result is True


def test_list_payments(db_session):
    payments = asyncio.run(list_payments(db_session, include_order=True))
    assert len(payments) == 0  # 因为我们刚刚删除了唯一的支付记录


def test_create_payment_with_order(db_session, sample_data):
    _, _, order = asyncio.run(sample_data)
    payment_create = PYD_PaymentCreate(
        payment_method=PaymentMethod.ALIPAY_QR,
        payment_price=100.0,
        payment_status=OrderStatus.PENDING,
        order_id=order.id
    )

    payment = asyncio.run(create_payment(db_session, payment_create, include_order=True))

    assert payment.id is not None
    assert payment.payment_method == PaymentMethod.ALIPAY_QR
    assert payment.payment_price == 100.0
    assert payment.payment_status == OrderStatus.PENDING
    assert payment.order_id == order.id
    assert payment.order is not None
    assert payment.order.id == order.id
    assert payment.order.order_number == order.order_number


def test_get_payment_by_order_number(db_session, sample_data):
    _, _, order = asyncio.run(sample_data)

    # 首先创建一个支付记录
    payment_create = PYD_PaymentCreate(
        payment_method=PaymentMethod.ALIPAY_QR,
        payment_price=100.0,
        payment_status=OrderStatus.PENDING,
        order_id=order.id
    )
    created_payment = asyncio.run(create_payment(db_session, payment_create))

    # 然后尝试获取这个支付记录
    payment = asyncio.run(get_payment(db_session, order_number=order.order_number, include_order=True))

    assert payment is not None
    assert payment.order is not None
    assert payment.order.order_number == order.order_number
    assert payment.product is not None
    assert payment.application is not None


def test_list_payments_with_order(db_session):
    payments = asyncio.run(list_payments(db_session, include_order=True))
    assert len(payments) > 0
    for payment in payments:
        assert payment.order is not None
        assert payment.product is not None
        assert payment.application is not None
