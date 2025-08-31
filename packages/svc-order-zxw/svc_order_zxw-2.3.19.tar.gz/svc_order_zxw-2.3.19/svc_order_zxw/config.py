"""
# File       : config.py
# Time       ：2024/8/20 下午5:25
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
import os
from pathlib import Path

if Path("configs/config_payments.py").exists():
    from configs.config_payments import *
else:
    # 如果配置文件不存在，则使用环境变量

    # 开发模式控制变量
    DEV_MODE = True

    # postgresql数据库
    DATABASE_URL = os.environ.get('PAYMENT_DATABASE_URL')  # 读取docker配置的环境变量
    if not DATABASE_URL:
        DATABASE_URL = "sqlite+aiosqlite:///./test_database.db"
        os.environ['PAYMENT_DATABASE_URL'] = DATABASE_URL  # 设置环境变量, 以便在docker、alembic中读取


    # 微信公众号
    class WeChatPub:
        app_id = "..."
        app_secret = "..."
        scope = "snsapi_login"
        scope_qrcode_login = "snsapi_login"  # 二维码登录必须用snsapi_login
        state = "your_custom_state"  # 用于防止CSRF
        接口配置信息_Token = "..."  # 自己去微信公众号设置


    # 微信小程序
    class WeChatMini:
        # 正式
        app_id = "..."
        app_secret = "..."


    # 阿里云
    class Aliyun:
        ali_access_key_id = "..."
        ali_access_key_secret = "..."
        ali_secretNo_pool_key = "..."


    # 微信支付专用
    class WeChatPay:
        APP_ID = "..."
        MCH_ID = '...'
        SECRET = '...'
        NONCE_STR = '...'
        KEY = '...'
        PAYMENT_NOTIFY_URL_小程序 = 'http://0.0.0.0:8000/msvc_order'  # 小程序支付成功后的回调地址
        REFUND_NOTIFY_URL_小程序 = 'http://0.0.0.0:8000/wxpay_recall'  # 小程序退款成功后的回调地址
        PAYMENT_NOTIFY_URL_二维码 = 'http://localhost:8000/wechat/pay_h5/payment_callback'  # 二维码支付成功后的回调地址
        REFUND_NOTIFY_URL_二维码 = 'http://localhost:8000/wechat/pay_h5/refund_callback'  # 二维码退款成功后的回调地址
        # 微信退款需要用到的商户证书，没有配置的话请求退款会出错
        # 详情见：https://pay.weixin.qq.com/wiki/doc/api/wxa/wxa_api.php?chapter=4_3
        CERT = '.../apiclient_cert.pem'
        CERT_KEY = '.../apiclient_key.pem'


    # 支付宝专用
    class AliPayConfig:
        appid = "..."
        key应用私钥 = Path("pems/应用私钥2048.txt")
        # key应用公钥 = Path(".../应用公钥2048.txt")
        key支付宝公钥 = Path("pems/支付宝公钥.pem")
        # 支付宝支付成功后的回调地址
        回调路径_root = "http://localhost:8000"
        回调路径_prefix = "/alipay/pay_qr"


    # 苹果支付
    class ApplePayConfig:
        """
        苹果内购商品配置
        注意：
        1. 商品类型必须与models.py中的ProductType匹配，
            consumable：消耗型商品，non_consumable：非消耗型商品，
            auto_renewable：自动续费订阅，non_renewable：非续费订阅
        """
        # 隐私数据，请勿泄露
        私钥文件路径 = "pems/....p8"  # 替换为实际路径
        密钥ID = "xxxxxxxx"  # 替换为实际的密钥ID
        发行者ID = "xxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxx"  # 替换为实际的发行者ID
        应用包ID = "xxx.xxxxxxxx.xxx"  # 替换为实际的Bundle ID
        是否沙盒环境 = True  # 测试时使用沙盒环境
        苹果ID = None  # 沙盒环境可以为空，生产环境必须提供
        共享密钥 = "xxxxxxxxxxxxxxxxxx"
        # 产品数据
        products = {
            "vip001": {
                "app_name": "fudaoyuan",
                "product_names": ["app1_study_fudaoyuan||辅导员基础知识"],
                "description": "基础30天会员",
                "price": 28,
                "currency": "CNY",
                "type": "non_renewable",
                # consumable, non_consumable, auto_renewable, non_renewable 必须与models.py中的ProductType匹配
                "duration": 30,
                "duration_type": "day",  # day, week, month, year
                "优惠券": {
                    "vip001_discount_9": {
                        "description": "9折",
                        "price": 18
                    }
                }
            },
            "vip002": {
                "app_name": "fudaoyuan",
                "product_names": ["app1_study_fudaoyuan||教育心理学_教资"],
                "description": "基础30天会员",
                "price": 48,
                "currency": "CNY",
                "type": "auto_renewable",
                # consumable, non_consumable, auto_renewable, non_renewable 必须与models.py中的ProductType匹配
                "duration": 30,
                "duration_type": "day",  # day, week, month, year
                "优惠券": {
                    "discount_9": {
                        "description": "9折",
                        "price": 38
                    },
                    "discount_5": {
                        "description": "5折",
                        "price": 28
                    }
                }
            },
            "vip003": {
                "app_name": "fudaoyuan",
                "product_names": ["app1_study_fudaoyuan||教育心理学_教资"],
                "description": "基础30天会员",
                "price": 48,
                "currency": "CNY",
                "type": "consumable",
                # consumable, non_consumable, auto_renewable, non_renewable 必须与models.py中的ProductType匹配
                "duration": None,
                "duration_type": None,  # day, week, month, year
                "优惠券": {
                    "discount_9": {
                        "description": "9折",
                        "price": 38
                    },
                    "discount_5": {
                        "description": "5折",
                        "price": 28
                    }
                }
            }
        }


    # 发送邮件
    class Email:
        sender = '...@163.com'  # 发件人
        server = 'smtp.163.com'  # 所使用的用来发送邮件的SMTP服务器
        username = '...@163.com'  # 发送邮箱的用户名和授权码（不是登录邮箱的密码）
        password = '...'  # 服务器: MVQDSPUQATBDOIFU / 自用电脑: FFHBMPJSXXFEEZIK


    # AES密码密匙
    class AESKey:
        key_web = "..."
        key_local = "..."
