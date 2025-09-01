<template>
	<view class="apple-pay-container">
		<!-- 导航栏 -->
		<view class="header">
			<text class="back-btn" @click="goBack">← 返回</text>
			<text class="title">苹果内购</text>
			<view class="header-placeholder"></view>
		</view>

		<!-- 商品信息 -->
		<view v-if="productInfo" class="product-section">
			<!-- <view class="product-card">
				<view class="product-header">
					<text class="product-name">{{ productInfo.name }}</text>
					<view class="price-info">
						<text v-if="productInfo.discountRate > 0"
							class="original-price">¥{{ productInfo.originalPrice }}</text>
						<text class="final-price">¥{{ selectedProduct?.price || productInfo.finalPrice }}</text>
					</view>
				</view>

				<view v-if="productInfo.discountRate > 0" class="discount-badge">
					<text class="discount-text">{{ (productInfo.discountRate * 10).toFixed(0) }}折优惠</text>
				</view>

				<view v-if="selectedProduct" class="apple-info">
					<text class="info-title">当前选择商品：</text>
					<text class="info-item">商品ID: {{ selectedProduct.productid }}</text>
					<text class="info-item">价格: ¥{{ selectedProduct.price }}</text>
					<text class="info-item">描述: {{ selectedProduct.description || '暂无描述' }}</text>
				</view>
			</view> -->
		</view>

		<!-- 商品选择列表 -->
		<view v-if="appleProducts.length >= 1" class="products-section">
			<text class="section-title">选择商品</text>
			<view v-for="product in appleProducts" :key="product.productid" class="product-item">
				<view class="product-content" @click="selectProduct(product)">
					<view class="product-info">
						<text class="product-id">{{ product.title }}</text>
						<text
							class="product-price">{{ getCurrencySymbol(product.pricelocal) }}{{ product.price }}</text>
						<text v-if="product.description" class="product-desc">{{ product.description }}</text>
					</view>
					<view class="selection-indicator">
						<view :class="['radio', { 'selected': selectedProduct?.productid === product.productid }]">
						</view>
					</view>
				</view>
			</view>
		</view>

		<!-- 优惠券选择 -->
		<view class="offers-section" v-if="selectedProduct?.discount && selectedProduct.discount.length > 0">
			<text class="section-title">活动优惠</text>
			<view v-for="discount in selectedProduct.discount" :key="discount.code" class="offer-item">
				<view class="offer-info">
					<text class="offer-title">{{ discount.code }}</text>
					<text
						class="offer-discount">{{ selectedCurrencySymbol }}{{ discount.price }}/{{ discount.units }}{{ discount.periodUnit === 'month' ? '月' : discount.periodUnit }}</text>
				</view>
				<button @click="selectOffer(discount)"
					:class="['offer-btn', { 'selected': selectedOffer?.code === discount.code }]">
					{{ selectedOffer?.code === discount.code ? '已选择' : '选择' }}
				</button>
			</view>
		</view>

		<!-- 操作按钮 -->
		<view class="actions">
			<text class="quantity-info">购买数量：{{ defaultQuantity }}</text>
			<button @click="startPurchase" :disabled="loading || !productInfo || !selectedProduct" class="purchase-btn">
				{{ loading ? '处理中...' : selectedProduct ? ('立即购买 ' + selectedCurrencySymbol + buttonTotalPrice) : '商品验证中...' }}
			</button>
			<button @click="handleRestorePurchases" :disabled="loading" class="restore-btn">
				恢复购买
			</button>
		</view>

		<!-- 操作日志 -->
		<view class="logs">
			<text class="log-title">操作日志:</text>
			<text v-for="(log, index) in logs" :key="index" class="log-item">
				{{ log }}
			</text>
		</view>
	</view>
</template>

