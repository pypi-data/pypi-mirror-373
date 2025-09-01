"""
# File       : test_商品管理2.py
# Time       ：2024/10/8 10:35
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
        运行前, 需要将项目根目录设置到 最根部,否则报错
"""
import pytest
import requests
import random
import string
from svc_order_zxw.apis.schemas_payments import PaymentMethod, PaymentResult

BASE_URL = "http://127.0.0.1:7999"  # 请替换为实际的测试服务器地址


def generate_random_name(prefix="测试", length=5):
    """生成随机名称"""
    random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return f"{prefix}_{random_suffix}"


@pytest.fixture
def create_application():
    # 创建应用的辅助函数
    def _create_application():
        name = generate_random_name("应用")
        response = requests.post(f"{BASE_URL}/applications", json={"name": name})
        assert response.status_code == 200
        return response.json()

    return _create_application


@pytest.fixture
def create_product():
    # 创建产品的辅助函数
    def _create_product(name, price, application_id):
        response = requests.post(f"{BASE_URL}/products", json={
            "name": name,
            "price": price,
            "app_id": application_id
        })
        assert response.status_code == 200
        return response.json()

    return _create_product


# 测试应用相关API
def test_application_crud(create_application):
    # 创建应用
    app = create_application()
    app_id = app["id"]
    original_name = app["name"]

    # 获取应用
    response = requests.get(f"{BASE_URL}/applications/{app_id}")
    assert response.status_code == 200
    assert response.json()["name"] == original_name

    # 更新应用
    new_name = generate_random_name("更新应用")
    response = requests.put(f"{BASE_URL}/applications/{app_id}", json={"name": new_name})
    assert response.status_code == 200
    assert response.json()["name"] == new_name

    # 获取所有应用
    response = requests.get(f"{BASE_URL}/applications")
    assert response.status_code == 200
    assert len(response.json()) > 0

    # 删除应用
    response = requests.delete(f"{BASE_URL}/applications/{app_id}")
    assert response.status_code == 200

    # 确认应用已被删除
    response = requests.get(f"{BASE_URL}/applications/{app_id}")
    assert response.text == "null"


# 测试产品相关API
def test_product_crud(create_application, create_product):
    app = create_application()

    # 创建产品
    print("app = ", app)
    product_name = generate_random_name("产品")
    product = create_product(product_name, 100, app["id"])
    product_id = product["id"]

    # 获取产品
    response = requests.get(f"{BASE_URL}/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["name"] == product_name

    # 更新产品
    response = requests.put(f"{BASE_URL}/products/{product_id}", json={"name": "更新后的产品", "price": 200})
    assert response.status_code == 200
    assert response.json()["name"] == "更新后的产品"
    assert response.json()["price"] == 200

    # 获取所有产品
    response = requests.get(f"{BASE_URL}/products")
    assert response.status_code == 200
    assert len(response.json()) > 0

    # 删除产品
    response = requests.delete(f"{BASE_URL}/products/{product_id}")
    assert response.status_code == 200

    # 确认产品已被删除
    response = requests.get(f"{BASE_URL}/products/{product_id}")
    assert response.text == "null"


# 测试订单相关API
def test_order_crud(create_application, create_product):
    app = create_application()
    product = create_product("测试产品", 100, app["id"])

    # 创建订单
    order_data = {
        "user_id": "test_user",
        "product_id": product["id"],
        "total_price": 0.01,
        "quantity": 1
    }
    response = requests.post(f"{BASE_URL}/orders", json=order_data)
    assert response.status_code == 200
    order = response.json()
    order_id = order["id"]

    # 获取订单
    response = requests.get(f"{BASE_URL}/orders/{order_id}")
    assert response.status_code == 200
    assert response.json()["user_id"] == "test_user"

    # 更新订单
    response = requests.put(f"{BASE_URL}/orders/{order_id}", json={"quantity": 2})
    assert response.status_code == 200
    assert response.json()["quantity"] == 2

    # 获取所有订单
    response = requests.get(f"{BASE_URL}/orders")
    assert response.status_code == 200
    assert len(response.json()) > 0

    # 删除订单
    response = requests.delete(f"{BASE_URL}/orders/{order_id}")
    assert response.status_code == 200

    # 确认订单已被删除
    response = requests.get(f"{BASE_URL}/orders/{order_id}")
    assert response.text == "null"


# 测试支付相关API
def test_payment_crud(create_application, create_product):
    app = create_application()
    product = create_product("测试产品", 100, app["id"])

    # 创建订单
    order_response = requests.post(f"{BASE_URL}/orders", json={
        "user_id": "test_user",
        "product_id": product["id"],
        "quantity": 100,
        "total_price": 100
    })
    assert order_response.status_code == 200
    order = order_response.json()
    print("order = ", order)

    # 创建支付
    payment_data = {
        "payment_method": PaymentMethod.ALIPAY_QR,
        "payment_price": 100,
        "payment_status": "pending",
        "callback_url": "http://example.com/callback",
        "payment_url": "http://example.com/pay",
        "order_id": order["id"]
    }
    response = requests.post(f"{BASE_URL}/payments", json=payment_data)

    assert response.status_code == 200
    payment = response.json()
    payment_id = payment["id"]

    # 获取支付
    response = requests.get(f"{BASE_URL}/payments/{payment_id}")
    assert response.status_code == 200
    assert response.json()["payment_price"] == 100

    # 更新支付
    update_data = {
        "payment_price": 200,
        "payment_status": "paid"
    }
    response = requests.put(f"{BASE_URL}/payments/{payment_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["payment_price"] == 200
    assert response.json()["payment_status"] == "paid"

    # 获取所有支付
    response = requests.get(f"{BASE_URL}/payments")
    assert response.status_code == 200
    assert len(response.json()) > 0

    # 删除支付
    response = requests.delete(f"{BASE_URL}/payments/{payment_id}")
    assert response.status_code == 200

    # 确认支付已被删除
    response = requests.get(f"{BASE_URL}/payments/{payment_id}")
    assert response.text == "null"

    # 清理创建的订单
    requests.delete(f"{BASE_URL}/orders/{order['id']}")
