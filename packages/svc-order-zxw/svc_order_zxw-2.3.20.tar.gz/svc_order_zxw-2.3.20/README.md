# svc_order_zxw - 订单与支付服务

一个基于FastAPI的订单与支付服务Python包，提供完整的电商订单管理、支付处理、用户管理和营销活动功能。

## 📝 更新日志

### v2.3.20

- **苹果内购验证逻辑优化**: api_IAP订单管理.py ， 苹果内购验证逻辑优化， 生产环境验证失败后， 尝试沙盒环境验证
- **配置文件优化**: config.py ， 苹果内购配置文件优化， 取消是否沙盒环境配置， 默认自动切换环境

### v2.3.19

- **查询行为优化**: `crud4_payments.py` 中的 `get_payment` 函数优化查询逻辑。将 `scalar_one_or_none()` 替换为 `scalars().first()` 配合时间排序，避免多条记录时的异常，特别适用于苹果内购等可能存在多次支付的场景

### v2.3.18

- **新增API接口**: 新增获取是否开启苹果内购(IAP)的配置接口 `/apple_pay/config/enable_ios_iap`
- **新增定时任务**: 新增定时任务，定时获取动态配置，并更新到内存中， 支持热更新
- **使用注意**: 需要在项目根目录下configs/dynamic_config.json 文件中配置是否开启苹果内购， 默认开启
- v2.3.15~v2.3.17 版本存在bug， 导致无法获取动态配置， 请升级到此版本

### v2.3.14

- 订单更新增加安全校验：apple内购相关字段，如transaction_id, receipt，只有数据库中不存在时才可以执行更新。



### v2.3.13

- 彻底重构苹果内购验证逻辑： api_IAP订单管理.py ， 分为三步：1、创建订单；2、验证收据并更新订单；3、恢复购买

### v2.3.12
- 加强 func_创建订单.py 功能性，同时向后兼容

### v2.3.11

- **数据库查询优化**: 将所有 `db.get()` 语句替换为标准的 `select` 查询语句，提升代码一致性和可维护性
- **修改文件**: `svc_order_zxw/db/crud4_payments.py`, `svc_order_zxw/db/crud活动表2_支付转换权限.py`, `svc_order_zxw/db/crud活动表5_用户优惠券.py`
- v2.3.10 版本存在bug， 导致无法创建订单， 请升级到此版本

### v2.3.10

- 新增func_创建订单.py ， 支持创建订单并创建支付单
- 新增通用订单创建函数， 支付宝创建订单接口使用此函数创建
- v2.3.9 版本存在bug， 导致无法创建订单， 请升级到此版本

### v2.3.8

- **支付查询功能增强**: `crud4_payments.py` 中的 `get_payment` 函数新增可选查询字段 `apple_transaction_id`，支持通过苹果交易ID直接查询支付记录，提升苹果内购订单的查询便利性 

### v2.3.7

- 新增苹果内购的uniapp完整演示页面（优惠券支付有点未知问题无法成功，其他正常）

### v 2.3.6

- **重要修复**: 解决 SQLAlchemy 异步操作错误 `greenlet_spawn has not been called`
- 数据库引擎配置优化：添加 `pool_pre_ping=True` 提高连接稳定性，修复同步引擎URL转换问题
- 支付管理模块异步操作优化：将 `await db.refresh()` 替换为更安全的 `await db.get()` 操作
- 数据库会话管理增强：改进异步会话的错误处理和回滚机制
- 修复文件：`svc_order_zxw/db/get_db.py`, `svc_order_zxw/db/crud4_payments.py`


### v 2.3.5

- 苹果内购订单创建流程优化：改进func0_查询或创建订单_仅限IAP函数，支持更新已存在订单的订阅信息和过期时间
- v2.3.3/v2.3.4 版本存在bug， 导致无法恢复购买， 请升级到此版本

### v2.3.2

- bug fix: 苹果内购订单, 消耗性项目创建订单, 过期时间为None的处理

### v2.3.1

- bug fix:产品表 ， apple_product_id 字段类型删除了index=True, 因为json类型无法建立索引

### v2.3.0

- 产品表 ， apple_product_id 字段类型由 str 改为 list[str]

--------非兼容性更新-----------

### v2.2.11

- 苹果内购订单管理接口优化， 支持获取优惠券签名
- v2.2.7,2.2.8 版本存在bug， 导致无法获取优惠券签名， 请升级到此版本
- v2.2.9 版本存在bug， 导致无法验证苹果内购， 请升级到此版本
- v2.2.10 版本存在bug， 导致无法验证苹果内购， 请升级到此版本

### v2.2.6

- 定时任务task1_定时更新商品表.py : 取消定时更新商品表功能， 改为手动更新，或在外部维护商品表

### v2.2.5

- 定时任务task1_定时更新商品表.py 重大调整， 增删改配置文件中的苹果产品到数据库

### v2.2.4

- 苹果内购优惠券接口优化

### v2.2.3

- 苹果内购api 集成进主项目中， 无需再单独配置

### v2.2.1

- api_商品查询_低权限.py 新增获取所有产品接口， 支持筛选苹果内购产品
- 内部定时任务无需外部再配置与启动

### v2.2.0

- api_商品管理.py 新增获取所有产品接口， 支持筛选苹果内购产品
- api_支付_苹果内购：尚未全部完成
- 定时任务task1_定时更新商品表.py 新增：苹果内购商品表更新功能

### v2.1.0

- 底层新增苹果内购订阅相关功能， api层功能尚未完成
- 数据库表结构优化： 新增苹果内购相关字段
- crud层优化： 新增苹果内购相关字段
- 尚未经过测试
- 理论上兼容旧版本， 但未经过测试

### v2.0.17

- 修复logger

### v2.0.16

- 管理性api添加安全控制： 仅config.DEV_MODE==True时开放全部管理接口用于调试

### v2.0.15

- 更新README： 添加用户表初始化说明

### v2.0.14

- 更新app-tools-zxw引用版本,旧版本存在bug

### v2.0.13

- bug fix: TypeError: 'Logger' object is not callable

### v2.0.12

- bug fix: 支付宝支付 - 回调地址配置优化

### v0.2.11

- bug fix: 支付宝支付 - 回调地址配置优化

### v0.2.10

- bug fix

### v0.2.9

- app-tools-zxw依赖版本更新, 支付宝支付回调api, 更方便在外部定义

