// 根据response_error格式定义的错误响应接口
interface ErrorDetail {
	code: number;
	data: string;
}

interface ErrorData {
	detail: ErrorDetail;
}
// 从 cookie 获取 token
const getTokenFromCookie = () => {
	return uni.getStorageSync('access_token');
}

// 设置header token
const setHeaderToken = () => {
	const token = getTokenFromCookie();
	return token ? { 'Authorization': `Bearer ${token}` } : {}
}
// 修改通用请求函数，自动带上 token
export const request = (url: string, method: string, data: any = null) => {
	return new Promise((resolve, reject) => {
		uni.request({
			url: url,
			method,
			data,
			header: setHeaderToken(),
			success: (res) => {
				if (res.statusCode >= 200 && res.statusCode < 300) {
					resolve(res.data)
				} else {
					// 安全地访问错误信息
					const errorData = res.data as ErrorData
					let errorMessage = `请求失败: HTTP ${res.statusCode}`;
					if (errorData) {
						errorMessage = `请求失败: ${errorData.detail.code}, ${errorData.detail.data || ''}`;
					}
					
					uni.showToast({
						title: errorMessage,
						icon: 'none',
						duration: 3000
					})
					reject(new Error(errorMessage))
				}
			},
			fail: (err) => {
				console.error('网络请求错误:', err)
				uni.showToast({
					title: `网络请求失败，请检查网络连接或服务器地址`,
					icon: 'none',
					duration: 3000
				})
				reject(new Error('网络请求失败，请检查网络连接或服务器地址'))
			}
		})
	})
}
