// 登录后返回值, res.data =
// const response_success = {
// 	"code": 200,
// 	"data": {
// 		"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNTA1MDU2MDAyOSIsInVzZXJuYW1lIjoiMTUwNTA1NjAwMjkiLCJuaWNrbmFtZSI6bnVsbCwicm9sZXMiOlt7InJvbGVfbmFtZSI6ImwwIiwiYXBwX25hbWUiOiJhcHAwIiwiYXBwX2lkIjoxfV0sImV4cCI6MTc1MDIzNDE5NH0.woXZl6SWdxqxExZIF6LjO72MAUqFyxL9QDmdwk6gOH8",
// 		"refresh_token": "31b95165d2688e57f983c1f17b1347ee3f1547e9a612d9263ab7c4499121e25f",
// 		"user_info": {
// 			"sub": "15050560029",
// 			"username": "15050560029",
// 			"nickname": null,
// 			"roles": [{
// 				"role_name": "l0",
// 				"app_name": "app0",
// 				"app_id": 1
// 			}]
// 		}
// 	}
// }

// 请求失败返回值, res=response_error
// const response_error = {
// 	"data": {
// 		"detail": {
// 			"code": 400011,
// 			"data": "无效的验证码"
// 		}
// 	},
// 	"statusCode": 400,
// 	"header": {
// 		"access-control-allow-origin": "*",
// 		"date": "Wed, 11 Jun 2025 08:25:47 GMT",
// 		"access-control-allow-credentials": "true",
// 		"server": "uvicorn",
// 		"content-length": "54",
// 		"content-type": "application/json"
// 	},
// 	"cookies": [],
// 	"errMsg": "request:ok"
// }

import { buildApiUrl } from '@/config.js'
import { request } from './login_request'

interface Role {
	role_name : string;
	app_name : string;
	app_id : number;
}

interface UserInfo {
	sub : string;
	username : string;
	nickname : string;
	roles : Role[];
}

interface LoginResult {
	access_token : string;
	refresh_token : string;
	user_info : UserInfo;
}

export interface LoginResponse {
	code:number
	data:LoginResult
}




// 保存token到本地存储
const saveTokenToCookie = (token : string, refresh_token : string, user_info : UserInfo) => {
	uni.setStorageSync('access_token', token);
	uni.setStorageSync('refresh_token', refresh_token);
	uni.setStorageSync('user_info', user_info);
}


export const sendVerificationCode = (phone : string | number | boolean) => {
	const url = `/user_center/account/phone/send-verification-code/?phone=${encodeURIComponent(phone)}`
	return request(buildApiUrl(url), 'POST');
}

export const loginPhone = async (data : { phone : string; sms_code : string; referer_id? : string; }) => {
	console.log('loginPhone: ', data)

	const requestData = {
		phone: data.phone,
		sms_code: data.sms_code,
		referer_id: data.referer_id || ""
	}

	const url = '/user_center/account/phone/register-or-login-phone/'
	const response = await request(buildApiUrl(url), 'POST', requestData);
	console.log("loginPhone response = ", response);

	const loginResponse = response as LoginResponse;
	
	if (loginResponse.data.access_token) {
		console.log("手机号注册登录，loginResponse.access_token = ", loginResponse.data.access_token);
		saveTokenToCookie(
			loginResponse.data.access_token,
			loginResponse.data.refresh_token,
			loginResponse.data.user_info
			);
	}

	return loginResponse.data;
}