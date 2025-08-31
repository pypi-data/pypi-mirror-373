<template>
	<view>
		<CustomNavbar ref="navbarRef" title="快捷登录" :show-back-btn="true" @back="handleback">
		</CustomNavbar>
		<view class="login-container" :style="{ paddingTop: pageTopPadding + 'px' }">
			<!-- 渐变背景装饰 -->
			<view class="background-decoration">
				<view class="gradient-circle circle-1"></view>
				<view class="gradient-circle circle-2"></view>
				<view class="gradient-circle circle-3"></view>
			</view>

			<!-- 主内容区域 -->
			<view class="content-wrapper">
				<!-- 顶部Logo和标题区域 -->
				<view class="header-section">
					<view class="logo-container">
						<image class="logo" src="/static/logo.png" mode="aspectFit" />
					</view>
					<view class="title-section">
						<text class="main-title">欢迎光临</text>
						<text class="sub-title">请使用手机号登录您的账户</text>
					</view>
				</view>

				<!-- 登录表单卡片 -->
				<view class="form-card">
					<view class="form-content">
						<!-- 手机号输入 -->
						<view class="input-container">
							<view class="input-wrapper" :class="{ 'input-focused': phoneFocused }">
								<view class="input-icon">
									<text class="icon-phone">📱</text>
								</view>
								<input type="number" v-model="phone" placeholder="请输入手机号" maxlength="11"
									class="input-field" @focus="phoneFocused = true" @blur="phoneFocused = false" />
							</view>
						</view>

						<!-- 验证码输入 -->
						<view class="input-container">
							<view class="input-wrapper" :class="{ 'input-focused': codeFocused }">
								<view class="input-icon">
									<text class="icon-lock">🔒</text>
								</view>
								<input type="number" v-model="code" placeholder="请输入验证码" maxlength="6"
									class="input-field" @focus="codeFocused = true" @blur="codeFocused = false" />
								<button class="code-btn" :class="{ 'code-btn-disabled': codeBtnDisabled }"
									@click="getCode" :disabled="codeBtnDisabled">
									{{ codeBtnText }}
								</button>
							</view>
						</view>

						<!-- 邀请码输入 -->
						<view class="input-container">
							<view class="input-wrapper" :class="{ 'input-focused': inviteCodeFocused }">
								<view class="input-icon">
									<text class="icon-invite">🎁</text>
								</view>
								<input type="text" v-model="inviteCode" placeholder="请输入邀请码（可选）" maxlength="20"
									class="input-field" @focus="inviteCodeFocused = true" @blur="inviteCodeFocused = false" />
							</view>
							<view class="input-hint">
								<text class="hint-text">输入邀请码可获得折扣优惠</text>
							</view>
						</view>

						<!-- 登录按钮 -->
						<view class="login-btn-container">
							<button class="login-btn" :class="{ 'login-btn-active': isFormValid }" @click="login"
								:disabled="!isFormValid">
								<text class="login-btn-text">立即登录</text>
							</button>
						</view>
					</view>
				</view>

				<!-- 底部装饰 -->
				<view class="footer-decoration">
					<view class="decoration-line"></view>
					<text class="footer-text">安全登录 · 隐私保护</text>
					<view class="decoration-line"></view>
				</view>
			</view>
		</view>
	</view>
</template>

