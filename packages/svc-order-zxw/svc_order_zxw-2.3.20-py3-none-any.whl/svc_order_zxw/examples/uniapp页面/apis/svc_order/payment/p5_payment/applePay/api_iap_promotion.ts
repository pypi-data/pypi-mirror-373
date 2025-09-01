/**
 * 苹果内购优惠券管理 API 接口
 * 对接后端 api_IAP优惠券管理.py
 */
import { buildApiUrl } from "@/config"
import { request } from "@/src/utils/request/request"

// 请求类型定义
export interface CreatePromotionRequest {
  username: string
  apple_product_id: string
  subscription_offer_id: string
}

// 响应类型定义
export interface PromotionSignatureResult {
  product_id: string
  subscription_offer_id: string
  application_username: string
  nonce: string
  timestamp: number
  signature: string
  key_identifier: string // 苹果密钥标识符 (必需)
  created_at: string
}

async function iapPromotionApi(params: CreatePromotionRequest): Promise<PromotionSignatureResult>{
	/**
	 * 创建苹果内购优惠券签名
	 * @param params 创建参数
	 * @returns Promise<PromotionSignatureResult>
	 */
	
	// 构建URL参数
	const urlParams = {
		...params
	};
	// 将参数转换为查询字符串
	const queryString = Object.entries(urlParams)
		.map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
		.join('&');
	
	const baseUrl = buildApiUrl('order_center/apple_pay/promotion/create');
	const url = `${baseUrl}?${queryString}`;
	
	const result = await request({
		url,
		method: 'POST'
	}) as PromotionSignatureResult
	console.log("[iapPromotionApi], result = ", JSON.stringify(result));
	return result;
}


// 导出默认对象
export default iapPromotionApi