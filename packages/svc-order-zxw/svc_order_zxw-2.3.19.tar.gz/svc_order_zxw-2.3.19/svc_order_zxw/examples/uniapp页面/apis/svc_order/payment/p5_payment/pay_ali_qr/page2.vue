<template>
	<view class="page-container">
		<CustomNavbar ref="navbarRef" title="支付确认" :showBackBtn="true" @back="handleBack" @ready="handleNavbarReady" />

		<!-- 加载状态 -->
		<view v-if="isLoading" class="loading-container" :style="{ paddingTop: navbarHeight + 'px' }">
			<view class="loading-spinner"></view>
			<text class="loading-text">正在生成支付订单...</text>
		</view>

		<!-- 支付内容 -->
		<view v-else class="container" :style="{ paddingTop: navbarHeight + 'px' }">
			<view class="payment-card">
				<view class="payment-header">
					<text class="payment-title">支付金额</text>
				</view>
				<text class="payment-price">¥{{ payment_price }}</text>
				<text class="quantity-text">购买数量: {{ quantity }}</text>
				<view class="qr-code-container">
					<image v-if="qr_img" :src="qr_img" class="qr-code-image"></image>
					<view v-else class="qr-code-placeholder">
						<text class="placeholder-text">正在生成二维码...</text>
					</view>
				</view>
				<view v-if="isMobile" class="mobile-pay-link">
					<a :href="qr_uri" target="_blank" class="app-pay-button">去支付宝支付</a>
				</view>
				<text class="payment-tip">{{ isMobile ? '点击按钮跳转支付宝支付' : '请使用支付宝扫码支付' }}</text>
			</view>
			<button class="status-button" @click="checkStatus">确认已支付</button>
		</view>
	</view>
</template>

<script setup>
	import {
		ref,
		onMounted
	} from 'vue';
	import {
		onLoad
	} from '@dcloudio/uni-app';
	import {
		orderApi
	} from './api_app_url';
	import CustomNavbar from '@/components/CustomNavbar/CustomNavbar.vue';

	// 导航栏引用和高度
	const navbarRef = ref(null);
	const navbarHeight = ref(120); // 默认高度

	const payment_price = ref(0);
	const product_id = ref(1);
	const quantity = ref(1);
	const qr_uri = ref('');
	const order_number = ref('');
	const qr_img = ref('');
	const isMobile = ref(false);
	const isLoading = ref(true);

	// 导航栏准备就绪事件
	const handleNavbarReady = (data) => {
		console.log('导航栏准备就绪', data);
		// 动态获取导航栏高度
		if (navbarRef.value) {
			navbarHeight.value = navbarRef.value.getNavbarHeight() + 20;
		}
	};

	onLoad((options) => {
		// 从URL参数加载支付信息
		payment_price.value = parseFloat(options.paymentPrice || options.payment_price || 0.01);
		product_id.value = parseInt(options.productId || options.product_id || 1);
		quantity.value = parseInt(options.quantity || 1);

		console.log("payment_price:", payment_price.value);
		console.log("product_id:", product_id.value);
		console.log("quantity:", quantity.value);

		// 检测平台类型 - 使用uni-app API
		// #ifdef H5
		const userAgent = navigator.userAgent.toLowerCase();
		isMobile.value = /mobile|android|iphone|ipad|phone/i.test(userAgent);
		// #endif

		// #ifdef MP
		isMobile.value = true; // 小程序环境默认为移动端
		// #endif 

		// #ifdef APP-PLUS
		isMobile.value = true; // APP环境默认为移动端
		// #endif
	});

	onMounted(() => {
		// 自动创建订单和发起支付
		handlePayment();
	});

	const handlePayment = async () => {

		isLoading.value = true;
		let orderResponse = null;
		
		try {
			// 创建订单
			orderResponse = await orderApi.createAlipayOrder({
				product_id: product_id.value,
				payment_price: payment_price.value,
				quantity: quantity.value
			});
			console.log("orderResponse:", orderResponse);
		} catch (error) {
			console.error('创建订单失败', error);
			uni.showToast({
				title: '创建订单失败',
				icon: 'none'
			});
			isLoading.value = false;
			return;
		}

		try {
			// 发起支付
			const paymentResponse = await orderApi.initiateAlipayPayment({
				order_number: orderResponse.order_number
			});
			console.log("paymentResponse:", paymentResponse);
			// 设置支付信息
			qr_uri.value = paymentResponse.qr_uri;
			order_number.value = paymentResponse.order_number;
			// 生成二维码
			await generateQRCode();
		} catch (error) {
			console.error('发起支付失败', error);
			uni.showToast({
				title: '发起支付失败',
				icon: 'none'
			});
			return;
		} finally {
			isLoading.value = false;
		}
	};

	const generateQRCode = async () => {
		try {
			// 使用在线二维码生成服务
			const qrCodeUrl =
				`https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=${encodeURIComponent(qr_uri.value)}`;
			qr_img.value = qrCodeUrl;
		} catch (error) {
			console.error('生成二维码时发生错误:', error);
			uni.showToast({
				title: '二维码生成失败',
				icon: 'none'
			});
		}
	};

	const checkStatus = async () => {
		try {
			const paymentResponse = await orderApi.queryAlipayPaymentStatus({
				order_number: order_number.value
			});
			if (paymentResponse.payment_status === 'paid') {
				uni.showToast({
					title: '支付成功',
					icon: 'success'
				});
				uni.switchTab({
					url: '/pages/p1_myself/p1_myself'
				});
			} else {
				uni.showToast({
					title: '支付未完成',
					icon: 'none'
				});
			}
		} catch (error) {
			console.error('查询支付状态出错', error);
			uni.showToast({
				title: '查询支付状态失败',
				icon: 'none'
			});
		}
	};

	// 返回按钮处理
	const handleBack = () => {
		uni.navigateBack({
			delta: 1
		});
	};
