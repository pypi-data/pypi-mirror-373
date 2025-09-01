import { buildApiUrl } from "@/config"
import { request } from "@/src/utils/request/request"


// 获取是否开启苹果内购配置
export const getIAPConfig = async (): Promise<boolean> => {
  const res = await request({
    url: buildApiUrl('/apple_pay/config/enable_ios_iap'),
    method: 'GET'
  })
  return res as boolean;
}
