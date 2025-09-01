/**
 * 苹果内购 API 接口
 * 对接后端 api_IAP订单管理.py
 */
import { buildApiUrl } from "@/config"
import { request } from "@/src/utils/request/request"


// 基础配置
const BASE_URL = buildApiUrl('/order_center/apple_pay') // 替换为实际的API域名

// 请求类型定义
export interface ValidPurchaseRequest {
  order_number:string
  payment_price: number
  quantity?: number
  transactionIdentifier?: string
  transactionReceipt?: string
}

export interface RestoreSubscriptionRequest {
  user_id: number
  product_id: number
  transactionIdentifier: string
  transactionReceipt:string
  apple_product_id: string
}

// 响应类型定义
export interface PaymentInfo {
  order_number: string
  payment_status: string
  payment_price: number
  quantity: number
  order_id: number
  product_name: string
  app_name: string
  transaction_id?: string
  original_transaction_id?: string
  subscription_expire_date?: string
  payment_method?: string
}


// API 接口函数



export const applePayApi = {
 /**
  * 1. 验证并更新苹果内购订单
  */
  async validAndUpdateOrder(params: ValidPurchaseRequest): Promise<PaymentInfo> {
    return await request({
      url: BASE_URL + '/valid_order',
      method: 'POST',
      data: params,
      header: {
        'Content-Type': 'application/json'
      }
    }) as PaymentInfo
  },

  /**
   * 2.恢复购买
   */
  async apiRestoreSubscription(params: RestoreSubscriptionRequest): Promise<PaymentInfo> {
    return await request({
      url: buildApiUrl('/payment/apple_iap/restore-purchase'),
      method: 'POST',
      data: params,
      header: {
        'Content-Type': 'application/json'
      }
    }) as PaymentInfo
  }
}