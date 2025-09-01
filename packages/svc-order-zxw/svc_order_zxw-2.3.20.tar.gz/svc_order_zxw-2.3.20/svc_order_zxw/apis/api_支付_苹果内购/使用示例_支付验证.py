"""
# File       : 使用示例_官方库.py
# Time       ：2024/12/20
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：苹果内购支付服务（官方库版本）使用示例
"""
import asyncio
from contextlib import asynccontextmanager
from app_tools_zxw.SDK_苹果应用服务.sdk_支付验证 import 苹果内购支付服务_官方库
from svc_order_zxw.config import ApplePayConfig

# 全局配置
基础配置 = {
    "私钥文件路径": ApplePayConfig.私钥文件路径,
    "密钥ID": ApplePayConfig.密钥ID,
    "发行者ID": ApplePayConfig.发行者ID,
    "应用包ID": ApplePayConfig.应用包ID,
    "是否沙盒环境": ApplePayConfig.是否沙盒环境,
    "苹果ID": ApplePayConfig.苹果ID
}

# 带根证书的配置（用于验证通知数据）
完整配置 = {
    **基础配置,
    "根证书路径": ["/path/to/apple-root-cert.pem"]
}


@asynccontextmanager
async def 获取支付服务(使用根证书=False):
    """通用的支付服务上下文管理器"""
    配置 = 完整配置 if 使用根证书 else 基础配置
    支付服务 = 苹果内购支付服务_官方库(**配置)
    try:
        async with 支付服务:
            yield 支付服务
    except Exception as e:
        print(f"操作失败: {e}")
        raise


async def 示例_基本功能():
    """基本功能示例：验证收据、交易历史、特定交易验证"""
    print("=== 基本功能示例 ===")

    async with 获取支付服务() as 支付服务:
        # 1. 验证收据
        print("1. 验证收据...")
        验证结果 = await 支付服务.验证收据_从应用收据(ApplePayConfig.recipt)
        print(f"验证结果: {验证结果}")
        print(验证结果.model_dump())

        # 2. 获取最新交易
        print("\n2. 获取最新交易...")
        最新交易 = await 支付服务.获取最新交易(ApplePayConfig.originalTransactionIdentifierIOS)
        print(f"最新交易: {最新交易}")
        print(最新交易.model_dump())

        # 3. 验证特定交易
        print("\n3. 验证特定交易...")
        交易验证结果 = await 支付服务.验证特定交易(ApplePayConfig.transaction_id)
        print(f"交易验证结果: {交易验证结果}")
        print(f"交易状态: {交易验证结果.交易状态}")
        print(f"产品ID: {交易验证结果.产品ID}")
        print(f"支付时间: {交易验证结果.支付时间}")
        print(交易验证结果.model_dump())


async def 示例_订阅功能():
    """订阅相关功能示例：订阅状态查询"""
    print("\n=== 订阅功能示例 ===")

    async with 获取支付服务() as 支付服务:
        # 获取订阅状态
        订阅状态 = await 支付服务.获取订阅状态(ApplePayConfig.originalTransactionIdentifierIOS)
        print(f"订阅状态: ")
        print(f"环境: {订阅状态.环境}")
        print(f"最新收据: {订阅状态.最新收据}")
        print(f"最新交易信息: {订阅状态.最新交易信息}")
        print(f"待续费信息: {订阅状态.待续费信息}")
        print(f"是否有效订阅: {订阅状态.是否有效订阅}")
        print(f"订阅状态: {订阅状态.订阅状态}")
        print(f"过期时间: {订阅状态.过期时间}")


async def 示例_通知功能():
    """通知相关功能示例：测试通知、验证通知数据"""
    print("\n=== 通知功能示例 ===")

    # 1. 请求测试通知
    print("1. 请求测试通知...")
    async with 获取支付服务() as 支付服务:
        测试令牌 = await 支付服务.请求测试通知()
        print(f"测试通知令牌: {测试令牌}")

    # 2. 验证通知数据（需要根证书）
    print("\n2. 验证通知数据...")
    try:
        async with 获取支付服务(使用根证书=True) as 支付服务:
            签名通知数据 = "eyJ..."  # 替换为实际收到的签名通知数据
            通知数据 = await 支付服务.验证通知数据(签名通知数据)
            print(f"通知数据: {通知数据}")
    except Exception as e:
        print(f"验证通知数据失败（可能需要有效的根证书路径）: {e}")


def 显示配置说明():
    """显示配置说明"""
    print("\n=== 配置说明 ===")
    print(f"""
当前使用的配置信息：
- 私钥文件路径: {ApplePayConfig.私钥文件路径}
- 密钥ID: {ApplePayConfig.密钥ID}
- 发行者ID: {ApplePayConfig.发行者ID}
- 应用包ID: {ApplePayConfig.应用包ID}
- 是否沙盒环境: {ApplePayConfig.是否沙盒环境}
- 苹果ID: {ApplePayConfig.苹果ID}
- 共享密钥: {ApplePayConfig.共享密钥}

测试数据：
- 收据数据长度: {len(ApplePayConfig.recipt)} 字符
- 交易ID: {ApplePayConfig.transaction_id}
- 原始交易ID: {ApplePayConfig.originalTransactionIdentifierIOS}

配置苹果内购支付服务（官方库版本）说明：

1. 私钥文件路径: 从 App Store Connect 下载的 .p8 私钥文件路径
2. 密钥ID: 在 App Store Connect 中创建密钥时生成的 ID (10位字符)
3. 发行者ID: App Store Connect 中的发行者 ID (UUID格式)
4. 应用包ID: 应用的 Bundle Identifier (com.yourcompany.yourapp)
5. 是否沙盒环境: 测试环境(True) / 生产环境(False)
6. 苹果ID: 应用在 App Store 的 Apple ID (生产环境必需)
7. 根证书路径: 苹果根证书文件路径列表 (验证签名数据用，可选)

安装依赖：
pip install 'app-store-server-library[async]'

注意事项：
- 生产环境必须提供苹果ID
- 验证通知数据需要提供根证书
- 私钥文件需要妥善保管，不要泄露
""")


async def main():
    """主函数"""
    # 显示配置说明
    显示配置说明()

    print("\n开始运行示例，使用配置文件中的真实参数：")

    # 运行各类功能示例
    await 示例_基本功能()
    await 示例_订阅功能()
    await 示例_通知功能()


if __name__ == "__main__":
    asyncio.run(main())
