import { appleIAP, IapTransactionState } from "./iap-core"
import {
	applePayApi
} from './api_apple_iap'
import iapPromotionApi from './api_iap_promotion'
import {
	apiCreateAppleIapOrder,
	apiCompleteAppleIapPayment
} from './api_apple_iap_order'

declare const uni : any;

// 添加日志
const addLog = (message : string) => {
	const timestamp = new Date().toLocaleTimeString()
	console.log(`[${timestamp}] ${message}`)
}

interface ProductInfo {
	product_name : string,
	product_id : number,
	apple_product_id : string[],
	original_price : number,
	final_price : number,
	duration_days : number,
	discount_rate : number,
	discount_info : object,
	book_title : string,
}

export async function purchaseAppleIap(product_info : ProductInfo, amount:number) {
	
	addLog(`[func_apple_iap_pay] 开始调用发起内购函数，product_info = ${JSON.stringify(product_info)}`)
	// 1. init appleIAP
	try {
		await appleIAP.init()
		addLog('[func_apple_iap_pay] 苹果内购服务初始化成功')
	} catch (error) {
		console.error('IAP初始化失败:', error)
		addLog(`[func_apple_iap_pay] IAP初始化失败: ${error.message}`)
	}

	// 2. getProducts
	addLog(`[func_apple_iap_pay] 开始getProducts ${product_info.apple_product_id}`)
	const apple_products = await appleIAP.getProducts(product_info.apple_product_id)
	addLog(`[func_apple_iap_pay] 获取商品信息:${JSON.stringify(apple_products)}`)

	// 3. get which apple product's price is the same as the finalPrice
	addLog(`[func_apple_iap_pay] ${typeof(product_info.final_price)}`,);
	const apple_product = apple_products.find(product => product.price.toString() === product_info.final_price.toString())
	addLog(`[func_apple_iap_pay] 找到商品:${JSON.stringify(apple_product)}`)

	// 4. purchase 
	if (!apple_product) {
		throw new Error('未找到商品')
	}
	
	const purchaseResult = await _startPurchase(
		product_info,
		amount,
		apple_product.productid,
		null
	)
	return purchaseResult
}

// 调用后端API更新订单
async function _apiUpdateOrder(
	order_number : string,
	payment_price : number,
	quantity : number,
	transactionIdentifier : string,
	transactionReceipt : string
) {
	try {
		addLog('[func_apple_iap_pay] 更新后端订单...')
		const orderRequest = {
			order_number: order_number,
			payment_price: payment_price,
			quantity: quantity,
			transactionIdentifier: transactionIdentifier,
			transactionReceipt: transactionReceipt
		}
		const orderResult = await applePayApi.validAndUpdateOrder(orderRequest)
		addLog(`[func_apple_iap_pay] 订单创建成功: ${orderResult.order_number}`)
		return orderResult
	} catch (error) {
		console.error('创建订单失败:', error)
		addLog(`[func_apple_iap_pay] 创建订单失败: ${error.message}`)
		throw error
	}
}

// 调用后端API恢复订阅
async function _restoreSubscriptionWithBackend(transaction : any, product_id : number, apple_product_id : string) {
	try {
		addLog(`[func_apple_iap_pay] 恢复订阅: ${transaction.transactionIdentifier}`)
		const restoreRequest = {
			user_id: -9,  // 无关紧要但必须填，实际上后台使用token自动获取user_id
			product_id: product_id,
			transactionReceipt: transaction.transactionReceipt,
			transactionIdentifier: transaction.transactionIdentifier,
			apple_product_id: apple_product_id
		}
		const restoreResult = await applePayApi.apiRestoreSubscription(restoreRequest)
		addLog(`[func_apple_iap_pay] 订阅恢复成功: ${restoreResult.order_number}`)
		return restoreResult
	} catch (error) {
		console.error('[func_apple_iap_pay] 恢复订阅失败:', error)
		addLog(`[func_apple_iap_pay] 恢复订阅失败: ${error.message}`)
		throw error
	}
}



