// api.js
export const createPayment = async (productId, userId, paymentMethod, callbackUrl) => {
    try {
        const response = await uni.request({
            url: 'https://localhost:8000/wechat/pay_h5/create_payment/', // 替换为你的API地址
            method: 'POST',
            data: {
                product_id: productId,
                user_id: userId,
                payment_method: paymentMethod,
                callback_url: callbackUrl,
            },
        });
        return response[1].data;
    } catch (error) {
        console.error("Create payment failed:", error);
        throw error;
    }
};

export const getOrderStatus = async (orderNumber) => {
    try {
        const response = await uni.request({
            url: `https://your-api-url/wechat/pay_h5/order_status/${orderNumber}`, // 替换为你的API地址
            method: 'GET',
        });
        return response[1].data;
    } catch (error) {
        console.error("Get order status failed:", error);
        throw error;
    }
};
