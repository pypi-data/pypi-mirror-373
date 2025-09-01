"""
# File       : models_活动表.py
# Time       ：2024/10/11 上午7:16
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：

1. 实体：
   - 用户 (Model用户)
   - 支付转换权限 (Model支付转换权限)
   - 促销活动 (Model促销活动)
   - 优惠券 (Model优惠券)
   - 用户优惠券 (Model用户优惠券)
   - 产品 (Product)
   - 订单 (Order)

2. 关系：
   - 用户 1:N 支付转换权限
   - 用户 1:N 用户优惠券
   - 支付转换权限 N:1 订单
   - 促销活动 1:N 优惠券
   - 促销活动 N:1 产品
   - 优惠券 1:N 用户优惠券
   - 产品 1:N 促销活动

3. 属性：
   对于每个实体，包含其主要属性：
   - 用户：id, external_user_id, created_at, updated_at
   - 支付转换权限：id, isCharged, created_at, updated_at, amount
   - 促销活动：id, name, threshold, discount_type, discount_value, start_date, end_date, is_active
   - 优惠券：id, code, discount_value, expiration_date
   - 用户优惠券：id, is_used
   - 产品：id (假设)
   - 订单：order_number (假设)

"""
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, DateTime, Float, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from svc_order_zxw.db.get_db import Base
from sqlalchemy.sql import func
from svc_order_zxw.db.models import Product, Order
from enum import Enum


class DiscountTypeEnum(str, Enum):
    AMOUNT = '金额'
    DISCOUNT = '折扣'
    COUPON = '优惠券'


class Model用户(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, comment="外部服务的用户ID")

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    支付转换权限 = relationship("Model支付转换权限", back_populates="user")
    用户优惠券 = relationship("Model用户优惠券", back_populates="user")


class Model支付转换权限(Base):
    __tablename__ = 'payment_conversion_permissions'

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    isCharged = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("Model用户", back_populates="支付转换权限")
    order_number = Column(String, ForeignKey('orders.order_number'))  # 确认 'orders' 表名和 'order_number' 字段
    order = relationship("Order", back_populates="支付转换权限")  # 修改 "支付转换权限"


class Model促销活动(Base):
    __tablename__ = 'promotions'  # promotion

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    threshold = Column(Float, comment="触发阈值")
    discount_type = Column(SQLAlchemyEnum(DiscountTypeEnum), nullable=False)
    discount_value = Column(Float, comment="优惠值")

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)

    coupons = relationship("Model优惠券", back_populates="promotion")
    product_id = Column(Integer, ForeignKey('products.id'))  # 确认 'products' 表名和 'id' 字段
    product = relationship("Product", back_populates="促销活动")


class Model优惠券(Base):
    __tablename__ = 'coupons'

    id = Column(Integer, primary_key=True, index=True)

    code = Column(String, unique=True, index=True)
    discount_value = Column(Float, nullable=False)

    expiration_date = Column(Date, nullable=False)

    user_coupons = relationship("Model用户优惠券", back_populates="coupon")

    promotion_id = Column(Integer, ForeignKey('promotions.id'))
    promotion = relationship("Model促销活动", back_populates="coupons")


class Model用户优惠券(Base):
    __tablename__ = 'user_coupons'

    id = Column(Integer, primary_key=True, index=True)
    is_used = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("Model用户", back_populates="用户优惠券")
    coupon_id = Column(Integer, ForeignKey('coupons.id'))
    coupon = relationship("Model优惠券", back_populates="user_coupons")


# 在原有的 models.py 类中添加反向关系
Product.促销活动 = relationship("Model促销活动", back_populates="product")
Order.支付转换权限 = relationship("Model支付转换权限", back_populates="order")  # 修改此处