### v0.2.8

- 支付宝支付 - 增加注册回调函数，用户可以外部传入 支付成功后的回调处理逻辑

### v0.2.7

- 增加UNIAPP前端代码示例

### v0.2.6

- 技术文档错误修正

### v0.2.5（2025.06.10）

- 技术文档完善

### v0.2.4

- 新特性：crud活动表2_支付转换权限.py 新增根据order_number查询数据
- Bug修复和性能优化

### v0.2.0

- 增加活动表相关功能
- 单元测试覆盖率100%

### v0.1.6

- 单元测试覆盖100%
- 性能优化：查询外键时取消额外的refresh操作

### v0.1.0 (重大更新)

- 表结构3NF优化
- 增加CRUD层
- 重构interface层，使用函数驱动
- 支付宝手机URL支付完成

### v0.0.6

- 新增支付宝二维码支付Vue页面示例
- config新增自动导入

## 📋 项目简介

`svc_order_zxw` 是一个功能完整的订单与支付微服务包，支持：

- **支付集成**：支付宝支付、微信支付
- **订单管理**：订单创建、查询、更新、状态管理
- **商品管理**：商品CRUD操作
- **用户管理**：用户信息管理
- **营销活动**：促销活动、优惠券系统
- **数据库**：基于SQLAlchemy的异步数据库操作

## 🚀 快速开始

### 安装

```bash
pip install svc_order_zxw
```

### 基本使用

```python
from fastapi import FastAPI
from svc_order_zxw.main import router

app = FastAPI()
app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## ⚙️ 配置说明

### 必需配置

- （不推荐）在项目根目录下创建 `config.py` 文件，
- （推荐）或在 `configs/config_payments.py`文件中配置以下参数：

#### 数据库配置

```python
# 数据库连接URL
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"
# 或使用SQLite（开发环境）
DATABASE_URL = "sqlite+aiosqlite:///./test_database.db"
```

#### 支付宝配置

```python
class AliPayConfig:
    appid = "你的支付宝应用ID"
    key应用私钥 = Path("pems/应用私钥2048.txt")  # 应用私钥文件路径
    key支付宝公钥 = Path("pems/支付宝公钥.pem")  # 支付宝公钥文件路径
    # 支付宝支付回调地址配置
    回调路径_root = "http://localhost:8000"
    回调路径_prefix = "/alipay/pay_qr"
```

#### 微信支付配置

```python
class WeChatPay:
    APP_ID = "你的微信应用ID"
    MCH_ID = "你的商户ID"
    SECRET = "你的应用密钥"
    KEY = "你的商户密钥"
    PAYMENT_NOTIFY_URL_小程序 = "http://localhost:8000/wxpay_callback"
    REFUND_NOTIFY_URL_小程序 = "http://localhost:8000/wxpay_refund_callback"
    CERT = "path/to/apiclient_cert.pem"
    CERT_KEY = "path/to/apiclient_key.pem"
```

### 环境变量

```bash
export PAYMENT_DATABASE_URL="your_database_url"
```

### ⚠️ 重要提醒：用户初始化配置

**在使用促销活动相关功能前，必须先初始化用户数据！**

本项目的促销活动系统（优惠券、支付转换权限等）使用独立的用户抽象层。在用户注册到您的主系统后，**必须**同步创建促销活动系统的用户记录，否则会出现以下错误：

#### 报错情况

- 创建优惠券时：`用户不存在 (错误代码: 7501)`
- 分配支付权限时：`用户不存在 (错误代码: 7501)`
- 数据库外键约束违反错误

#### 解决方案

**方案1：用户注册时同步创建**

```python
from svc_order_zxw.db.crud活动表1_用户 import create_user
from svc_order_zxw.db.get_db import get_db

async def 用户注册流程(external_user_id: int):
    """用户注册后的完整流程"""
    # 1. 在您的主系统中创建用户
    # your_main_system.create_user(user_data)

    # 2. 在促销活动系统中创建用户记录
    async with get_db() as db:
        try:
            user = await create_user(db, external_user_id)
            print(f"用户 {external_user_id} 已同步到促销活动系统")
        except Exception as e:
            print(f"促销活动系统用户创建失败: {e}")
```

**方案2：使用前检查并自动创建**

```python
from svc_order_zxw.db.crud活动表1_用户 import get_user, create_user

async def 确保用户存在(user_id: int):
    """确保用户在促销活动系统中存在"""
    async with get_db() as db:
        user = await get_user(db, user_id)
        if not user:
            # 用户不存在，自动创建用户记录
            user = await create_user(db, user_id)
            print(f"用户 {user_id} 已自动创建到促销活动系统")
        return user

# 使用示例：在分配优惠券前检查
async def 安全分配优惠券(user_id: int, coupon_id: int):
    await 确保用户存在(user_id)  # 先确保用户存在
    # 然后再分配优惠券
    async with get_db() as db:
        user_coupon = await create_用户优惠券(db, user_id, coupon_id)
        return user_coupon
```

**方案3：批量初始化现有用户**

```python
async def 批量初始化现有用户(user_ids: list):
    """为现有用户批量创建促销活动系统记录"""
    async with get_db() as db:
        success_count = 0
        for user_id in user_ids:
            try:
                await create_user(db, user_id)
                success_count += 1
            except Exception as e:
                print(f"用户 {user_id} 创建失败: {e}")
        print(f"成功创建 {success_count} 个用户记录")
```

#### 数据库关系说明

- `Model用户表` ← 1:N → `Model支付转换权限表`
- `Model用户表` ← 1:N → `Model用户优惠券表`
- 两个子表都有外键约束指向用户表，必须先有用户记录

## 📚 模块说明

### 1. 数据库层 (db/)

#### CRUD操作模块

- `crud1_applications.py` - 应用程序管理
- `crud2_products.py` - 商品管理
- `crud3_orders.py` - 订单管理
- `crud4_payments.py` - 支付管理
- `crud活动表1_用户.py` - 用户管理
- `crud活动表2_支付转换权限.py` - 支付权限管理
- `crud活动表3_促销活动.py` - 促销活动管理
- `crud活动表4_优惠券.py` - 优惠券管理
- `crud活动表5_用户优惠券.py` - 用户优惠券管理

#### 数据模型

- `models.py` - 基础数据模型
- `models_活动表.py` - 活动相关数据模型

### 2. API层 (apis/)

#### 商品管理API

```python
from svc_order_zxw.apis import api_商品管理

