import { buildApiUrl } from '../../config.js'
import { request } from '../../src/utils/request/request'

// 定义商品信息返回类型
export interface ProductInfo {
  id: number;
  name: string;
  description: string;
  original_price: number;
  final_price: number;
  discount_rate: number;
  invited_count: number;
  app_name: string;
  duration_days: number;
  features: string[];
  discount_info: {
    current_discount: string;      // 当前折扣百分比，如 "20%"
    discount_source: string;       // 折扣来源，如 "inviter" 或 "invitee"
    description: string;           // 折扣描述
    is_invitee: boolean;          // 是否为被邀请者
    activity_active: boolean;      // 活动是否激活
  };
}

// 定义邀请活动信息返回类型
export interface InvitationActivity {
  activity: {
    name: string;
    description: string;
    is_active: boolean;
  };
  user_status: {
    user_id: number;
    invited_count: number;
    is_invitee: boolean;
    current_discount: {
      discount_rate: number;
      discount_source: string;
      description: string;
    };
    next_discount: {
      need_invites: number;
      target_discount: string;
      description: string;
    } | null;
  };
  rules: {
    inviter_rules: Array<{
      min_invites: number;
      discount_rate: number;
      description: string;
    }>;
    invitee_discount: {
      rate: number;
      description: string;
    };
    max_discount_rate: number;
    priority: string;
  };
}


// 商品信息 API
export const productInfoApi = {
  /**
   * 获取产品信息（含邀请数据和折扣信息）
   * @param bookTitle 书籍标题
   * @returns Promise<ProductInfo>
   */
  getProductInfo(bookTitle: string): Promise<ProductInfo> {
    return request({
      url: buildApiUrl('/payment/product-info'),
      method: 'GET',
      data: {
        book_title: bookTitle
      },
    }) as Promise<ProductInfo>;
  },

  /**
   * 获取邀请活动信息和用户当前状态
   * @returns Promise<InvitationActivity>
   */
  getInvitationActivity(): Promise<InvitationActivity> {
    return request({
      url: buildApiUrl('/payment/invitation-activity'),
      method: 'GET',
    }) as Promise<InvitationActivity>;
  },

}; 