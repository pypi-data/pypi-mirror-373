import {request} from './login_request'
import {buildApiUrl} from '@/config.js'

// 定义接口返回数据类型
interface ResponseInitUserInfo {
	message : string
	status : string
}


/**
 * 首次注册增加默认权限
 * @param referrerId 邀请人id (可选)
 */
export const initUserInfo = async (referrerId ?: number) => {
	let url = buildApiUrl('/user_center/update-user-info');

	if (referrerId) {
		url = `${url}?referrer_id=${referrerId}`;
	}

	// const res = await request(url, 'GET', null)
	// console.log("res = ", res)
	console.log("首次注册后，初始化用户权限成功 ")
	// return res.data
}