# 提供商品的增删改查功能
```

#### 支付API

```python
from svc_order_zxw.apis.api_支付_支付宝 import api_app与url方式
from svc_order_zxw.apis.api_支付_微信 import api_二维码
```

### 3. 接口层 (interface/)

#### 支付宝支付接口

```python
from svc_order_zxw.interface.interface_支付宝支付 import 创建支付订单, 验证支付回调
```

## 📊 API文档

启动服务后访问以下地址查看API文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 数据类型定义

#### 订单状态枚举 (OrderStatus)

```python
class OrderStatus(str, enum.Enum):
    PENDING = "pending"      # 待支付
    PAID = "paid"           # 已支付
    FAILED = "failed"       # 支付失败
    CANCELLED = "cancelled" # 已取消
    FINISHED = "finished"   # 交易完成（不可退款）
```

#### 支付方式枚举 (PaymentMethod)

```python
class PaymentMethod(str, enum.Enum):
    WECHAT_H5 = "wechat_h5"     # 微信H5支付
    WECHAT_QR = "wechat_qr"     # 微信二维码支付
    WECHAT_MINI = "wechat_mini" # 微信小程序支付
    WECHAT_APP = "wechat_app"   # 微信APP支付
    ALIPAY_H5 = "alipay_h5"     # 支付宝H5支付
    ALIPAY_QR = "alipay_qr"     # 支付宝二维码支付
    ALIPAY_APP = "alipay_app"   # 支付宝APP支付
    PAYPAL = "paypal"           # PayPal支付
    APPLE_PAY = "apple_pay"     # Apple Pay
    GOOGLE_PAY = "google_pay"   # Google Pay
