/**
 * UniApp Vue3 前端API接口 - 获取用户邀请码和生成邀请活动图片
 * @author xuewei zhang
 * @email sunshineinwater2015@gmail.com
 * @description 用于获取当前用户的邀请码和生成邀请活动图片
 */
import { buildApiUrl } from "@/config.js"
import { request } from "@/src/utils/request/request.ts"

// 邀请码响应数据接口（根据后端接口返回格式定义）
interface InviteCodeData {
	user_id : number;
	invite_code : string;
	message : string;
}

// API响应基础接口
interface ApiResponse<T = any> {
	success : boolean;
	data : T | null;
	message : string;
	error_code ?: string;
}

// 获取邀请码的响应类型
type GetInviteCodeResponse = ApiResponse<InviteCodeData>;

// 生成邀请图片的响应类型
interface GenerateInviteImageResponse {
	success : boolean;
	data : {
		imagePath : string;
		imageUrl : string;
		message : string;
	} | null;
	message : string;
	error_code ?: string;
}

// 图片格式类型
type ImageFormat = 'png' | 'jpg' | 'jpeg';

/**
 * 将ArrayBuffer转换为Base64字符串
 * @param {ArrayBuffer} buffer - 需要转换的ArrayBuffer
 * @returns {string} Base64字符串
 */
const arrayBufferToBase64 = (buffer : ArrayBuffer) : string => {
	let binary = '';
	const bytes = new Uint8Array(buffer);
	const len = bytes.byteLength;
	for (let i = 0; i < len; i++) {
		binary += String.fromCharCode(bytes[i]);
	}
	return btoa(binary);
};

/**
 * 获取当前用户的邀请码
 * @returns {Promise<GetInviteCodeResponse>} 包含用户邀请码信息的响应对象
 */
export const getMyInviteCode = async () : Promise<GetInviteCodeResponse> => {
	try {
		const response = await request({
			url: buildApiUrl(`/payment/my-invite-code`),
			method: 'GET',
			header: {
				'Content-Type': 'application/json'
			}
		});

		// 参考后端代码的日志记录风格
		console.log(`[邀请码接口] 获取邀请码成功:`, response);

		// request 函数成功时直接返回后端的数据格式
		// 后端返回格式：{ user_id: number, invite_code: string, message: string }
		const responseData = response as InviteCodeData;
		return {
			success: true,
			data: responseData,
			message: (responseData as any) && (responseData as any).message || '邀请码获取成功'
		};
	} catch (error : unknown) {
		// 参考后端代码的错误处理方式
		console.error('获取邀请码失败:', error);

		const errorMessage = error instanceof Error ? error.message : '获取邀请码失败';
		const errorCode = (error as any) && (error as any).code || 'INVITE_CODE_ERROR';

		return {
			success: false,
			data: null,
			message: errorMessage,
			error_code: errorCode
		};
	}
};

/**
 * 生成邀请活动图片
 * @param {string} inviteCode - 邀请码
 * @param {ImageFormat} format - 图片格式，默认png
 * @returns {Promise<GenerateInviteImageResponse>} 包含生成图片信息的响应对象
 */
export const generateInviteImage = async (
	inviteCode : string,
	format : ImageFormat = 'png'
) : Promise<GenerateInviteImageResponse> => {
	try {
		if (!inviteCode) {
			throw new Error('邀请码不能为空');
		}

		// 构建API URL，包含路径参数和查询参数
		const image_url = buildApiUrl(`/api/invitation-image/${inviteCode}.${format}`);

		// uniapp 下载图片
		const tempFilePath = await new Promise<string>((resolve, reject) => {
			uni.downloadFile({
				url: image_url,
				success: (res) => {
					if (res.statusCode === 200) {
						resolve(res.tempFilePath)
					} else {
						reject(new Error(`下载失败，状态码：${res.statusCode}`))
					}
				},
				fail: (error) => {
					reject(error)
				}
			})
		})

		return {
			success: true,
			data: {
				imagePath: tempFilePath,
				imageUrl: image_url,
				message: '邀请图片生成成功'
			},
			message: '邀请图片生成成功'
		};
	} catch (error : unknown) {
		// 参考后端代码的错误处理方式
		console.error('生成邀请图片失败:', error);

		const errorMessage = error instanceof Error ? error.message : '生成邀请图片失败';
		const errorCode = (error as any) && (error as any).code || 'GENERATE_IMAGE_ERROR';

		return {
			success: false,
			data: null,
			message: errorMessage,
			error_code: errorCode
		};
	}
};

/**
 * 获取邀请码并生成邀请图片的组合操作
 * @param {ImageFormat} format - 图片格式，默认png
 * @returns {Promise<GenerateInviteImageResponse>} 包含生成图片信息的响应对象
 */
export const getInviteCodeAndGenerateImage = async (
	format : ImageFormat = 'png'
) : Promise<GenerateInviteImageResponse> => {
	try {
		// 先获取邀请码
		const inviteCodeResponse = await getMyInviteCode();

		if (!inviteCodeResponse.success || !inviteCodeResponse.data) {
			throw new Error(inviteCodeResponse.message || '获取邀请码失败');
		}

		// 使用邀请码生成图片
		const imageResponse = await generateInviteImage(
			inviteCodeResponse.data.invite_code,
			format
		);

		return imageResponse;
	} catch (error : unknown) {
		console.error('获取邀请码并生成图片失败:', error);

		const errorMessage = error instanceof Error ? error.message : '获取邀请码并生成图片失败';
		const errorCode = (error as any) && (error as any).code || 'COMBINED_OPERATION_ERROR';

		return {
			success: false,
			data: null,
			message: errorMessage,
			error_code: errorCode
		};
	}
};

// 导出默认配置
export default {
	getMyInviteCode,
	generateInviteImage,
	getInviteCodeAndGenerateImage
};

// 导出类型定义，便于其他文件使用
export type {
	InviteCodeData,
	ApiResponse,
	GetInviteCodeResponse,
	GenerateInviteImageResponse,
	ImageFormat
};