import pytest
import requests

# 设置基础URL
BASE_URL = "http://localhost:7999"  # 请根据实际情况调整端口号


@pytest.fixture(scope="module")
def setup_data(request):
    # 1. 创建app
    app_response = requests.post(f"{BASE_URL}/applications", json={
        "name": "测试应用",
        "description": "用于测试的应用"
    })
    print(app_response.text)
    assert app_response.status_code == 200
    app_data = app_response.json()
    app_id = app_data["id"]

    # 2. 创建产品
    product_response = requests.post(f"{BASE_URL}/products", json={
        "name": "测试产品",
        "price": 0.01,
        "app_id": app_id
    })
    print(product_response.text)
    assert product_response.status_code == 200
    product_data = product_response.json()
    product_id = product_data["id"]

    def finalizer():
        cleanup_data(app_id, product_id)

    request.addfinalizer(finalizer)

    return app_id, product_id
    
    # 清理数据
    cleanup_data(app_id, product_id)


def cleanup_data(app_id, product_id):
    # 删除产品
    product_delete_response = requests.delete(f"{BASE_URL}/products/{product_id}")
    assert product_delete_response.status_code == 200, f"删除产品失败：{product_delete_response.text}"

    # 删除应用
    app_delete_response = requests.delete(f"{BASE_URL}/applications/{app_id}")
    assert app_delete_response.status_code == 200, f"删除应用失败：{app_delete_response.text}"

    print("测试数据清理完成")


def test_创建订单(setup_data):
    try:
        _, product_id = setup_data
        response = requests.post(f"{BASE_URL}/alipay/pay_qr/create_order/", json={
            "user_id": "test_user_123",
            "product_id": product_id,
            "payment_price": 100.0,
            "quantity": 2
        })

        assert response.status_code == 200
        data = response.json()
        assert "order_number" in data
        assert data["user_id"] == "test_user_123"
        assert data["product_id"] == product_id
        assert "total_price" in data
        assert data["payment_price"] == 100.0
        assert data["quantity"] == 2
        assert data["status"] == "pending"
    finally:
        pass  # cleanup_data 将由 fixture 的 finalizer 处理


def test_发起支付(setup_data):
    try:
        _, product_id = setup_data
        # 首先创建一个订单
        create_order_response = requests.post(f"{BASE_URL}/alipay/pay_qr/create_order/", json={
            "user_id": "test_user_456",
            "product_id": product_id,
            "payment_price": 200.0,
            "quantity": 1
        })
        assert create_order_response.status_code == 200
        order_data = create_order_response.json()
        order_number = order_data["order_number"]

        # 然后发起支付
        pay_response = requests.post(f"{BASE_URL}/alipay/pay_qr/pay/", json={
            "order_number": order_number,
            "callback_url": "http://example.com/callback"
        })

        # 打印响应内容以便调试
        print(f"支付响应状态码: {pay_response.status_code}")
        print(f"支付响应内容: {pay_response.text}")

        assert pay_response.status_code == 200, f"预期状态码200，实际状态码{pay_response.status_code}，响应内容：{pay_response.text}"
        pay_data = pay_response.json()
        assert pay_data["order_number"] == order_number
        assert pay_data["payment_status"] == "pending"
        assert "qr_uri" in pay_data
        assert "payment_price" in pay_data
        assert "quantity" in pay_data
        assert "order_id" in pay_data
        assert "product_name" in pay_data
        assert "app_name" in pay_data
    finally:
        pass  # cleanup_data 将由 fixture 的 finalizer 处理


def test_查询支付状态(setup_data):
    try:
        _, product_id = setup_data
        # 首先创建一个订单并发起支付
        create_order_response = requests.post(f"{BASE_URL}/alipay/pay_qr/create_order/", json={
            "user_id": "test_user_789",
            "product_id": product_id,
            "payment_price": 300.0,
            "quantity": 1
        })
        order_number = create_order_response.json()["order_number"]

        requests.post(f"{BASE_URL}/alipay/pay_qr/pay/", json={
            "order_number": order_number,
            "callback_url": "http://example.com/callback"
        })

        # 查询支付状态
        status_response = requests.get(f"{BASE_URL}/alipay/pay_qr/payment_status/{order_number}")
        print(status_response.text)
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["order_number"] == order_number
        assert "payment_status" in status_data
        assert "payment_price" in status_data
        assert "quantity" in status_data
        assert "order_id" in status_data
        assert "product_name" in status_data
        assert "app_name" in status_data
        assert "qr_uri" in status_data
    finally:
        pass  # cleanup_data 将由 fixture 的 finalizer 处理