```

## 🔗 API接口详情

### 1. 应用管理 API

#### 创建应用

- **URL**: `POST /applications`
- **描述**: 创建新的应用
- **请求体**:

```json
{
    "name": "应用名称"
}
```

- **响应**:

```json
{
    "id": 1,
    "name": "应用名称",
    "products": []
}
```

#### 获取应用详情

- **URL**: `GET /applications/{application_id}`
- **描述**: 根据应用ID获取应用详情
- **路径参数**:
  - `application_id`: 应用ID (整数)
- **响应**:

```json
{
    "id": 1,
    "name": "应用名称",
    "products": [
        {
            "id": 1,
            "name": "商品名称",
            "app_name": "应用名称",
            "price": 99.99
        }
    ]
}
```

#### 更新应用

- **URL**: `PUT /applications/{application_id}`
- **描述**: 更新应用信息
- **路径参数**:
  - `application_id`: 应用ID (整数)
- **请求体**:

```json
{
    "name": "新的应用名称"
}
```

- **响应**: 同创建应用响应格式

#### 删除应用

- **URL**: `DELETE /applications/{application_id}`
- **描述**: 删除指定应用
- **路径参数**:
  - `application_id`: 应用ID (整数)
- **响应**: HTTP 200 成功

#### 获取所有应用

- **URL**: `GET /applications`
- **描述**: 获取应用列表
- **查询参数**:
  - `skip`: 跳过记录数 (默认: 0)
  - `limit`: 返回记录数 (默认: 100)
- **响应**: 应用列表数组

### 2. 商品管理 API

#### 创建商品

- **URL**: `POST /products`
- **描述**: 创建新商品
- **请求体**:

```json
{
    "name": "商品名称",
    "app_id": 1,
    "price": 99.99
}
```

- **响应**:

```json
{
    "id": 1,
    "name": "商品名称",
    "app_name": "应用名称",
    "price": 99.99
}
```

#### 获取商品详情

- **URL**: `GET /products/{product_id}`
- **描述**: 根据商品ID获取商品详情
- **路径参数**:
  - `product_id`: 商品ID (整数)
- **响应**: 同创建商品响应格式

#### 更新商品

- **URL**: `PUT /products/{product_id}`
- **描述**: 更新商品信息
- **路径参数**:
  - `product_id`: 商品ID (整数)
- **请求体**:

```json
{
    "name": "新商品名称",
    "app_id": 1,
    "price": 199.99
}
```

- **响应**: 同创建商品响应格式

#### 删除商品

- **URL**: `DELETE /products/{product_id}`
- **描述**: 删除指定商品
- **路径参数**:
  - `product_id`: 商品ID (整数)
- **响应**: HTTP 200 成功

#### 获取所有商品

- **URL**: `GET /products`
- **描述**: 获取商品列表
- **查询参数**:
  - `skip`: 跳过记录数 (默认: 0)
  - `limit`: 返回记录数 (默认: 100)
- **响应**: 商品列表数组

### 3. 订单管理 API

#### 创建订单

- **URL**: `POST /orders`
- **描述**: 创建新订单（自动生成订单号）
- **请求体**:

```json
{
    "user_id": "user123",
    "product_id": 1,
    "total_price": 99.99,
    "quantity": 2
}
```

- **响应**:

```json
{
    "id": 1,
    "user_id": "user123",
    "total_price": 99.99,
    "quantity": 2,
    "order_number": "ORD20241201123456789",
    "created_at": "2024-12-01T10:00:00Z",
    "updated_at": "2024-12-01T10:00:00Z",
    "product_id": 1,
    "product": {
        "id": 1,
        "name": "商品名称",
        "price": 49.99,
        "app_id": 1
    },
    "application": {
        "id": 1,
        "name": "应用名称"
    },
    "payment": null
}
```

#### 获取订单详情

- **URL**: `GET /orders/{order_id}`
- **描述**: 根据订单ID获取订单详情（包含商品、应用、支付信息）
- **路径参数**:
  - `order_id`: 订单ID (整数)
- **响应**: 同创建订单响应格式

#### 更新订单

- **URL**: `PUT /orders/{order_id}`
- **描述**: 更新订单信息
- **路径参数**:
  - `order_id`: 订单ID (整数)
- **请求体**:

```json
{
    "total_price": 199.99,
    "quantity": 3
}
```

- **响应**:

```json
{
    "id": 1,
    "user_id": "user123",
    "total_price": 199.99,
    "quantity": 3,
    "order_number": "ORD20241201123456789",
    "created_at": "2024-12-01T10:00:00Z",
    "updated_at": "2024-12-01T10:05:00Z",
    "product_id": 1
}
```

#### 删除订单

- **URL**: `DELETE /orders/{order_id}`
- **描述**: 删除指定订单
- **路径参数**:
  - `order_id`: 订单ID (整数)
- **响应**: HTTP 200 成功

#### 获取订单列表

- **URL**: `GET /orders`
- **描述**: 获取订单列表（支持筛选）
- **查询参数**:
  - `skip`: 跳过记录数 (默认: 0)
  - `limit`: 返回记录数 (默认: 100)
  - `user_id`: 用户ID筛选 (可选)
  - `product_id`: 商品ID筛选 (可选)
  - `application_id`: 应用ID筛选 (可选)
- **响应**: 订单列表数组

### 4. 支付管理 API

#### 创建支付记录

- **URL**: `POST /payments`
- **描述**: 创建新的支付记录
- **请求体**:

```json
{
    "order_id": 1,
    "payment_method": "alipay_qr",
    "payment_price": 99.99,
    "payment_status": "pending",
    "callback_url": "http://example.com/callback",
    "payment_url": "https://qr.alipay.com/xxx"
}
```

- **响应**:

```json
{
    "id": 1,
    "order_id": 1,
    "payment_method": "alipay_qr",
    "payment_price": 99.99,
    "payment_status": "pending",
    "callback_url": "http://example.com/callback",
    "payment_url": "https://qr.alipay.com/xxx",
    "created_at": "2024-12-01T10:00:00Z",
    "updated_at": "2024-12-01T10:00:00Z",
    "order": {
        "id": 1,
        "order_number": "ORD20241201123456789",
        "user_id": "user123",
        "total_price": 99.99,
        "quantity": 1,
        "created_at": "2024-12-01T10:00:00Z",
        "updated_at": "2024-12-01T10:00:00Z",
        "product_id": 1
    }
}
```

#### 获取支付详情

- **URL**: `GET /payments/{payment_id}`
- **描述**: 根据支付ID获取支付详情
- **路径参数**:
  - `payment_id`: 支付ID (整数)
- **响应**: 同创建支付记录响应格式

#### 更新支付记录

- **URL**: `PUT /payments/{payment_id}`
- **描述**: 更新支付记录
- **路径参数**:
  - `payment_id`: 支付ID (整数)
- **请求体**:

```json
{
    "payment_status": "paid",
    "payment_url": "https://new.payment.url"
}
```

- **响应**: 同创建支付记录响应格式

#### 删除支付记录

- **URL**: `DELETE /payments/{payment_id}`
- **描述**: 删除指定支付记录
- **路径参数**:
  - `payment_id`: 支付ID (整数)
- **响应**: HTTP 200 成功

#### 获取支付列表

- **URL**: `GET /payments`
- **描述**: 获取支付记录列表
- **查询参数**:
  - `skip`: 跳过记录数 (默认: 0)
  - `limit`: 返回记录数 (默认: 100)
- **响应**: 支付记录列表数组

### 5. 支付宝支付 API

#### 创建支付宝订单

- **URL**: `POST /alipay/pay_qr/create_order/`
- **描述**: 创建支付宝支付订单
- **请求体**:

```json
{
    "user_id": "user123",
    "product_id": 1,
    "payment_price": 99.99,
    "quantity": 1
}
```

- **响应**:

```json
{
    "user_id": "user123",
    "product_id": 1,
    "order_number": "ORD20241201123456789",
    "total_price": 99.99,
    "payment_price": 99.99,
    "quantity": 1,
    "status": "pending"
}
```

#### 发起支付宝支付

- **URL**: `POST /alipay/pay_qr/pay/`
- **描述**: 发起支付宝二维码支付
- **请求体**:

```json
{
    "order_number": "ORD20241201123456789",
    "callback_url": "http://example.com/callback"
}
```

- **响应**:

```json
{
    "order_number": "ORD20241201123456789",
    "payment_status": "pending",
    "payment_price": 99.99,
    "quantity": 1,
    "order_id": 1,
    "product_name": "商品名称",
    "app_name": "应用名称",
    "qr_uri": "https://qr.alipay.com/xxx"
}
```

#### 查询支付宝支付状态

- **URL**: `GET /alipay/pay_qr/payment_status/{order_number}`
- **描述**: 查询支付宝支付状态
- **路径参数**:
  - `order_number`: 订单号 (字符串)
- **响应**: 同发起支付宝支付响应格式

### 6. 错误响应格式

所有API在发生错误时返回统一格式：

```json
{
    "detail": "错误详情描述",
    "error_code": "具体错误代码",
    "http_status_code": 400
}
```

常见错误代码：

- `商品不存在`: 404 - 指定商品不存在
- `订单号不存在`: 404 - 指定订单不存在
- `支付单号不存在`: 404 - 指定支付记录不存在
- `用户不存在`: 404 - 指定用户不存在
- `新增数据失败`: 500 - 创建数据时发生错误
- `更新数据失败`: 500 - 更新数据时发生错误
- `删除数据失败`: 500 - 删除数据时发生错误

## 🗄️ CRUD操作详细指南

本节提供所有数据库CRUD操作的详细使用指南，您可以直接在业务代码中使用这些函数。

### 📋 CRUD函数快速参考

| 模块             | 功能                          | 创建                  | 读取               | 更新                  | 删除                  | 列表                |
| ---------------- | ----------------------------- | --------------------- | ------------------ | --------------------- | --------------------- | ------------------- |
| **应用管理**     | `crud1_applications.py`       | `create_application`  | `get_application`  | `update_application`  | `delete_application`  | `list_applications` |
| **商品管理**     | `crud2_products.py`           | `create_product`      | `get_product`      | `update_product`      | `delete_product`      | `get_products`      |
| **订单管理**     | `crud3_orders.py`             | `create_order`        | `get_order`        | `update_order`        | `delete_order`        | `list_orders`       |
| **支付管理**     | `crud4_payments.py`           | `create_payment`      | `get_payment`      | `update_payment`      | `delete_payment`      | `list_payments`     |
| **用户管理**     | `crud活动表1_用户.py`         | `create_user`         | `get_user`         | -                     | `delete_user`         | `list_users`        |
| **支付转换权限** | `crud活动表2_支付转换权限.py` | `create_支付转换权限` | `get_支付转换权限` | `update_支付转换权限` | `delete_支付转换权限` | `list_支付转换权限` |
| **促销活动**     | `crud活动表3_促销活动.py`     | `create_promotion`    | `get_promotion`    | `update_promotion`    | `delete_promotion`    | `list_promotions`   |
| **优惠券**       | `crud活动表4_优惠券.py`       | `create_coupon`       | `get_coupon`       | `update_coupon`       | `delete_coupon`       | `list_coupons`      |
| **用户优惠券**   | `crud活动表5_用户优惠券.py`   | `create_用户优惠券`   | `get_用户优惠券`   | `update_用户优惠券`   | `delete_用户优惠券`   | `list_用户优惠券`   |

### 数据库连接

所有CRUD操作都需要数据库会话，使用以下方式获取：

```python
from svc_order_zxw.db.get_db import get_db

