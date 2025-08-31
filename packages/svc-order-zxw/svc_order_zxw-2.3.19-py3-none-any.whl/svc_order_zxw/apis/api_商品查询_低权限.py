from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from svc_order_zxw.db.crud2_products import get_products, get_product_by_apple_id
from svc_order_zxw.db import get_db

router = APIRouter(prefix="/products", tags=["商品查询_低权限"])


# 获取所有产品
async def i_get_products(
        app_name: str,
        is_apple_product: bool,
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db)):
    return await get_products(db, app_name=app_name, is_apple_product=is_apple_product, skip=skip, limit=limit)


# 根据苹果产品ID查询商品
async def i_get_product_by_apple_id(
        apple_product_id: str,
        db: AsyncSession = Depends(get_db)):
    """根据苹果产品ID查询商品"""
    return await get_product_by_apple_id(db, apple_product_id)


router.add_api_route("/get_all_products", i_get_products, methods=["GET"])
router.add_api_route("/get_by_apple_id", i_get_product_by_apple_id, methods=["GET"])
