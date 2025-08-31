/**
 * 苹果内购核心模块
 * 简洁的IAP功能封装，避免过度抽象
 */

// 使用 declare global 来访问 uni 对象
declare const uni : any

export const IapTransactionState = {
	purchasing: "0", // A transaction that is being processed by the App Store.
	purchased: "1", // A successfully processed transaction.
	failed: "2", // A failed transaction.
	restored: "3", // A transaction that restores content previously purchased by the user.
	deferred: "4" // A transaction that is in the queue, but its final status is pending external action such as Ask to Buy.
};

export interface OfferOptions {
	subscriptionOfferId : string
	keyIdentifier : string
	nonce : string
	signature : string
	timestamp : number
	applicationUsername ?: string
}

export interface Transaction {
	transactionIdentifier : string
	transactionReceipt : string
	transactionState : string
	productid ?: string
}

export interface ProductInfo {
	productid : string
	price : string
	description ?: string
	discount ?: any[]
}

class AppleIAP {
	private iapChannel : any = null

	// 初始化IAP服务
	async init() : Promise<void> {
		return new Promise((resolve, reject) => {
			uni.getProvider({
				service: 'payment',
				success: (res) => {
					const provider = res.providers.find(p => p.id === 'appleiap')
					if (!provider) {
						reject(new Error('IAP服务不可用'))
					} else {
						this.iapChannel = provider
						resolve()
					}
				},
				fail: reject
			})
		})
	}

	// 获取商品信息
	async getProducts(productIds : string[]) : Promise<ProductInfo[]> {
		if (!this.iapChannel) throw new Error('IAP未初始化')

		return new Promise((resolve, reject) => {
			this.iapChannel.requestProduct(productIds, resolve, reject)
		})
	}

	// 购买商品
	async purchase(productId : string, order_number ?: string, offerOptions ?: OfferOptions) : Promise<Transaction> {
		if (!this.iapChannel) throw new Error('IAP未初始化')

		const orderInfo : any = {
			productid: productId,
			manualFinishTransaction: true,
		}
		if (order_number) {
			orderInfo.username = order_number
		}

		// 添加优惠券参数
		if (offerOptions) {
			orderInfo.paymentDiscount = {
				offerIdentifier: offerOptions.subscriptionOfferId,
				keyIdentifier: offerOptions.keyIdentifier,
				nonce: offerOptions.nonce,
				signature: offerOptions.signature,
				timestamp: Math.round(offerOptions.timestamp)
			}
			// orderInfo.paymentDiscount = {
			// 	identifier: offerOptions.subscriptionOfferId,
			// 	keyIdentifier: offerOptions.keyIdentifier,
			// 	nonce: offerOptions.nonce,
			// 	signature: offerOptions.signature,
			// 	timestamp: Math.round(offerOptions.timestamp)
			// }
			if (offerOptions.applicationUsername) {
				orderInfo.username = offerOptions.applicationUsername
			}
			console.log(`优惠券参数， timestamp = ${orderInfo.paymentDiscount.timestamp}`)
			console.log(`发起支付参数orderInfo = ${JSON.stringify(orderInfo)}`)
		}

		return new Promise((resolve, reject) => {
			uni.requestPayment({
				provider: 'appleiap',
				orderInfo,
				success: resolve,
				fail: reject
			})
		})
	}

	// 恢复购买
	async restorePurchases(order_number ?: string) : Promise<{ transactions : Transaction[] }> {
		if (!this.iapChannel) throw new Error('IAP未初始化')

		const orderInfo : any = {
			manualFinishTransaction: true,
		}
		if (order_number) {
			orderInfo.username = order_number
		}

		return new Promise((resolve, reject) => {
			this.iapChannel.restoreCompletedTransactions(orderInfo, resolve, reject)
		})
	}

	// 完成交易
	async finishTransaction(transaction : Transaction) : Promise<void> {
		if (!this.iapChannel) throw new Error('IAP未初始化')

		return new Promise((resolve, reject) => {
			this.iapChannel.finishTransaction(transaction, resolve, reject)
		})
	}

	// 检查是否已初始化
	get isInitialized() : boolean {
		return this.iapChannel !== null
	}
}

// 导出单例实例
export const appleIAP = new AppleIAP()

// 导出便捷方法
// export const initAppleIAP = () => appleIAP.init()
// export const getAppleProducts = (productIds : string[]) => appleIAP.getProducts(productIds)
// export const purchaseProduct = (productId : string, order_number ?: string, offerOptions ?: OfferOptions) =>
// 	appleIAP.purchase(productId, order_number, offerOptions)
// export const restoreApplePurchases = (order_number ?: string) => appleIAP.restorePurchases(order_number)
// export const finishAppleTransaction = (transaction : Transaction) =>
// 	appleIAP.finishTransaction(transaction)