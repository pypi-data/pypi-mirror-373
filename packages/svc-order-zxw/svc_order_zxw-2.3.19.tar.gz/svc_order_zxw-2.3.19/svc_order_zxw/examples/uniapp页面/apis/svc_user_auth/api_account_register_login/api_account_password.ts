import { buildApiUrl, app_name,app_default_role } from '@/config.js'
import { request } from './login_request'

// uniapp全局类型声明
declare const uni : any;

// 请求数据结构
interface RegisterRequest {
	username : string;
	password : string;
	role_name ?: string;  // 默认 config.app_default_role
	app_name ?: string;   // 默认 config.app_name
}

interface LoginRequest {
	username : string;
	password : string;
}

// 响应数据结构
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
	code : number;
	data : LoginResult;
}

// 保存token到本地存储
const saveTokenToCookie = (token : string, refresh_token : string, user_info : UserInfo) => {
	uni.setStorageSync('access_token', token);
	uni.setStorageSync('refresh_token', refresh_token);
	uni.setStorageSync('user_info', user_info);
}

/**
 * 账号密码注册
 * @param data 注册数据
 * @returns 登录响应数据
 */
export const registerWithPassword = async (data : RegisterRequest) => {
	console.log('registerWithPassword: ', data.username)

	const requestData = {
		username: data.username,
		password: data.password,
		role_name: data.role_name || app_default_role,
		app_name: app_name
	}

	const url = '/user_center/account/normal/register/'
	const response = await request(buildApiUrl(url), 'POST', requestData);
	console.log("registerWithPassword response = ", response);

	const loginResponse = response as LoginResponse;

	if (loginResponse.data.access_token) {
		console.log("账号密码注册成功，access_token = ", loginResponse.data.access_token);
		saveTokenToCookie(
			loginResponse.data.access_token,
			loginResponse.data.refresh_token,
			loginResponse.data.user_info
		);
	}

	return loginResponse.data;
}

/**
 * 账号密码登录
 * @param data 登录数据
 * @returns 登录响应数据
 */
export const loginWithPassword = async (data : LoginRequest) => {
	console.log('loginWithPassword: ', data)

	const requestData = {
		username: data.username,
		password: data.password
	}

	const url = '/user_center/account/normal/login/'
	const response = await request(buildApiUrl(url), 'POST', requestData);
	console.log("loginWithPassword response = ", response);

	const loginResponse = response as LoginResponse;

	if (loginResponse.data.access_token) {
		console.log("账号密码登录成功，access_token = ", loginResponse.data.access_token);
		saveTokenToCookie(
			loginResponse.data.access_token,
			loginResponse.data.refresh_token,
			loginResponse.data.user_info
		);
	}

	return loginResponse;
}