async def your_business_function():
    async with get_db() as db:
        # 在这里使用CRUD函数
        pass
```

### 1. 应用管理 CRUD (`crud1_applications.py`)

#### 1.1 创建应用

```python
from svc_order_zxw.db.crud1_applications import create_application, PYD_ApplicationCreate

async def create_app():
    async with get_db() as db:
        app_data = PYD_ApplicationCreate(name="我的应用")
        app = await create_application(db, app_data)
        return app
```

#### 1.2 获取应用

```python
from svc_order_zxw.db.crud1_applications import get_application

async def get_app():
    async with get_db() as db:
        # 通过ID获取
        app = await get_application(db, 1, include_products=True)
        # 通过名称获取
        app = await get_application(db, "应用名称", include_products=True)
        return app
```

#### 1.3 更新应用

```python
from svc_order_zxw.db.crud1_applications import update_application, PYD_ApplicationUpdate

async def update_app():
    async with get_db() as db:
        update_data = PYD_ApplicationUpdate(name="新应用名称")
        app = await update_application(db, 1, update_data)
        return app
```

#### 1.4 删除应用

```python
from svc_order_zxw.db.crud1_applications import delete_application

async def delete_app():
    async with get_db() as db:
        success = await delete_application(db, 1)
        return success
```

#### 1.5 列出应用

```python
from svc_order_zxw.db.crud1_applications import list_applications

async def list_apps():
    async with get_db() as db:
        apps = await list_applications(db, skip=0, limit=10, include_products=True)
        return apps
```

### 2. 商品管理 CRUD (`crud2_products.py`)

#### 2.1 创建商品

```python
from svc_order_zxw.db.crud2_products import create_product, PYD_ProductCreate

async def create_new_product():
    async with get_db() as db:
        product_data = PYD_ProductCreate(
            name="测试商品",
            app_id=1,
            price=99.99
        )
        product = await create_product(db, product_data)
        return product
```

#### 2.2 获取商品

```python
from svc_order_zxw.db.crud2_products import get_product

async def get_product_info():
    async with get_db() as db:
        product = await get_product(db, 1)
        return product
```

#### 2.3 更新商品

```python
from svc_order_zxw.db.crud2_products import update_product, PYD_ProductUpdate

async def update_product_info():
    async with get_db() as db:
        update_data = PYD_ProductUpdate(
            name="更新的商品名称",
            price=199.99
        )
        product = await update_product(db, 1, update_data)
        return product
```

#### 2.4 删除商品

```python
from svc_order_zxw.db.crud2_products import delete_product

async def delete_product_by_id():
    async with get_db() as db:
        success = await delete_product(db, 1)
        return success
```

#### 2.5 列出商品

```python
from svc_order_zxw.db.crud2_products import get_products

async def list_all_products():
    async with get_db() as db:
        products = await get_products(db, skip=0, limit=100)
        return products
```

### 3. 订单管理 CRUD (`crud3_orders.py`)

#### 3.1 创建订单

```python
from svc_order_zxw.db.crud3_orders import create_order, PYD_OrderCreate

async def create_new_order():
    async with get_db() as db:
        order_data = PYD_OrderCreate(
            user_id="user123",
            product_id=1,
            total_price=99.99,
            quantity=2
        )
        order = await create_order(
            db, order_data,
            include_product=True,
            include_application=True
        )
        return order
```

#### 3.2 获取订单

```python
from svc_order_zxw.db.crud3_orders import get_order

async def get_order_info():
    async with get_db() as db:
        # 通过订单ID获取
        order = await get_order(
            db, 1,
            include_product=True,
            include_application=True,
            include_payment=True
        )
        # 通过订单号获取
        order = await get_order(
            db, "ORD20241201123456789",
            include_product=True
        )
        return order
```

#### 3.3 更新订单

```python
from svc_order_zxw.db.crud3_orders import update_order, PYD_OrderUpdate

async def update_order_info():
    async with get_db() as db:
        update_data = PYD_OrderUpdate(
            total_price=199.99,
            quantity=3
        )
        order = await update_order(db, 1, update_data)
        return order
```

#### 3.4 删除订单

```python
from svc_order_zxw.db.crud3_orders import delete_order

async def delete_order_by_id():
    async with get_db() as db:
        success = await delete_order(db, 1)
        return success
```

#### 3.5 列出订单（支持筛选）

```python
from svc_order_zxw.db.crud3_orders import list_orders, PYD_OrderFilter

async def list_filtered_orders():
    async with get_db() as db:
        filter_data = PYD_OrderFilter(
            user_id="user123",  # 筛选特定用户的订单
            product_id=1,       # 筛选特定商品的订单
            application_id=1    # 筛选特定应用的订单
        )
        orders = await list_orders(
            db, filter_data,
            skip=0, limit=100,
            include_product=True,
            include_application=True
        )
        return orders
```

### 4. 支付管理 CRUD (`crud4_payments.py`)

#### 4.1 创建支付记录

```python
from svc_order_zxw.db.crud4_payments import create_payment, PYD_PaymentCreate
from svc_order_zxw.apis.schemas_payments import PaymentMethod, OrderStatus

async def create_payment_record():
    async with get_db() as db:
        payment_data = PYD_PaymentCreate(
            order_id=1,
            payment_method=PaymentMethod.ALIPAY_QR,
            payment_price=99.99,
            payment_status=OrderStatus.PENDING,
            callback_url="http://example.com/callback",
            payment_url="https://qr.alipay.com/xxx"
        )
        payment = await create_payment(db, payment_data, include_order=True)
        return payment
