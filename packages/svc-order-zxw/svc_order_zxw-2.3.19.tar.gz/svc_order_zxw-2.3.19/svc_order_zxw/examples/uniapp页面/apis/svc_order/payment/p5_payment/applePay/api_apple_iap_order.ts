import { buildApiUrl } from "@/config"
import { request } from "@/src/utils/request/request"

declare const uni: any;

export type ModelCreateOrder = {
  product_id: number;
  payment_price: number;
  quantity: number;
};

export type OrderStatus = 'pending' | 'paid' | 'failed' | 'cancelled' | 'finished';

export type Model创建订单返回值 = {
  user_id: number;
  product_id: number;
  order_number: string;
  total_price: number;   // 原始价格
  payment_price: number; // 实际支付金额
  quantity: number;
  status: OrderStatus;
};

// 创建苹果内购订单
export async function apiCreateAppleIapOrder(payload: ModelCreateOrder): Promise<Model创建订单返回值> {
  const response = await request({
    url: buildApiUrl(`/payment/apple_iap/create-order`),
    method: 'POST',
    data: payload,
  });
  console.log("[apiCreateAppleIapOrder], response = ", JSON.stringify(response));
  return response as Model创建订单返回值;
}

// 支付完成后通知后端进行权限充值（苹果回调确认）
export async function apiCompleteAppleIapPayment(transactionId: string): Promise<boolean> {
  const response = await request({
    url: buildApiUrl(`/payment/apple_iap/payment_recall`),
    method: 'GET',
    data: { transaction_id: transactionId },
  });
  console.log("[apiCompleteAppleIapPayment], response = ", JSON.stringify(response));
  return response as boolean;
}