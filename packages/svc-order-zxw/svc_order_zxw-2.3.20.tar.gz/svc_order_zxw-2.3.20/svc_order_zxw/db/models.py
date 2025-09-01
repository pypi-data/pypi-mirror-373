from sqlalchemy import Column, String, Integer, Float, ForeignKey, Enum, DateTime, func, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from svc_order_zxw.apis.schemas_payments import OrderStatus, PaymentMethod
from svc_order_zxw.db.get_db import Base
import enum


class ProductType(str, enum.Enum):
    """商品类型枚举"""
    CONSUMABLE = "consumable"              # 消耗型商品
    NON_CONSUMABLE = "non_consumable"      # 非消耗型商品
    AUTO_RENEWABLE = "auto_renewable"      # 自动续费订阅
    NON_RENEWABLE = "non_renewable"        # 非续费订阅


class Application(Base):
    """应用表"""
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)

    products = relationship("Product", back_populates="app")


class Product(Base):
    """产品表"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)

    # 苹果内购特有字段
    apple_product_id = Column(JSON, nullable=True, comment="苹果商店产品ID列表，如['com.yourapp.product1', 'com.yourapp.product2']")
    product_type = Column(Enum(ProductType), nullable=True, comment="商品类型：消耗型、非消耗型、订阅型等")
    subscription_duration = Column(String, nullable=True, comment="订阅周期，如'1 month', '1 year'等，仅订阅型商品使用")

    app_id = Column(Integer, ForeignKey("applications.id"))
    app = relationship("Application", back_populates="products")
    orders = relationship("Order", back_populates="product")


class Order(Base):
    """订单表"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user_id = Column(String, index=True)
    total_price = Column(Float, nullable=False, comment="订单总金额")
    quantity = Column(Integer, nullable=False, default=1, comment="购买数量")

    # 苹果内购订阅相关字段
    original_transaction_id = Column(String, nullable=True, comment="苹果原始交易ID，订阅续费时保持不变", index=True)
    subscription_expire_date = Column(DateTime, nullable=True, comment="订阅过期时间，仅订阅型商品使用")
    auto_renew_status = Column(Boolean, nullable=True, comment="是否自动续费，仅订阅型商品使用")

    # 外键:商品
    product_id = Column(Integer, ForeignKey("products.id"))
    product = relationship("Product", back_populates="orders")
    # 外键:优惠卷 - 二期计划
    # user_coupon_id = Column(Integer, ForeignKey('user_coupons.user_coupon_id'))
    # user_coupon = relationship("UserCoupon", back_populates="order")
    # 外键:支付
    payment = relationship("Payment", back_populates="order", uselist=False)


class Payment(Base):
    """支付记录表"""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    payment_price = Column(Float, nullable=False, comment="支付金额")
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    payment_status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)

    callback_url = Column(String, nullable=True)
    payment_url = Column(String, nullable=True)

    # 苹果内购特有字段
    apple_receipt = Column(Text, nullable=True, comment="苹果内购收据数据，base64编码")
    apple_transaction_id = Column(String, nullable=True, comment="苹果交易ID", index=True)
    apple_original_transaction_id = Column(String, nullable=True, comment="苹果原始交易ID", index=True)
    apple_environment = Column(String, nullable=True, comment="苹果支付环境：Sandbox或Production")
    apple_expires_date = Column(DateTime, nullable=True, comment="苹果订阅过期时间")
    apple_auto_renew_status = Column(Boolean, nullable=True, comment="苹果自动续费状态")
    apple_offer_identifier = Column(String, nullable=True, comment="苹果促销优惠标识符")
    apple_offer_type = Column(String, nullable=True, comment="苹果促销优惠类型")

    order_id = Column(Integer, ForeignKey("orders.id"), unique=True)
    order = relationship("Order", back_populates="payment")

