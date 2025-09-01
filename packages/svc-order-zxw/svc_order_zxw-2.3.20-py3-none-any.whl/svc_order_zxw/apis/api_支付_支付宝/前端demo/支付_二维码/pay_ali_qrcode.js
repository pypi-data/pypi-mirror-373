const BASE_URL = 'http://0.0.0.0:8000';
const APP_ID = "AutoJiaoAn";
const PRODUCT_ID = 0; // 商品id, 根据商品表内id而定

export async function createOrder(
    {
        user_id,
        amount,
    }
) {
    const requestData = {
        user_id,
        amount,
        product_id: PRODUCT_ID,
        callback_url: "",
        app_id: APP_ID
    };

    try {
        const res = await uni.request({
            url: `${BASE_URL}/alipay/pay_qr/create_order/`,
            method: 'POST',
            data: requestData
        });

        // 检查状态码
        if (res.statusCode !== 200) {
            uni.showModal({
                title: `请求失败${res.statusCode}`,
                content: `，错误信息：${res.data?.detail || '未知错误'}`,
                showCancel: false
            });
            // throw new Error(`请求失败，状态码：${res.statusCode}`);
        }

        return res.data;
    } catch (error) {
        uni.showModal({
            title: '错误',
            content: error.message,
            showCancel: false
        });
        throw error;
    }
}

export async function initiatePayment(
    {order_number, user_id}
) {
    const requestData = {
        order_number,
        user_id,
        amount: 0,
        product_id: PRODUCT_ID,
        callback_url: "",
        app_id: APP_ID
    };

    try {
        const res = await uni.request({
            url: `${BASE_URL}/alipay/pay_qr/pay/`,
            method: 'POST',
            data: requestData
        });
        console.log("res ========", res);
        // 检查状态码
        if (res.statusCode !== 200) {
            uni.showModal({
                title: `请求失败${res.statusCode}`,
                content: `，错误信息：${res.data?.detail || '未知错误'}`,
                showCancel: false
            });
            // throw new Error(`请求失败，状态码：${res.statusCode}`);
        }

        return res.data;
    } catch (error) {
        uni.showModal({
            title: '错误',
            content: error.message,
            showCancel: false
        });
        throw error;
    }
}

export async function checkPaymentStatus(transaction_id) {
    try {
        const res = await uni.request({
            url: `${BASE_URL}/alipay/pay_qr/payment_status/${transaction_id}`,
            method: 'GET'
        });

        // 检查状态码
        if (res.statusCode !== 200) {
            console.log("res ========", res);

            uni.showModal({
                title: `请求失败${res.statusCode}`,
                content: `，错误信息：${res.data?.detail || '未知错误'}`,
                showCancel: false
            });
            // throw new Error(`请求失败，状态码：${res.statusCode}`);
        }

        return res.data;
    } catch (error) {
        uni.showModal({
            title: '错误',
            content: error.message,
            showCancel: false
        });
        throw error;
    }
}
