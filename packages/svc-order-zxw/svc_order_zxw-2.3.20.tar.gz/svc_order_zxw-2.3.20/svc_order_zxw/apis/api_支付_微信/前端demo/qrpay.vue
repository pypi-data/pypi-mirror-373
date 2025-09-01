<template>
  <view class="container">
    <view class="qr-container">
      <image :src="decodedPaymentUrl" style="width: 200px; height: 200px;"/>
      <view class="status-message">{{ statusMessage }}</view>
    </view>
  </view>
</template>

<script>
import {getOrderStatus} from '@/api.js';

export default {
  data() {
    return {
      paymentUrl: '',
      orderNumber: '',
      statusMessage: '请扫描二维码进行支付',
    };
  },
  computed: {
    decodedPaymentUrl() {
      return decodeURIComponent(this.paymentUrl);
    },
  },
  onLoad(options) {
    this.paymentUrl = options.paymentUrl;
    this.orderNumber = options.orderNumber;
    this.checkPaymentStatus();
  },
  methods: {
    async checkPaymentStatus() {
      try {
        const statusResponse = await getOrderStatus(this.orderNumber);
        if (statusResponse.status === 'PAID') {
          this.statusMessage = '支付成功，正在跳转...';
          setTimeout(() => {
            uni.redirectTo({
              url: '/pages/success/success', // 替换为支付成功后的页面
            });
          }, 2000);
        } else if (statusResponse.status === 'FAILED') {
          this.statusMessage = '支付失败，请重试';
        } else {
          setTimeout(this.checkPaymentStatus, 3000); // 每3秒检测一次支付状态
        }
      } catch (error) {
        this.statusMessage = '支付状态获取失败';
        console.error(error);
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
  flex-direction: column;
}

.qr-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.status-message {
  margin-top: 20px;
  font-size: 16px;
  color: #333;
}
</style>
