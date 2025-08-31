<template>
  <view class="container">
    <text class="price">支付金额: ¥{{ amount }}</text>
    <button class="pay-button" @click="handlePayment">发起支付</button>
  </view>
</template>

<script>
import {
  createOrder,
  initiatePayment
} from '@/apis/pay_ali_qrcode.js';

export default {
  data() {
    return {
      amount: 0.01, // 设置不可修改的支付金额
      user_id: 'user_123',
      product_id: 0,
      callback_url: 'https://your-callback-url.com',
      app_id: 'autoJiaoAn'
    };
  },
  methods: {
    async handlePayment() {
      try {
        // 弹窗提示用户正在发起支付,为了禁止用户多次点击支付按钮
        uni.showLoading({
          title: '支付中...',
          mask: true
        });
        // 创建订单
        const orderResponse = await createOrder({
          user_id: this.user_id,
          amount: this.amount,
          product_id: this.product_id,
          callback_url: this.callback_url,
          app_id: this.app_id
        });
        console.log("orderResponse:", orderResponse);

        // 发起支付
        const paymentResponse = await initiatePayment({
          order_number: orderResponse.order_number,
          user_id: this.user_id,
          product_id: this.product_id,
          callback_url: this.callback_url,
          app_id: this.app_id
        });
        console.log("paymentResponse:", paymentResponse);
        // 跳转到页面二并传递支付信息
        console.log("跳转页面...");
        uni.navigateTo({
          url: `/pages/pay_ali_qr/page2?amount=${encodeURIComponent(this.amount)}&qr_uri=${encodeURIComponent(paymentResponse.qr_uri)}&transaction_id=${encodeURIComponent(paymentResponse.transaction_id)}`
        });
      } catch (error) {
        console.error('支付过程出错', error);
      }
    }
  }
};
</script>

<style>
.container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  background-color: #f2f2f2;
}

.price {
  font-size: 24px;
  margin-bottom: 20px;
}

.pay-button {
  padding: 10px 20px;
  background-color: #1aad19;
  color: white;
  border-radius: 5px;
}
</style>
