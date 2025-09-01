/**
 * 商品查询 API 接口
 * 对接后端 api_商品查询_低权限.py
 */

import { request } from '../utils/request/request';
import { buildApiUrl } from '../../config.js';

// 定义请求参数类型
export interface GetProductsParams {
  app_name: string;
  is_apple_product: boolean;
  skip?: number;
  limit?: number;
}

// 定义商品信息类型
export interface ProductInfo {
  id: number;
  product_name: string;
  product_description?: string;
  price: number;
  apple_product_id?: string;
  app_name: string;
  is_apple_product: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// 定义响应类型
export interface GetProductsResponse {
  success: boolean;
  data: ProductInfo[];
  total?: number;
  message?: string;
}



// API函数
export const productsApi = {
  /**
   * 获取所有商品
   * @param params 查询参数
   * @returns Promise<GetProductsResponse>
   */
  getAllProducts(params: GetProductsParams): Promise<GetProductsResponse> {
    // 构建查询参数
    const queryParams = new URLSearchParams();
    queryParams.append('app_name', params.app_name);
    queryParams.append('is_apple_product', params.is_apple_product.toString());
    
    if (params.skip !== undefined) {
      queryParams.append('skip', params.skip.toString());
    }
    
    if (params.limit !== undefined) {
      queryParams.append('limit', params.limit.toString());
    }

    const apiUrl = buildApiUrl(`/products/get_all_products?${queryParams.toString()}`);
    console.log(`请求URL: ${apiUrl}`);
    
    return request({
      url: apiUrl,
      method: 'GET',
      header: {
        'Content-Type': 'application/json'
      }
    }) as Promise<GetProductsResponse>;
  },

  /**
   * 获取苹果商品
   * @param app_name 应用名称
   * @param skip 跳过数量，默认0
   * @param limit 限制数量，默认100
   * @returns Promise<GetProductsResponse>
   */
  getAppleProducts(app_name: string, skip: number = 0, limit: number = 100): Promise<GetProductsResponse> {
    return this.getAllProducts({
      app_name,
      is_apple_product: true,
      skip,
      limit
    });
  },

  /**
   * 获取非苹果商品
   * @param app_name 应用名称
   * @param skip 跳过数量，默认0
   * @param limit 限制数量，默认100
   * @returns Promise<GetProductsResponse>
   */
  getNonAppleProducts(app_name: string, skip: number = 0, limit: number = 100): Promise<GetProductsResponse> {
    return this.getAllProducts({
      app_name,
      is_apple_product: false,
      skip,
      limit
    });
  }
};

// 导出默认对象（兼容不同导入方式）
export default productsApi;