```

#### 4.2 获取支付记录

```python
from svc_order_zxw.db.crud4_payments import get_payment

async def get_payment_info():
    async with get_db() as db:
        # 通过支付ID获取
        payment = await get_payment(db, payment_id=1, include_order=True)
        # 通过订单号获取
        payment = await get_payment(db, order_number="ORD20241201123456789", include_order=True)
        return payment
```

#### 4.3 更新支付记录

```python
from svc_order_zxw.db.crud4_payments import update_payment, PYD_PaymentUpdate

async def update_payment_status():
    async with get_db() as db:
        update_data = PYD_PaymentUpdate(
            payment_status=OrderStatus.PAID,
            payment_url="https://new.payment.url"
        )
        payment = await update_payment(db, 1, update_data, include_order=True)
        return payment
```

#### 4.4 删除支付记录

```python
from svc_order_zxw.db.crud4_payments import delete_payment

async def delete_payment_record():
    async with get_db() as db:
        success = await delete_payment(db, 1)
        return success
```

#### 4.5 列出支付记录

```python
from svc_order_zxw.db.crud4_payments import list_payments

async def list_payment_records():
    async with get_db() as db:
        payments = await list_payments(db, skip=0, limit=100, include_order=True)
        return payments
```

## 💡 使用示例

### 1. 创建订单

```python
from svc_order_zxw.db.crud3_orders import create_order
from svc_order_zxw.db.get_db import get_db

async def create_new_order():
    async with get_db() as db:
        order_data = {
            "product_id": 1,
            "quantity": 2,
            "total_amount": 199.98,
            "user_id": 1
        }
        order = await create_order(db, order_data)
        return order
```

### 2. 支付宝支付

```python
from svc_order_zxw.interface.interface_支付宝支付 import 创建支付订单

async def create_alipay_order():
    支付订单 = await 创建支付订单(
        order_number="ORDER_20241201_001",
        total_amount=99.99,
        subject="商品名称",
        return_url="http://localhost:8000/success"
    )
    return 支付订单
```

### 3. 商品管理

```python
from svc_order_zxw.db.crud2_products import create_product, get_products

async def manage_products():
    async with get_db() as db:
        # 创建商品
        product_data = {
            "name": "测试商品",
            "price": 99.99,
            "description": "这是一个测试商品",
            "stock": 100
        }
        product = await create_product(db, product_data)

        # 查询所有商品
        products = await get_products(db)
        return products
```

### 5. 用户管理 CRUD (`crud活动表1_用户.py`)

#### 5.1 创建用户

```python
from svc_order_zxw.db.crud活动表1_用户 import create_user

async def create_new_user():
    async with get_db() as db:
        user = await create_user(db, external_user_id=12345)
        return user
```

#### 5.2 获取用户

```python
from svc_order_zxw.db.crud活动表1_用户 import get_user

async def get_user_info():
    async with get_db() as db:
        user = await get_user(
            db, 12345,
            include_支付转换权限=True,
            include_用户优惠券=True
        )
        return user
```

#### 5.3 删除用户

```python
from svc_order_zxw.db.crud活动表1_用户 import delete_user

async def delete_user_by_id():
    async with get_db() as db:
        success = await delete_user(db, 12345)
        return success
```

#### 5.4 列出用户

```python
from svc_order_zxw.db.crud活动表1_用户 import list_users

async def list_all_users():
    async with get_db() as db:
        users = await list_users(
            db, skip=0, limit=100,
            include_支付转换权限=True,
            include_用户优惠券=True
        )
        return users
```

### 6. 支付转换权限管理 CRUD (`crud活动表2_支付转换权限.py`)

#### 6.1 创建支付转换权限

```python
from svc_order_zxw.db.crud活动表2_支付转换权限 import create_支付转换权限

async def create_payment_permission():
    async with get_db() as db:
        permission = await create_支付转换权限(
            db,
            user_id=12345,
            isCharged=True,
            order_number="ORD20241201123456789"  # 可选
        )
        return permission
```

#### 6.2 获取支付转换权限

```python
from svc_order_zxw.db.crud活动表2_支付转换权限 import get_支付转换权限

async def get_payment_permission():
    async with get_db() as db:
        # 通过权限ID获取
        permission = await get_支付转换权限(
            db, 支付转换权限_id=1,
            include_user=True,
            include_order=True
        )
        # 通过订单号获取
        permission = await get_支付转换权限(
            db, order_number="ORD20241201123456789",
            include_user=True
        )
        return permission
```

#### 6.3 更新支付转换权限

```python
from svc_order_zxw.db.crud活动表2_支付转换权限 import update_支付转换权限

async def update_payment_permission():
    async with get_db() as db:
        permission = await update_支付转换权限(
            db, 1,
            isCharged=False,
            order_number="NEW_ORDER_NUMBER"
        )
        return permission
```

#### 6.4 删除支付转换权限

```python
from svc_order_zxw.db.crud活动表2_支付转换权限 import delete_支付转换权限

async def delete_payment_permission():
    async with get_db() as db:
        success = await delete_支付转换权限(db, 1)
        return success
```

#### 6.5 列出支付转换权限

```python
from svc_order_zxw.db.crud活动表2_支付转换权限 import list_支付转换权限

async def list_payment_permissions():
    async with get_db() as db:
        permissions = await list_支付转换权限(
            db, user_id=12345,
            skip=0, limit=100
        )
        return permissions
```

### 7. 促销活动管理 CRUD (`crud活动表3_促销活动.py`)

#### 7.1 创建促销活动

```python
from svc_order_zxw.db.crud活动表3_促销活动 import create_promotion, PYD_CreatePromotion, DiscountType
from datetime import date

async def create_new_promotion():
    async with get_db() as db:
        promotion_data = PYD_CreatePromotion(
            name="双十一特价",
            threshold=100.0,  # 满100元
            discount_type=DiscountType.折扣,
            discount_value=0.8,  # 8折
            start_date=date(2024, 11, 1),
            end_date=date(2024, 11, 11),
            is_active=True,
            product_id=1
        )
        promotion = await create_promotion(db, promotion_data)
        return promotion
```

#### 7.2 获取促销活动

```python
from svc_order_zxw.db.crud活动表3_促销活动 import get_promotion

async def get_promotion_info():
    async with get_db() as db:
        promotion = await get_promotion(db, 1, include_product=True)
        return promotion
