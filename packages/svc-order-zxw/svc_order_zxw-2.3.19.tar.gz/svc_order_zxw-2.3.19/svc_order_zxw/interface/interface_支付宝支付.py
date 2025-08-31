"""
# File       : interface_支付宝支付.py
# Time       ：2024/8/29 上午10:47
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable, Awaitable
from svc_order_zxw.apis.api_支付_支付宝.api_app与url方式 import (
    请求_支付宝url_创建订单,
    返回_支付宝url_订单信息,
    请求_支付宝url_发起支付,
    返回_支付宝url_支付信息,
    创建订单,
    发起支付,
    查询支付状态,
    支付宝_注册支付回调
)
from app_tools_zxw.SDK_支付宝.支付服务_async import PaymentResult


class 支付宝支付:

    @staticmethod
    async def 创建订单(
            db: AsyncSession,
            user_id: str,
            product_id: int, payment_price: float,
            quantity: int = 1) -> 返回_支付宝url_订单信息:
        payload = 请求_支付宝url_创建订单(
            user_id=user_id,
            product_id=product_id,
            payment_price=payment_price,
            quantity=quantity
        )

        return await 创建订单(payload, db)

    @staticmethod
    async def 发起支付(
            db: AsyncSession,
            order_number: str,
            callback_url: str) -> 返回_支付宝url_支付信息:
        payload = 请求_支付宝url_发起支付(
            order_number=order_number,
            callback_url=callback_url
        )
        return await 发起支付(payload, db)

    @staticmethod
    async def 查询支付状态(db: AsyncSession, order_number: str) -> 返回_支付宝url_支付信息:
        return await 查询支付状态(order_number, db)

    @staticmethod
    def 注册回调函数(回调func_支付成功: Callable[[PaymentResult], Awaitable[None]]):
        """
        注册回调函数
        回调func_支付成功: 回调函数在判断支付成功后执行的外部函数，参数为PaymentResult对象，返回值为None.
        """
        支付宝_注册支付回调(回调func_支付成功)