<script setup>
	import {
		ref,
		computed
	} from 'vue'
	import {
		onLoad
	} from '@dcloudio/uni-app'
	import {
		applePayApi
	} from './api_apple_iap'
	import {
		apiCreateAppleIapOrder,
		apiCompleteAppleIapPayment
	} from './api_apple_iap_order'
	import {
		getCurrentUserInfo
	} from '@/src/api_account_register_login/api_update_phone'
	import iapPromotionApi from './api_iap_promotion'
	import {
		appleIAP,
		// initAppleIAP,
		// getAppleProducts,
		// purchaseProduct,
		// restoreApplePurchases,
		// finishAppleTransaction,
		IapTransactionState
	} from './iap-core'
	import {
		getCurrencySymbol
	} from './currency'

	// 响应式数据
	const productInfo = ref(null)
	const appleProducts = ref([]) // 所有苹果产品列表
	const selectedProduct = ref(null) // 当前选中的产品
	const selectedOffer = ref(null)
	const loading = ref(false)
	const logs = ref([])

	const selectedCurrencySymbol = computed(() => {
		// 优先当前选中商品的 pricelocal
		if (selectedProduct.value?.pricelocal) return getCurrencySymbol(selectedProduct.value.pricelocal)
		// 其次列表第一个商品
		if (appleProducts.value?.[0]?.pricelocal) return getCurrencySymbol(appleProducts.value[0].pricelocal)
		return '¥'
	})


	// 页面加载时获取参数
	onLoad(async (options) => {
		addLog('页面加载')
		try {
			productInfo.value = {
				name: decodeURIComponent(options.productName || ''),
				id: options.productId,
				appleProductId: JSON.parse(options.apple_product_id),
				originalPrice: parseFloat(options.originalPrice || 0),
				finalPrice: parseFloat(options.finalPrice || 0),
				duration_days: parseInt(options.duration_days) || 0,
				discountRate: parseFloat(options.discountRate || 0),
				discountInfo: options.discountInfo ? JSON.parse(decodeURIComponent(options.discountInfo)) :
				{},
				bookTitle: decodeURIComponent(options.bookTitle || '')
			}
			addLog(`商品: ${productInfo.value.appleProductId}, ${typeof(productInfo.value.appleProductId)}`)
		} catch (error) {
			console.error('参数解析失败:', error)
			addLog(`参数解析失败: ${error.message}`)
		}
		await initIAP()
		if (productInfo.value?.appleProductId) {
			await getAllAppleProductInfo()
		}
	})


	// 计算当前显示价格（选择优惠券后显示优惠价）
	const currentPrice = computed(() => {
		if (selectedOffer.value) {
			return selectedOffer.value.price
		}
		return selectedProduct.value?.price || productInfo.value?.finalPrice || '0'
	})

	// 默认购买数量：finalPrice / apple_product_price（向下取整，至少为1）
	const defaultQuantity = computed(() => {
		const total = Number(productInfo.value?.finalPrice) || 0
		const unit = Number(selectedProduct.value?.price) || 0
		if (total > 0 && unit > 0) {
			return Math.max(1, Math.floor(total / unit))
		}
		return 1
	})

	// 按钮展示的总价：购买数量 * selectedProduct.price
	const buttonTotalPrice = computed(() => {
		const unit = Number(selectedProduct.value?.price) || 0
		const qty = Number(defaultQuantity.value) || 1
		return (unit * qty).toFixed(2)
	})

	// 获取订阅周期显示文本
	const getSubscriptionPeriod = (product) => {
		if (!product) return ''

		// 通过产品ID判断是否为订阅类型
		const productId = product.productid || ''

		// 常见的订阅类型产品ID包含这些关键词
		const subscriptionKeywords = [
			'subscription', 'monthly', 'yearly', 'annual', 'week', 'month', 'year',
			'订阅', '月', '年', '周'
		]

		const isSubscription = subscriptionKeywords.some(keyword =>
			productId.toLowerCase().includes(keyword.toLowerCase())
		)

		if (!isSubscription) return ''

		// 如果当前有选中的优惠券，并且优惠券有周期信息，使用优惠券的周期
		if (selectedOffer.value && selectedOffer.value.periodUnit) {
			const periodUnit = selectedOffer.value.periodUnit
			if (periodUnit === 'month') return '/月'
			if (periodUnit === 'year') return '/年'
			if (periodUnit === 'week') return '/周'
		}

		// 根据产品ID推断周期
		if (productId.includes('week') || productId.includes('周')) {
			return '/周'
		} else if (productId.includes('month') || productId.includes('monthly') || productId.includes('月')) {
			return '/月'
		} else if (productId.includes('year') || productId.includes('yearly') || productId.includes('annual') ||
			productId.includes('年')) {
			return '/年'
		} else if (productId.includes('subscription') || productId.includes('订阅')) {
			// 默认为月度订阅
			return '/月'
		}

		return ''
	}

	// 添加日志
	const addLog = (message) => {
		const timestamp = new Date().toLocaleTimeString()
		logs.value.unshift(`[${timestamp}] ${message}`)
		if (logs.value.length > 20) logs.value.pop()
	}

	// 初始化IAP
	const initIAP = async () => {
		try {
			await appleIAP.init()
			addLog('苹果内购服务初始化成功')
		} catch (error) {
			console.error('IAP初始化失败:', error)
			addLog(`IAP初始化失败: ${error.message}`)
		}
	}

	// 获取所有苹果商品信息
	const getAllAppleProductInfo = async () => {
		if (!productInfo.value?.appleProductId) {
			addLog('商品ID无效')
			return false
		}

		loading.value = true
		try {
			addLog(`获取商品信息: ${productInfo.value.appleProductId}`)
			const result = await appleIAP.getProducts(productInfo.value.appleProductId)
			// const result = await getAppleProducts(productInfo.value.appleProductId)
			console.log(`获取商品信息:${JSON.stringify(result)}`)

			if (result && result.length > 0) {
				// 直接使用苹果返回的产品数据，其中已包含优惠券信息
				appleProducts.value = result.map(product => ({
					...product,
					discount: product.discount || [] // 确保有 discount 字段
				}))

				// 默认选择第一个产品
				if (result.length > 0) {
					selectedProduct.value = appleProducts.value[0]
				}
				addLog(`成功获取${result.length}个商品信息`)
				return true
			} else {
				addLog('未找到任何商品')
				uni.showToast({
					title: '商品不存在',
					icon: 'error'
				})
				return false
			}
		} catch (error) {
			console.error('获取商品信息失败:', error)
			addLog(`获取商品信息失败: ${error.message}`)
			return false
		} finally {
			loading.value = false
		}
	}



	// 选择产品
	const selectProduct = (product) => {
		selectedProduct.value = product
		selectedOffer.value = null // 切换产品时清除已选优惠券
		addLog(`选择产品: ${product.productid} - ${getCurrencySymbol(product.pricelocal)}${product.price}`)
	}

	// 选择优惠券
	const selectOffer = (discount) => {
		selectedOffer.value = selectedOffer.value?.code === discount.code ? null : discount
		addLog(selectedOffer.value ? `选择优惠: ${discount.code}` : '取消优惠选择')
	}

	// 发起支付
	const startPurchase = async () => {
		if (!selectedProduct.value) {
			addLog('请先选择商品')
			return
		}
		loading.value = true

		addLog(`开始支付: ${productInfo.value.name}`)
		let purchaseOptions = undefined

		// 0. 向后端创建订单，获取订单号
		const orderResult = await apiCreateAppleIapOrder({
			product_id: productInfo.value.id,
			payment_price: parseFloat(currentPrice.value),
			quantity: defaultQuantity.value,
		})
		const order_number = orderResult.order_number
		addLog(`后端订单号: ${order_number}`)

		// 1. 如果选择了优惠券，先获取苹果签名
		if (selectedOffer.value) {
			addLog(`使用优惠: ${selectedOffer.value.code}`)
			try {
				const promotionRequest = {
					username: order_number,
					apple_product_id: selectedProduct.value.productid,
					subscription_offer_id: selectedOffer.value.code || selectedOffer.value
						.subscriptionOfferId
				}
				addLog(`获取优惠券签名...${JSON.stringify(promotionRequest)}`)
				const promotionResult = await iapPromotionApi(promotionRequest)
				purchaseOptions = {
					subscriptionOfferId: promotionResult.subscription_offer_id,
					applicationUsername: promotionResult.application_username,
					nonce: promotionResult.nonce,
					timestamp: promotionResult.timestamp,
					signature: promotionResult.signature,
					keyIdentifier: promotionResult.key_identifier
				}
				// 验证必要参数
				if (!purchaseOptions.keyIdentifier) {
					throw new Error('缺少 keyIdentifier，请检查后端配置')
				}
				addLog(`优惠券签名获取成功 ${JSON.stringify(promotionResult)}`)
			} catch (error) {
				addLog(`获取优惠券签名失败: ${error.message}`)
				// 记录更详细的错误信息
				if (error.response) {
					addLog(`后端响应错误: ${JSON.stringify(error.response)}`)
				}
				// 签名失败时继续普通购买
				purchaseOptions = undefined
			}
		}

		let purchaseResult, transaction
		try {
			// 使用验证过的商品ID进行购买
			addLog(`待购买的商品ID: ${selectedProduct.value.productid}`)
			const productIdToPurchase = selectedProduct.value.productid
			purchaseResult = await appleIAP.purchase(productIdToPurchase, order_number, purchaseOptions)
			// purchaseResult = await purchaseProduct(productIdToPurchase,order_number, purchaseOptions)
			transaction = {
				transactionIdentifier: purchaseResult.transactionIdentifier,
				transactionReceipt: purchaseResult.transactionReceipt,
				transactionState: purchaseResult.transactionState,
				productid: purchaseResult.payment?.productid
			}
		} catch (error) {
			console.error('支付失败:', error)
			addLog(`支付失败: ${error.message}`)
			return
		} finally {
			loading.value = false
		}

		// 只有状态为"1"且有交易标识符和交易收据才认为支付真正成功
		addLog(`支付返回状态: ${purchaseResult.transactionState}`)
		addLog(`支付返回详情: ${purchaseResult.productid}`)
		const state = String(purchaseResult.transactionState)
		switch (state) {
			case IapTransactionState.purchased: {
				if (purchaseResult.transactionIdentifier && purchaseResult.transactionReceipt) {
					// 添加额外验证：检查交易收据是否有效
					if (!purchaseResult.transactionReceipt || purchaseResult.transactionReceipt.length < 10) {
						addLog('交易收据无效，支付可能未完成')
						break
					}
					// 调用后端API，更新订单
					addLog(
						`支付成功，开始创建订单...${transaction.productid+' | '+JSON.stringify(transaction.transactionIdentifier)}`
						)
					const orderResult = await apiUpdateOrder(order_number, transaction)
					if (orderResult.payment_status === 'success' || orderResult.payment_status === 'paid' ||
						orderResult.payment_status === 'completed') {
						addLog(`后端验单成功，开始完成交易...${JSON.stringify(orderResult)}`)
						const isSuccess = await apiCompleteAppleIapPayment(transaction.transactionIdentifier)
						addLog('交易完成')
						if (isSuccess) {
							await appleIAP.finishTransaction(transaction)
							// await finishAppleTransaction(transaction)
							uni.showToast({
								title: '支付成功！',
								icon: 'success'
							})
						} else {
							uni.showToast({
								title: '支付成功，但回调失败',
								icon: 'none'
							})
						}
					} else {
						addLog(`后端验单未成功，状态: ${orderResult?.payment_status ?? 'unknown'}`)
					}
				} else {
					addLog('状态为已购买，但尚未拿到交易ID或收据，等待用户完成验证')
				}
				break
			}
			case IapTransactionState.purchasing: {
				addLog('支付进行中，请完成密码/FaceID 验证')
				break
			}
			case IapTransactionState.deferred: {
				addLog('支付延期处理中，等待授权')
				break
			}
			case IapTransactionState.failed: {
				addLog('支付失败')
				break
			}
			case IapTransactionState.restored: {
				// 复用已有的恢复订阅后端接口
				await restoreSubscriptionWithBackend(transaction)
				const isSuccess = await apiCompleteAppleIapPayment(transaction.transactionIdentifier)
				if (isSuccess) {
					await appleIAP.finishTransaction(transaction)
					// await finishAppleTransaction(transaction)
					uni.showToast({
						title: '已恢复购买',
						icon: 'success'
					})
				} else {
					uni.showToast({
						title: '已恢复购买，但充值权限失败',
						icon: 'none'
					})
				}
				break
			}
			default: {
				addLog(`支付未完成，状态: ${state}`)
				break
			}
		}

	}

	// 恢复购买
	const handleRestorePurchases = async () => {
		loading.value = true
		try {
			addLog('恢复购买...')
			const result = await appleIAP.restorePurchases()
			// const result = await restoreApplePurchases()
			if (result.transactions?.length > 0) {
				addLog(`恢复了${result.transactions.length}个购买`)
				for (const transaction of result.transactions) {
					await restoreSubscriptionWithBackend(transaction, productInfo.value.id)
				}
				addLog('恢复完成')
			} else {
				addLog('没有可恢复的购买')
			}
		} catch (error) {
			console.error('恢复购买失败:', error)
			addLog(`恢复购买失败: ${error.message}`)
		} finally {
			loading.value = false
		}
	}

	// 调用后端API更新订单
	async function apiUpdateOrder(order_number, transaction = null) {
		try {
			addLog('创建后端订单...')
			const userInfo = getCurrentUserInfo()
			if (!userInfo || !userInfo.username) {
				throw new Error('用户未登录')
			}
			const orderRequest = {
				order_number: order_number,
				payment_price: parseFloat(currentPrice.value),
				quantity: 1,
				transactionIdentifier: transaction?.transactionIdentifier,
				transactionReceipt: transaction?.transactionReceipt
			}
			const orderResult = await applePayApi.validAndUpdateOrder(orderRequest)
			addLog(`订单创建成功: ${orderResult.order_number}`)
			return orderResult
		} catch (error) {
			console.error('创建订单失败:', error)
			addLog(`创建订单失败: ${error.message}`)
			throw error
		}
	}

	// 调用后端API恢复订阅
	const restoreSubscriptionWithBackend = async (transaction) => {
		try {
			addLog(`恢复订阅: ${transaction.transactionIdentifier}`)
			const userInfo = getCurrentUserInfo()
			if (!userInfo || !userInfo.username) {
				throw new Error('用户未登录')
			}
			const restoreRequest = {
				user_id: userInfo.username,
				product_id: productInfo.value.id,
				transactionReceipt: transaction.transactionReceipt,
				transactionIdentifier: transaction.transactionIdentifier,
				apple_product_id: transaction.productid || selectedProduct.value?.productid
			}
			const restoreResult = await applePayApi.restoreSubscription(restoreRequest)
			addLog(`订阅恢复成功: ${restoreResult.order_number}`)
			return restoreResult
		} catch (error) {
			console.error('恢复订阅失败:', error)
			addLog(`恢复订阅失败: ${error.message}`)
			throw error
		}
	}

	// 返回上一页
	const goBack = () => uni.navigateBack()