```

#### 7.3 更新促销活动

```python
from svc_order_zxw.db.crud活动表3_促销活动 import update_promotion, PYD_UpdatePromotion

async def update_promotion_info():
    async with get_db() as db:
        update_data = PYD_UpdatePromotion(
            name="双十一超级特价",
            discount_value=0.7,  # 改为7折
            is_active=False
        )
        promotion = await update_promotion(db, 1, update_data)
        return promotion
```

#### 7.4 删除促销活动

```python
from svc_order_zxw.db.crud活动表3_促销活动 import delete_promotion

async def delete_promotion_by_id():
    async with get_db() as db:
        success = await delete_promotion(db, 1)
        return success
```

#### 7.5 列出促销活动

```python
from svc_order_zxw.db.crud活动表3_促销活动 import list_promotions, PYD_PromotionFilter

async def list_active_promotions():
    async with get_db() as db:
        filter_data = PYD_PromotionFilter(
            product_id=1,     # 筛选特定商品的促销
            is_active=True    # 只要激活的促销
        )
        promotions = await list_promotions(
            db, filter_data,
            skip=0, limit=100,
            include_product=True
        )
        return promotions
```

### 8. 优惠券管理 CRUD (`crud活动表4_优惠券.py`)

#### 8.1 创建优惠券

```python
from svc_order_zxw.db.crud活动表4_优惠券 import create_coupon
from datetime import date

async def create_new_coupon():
    async with get_db() as db:
        coupon = await create_coupon(
            db,
            code="DISCOUNT10",
            discount_value=10.0,  # 10元优惠
            expiration_date=date(2024, 12, 31),
            promotion_id=1
        )
        return coupon
```

#### 8.2 获取优惠券

```python
from svc_order_zxw.db.crud活动表4_优惠券 import get_coupon

async def get_coupon_info():
    async with get_db() as db:
        coupon = await get_coupon(db, 1, include_promotion=True)
        return coupon
```

#### 8.3 更新优惠券

```python
from svc_order_zxw.db.crud活动表4_优惠券 import update_coupon
from datetime import date

async def update_coupon_info():
    async with get_db() as db:
        coupon = await update_coupon(
            db, 1,
            code="NEWDISCOUNT15",
            discount_value=15.0,
            expiration_date=date(2025, 1, 31)
        )
        return coupon
```

#### 8.4 删除优惠券

```python
from svc_order_zxw.db.crud活动表4_优惠券 import delete_coupon

async def delete_coupon_by_id():
    async with get_db() as db:
        success = await delete_coupon(db, 1)
        return success
```

#### 8.5 列出优惠券

```python
from svc_order_zxw.db.crud活动表4_优惠券 import list_coupons, PYD_优惠券Filter
from datetime import date

async def list_active_coupons():
    async with get_db() as db:
        filter_data = PYD_优惠券Filter(
            promotion_id=1,  # 特定促销活动的优惠券
            expiration_date_after=date.today()  # 未过期的优惠券
        )
        coupons = await list_coupons(
            db, filter_data,
            skip=0, limit=100,
            include_promotion=True
        )
        return coupons
```

### 9. 用户优惠券管理 CRUD (`crud活动表5_用户优惠券.py`)

#### 9.1 分配优惠券给用户

```python
from svc_order_zxw.db.crud活动表5_用户优惠券 import create_用户优惠券

async def assign_coupon_to_user():
    async with get_db() as db:
        user_coupon = await create_用户优惠券(db, user_id=12345, coupon_id=1)
        return user_coupon
```

#### 9.2 获取用户优惠券

```python
from svc_order_zxw.db.crud活动表5_用户优惠券 import get_用户优惠券

async def get_user_coupon():
    async with get_db() as db:
        user_coupon = await get_用户优惠券(
            db, 1,
            include_user=True,
            include_coupon=True
        )
        return user_coupon
```

#### 9.3 更新用户优惠券状态

```python
from svc_order_zxw.db.crud活动表5_用户优惠券 import update_用户优惠券

async def mark_coupon_as_used():
    async with get_db() as db:
        user_coupon = await update_用户优惠券(db, 1, is_used=True)
        return user_coupon
```

#### 9.4 删除用户优惠券

```python
from svc_order_zxw.db.crud活动表5_用户优惠券 import delete_用户优惠券

async def remove_user_coupon():
    async with get_db() as db:
        success = await delete_用户优惠券(db, 1)
        return success
```

#### 9.5 列出用户优惠券

```python
from svc_order_zxw.db.crud活动表5_用户优惠券 import list_用户优惠券

async def list_user_coupons():
    async with get_db() as db:
        user_coupons = await list_用户优惠券(
            db, user_id=12345,
            skip=0, limit=100
        )
        return user_coupons
```

### CRUD操作最佳实践

#### 1. 异常处理

```python
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW

async def safe_create_order():
    try:
        async with get_db() as db:
            order = await create_order(db, order_data)
            return order
    except HTTPException_AppToolsSZXW as e:
        print(f"业务异常: {e.detail}")
        raise
    except Exception as e:
        print(f"系统异常: {str(e)}")
        raise
```

#### 2. 事务管理

```python
async def complex_business_operation():
    async with get_db() as db:
        try:
            # 创建订单
            order = await create_order(db, order_data)
            # 创建支付记录
            payment = await create_payment(db, payment_data)
            # 分配优惠券
            user_coupon = await create_用户优惠券(db, user_id, coupon_id)

            # 如果所有操作成功，事务会自动提交
            return {"order": order, "payment": payment, "user_coupon": user_coupon}
        except Exception as e:
            # 出现异常时，事务会自动回滚
            raise
```

#### 3. 批量操作优化

```python
async def batch_create_orders(order_list):
    async with get_db() as db:
        orders = []
        for order_data in order_list:
            order = await create_order(db, order_data)
            orders.append(order)
        return orders