<script setup>
	import {
		ref,
		computed,
		onMounted
	} from 'vue'
	import CustomNavbar from '@/components/CustomNavbar/CustomNavbar.vue';
	import {
		sendVerificationCode,
		loginPhone
	} from './apis.ts'
	import {
		initUserInfo
	} from './api_after_register.ts'
	import {
		getAndStoreReferrerId
	} from '@/src/utils/request/refererID.ts'

	// 导航栏组件引用，用于记录导航栏高度
	const navbarRef = ref(null)
	//
	const pageTopPadding = computed(() => {
		if (navbarRef.value) {
			return navbarRef.value.getNavbarHeight() + 20
		}
		return 120 // 默认值
	})

	const phone = ref('')
	const code = ref('')
	const inviteCode = ref('')
	const codeBtnText = ref('获取验证码')
	const codeBtnDisabled = ref(false)
	const phoneFocused = ref(false)
	const codeFocused = ref(false)
	const inviteCodeFocused = ref(false)

	const isFormValid = computed(() => {
		return phone.value.length === 11 && code.value.length === 4
	})

	const referrerId = ref(null)

	onMounted(() => {
		const pages = getCurrentPages()
		const currentPage = pages[pages.length - 1]
		const fullPath = currentPage.$page.fullPath
		getAndStoreReferrerId(fullPath).then(id => {
			referrerId.value = id
		})
	})

	const handleback = () => {
		uni.switchTab({
			url: '/pages/p1_myself/p1_myself'
		})
	}

	const getCode = async () => {
		if (phone.value.length !== 11) {
			uni.showToast({
				title: '请输入正确的手机号',
				icon: 'none'
			})
			return
		}

		codeBtnDisabled.value = true
		try {
			await sendVerificationCode(phone.value)
			uni.showToast({
				title: '验证码已发送',
				icon: 'success'
			})
			let countdown = 60
			const timer = setInterval(() => {
				codeBtnText.value = `${countdown}秒后重试`
				countdown--
				if (countdown < 0) {
					clearInterval(timer)
					codeBtnText.value = '获取验证码'
					codeBtnDisabled.value = false
				}
			}, 1000)
		} catch (error) {
			uni.showToast({
				title: '发送验证码失败',
				icon: 'none'
			})
			codeBtnDisabled.value = false
		}
	}

	const login = async () => {
		if (!isFormValid.value) {
			uni.showToast({
				title: '请填写完整信息',
				icon: 'none'
			})
			return
		}

		try {
			const result = await loginPhone({
				phone: phone.value,
				sms_code: code.value,
				referer_id: inviteCode.value
			})
			console.log("result = ", result);

			if (result.access_token) {
				uni.showToast({
					title: '登录成功',
					icon: 'success'
				})
				// 调用首次注册api
				console.log("首次注册成功，执行调用首次注册api");
				await initUserInfo(referrerId.value);
				console.log("首次注册api调用完毕...");
				// 这里可以添加登录成功后的逻辑，比如跳转到首页
				uni.switchTab({
					url: "/pages/p1_myself/p1_myself"
				})
				// uni.navigateBack()
			}
		} catch (error) {

		}
	}
</script>