async function _startPurchase(
	product_info : ProductInfo,
	quantity : number,
	apple_product_id : string,
	apple_offer_code : string | null
) {
	addLog(`[func_apple_iap_pay] 开始支付: ${product_info.product_name}`)
	// 0. 向后端创建订单，获取订单号
	const orderResult = await apiCreateAppleIapOrder({
		product_id: product_info.product_id,
		payment_price: product_info.final_price,
		quantity: quantity,
	})
	const order_number = orderResult.order_number
	addLog(`[func_apple_iap_pay] 后端订单号: ${order_number}`)

	// 1. 如果选择了优惠券，先获取苹果签名
	let purchaseOptions : any;
	if (apple_offer_code) {
		addLog(`[func_apple_iap_pay] 使用优惠: ${apple_offer_code}`)
		try {
			const promotionRequest = {
				username: order_number,
				apple_product_id: apple_product_id,
				subscription_offer_id: apple_offer_code
			}
			addLog(`[func_apple_iap_pay] 获取优惠券签名...${JSON.stringify(promotionRequest)}`)
			const promotionResult = await iapPromotionApi(promotionRequest)
			purchaseOptions = {
				subscriptionOfferId: promotionResult.subscription_offer_id,
				applicationUsername: promotionResult.application_username,
				nonce: promotionResult.nonce,
				timestamp: promotionResult.timestamp,
				signature: promotionResult.signature,
				keyIdentifier: promotionResult.key_identifier
			}
			addLog(`[func_apple_iap_pay] 优惠券签名获取成功 ${JSON.stringify(promotionResult)}`)
		} catch (error) {
			addLog(`[func_apple_iap_pay] 获取优惠券签名失败: ${error.message}`)
			// 签名失败时继续普通购买
			purchaseOptions = undefined
		}
	}

	// 2. 发起购买
	let purchaseResult : any, transaction : any
	try {
		// 使用验证过的商品ID进行购买
		addLog(`[func_apple_iap_pay] 待购买的商品ID: ${apple_product_id}`)
		purchaseResult = await appleIAP.purchase(apple_product_id, order_number, purchaseOptions)
		transaction = {
			transactionIdentifier: purchaseResult.transactionIdentifier,
			transactionReceipt: purchaseResult.transactionReceipt,
			transactionState: purchaseResult.transactionState,
			productid: purchaseResult.payment?.productid
		}
	} catch (error) {
		console.error('[func_apple_iap_pay] 支付失败:', error)
		addLog(`[func_apple_iap_pay] 支付失败: ${error.message}`)
		return
	}

	// 3. 处理购买结果  |  只有状态为"1"且有交易标识符和交易收据才认为支付真正成功
	addLog(`[func_apple_iap_pay] 支付返回状态: ${purchaseResult.transactionState}`)
	addLog(`[func_apple_iap_pay] 支付返回详情: ${purchaseResult.productid}`)
	const state = String(purchaseResult.transactionState)
	switch (state) {
		case IapTransactionState.purchased: {
			if (purchaseResult.transactionIdentifier && purchaseResult.transactionReceipt) {
				// 添加额外验证：检查交易收据是否有效
				if (!purchaseResult.transactionReceipt || purchaseResult.transactionReceipt.length < 10) {
					addLog('[func_apple_iap_pay] 交易收据无效，支付可能未完成')
					break
				}
				// 调用后端API，更新订单
				addLog(
					`[func_apple_iap_pay] 支付成功，开始创建订单...${transaction.productid + ' | ' + JSON.stringify(transaction.transactionIdentifier)}`)
				const orderResult = await _apiUpdateOrder(
					order_number,
					product_info.final_price,
					quantity,
					transaction.transactionIdentifier,
					transaction.transactionReceipt
				)
				// 完成交易
				if (orderResult.payment_status === 'success' || orderResult.payment_status === 'paid' || orderResult.payment_status === 'completed') {
					addLog(`[func_apple_iap_pay] 后端验单成功，开始完成交易...${JSON.stringify(orderResult)}`)
					const isSuccess = await apiCompleteAppleIapPayment(transaction.transactionIdentifier)
					addLog('[func_apple_iap_pay] 交易完成')
					if (isSuccess) {
						await appleIAP.finishTransaction(transaction)
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
					addLog(`[func_apple_iap_pay] 后端验单未成功，状态: ${orderResult?.payment_status ?? 'unknown'}`)
				}
			} else {
				addLog('[func_apple_iap_pay] 状态为已购买，但尚未拿到交易ID或收据，等待用户完成验证')
			}
			break
		}
		case IapTransactionState.purchasing: {
			addLog('[func_apple_iap_pay] 支付进行中，请完成密码/FaceID 验证')
			break
		}
		case IapTransactionState.deferred: {
			addLog('[func_apple_iap_pay] 支付延期处理中，等待授权')
			break
		}
		case IapTransactionState.failed: {
			addLog('[func_apple_iap_pay] 支付失败')
			break
		}
		case IapTransactionState.restored: {
			// 复用已有的恢复订阅后端接口
			await _restoreSubscriptionWithBackend(transaction, product_info.product_id, apple_product_id)
			const isSuccess = await apiCompleteAppleIapPayment(transaction.transactionIdentifier)
			if (isSuccess) {
				await appleIAP.finishTransaction(transaction)
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
			addLog(`[func_apple_iap_pay] 支付未完成，状态: ${state}`)
			break
		}
	}

}