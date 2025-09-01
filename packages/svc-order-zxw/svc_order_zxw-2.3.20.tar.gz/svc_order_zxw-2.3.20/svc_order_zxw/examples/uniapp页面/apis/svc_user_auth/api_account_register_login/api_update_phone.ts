// 手机号管理API接口文件
// 更新绑定手机号API

import { buildApiUrl } from '@/config.js'
import { request } from './login_request'
import { set_bind_phone_flag } from './auto_register'

declare const uni : any;

// 角色信息接口
interface Role {
	role_name: string;
	app_name: string;
	app_id: number;
}

// 用户信息接口
interface UserInfo {
	sub: string;
	username: string;
	nickname: string;
	roles: Role[];
}

// 登录结果接口
interface LoginResult {
	access_token: string;
	refresh_token: string;
	user_info: UserInfo;
}

// 更新手机号返回响应接口
export interface UpdatePhoneResponse {
	code: number;
	data: LoginResult;
}

// 更新绑定手机号请求参数接口
export interface UpdatePhoneRequest {
	new_phone: string;
	sms_code: string;
}

// 保存token到本地存储
const saveTokenToCookie = (token: string, refresh_token: string, user_info: UserInfo) => {
	uni.setStorageSync('access_token', token);
	uni.setStorageSync('refresh_token', refresh_token);
	uni.setStorageSync('user_info', user_info);
}

/**
 * 发送验证码到新手机号
 * @param phone 新手机号
 * @returns Promise
 */
export const sendVerificationCodeForUpdate = (phone: string | number | boolean) => {
	const url = `/user_center/account/phone/send-verification-code/?phone=${encodeURIComponent(phone)}`
	return request(buildApiUrl(url), 'POST');
}

/**
 * 更新绑定手机号
 * @param data 更新手机号的请求数据
 * @returns Promise<LoginResult>
 */
export const updateBindingPhone = async (data: UpdatePhoneRequest): Promise<LoginResult> => {
	console.log('updateBindingPhone: ', data)

	const requestData = {
		new_phone: data.new_phone,
		sms_code: data.sms_code
	}

	const url = '/user_center/account/phone/update-phone/'
	const response = await request(buildApiUrl(url), 'POST', requestData);
	console.log("updateBindingPhone response = ", response);

	const updateResponse = response as UpdatePhoneResponse;

	// 更新成功后，保存新的token信息
	if (updateResponse.data.access_token) {
		console.log("手机号更新成功，新的access_token = ", updateResponse.data.access_token);
		saveTokenToCookie(
			updateResponse.data.access_token,
			updateResponse.data.refresh_token,
			updateResponse.data.user_info
		);
		set_bind_phone_flag()
	}

	return updateResponse.data;
}

/**
 * 获取当前用户信息（从本地存储）
 * @returns UserInfo | null
 */
export const getCurrentUserInfo = (): UserInfo | null => {
	try {
		const userInfo = uni.getStorageSync('user_info');
		return userInfo || null;
	} catch (error) {
		console.error('获取用户信息失败:', error);
		return null;
	}
}

/**
 * 获取当前绑定的手机号
 * @returns string | null
 */
export const getCurrentPhone = (): string | null => {
	const userInfo = getCurrentUserInfo();
	return userInfo ? userInfo.username : null;
}
