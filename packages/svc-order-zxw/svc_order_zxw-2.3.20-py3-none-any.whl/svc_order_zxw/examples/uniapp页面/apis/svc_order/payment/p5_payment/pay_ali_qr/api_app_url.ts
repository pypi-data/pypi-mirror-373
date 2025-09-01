import {request} from '@/src/utils/request/request';
import { buildApiUrl } from '@/config.js'


// 定义返回类型
interface CreateOrderResponse {
  user_id: string;
  product_id: number;
  order_number: string;
  total_price: number;
  payment_price: number;
  quantity: number;
  status: string;
}

interface PaymentResponse {
  order_number: string;
  payment_status: string;
  payment_price: number;
  quantity: number;
  order_id: number;
  product_name: string;
  app_name: string;
  qr_uri?: string;
}

// API函数
export const orderApi = {
  // 创建支付宝订单
  createAlipayOrder(data: {
    product_id: number;
    payment_price: number;
    quantity: number;
  }): Promise<CreateOrderResponse> {
	  console.log(buildApiUrl('/payment/alipay/create-order'));
    return request({
      url: buildApiUrl('/payment/alipay/create-order'),
      method: 'POST',
      data
    }) as Promise<CreateOrderResponse>;
  },

  // 发起支付宝支付
  initiateAlipayPayment(data: {
    order_number: string;
  }): Promise<PaymentResponse> {
    return request({
      url: buildApiUrl('/payment/alipay'),
      method: 'POST',
      data
    }) as Promise<PaymentResponse>;
  },

  // 查询支付宝支付状态
  queryAlipayPaymentStatus(params: {
    order_number: string;
  }): Promise<PaymentResponse> {
    return request({
      url: buildApiUrl(`/payment/alipay?order_number=${encodeURIComponent(params.order_number)}`),
      method: 'GET'
    }) as Promise<PaymentResponse>;
  }
};