</script>

<style scoped>
	/* 基于UI颜色规范的样式系统 */

	.apple-pay-container {
		min-height: 100vh;
		background: #f5f5f5;
		padding: 0;
	}

	.header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 44px 20px 20px;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		box-shadow: 0 2rpx 20rpx rgba(0, 0, 0, 0.1);
	}

	.back-btn {
		font-size: 16px;
		color: #ffffff;
		padding: 5px;
		opacity: 0.9;
		transition: opacity 0.2s;
	}

	.back-btn:active {
		opacity: 0.7;
	}

	.title {
		font-size: 18px;
		font-weight: bold;
		color: #ffffff;
	}

	.header-placeholder {
		width: 50px;
	}

	.product-section {
		margin: 20px;
	}

	.product-card {
		background: #ffffff;
		border-radius: 12px;
		padding: 20px;
		box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
		border: 1px solid #eeeeee;
	}

	.product-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 15px;
		padding-bottom: 15px;
		border-bottom: 1px solid #f0f0f0;
	}

	.product-name {
		font-size: 18px;
		font-weight: bold;
		color: #333333;
		flex: 1;
		margin-right: 15px;
	}

	.price-info {
		text-align: right;
	}

	.original-price {
		display: block;
		font-size: 14px;
		color: #888888;
		text-decoration: line-through;
		margin-bottom: 5px;
	}

	.final-price {
		display: block;
		font-size: 20px;
		font-weight: bold;
		color: #667eea;
	}

	.discount-badge {
		display: inline-block;
		background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
		padding: 6px 14px;
		border-radius: 20px;
		margin-bottom: 15px;
		box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.2);
	}

	.discount-text {
		font-size: 12px;
		color: #8b4513;
		font-weight: bold;
	}

	.apple-info {
		margin-top: 15px;
		padding: 15px;
		background: #f8f9ff;
		border-radius: 8px;
		border: 1px solid #eeeeee;
	}

	.info-title {
		display: block;
		font-size: 14px;
		font-weight: bold;
		color: #667eea;
		margin-bottom: 10px;
		padding-bottom: 5px;
		border-bottom: 1px solid #eeeeee;
	}

	.info-item {
		display: block;
		font-size: 12px;
		color: #666666;
		margin-bottom: 5px;
		line-height: 1.4;
	}

	.discount-info {
		margin-top: 10px;
		padding: 12px;
		background: rgba(255, 255, 255, 0.5);
		border-radius: 8px;
		border-left: 3px solid #4facfe;
	}

	.discount-title {
		color: #4facfe !important;
		font-weight: bold !important;
		margin-bottom: 8px !important;
	}

	.discount-item {
		margin-bottom: 5px;
		padding-left: 10px;
	}

	.products-section {
		margin: 0 20px 20px;
	}

	.product-item {
		background: #ffffff;
		border-radius: 12px;
		margin-bottom: 10px;
		box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
		border: 1px solid #eeeeee;
		overflow: hidden;
	}

	.product-content {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 15px;
		transition: background-color 0.2s;
	}

	.product-content:active {
		background-color: #f8f9ff;
	}

	.product-info {
		flex: 1;
	}

	.product-id {
		display: block;
		font-size: 16px;
		font-weight: bold;
		color: #333333;
		margin-bottom: 5px;
	}

	.product-price {
		display: block;
		font-size: 18px;
		font-weight: bold;
		color: #667eea;
		margin-bottom: 5px;
	}

	.product-desc {
		display: block;
		font-size: 14px;
		color: #666666;
		line-height: 1.4;
	}

	.selection-indicator {
		margin-left: 15px;
	}

	.radio {
		width: 20px;
		height: 20px;
		border-radius: 50%;
		border: 2px solid #cccccc;
		background: #ffffff;
		transition: all 0.2s;
		position: relative;
	}

	.radio.selected {
		border-color: #667eea;
		background: #667eea;
	}

	.radio.selected::after {
		content: '';
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background: #ffffff;
	}

	.offers-section {
		margin: 0 20px 20px;
	}

	.section-title {
		display: block;
		font-size: 16px;
		font-weight: bold;
		color: #333333;
		margin-bottom: 15px;
	}

	.offer-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		background: #ffffff;
		padding: 15px;
		border-radius: 12px;
		margin-bottom: 10px;
		box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
		border: 1px solid #eeeeee;
		transition: transform 0.2s, box-shadow 0.2s;
	}

	.offer-item:active {
		transform: translateY(1px);
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
	}

	.offer-info {
		flex: 1;
	}

	.offer-title {
		display: block;
		font-size: 16px;
		font-weight: bold;
		color: #333333;
		margin-bottom: 5px;
	}

	.offer-discount {
		display: block;
		font-size: 14px;
		color: #667eea;
		font-weight: 500;
	}

	.offer-btn {
		background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
		color: #ffffff;
		border: none;
		padding: 8px 16px;
		border-radius: 20px;
		font-size: 14px;
		min-width: 60px;
		box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.2);
		transition: transform 0.2s;
	}

	.offer-btn:active {
		transform: scale(0.95);
	}

	.offer-btn.selected {
		background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
		color: #8b4513;
	}

	.offer-btn:disabled {
		background: rgba(200, 200, 200, 0.2);
		color: #888888;
		box-shadow: none;
	}

	.actions {
		margin: 0 20px 20px;
		display: flex;
		flex-direction: column;
		gap: 15px;
	}

	.quantity-info {
		font-size: 14px;
		color: #555555;
		margin-bottom: -5px;
	}

	.purchase-btn {
		background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
		color: #ffffff;
		border: none;
		padding: 16px;
		border-radius: 12px;
		font-size: 16px;
		font-weight: bold;
		box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.2);
		transition: transform 0.2s, box-shadow 0.2s;
	}

	.purchase-btn:active {
		transform: translateY(1px);
		box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
	}

	.purchase-btn:disabled {
		background: rgba(200, 200, 200, 0.2);
		color: #888888;
		box-shadow: none;
		transform: none;
	}

	.restore-btn {
		background: linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%);
		color: #5a67d8;
		border: none;
		padding: 12px;
		border-radius: 12px;
		font-size: 14px;
		box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.2);
		transition: transform 0.2s;
	}

	.restore-btn:active {
		transform: translateY(1px);
	}

	.restore-btn:disabled {
		background: rgba(200, 200, 200, 0.2);
		color: #888888;
		box-shadow: none;
	}

	.logs {
		margin: 0 20px 20px;
		background: #ffffff;
		padding: 15px;
		border-radius: 12px;
		max-height: 200px;
		overflow-y: auto;
		box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
		border: 1px solid #eeeeee;
	}

	.log-title {
		display: block;
		font-weight: bold;
		margin-bottom: 10px;
		color: #333333;
		padding-bottom: 8px;
		border-bottom: 1px solid #f0f0f0;
	}

	.log-item {
		display: block;
		font-size: 12px;
		color: #666666;
		margin-bottom: 5px;
		line-height: 1.4;
		word-break: break-all;
		padding: 2px 0;
	}
</style>