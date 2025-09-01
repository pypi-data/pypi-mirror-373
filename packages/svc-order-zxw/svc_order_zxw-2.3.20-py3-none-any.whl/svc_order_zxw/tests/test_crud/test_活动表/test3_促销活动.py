import asyncio
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from svc_order_zxw.db.models_活动表 import Base, Model促销活动, Product
from svc_order_zxw.db.crud活动表3_促销活动 import (
    create_promotion, get_promotion, update_promotion, delete_promotion, list_promotions,
    PYD_CreatePromotion, PYD_UpdatePromotion, PYD_PromotionFilter, DiscountType
)
from datetime import date, timedelta

# 使用 SQLite 本地文件作为测试数据库
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_database.db"


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
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
def sample_product(db_session):
    async def sample_product(db_session):
        print("创建测试产品")
        product = Product(name="测试产品", price=0.01, app_id=1)
        db_session.add(product)
        await db_session.commit()
        await db_session.refresh(product)
        return product

    tmp = asyncio.run(sample_product(db_session))
    print("测试产品成功：", tmp)
    return tmp


def test_create_promotion(db_session, sample_product):
    async def _test_():
        promotion_data = PYD_CreatePromotion(
            name="测试促销活动",
            threshold=100.0,
            discount_type=DiscountType.金额,
            discount_value=10.0,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            is_active=True,
            product_id=sample_product.id
        )

        result = await create_promotion(db_session, promotion_data)
        assert result.name == "测试促销活动"
        assert result.threshold == 100.0
        assert result.discount_type == DiscountType.金额
        assert result.discount_value == 10.0

    asyncio.run(_test_())


def test_get_promotion(db_session, sample_product):
    # 创建一个促销活动
    promotion_data = PYD_CreatePromotion(
        name="获取测试促销活动",
        threshold=200.0,
        discount_type=DiscountType.折扣,
        discount_value=0.8,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=14),
        is_active=True,
        product_id=sample_product.id
    )
    created_promotion = asyncio.run(create_promotion(db_session, promotion_data))

    # 获取促销活动
    result = asyncio.run(get_promotion(db_session, created_promotion.id))
    assert result is not None
    assert result.name == "获取测试促销活动"
    assert result.threshold == 200.0
    assert result.discount_type == DiscountType.折扣
    assert result.discount_value == 0.8


def test_get_promotion_with_product(db_session, sample_product):
    async def _test_():
        # 创建一个促销活动
        promotion_data = PYD_CreatePromotion(
            name="获取测试促销活动（含产品）",
            threshold=250.0,
            discount_type=DiscountType.折扣,
            discount_value=0.75,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=14),
            is_active=True,
            product_id=sample_product.id
        )
        created_promotion = await create_promotion(db_session, promotion_data)

        # 获取促销活动（包含产品信息）
        result = await get_promotion(db_session, created_promotion.id, include_product=True)
        assert result is not None
        assert result.name == "获取测试促销活动（含产品）"
        assert result.threshold == 250.0
        assert result.discount_type == DiscountType.折扣
        assert result.discount_value == 0.75
        assert result.product is not None
        assert hasattr(result, 'product')
        assert result.product.id == sample_product.id
        assert result.product.name == sample_product.name

        # 获取促销活动（不包含产品信息）
        result_without_product = await get_promotion(db_session, created_promotion.id, include_product=False)
        assert result_without_product is not None
        assert result_without_product.name == "获取测试促销活动（含产品）"
        print("result_without_product.product = ", result_without_product.product)
        assert result_without_product.product is not None  # 错误

    asyncio.run(_test_())


def test_update_promotion(db_session, sample_product):
    async def _test(db_session, sample_product):
        # 创建一个促销活动
        promotion_data = PYD_CreatePromotion(
            name="更新前促销活动",
            threshold=300.0,
            discount_type=DiscountType.优惠券,
            discount_value=50.0,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=21),
            is_active=True,
            product_id=sample_product.id
        )
        created_promotion = await create_promotion(db_session, promotion_data)

        # 更新促销活动
        update_data = PYD_UpdatePromotion(
            name="更新后促销活动",
            threshold=350.0,
            is_active=False
        )
        updated_promotion = await update_promotion(db_session, created_promotion.id, update_data)

        assert updated_promotion is not None
        assert updated_promotion.name == "更新后促销活动"
        assert updated_promotion.threshold == 350.0
        assert updated_promotion.is_active == False

    asyncio.run(_test(db_session, sample_product))


def test_delete_promotion(db_session, sample_product):
    async def _test_(db_session, sample_product):
        # 创建一个促销活动
        promotion_data = PYD_CreatePromotion(
            name="待删除促销活动",
            threshold=400.0,
            discount_type=DiscountType.金额,
            discount_value=20.0,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=28),
            is_active=True,
            product_id=sample_product.id
        )
        created_promotion = await create_promotion(db_session, promotion_data)

        # 删除促销活动
        result = await delete_promotion(db_session, created_promotion.id)
        assert result == True

        # 确认促销活动已被删除
        deleted_promotion = await get_promotion(db_session, created_promotion.id)
        assert deleted_promotion is None

    asyncio.run(_test_(db_session, sample_product))


def test_list_promotions(db_session, sample_product):
    async def _test_(db_session, sample_product):
        # 创建多个促销活动
        for i in range(5):
            promotion_data = PYD_CreatePromotion(
                name=f"列表测试促销活动{i}",
                threshold=100.0 * (i + 1),
                discount_type=DiscountType.金额,
                discount_value=10.0 * (i + 1),
                start_date=date.today(),
                end_date=date.today() + timedelta(days=7 * (i + 1)),
                is_active=i % 2 == 0,
                product_id=sample_product.id
            )
            await create_promotion(db_session, promotion_data)

        # 测试列表查询
        filter_data = PYD_PromotionFilter(is_active=True)
        promotions = await list_promotions(db_session, filter_data, skip=0, limit=10)

        assert len(promotions) == 6  # 应该有6个活跃的促销活动
        for promotion in promotions:
            assert promotion.is_active == True

    asyncio.run(_test_(db_session, sample_product))


def test_list_promotions_with_product(db_session, sample_product):
    async def _test_():
        # 创建多个促销活动
        for i in range(3):
            promotion_data = PYD_CreatePromotion(
                name=f"列表测试促销活动{i}",
                threshold=100.0 * (i + 1),
                discount_type=DiscountType.金额,
                discount_value=10.0 * (i + 1),
                start_date=date.today(),
                end_date=date.today() + timedelta(days=7 * (i + 1)),
                is_active=True,
                product_id=sample_product.id
            )
            await create_promotion(db_session, promotion_data)

        # 测试列表查询（包含产品信息）
        filter_data = PYD_PromotionFilter(is_active=True)
        promotions_with_product = await list_promotions(db_session, filter_data, skip=0, limit=10, include_product=True)

        assert len(promotions_with_product) == 9
        for promotion in promotions_with_product:
            assert hasattr(promotion, 'product')
            # assert promotion.product.id == sample_product.id
            assert promotion.product.name == sample_product.name

        # 测试列表查询（不包含产品信息）
        promotions_without_product = await list_promotions(db_session, filter_data, skip=0, limit=10,
                                                           include_product=False)

        assert len(promotions_without_product) == 9
        for promotion in promotions_without_product:
            assert hasattr(promotion, 'product')

    asyncio.run(_test_())