</script>

<style lang="scss">
	/* 引入UI颜色规范变量 - 完全按照 UI_Color_Guidelines.md 规范 */
	:root {
		/* 品牌主色 */
		--primary-purple: #667eea;
		--primary-deep-purple: #764ba2;
		--primary-blue: #4facfe;
		--primary-cyan: #00f2fe;

		/* 辅助色 */
		--secondary-warm-light: #ffecd2;
		--secondary-warm-deep: #fcb69f;
		--secondary-soft-pink: #fbc2eb;
		--secondary-soft-blue: #a6c1ee;

		/* 渐变色 */
		--gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		--gradient-progress: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #4facfe 100%);
		--gradient-success: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
		--gradient-warning: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
		--gradient-cancel: linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%);

		/* 文字颜色 */
		--text-primary: #333333;
		--text-secondary: #666666;
		--text-tertiary: #888888;
		--text-inverse: #ffffff;
		--text-warning: #8b4513;
		--text-cancel: #5a67d8;

		/* 背景色 */
		--bg-page: #f5f5f5;
		--bg-card: #ffffff;
		--bg-card-header: #f8f9ff;
		--bg-overlay-light: rgba(255, 255, 255, 0.5);
		--bg-overlay-gray: rgba(200, 200, 200, 0.2);

		/* 边框 */
		--border-primary: #eeeeee;
		--border-secondary: #f0f0f0;
		--border-emphasis: rgba(255, 255, 255, 1);

		/* 阴影 */
		--shadow-card: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
		--shadow-header: 0 2rpx 20rpx rgba(0, 0, 0, 0.1);
		--shadow-bottom: 0 -4rpx 20rpx rgba(0, 0, 0, 0.1);
		--shadow-button: 0 2rpx 8rpx rgba(0, 0, 0, 0.2);
		--shadow-progress: 0 0 10rpx rgba(102, 126, 234, 0.3);
	}

	.page-container {
		height: 100vh;
		background-color: var(--bg-page);
		overflow: hidden;
	}

	.loading-container {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		height: 100%;
	}

	.loading-spinner {
		width: 40rpx;
		height: 40rpx;
		border: 3rpx solid var(--bg-overlay-gray);
		border-top: 3rpx solid var(--primary-purple);
		border-radius: 50%;
		animation: spin 1s linear infinite;
		margin-bottom: 20rpx;
	}

	@keyframes spin {
		0% {
			transform: rotate(0deg);
		}

		100% {
			transform: rotate(360deg);
		}
	}

	.loading-text {
		font-size: 32rpx;
		color: var(--text-secondary);
		margin-top: 20rpx;
	}

	.container {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		height: 100%;
		padding: 20rpx;
		box-sizing: border-box;
		overflow: hidden;
	}

	.payment-card {
		background-color: var(--bg-card);
		border-radius: 24rpx;
		padding: 0;
		box-shadow: var(--shadow-card);
		display: flex;
		flex-direction: column;
		align-items: center;
		width: 90%;
		max-width: 700rpx;
		overflow: hidden;
		flex: 1;
		min-height: 0;
	}

	.payment-header {
		width: 100%;
		background-color: var(--bg-card-header);
		padding: 20rpx;
		display: flex;
		justify-content: center;
		border-bottom: 1rpx solid var(--border-primary);
	}

	.payment-title {
		font-size: 32rpx;
		color: var(--text-secondary);
		font-weight: 500;
	}

	.payment-price {
		font-size: 60rpx;
		font-weight: bold;
		color: var(--text-primary);
		margin: 20rpx 0 15rpx 0;
	}

	.quantity-text {
		font-size: 28rpx;
		color: var(--text-tertiary);
		margin-bottom: 25rpx;
	}

	.qr-code-container {
		width: 320rpx;
		height: 320rpx;
		display: flex;
		justify-content: center;
		align-items: center;
		background-color: var(--bg-card);
		border-radius: 16rpx;
		box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);
		margin-bottom: 25rpx;
		border: 2rpx solid var(--border-secondary);
	}

	.qr-code-image {
		width: 300rpx;
		height: 300rpx;
		border-radius: 12rpx;
	}

	.qr-code-placeholder {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100%;
	}

	.placeholder-text {
		font-size: 28rpx;
		color: var(--text-tertiary);
	}

	.mobile-pay-link {
		margin: 20rpx 0;
	}

	.app-pay-button {
		display: inline-block;
		padding: 24rpx 60rpx;
		background: var(--gradient-success);
		color: var(--text-inverse);
		text-decoration: none;
		border-radius: 50rpx;
		font-size: 32rpx;
		font-weight: 500;
		box-shadow: var(--shadow-button);
		transition: all 0.3s ease;

		&:active {
			transform: translateY(2rpx);
			box-shadow: 0 1rpx 4rpx rgba(0, 0, 0, 0.2);
		}
	}

	.payment-tip {
		font-size: 28rpx;
		color: var(--text-secondary);
		margin-bottom: 20rpx;
		text-align: center;
		line-height: 1.5;
	}

	.status-button {
		margin-top: 30rpx;
		padding: 24rpx 60rpx;
		background: var(--gradient-primary);
		color: var(--text-inverse);
		font-size: 32rpx;
		font-weight: 500;
		border: none;
		border-radius: 50rpx;
		box-shadow: var(--shadow-button);
		transition: all 0.3s ease;

		&:active {
			transform: translateY(2rpx);
			box-shadow: 0 1rpx 4rpx rgba(0, 0, 0, 0.2);
		}
	}

	/* 响应式设计 */
	@media (max-width: 750rpx) {
		.payment-card {
			width: 95%;
			margin: 0 20rpx;
		}

		.qr-code-container {
			width: 280rpx;
			height: 280rpx;
		}

		.qr-code-image {
			width: 260rpx;
			height: 260rpx;
		}

		.payment-price {
			font-size: 52rpx;
		}
	}
</style>