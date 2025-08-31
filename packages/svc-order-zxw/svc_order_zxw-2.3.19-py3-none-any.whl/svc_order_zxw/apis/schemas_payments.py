"""
# File       : schemas_payments.py
# Time       ：2024/9/24 14:49
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
import enum
from pydantic import BaseModel, Field


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"
    FINISHED = "finished"  # 交易完成，且不可退款（与PAID的区别之处）


class PaymentMethod(str, enum.Enum):
    WECHAT_H5 = "wechat_h5"
    WECHAT_QR = "wechat_qr"
    WECHAT_MINI = "wechat_mini"
    WECHAT_APP = "wechat_app"
    ALIPAY_H5 = "alipay_h5"
    ALIPAY_QR = "alipay_qr"
    ALIPAY_APP = "alipay_app"
    PAYPAL = "paypal"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"


class PaymentResult(BaseModel):
    商户订单号: str = Field(..., title="商户订单号", description="order_number")
    支付平台交易号: str = Field(..., title="支付平台交易号", description="")
    交易金额: float = Field(..., title="交易金额", description="amount")
    交易状态: OrderStatus
    支付时间: str = Field(..., title="支付时间", description="payment_time")
    支付账号: str = None
    支付方式: PaymentMethod
    支付失败原因: str = None
    备注: str = None