<style scoped>
	/* CSS变量定义 - 基于UI_Color_Guidelines.md */
	:root {
		/* 主色调 */
		--primary-purple: #667eea;
		--primary-deep-purple: #764ba2;
		--primary-blue: #4facfe;
		--primary-cyan: #00f2fe;

		/* 渐变色 */
		--gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		--gradient-success: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
		--gradient-background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #4facfe 100%);

		/* 文字颜色 */
		--text-primary: #333333;
		--text-secondary: #666666;
		--text-tertiary: #888888;
		--text-inverse: #ffffff;

		/* 背景色 */
		--bg-page: #f5f5f5;
		--bg-card: #ffffff;
		--bg-overlay-light: rgba(255, 255, 255, 0.5);

		/* 边框和阴影 */
		--border-primary: #eeeeee;
		--shadow-card: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
		--shadow-button: 0 2rpx 8rpx rgba(0, 0, 0, 0.2);
		--shadow-input: 0 0 0 2rpx rgba(102, 126, 234, 0.2);
	}

	.login-container {
		position: relative;
		width: 100vw;
		min-height: 100vh;
		background: var(--gradient-background);
		overflow: hidden;
	}

	/* 背景装饰 */
	.background-decoration {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		z-index: 0;
	}

	.gradient-circle {
		position: absolute;
		border-radius: 50%;
		background: var(--bg-overlay-light);
		backdrop-filter: blur(20rpx);
	}

	.circle-1 {
		width: 400rpx;
		height: 400rpx;
		top: -200rpx;
		right: -200rpx;
		animation: float 6s ease-in-out infinite;
	}

	.circle-2 {
		width: 300rpx;
		height: 300rpx;
		bottom: -150rpx;
		left: -150rpx;
		animation: float 8s ease-in-out infinite reverse;
	}

	.circle-3 {
		width: 200rpx;
		height: 200rpx;
		top: 50%;
		left: -100rpx;
		animation: float 7s ease-in-out infinite;
	}

	@keyframes float {

		0%,
		100% {
			transform: translateY(0px) rotate(0deg);
		}

		50% {
			transform: translateY(-20rpx) rotate(5deg);
		}
	}

	/* 主内容区域 */
	.content-wrapper {
		position: relative;
		z-index: 1;
		padding: 60rpx 40rpx 40rpx;
		min-height: 100vh;
		display: flex;
		flex-direction: column;
	}

	/* 头部区域 */
	.header-section {
		text-align: center;
		margin-bottom: 80rpx;
	}

	.logo-container {
		margin-bottom: 40rpx;
	}

	.logo {
		width: 160rpx;
		height: 160rpx;
		border-radius: 32rpx;
		box-shadow: var(--shadow-card);
	}

	.title-section {
		margin-top: 40rpx;
	}

	.main-title {
		display: block;
		font-size: 48rpx;
		font-weight: 600;
		color: var(--text-inverse);
		margin-bottom: 16rpx;
		text-shadow: 0 2rpx 4rpx rgba(0, 0, 0, 0.1);
	}

	.sub-title {
		display: block;
		font-size: 28rpx;
		color: rgba(255, 255, 255, 0.8);
		font-weight: 400;
	}

	/* 表单卡片 */
	.form-card {
		background: var(--bg-card);
		border-radius: 32rpx;
		box-shadow: var(--shadow-card);
		backdrop-filter: blur(20rpx);
		overflow: hidden;
		margin-bottom: 60rpx;
	}

	.form-content {
		padding: 60rpx 40rpx;
	}

	/* 输入框容器 */
	.input-container {
		margin-bottom: 40rpx;
	}

	.input-wrapper {
		position: relative;
		display: flex;
		align-items: center;
		background: #f8f9ff;
		border-radius: 24rpx;
		padding: 24rpx 28rpx;
		border: 2rpx solid transparent;
		transition: all 0.3s ease;
	}

	.input-wrapper.input-focused {
		border-color: var(--primary-purple);
		box-shadow: var(--shadow-input);
		background: #ffffff;
	}

	.input-icon {
		margin-right: 20rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		width: 40rpx;
		height: 40rpx;
	}

	/* CSS图标样式 */
	.icon-phone,
	.icon-lock,
	.icon-invite {
		font-size: 36rpx;
		line-height: 1;
		display: block;
	}

	.input-field {
		flex: 1;
		font-size: 32rpx;
		color: var(--text-primary);
		background: transparent;
		border: none;
		outline: none;
	}

	.input-field::placeholder {
		color: var(--text-tertiary);
		font-size: 28rpx;
	}

	/* 验证码按钮 */
	.code-btn {
		background: var(--gradient-success);
		color: var(--text-inverse);
		border: none;
		border-radius: 20rpx;
		padding: 16rpx 24rpx;
		font-size: 24rpx;
		font-weight: 500;
		box-shadow: var(--shadow-button);
		transition: all 0.3s ease;
		min-width: 160rpx;
	}

	.code-btn:active {
		transform: translateY(2rpx);
		box-shadow: 0 1rpx 4rpx rgba(0, 0, 0, 0.2);
	}

	.code-btn-disabled {
		background: linear-gradient(135deg, #cccccc 0%, #aaaaaa 100%) !important;
		color: var(--text-tertiary) !important;
		transform: none !important;
	}

	/* 登录按钮 */
	.login-btn-container {
		margin-top: 60rpx;
	}

	.login-btn {
		width: 100%;
		background: linear-gradient(135deg, #cccccc 0%, #aaaaaa 100%);
		border: none;
		border-radius: 28rpx;
		padding: 32rpx 0;
		position: relative;
		overflow: hidden;
		transition: all 0.3s ease;
	}

	.login-btn-active {
		background: var(--gradient-success);
		box-shadow: var(--shadow-button);
	}

	.login-btn-active:active {
		transform: translateY(2rpx);
	}

	.login-btn-text {
		font-size: 36rpx;
		font-weight: 600;
		color: var(--text-inverse);
		text-shadow: 0 1rpx 2rpx rgba(0, 0, 0, 0.1);
	}

	/* 底部装饰 */
	.footer-decoration {
		margin-top: auto;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 40rpx 0;
	}

	.decoration-line {
		flex: 1;
		height: 1rpx;
		background: rgba(255, 255, 255, 0.3);
		max-width: 80rpx;
	}

	.footer-text {
		margin: 0 30rpx;
		font-size: 24rpx;
		color: rgba(255, 255, 255, 0.6);
		font-weight: 300;
	}

	/* 响应式适配 */
	@media screen and (max-height: 800px) {
		.header-section {
			margin-bottom: 60rpx;
		}

		.logo {
			width: 120rpx;
			height: 120rpx;
		}

		.main-title {
			font-size: 40rpx;
		}

		.form-content {
			padding: 40rpx 30rpx;
		}

		.login-btn-container {
			margin-top: 40rpx;
		}
	}

	/* 暗黑模式适配 */
	@media (prefers-color-scheme: dark) {
		.form-card {
			background: rgba(255, 255, 255, 0.95);
		}

		.input-wrapper {
			background: #f0f0f0;
		}

		.input-wrapper.input-focused {
			background: #ffffff;
		}
	}

	/* 输入提示文字 */
	.input-hint {
		margin-top: 12rpx;
		padding-left: 60rpx;
	}

	.hint-text {
		font-size: 24rpx;
		color: var(--text-tertiary);
		line-height: 1.4;
	}
</style>