<template>
  <view class="container">
    <button @click="initiatePayment" class="pay-button">微信支付</button>
  </view>
</template>
<script>
import {createPayment, getOrderStatus} from '@/api.js';

export default {
  data() {
    return {
      productId: 1, // 替换为真实的产品ID
      userId: 'user_123', // 替换为真实的用户ID
      paymentMethod: 'WeChat', // 替换为真实的支付方式
      callbackUrl: 'https://your-callback-url/', // 替换为你的回调地址
    };
  },
  methods: {
    async initiatePayment() {
      try {
        uni.showLoading({
          title: '支付验证中...',
        });

        const paymentResponse = await createPayment(this.productId, this.userId, this.paymentMethod, this.callbackUrl);

        // 跳转到二维码支付页面，并传递支付链接
        uni.navigateTo({
          url: `/pages/qrpay/qrpay?paymentUrl=${encodeURIComponent(paymentResponse.payment_url)}&orderNumber=${paymentResponse.order_number}`,
        });

        uni.hideLoading();
      } catch (error) {
        uni.hideLoading();
        uni.showToast({
          title: '支付请求失败',
          icon: 'none',
        });
      }
    },
  },
};
</script>

<style scoped>
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

.pay-button {
  padding: 10px 20px;
  background-color: #1AAD19;
  color: white;
  border-radius: 5px;
}
</style>
