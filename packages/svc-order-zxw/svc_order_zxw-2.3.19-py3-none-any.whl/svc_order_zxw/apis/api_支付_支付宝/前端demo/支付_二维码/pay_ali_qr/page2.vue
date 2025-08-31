<template>
	<div class="container">
		<text class="amount">支付金额: ¥{{ amount }}</text>
		<div ref="qrCodeContainer" class="qr-code-container"></div>
		<button class="status-button" @click="checkStatus">已支付</button>
	</div>
</template>

<script>
	import {
		checkPaymentStatus
	} from '@/apis/pay_ali_qrcode.js';
	import QRCode from 'qrcodejs2';

	export default {
		data() {
			return {
				amount: 0,
				qr_uri: '',
				transaction_id: '',
				qr_img: ''
			};
		},
		onLoad(options) {
			this.amount = options.amount;
			this.qr_uri = decodeURIComponent(options.qr_uri);
			this.transaction_id = options.transaction_id;
		},
		onReady() {
			this.generateQRCode();
		},
		methods: {
			generateQRCode() {
				const containerEl = this.$refs.qrCodeContainer;
				if (containerEl) {
					containerEl.innerHTML = '';
					new QRCode(containerEl, {
						text: this.qr_uri,
						width: 250,
						height: 250,
						colorDark: "#000000",
						colorLight: "#ffffff",
            correctLevel: QRCode.CorrectLevel.H
          });
          // Convert canvas to image
          setTimeout(() => {
            const canvas = containerEl.querySelector('canvas');
            if (canvas) {
              this.qr_img = canvas.toDataURL('image/png');
            } else {
              console.error('二维码生成失败：未找到canvas元素');
            }
          }, 500);
        } else {
          console.error('无法找到二维码生成的容器元素');
        }
      },
      async checkStatus() {
        try {
          const paymentStatus = await checkPaymentStatus(this.transaction_id);
          if (paymentStatus.payment_status === 'SUCCESS') {
            uni.showToast({
              title: '支付成功',
              icon: 'success'
            });
            uni.navigateTo({
              url: '/pages/success/success'
            });
          } else {
            uni.showModal({
              title: '支付失败',
              content: '请重试或检查您的支付信息',
              showCancel: false
            });
          }
        } catch (error) {
          console.error('查询支付状态出错', error);
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
  height: 100vh;
  background-color: #f2f2f2;
  padding: 20px;
  box-sizing: border-box;
}

.amount {
  font-size: 28px;
  font-weight: bold;
  color: #333;
  margin-bottom: 30px;
}

.qr-code-container {
  width: 250px;
  height: 250px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.status-button {
  padding: 12px 24px;
  background-color: #0a8a2b;
  /* 更深的绿色，表达确认和完成 */
  color: white;
  font-size: 18px;
  border: none;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.status-button:hover {
  background-color: #075f1e;
  /* 悬停时颜色变得更深，强化点击意图 */
}
</style>