```

### 🎯 常用数据类型与枚举

#### Pydantic模型类型

| 模块         | 创建类型                | 更新类型                | 响应类型                  | 筛选类型              |
| ------------ | ----------------------- | ----------------------- | ------------------------- | --------------------- |
| **应用管理** | `PYD_ApplicationCreate` | `PYD_ApplicationUpdate` | `PYD_ApplicationResponse` | -                     |
| **商品管理** | `PYD_ProductCreate`     | `PYD_ProductUpdate`     | `PYD_ProductResponse`     | -                     |
| **订单管理** | `PYD_OrderCreate`       | `PYD_OrderUpdate`       | `PYD_OrderResponse`       | `PYD_OrderFilter`     |
| **支付管理** | `PYD_PaymentCreate`     | `PYD_PaymentUpdate`     | `PYD_PaymentResponse`     | -                     |
| **促销活动** | `PYD_CreatePromotion`   | `PYD_UpdatePromotion`   | `PYD_PromotionResponse`   | `PYD_PromotionFilter` |
| **优惠券**   | -                       | -                       | `PYD_优惠券Response`      | `PYD_优惠券Filter`    |

#### 枚举类型

```python
# 支付方式枚举
from svc_order_zxw.apis.schemas_payments import PaymentMethod
PaymentMethod.WECHAT_H5     # 微信H5支付
PaymentMethod.WECHAT_QR     # 微信二维码支付
PaymentMethod.ALIPAY_H5     # 支付宝H5支付
PaymentMethod.ALIPAY_QR     # 支付宝二维码支付

# 订单状态枚举
from svc_order_zxw.apis.schemas_payments import OrderStatus
OrderStatus.PENDING         # 待支付
OrderStatus.PAID           # 已支付
OrderStatus.FAILED         # 支付失败
OrderStatus.CANCELLED      # 已取消
OrderStatus.FINISHED       # 交易完成

# 折扣类型枚举
from svc_order_zxw.db.crud活动表3_促销活动 import DiscountType
DiscountType.金额          # 金额折扣
DiscountType.折扣          # 百分比折扣
DiscountType.优惠券        # 优惠券
```

#### 常用导入语句

```python
# 数据库连接
from svc_order_zxw.db.get_db import get_db

# 应用管理
from svc_order_zxw.db.crud1_applications import (
    create_application, get_application, update_application,
    delete_application, list_applications,
    PYD_ApplicationCreate, PYD_ApplicationUpdate, PYD_ApplicationResponse
)

# 商品管理
from svc_order_zxw.db.crud2_products import (
    create_product, get_product, update_product, delete_product, get_products,
    PYD_ProductCreate, PYD_ProductUpdate, PYD_ProductResponse
)

# 订单管理
from svc_order_zxw.db.crud3_orders import (
    create_order, get_order, update_order, delete_order, list_orders,
    PYD_OrderCreate, PYD_OrderUpdate, PYD_OrderResponse, PYD_OrderFilter
)

# 支付管理
from svc_order_zxw.db.crud4_payments import (
    create_payment, get_payment, update_payment, delete_payment, list_payments,
    PYD_PaymentCreate, PYD_PaymentUpdate, PYD_PaymentResponse
)

# 用户管理
from svc_order_zxw.db.crud活动表1_用户 import (
    create_user, get_user, delete_user, list_users
)

# 支付转换权限管理
from svc_order_zxw.db.crud活动表2_支付转换权限 import (
    create_支付转换权限, get_支付转换权限, update_支付转换权限,
    delete_支付转换权限, list_支付转换权限
)

# 促销活动管理
from svc_order_zxw.db.crud活动表3_促销活动 import (
    create_promotion, get_promotion, update_promotion, delete_promotion, list_promotions,
    PYD_CreatePromotion, PYD_UpdatePromotion, PYD_PromotionResponse,
    PYD_PromotionFilter, DiscountType
)

# 优惠券管理
from svc_order_zxw.db.crud活动表4_优惠券 import (
    create_coupon, get_coupon, update_coupon, delete_coupon, list_coupons,
    PYD_优惠券Filter
)

# 用户优惠券管理
from svc_order_zxw.db.crud活动表5_用户优惠券 import (
    create_用户优惠券, get_用户优惠券, update_用户优惠券,
    delete_用户优惠券, list_用户优惠券
)

# 异常处理
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW

# 时间相关
from datetime import date, datetime
```

### 4. 优惠券系统

```python
from svc_order_zxw.db.crud活动表4_优惠券 import create_coupon
from svc_order_zxw.db.crud活动表5_用户优惠券 import create_用户优惠券

async def coupon_example():
    async with get_db() as db:
        # 创建优惠券
        coupon = await create_coupon(
            db,
            code="NEWUSER10",
            discount_value=10.0,
            expiration_date=date(2024, 12, 31),
            promotion_id=1
        )

        # 分配给用户
        user_coupon = await create_用户优惠券(db, user_id=12345, coupon_id=coupon.id)
        return {"coupon": coupon, "user_coupon": user_coupon}
```

## 🔧 开发指南

### 运行测试

```bash
cd svc_order_zxw
python -m pytest tests/ -v
```

### 数据库迁移

```bash
# 如果使用Alembic进行数据库迁移
alembic upgrade head
```

### 启动开发服务器

```bash
python main.py
```

或使用uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🏗️ 架构设计

```
svc_order_zxw/
├── db/                     # 数据库层
│   ├── models.py          # 数据模型
│   ├── crud*.py           # CRUD操作
│   └── get_db.py          # 数据库连接
├── apis/                   # API路由层
│   ├── api_商品管理.py     # 商品API
│   └── api_支付_*/         # 支付API
├── interface/              # 业务接口层
└── tests/                 # 测试用例
```

## 📋 依赖要求

- Python >= 3.10
- FastAPI >= 0.112.0
- SQLAlchemy == 2.0.32
- asyncpg == 0.29.0 (PostgreSQL)
- uvicorn >= 0.30.0
- app-tools-zxw >= 1.0.81

## 🔍 故障排除

### 常见问题

1. **数据库连接失败**

   - 检查 `DATABASE_URL` 配置
   - 确保数据库服务正在运行
2. **支付配置错误**

   - 验证支付宝/微信支付的配置参数
   - 检查证书文件路径是否正确
3. **导入错误**

   - 确保已正确安装所有依赖
   - 检查Python版本兼容性

### 日志配置

项目支持详细的日志记录，可以在 `logs/` 目录下查看运行日志。

## 📞 支持与贡献

- **作者**: 薛伟的小工具
- **GitHub**: https://github.com/sunshineinwater/
- **邮箱**: shuiheyangguang@gmail.com

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

MIT License - 详见LICENSE文件

---

*本文档会随着项目更新而持续更新，请关注最新版本。*

