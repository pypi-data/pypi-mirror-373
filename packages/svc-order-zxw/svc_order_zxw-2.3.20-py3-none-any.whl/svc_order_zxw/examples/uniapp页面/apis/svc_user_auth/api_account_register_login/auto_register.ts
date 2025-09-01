import {
	registerWithPassword, loginWithPassword
} from './api_account_password'

declare const uni : any;

async function auto_register() {
	// 1. 获取本机信息（最好是独一无二的编码信息，如Mac地址）
	const systemInfo = uni.getSystemInfoSync();
	console.log('【auto_register】系统信息:', systemInfo);
	const deviceId = systemInfo.deviceId || systemInfo.uuid || systemInfo.deviceModel;
	console.log('【auto_register】设备ID:', deviceId);

	// 2. 检查是否已登录
	const access_token = uni.getStorageSync('access_token');
	const refresh_token = uni.getStorageSync('refresh_token');
	const user_info = uni.getStorageSync('user_info');
	if (access_token && refresh_token && user_info) {
		console.log('已登录，不做任何处理直接返回')
		return
	}
	
	// 3. 首先尝试自动登录
	var auto_login_success = false;
	try {
		const loginResult = await loginWithPassword({
			username: deviceId,
			password: deviceId
		})
		console.log(loginResult);
		if (loginResult.code == 200) {
			console.log('【auto_register】自动登录成功')
			auto_login_success = true;
		} else {
			console.log('【auto_register】自动登录失败')
		}
	} catch (error) {
		console.log('【auto_register】自动登录失败', error)
	}

	// 4. 其次尝试自动注册账号
	if (!auto_login_success) {
		console.log('【auto_register】iOS平台，自动注册账号')
		await registerWithPassword({
			username: deviceId,
			password: deviceId
		})
		// 设置自动注册标志
		set_auto_register_flag()
	} else {
		console.log('【auto_register】自动登录成功，不自动注册账号')
	}

}



// 设置自动注册标志
function set_auto_register_flag() : void {
	uni.setStorageSync('isAutoRegister', 'yes')
	uni.setStorageSync('isBindPhone', 'no')
}

function check_is_auto_register() : boolean {
	const is_bind_phone = uni.getStorageSync('isAutoRegister');
	return is_bind_phone === 'yes';
}

function set_bind_phone_flag() : void {
	uni.setStorageSync('isBindPhone', 'yes')
}

// 检测已登录账号是否绑定手机号
function check_is_bind_phone() : boolean {
	const is_bind_phone = uni.getStorageSync('isBindPhone');
	return is_bind_phone === 'yes';
}

export {
	auto_register,
	check_is_bind_phone,
	check_is_auto_register,
	set_bind_phone_flag
}