"""
# File       : 使用示例_促销优惠管理.py
# Time       ：2025/1/28
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：苹果内购促销优惠管理服务使用示例
"""
import asyncio
from app_tools_zxw.SDK_苹果应用服务.sdk_促销优惠管理 import (
    苹果内购优惠管理服务,
    促销优惠签名请求,
    促销优惠签名结果
)
from pems.config_苹果支付 import ApplePayConfig

product_ids = ["vip001", "vip002", "vip003"]
subscription_offer_ids = ["promo_offer_1", "promo_offer_2", "promo_offer_3"]
application_usernames = ["user123", "user456", "user789"]


async def 示例_单个促销优惠签名():
    """示例：生成单个促销优惠签名"""
    print("=" * 50)
    print("示例：生成单个促销优惠签名")
    print("=" * 50)

    # 初始化服务
    服务 = 苹果内购优惠管理服务(
        私钥文件路径=ApplePayConfig.私钥文件路径,
        密钥ID=ApplePayConfig.密钥ID,
        应用包ID=ApplePayConfig.应用包ID
    )

    try:
        # 生成促销优惠签名
        result = 服务.生成促销优惠签名(
            product_id=product_ids[0],
            subscription_offer_id=subscription_offer_ids[0],
            application_username=application_usernames[0]
        )

        print(f"签名结果:")
        print(f"  产品ID: {result.product_id}")
        print(f"  优惠ID: {result.subscription_offer_id}")
        print(f"  用户名: {result.application_username}")
        print(f"  随机数: {result.nonce}")
        print(f"  时间戳: {result.timestamp}")
        print(f"  签名: {result.signature[:20]}...")
        print(f"  创建时间: {result.created_at}")

    except Exception as e:
        print(f"生成签名失败: {e}")


async def 示例_批量促销优惠签名():
    """示例：批量生成促销优惠签名"""
    print("=" * 50)
    print("示例：批量生成促销优惠签名")
    print("=" * 50)

    # 初始化服务
    服务 = 苹果内购优惠管理服务(
        私钥文件路径=ApplePayConfig.私钥文件路径,
        密钥ID=ApplePayConfig.密钥ID,
        应用包ID=ApplePayConfig.应用包ID
    )

    # 准备批量请求
    requests = [
        促销优惠签名请求(
            product_id=product_ids[0],
            subscription_offer_id=subscription_offer_ids[0],
            application_username=application_usernames[0]
        ),
        促销优惠签名请求(
            product_id=product_ids[1],
            subscription_offer_id=subscription_offer_ids[1],
            application_username=application_usernames[1]
        ),
        促销优惠签名请求(
            product_id=product_ids[2],
            subscription_offer_id=subscription_offer_ids[2]
        )
    ]

    try:
        # 批量生成签名
        results = 服务.批量生成促销优惠签名(requests)

        print(f"批量生成完成，成功数量: {len(results)}")
        for i, result in enumerate(results, 1):
            print(f"  第{i}个签名:")
            print(f"    产品ID: {result.product_id}")
            print(f"    优惠ID: {result.subscription_offer_id}")
            print(f"    签名: {result.signature[:20]}...")

    except Exception as e:
        print(f"批量生成签名失败: {e}")


async def 示例_参数验证():
    """示例：验证签名参数"""
    print("=" * 50)
    print("示例：验证签名参数")
    print("=" * 50)

    # 初始化服务
    服务 = 苹果内购优惠管理服务(
        私钥文件路径=ApplePayConfig.私钥文件路径,
        密钥ID=ApplePayConfig.密钥ID,
        应用包ID=ApplePayConfig.应用包ID
    )

    # 测试不同的参数组合
    test_cases = [
        ("com.example.product1", "promo_offer_1", "user123", "有效参数"),
        ("", "promo_offer_1", "user123", "无效产品ID"),
        ("com.example.product1", "", "user123", "无效优惠ID"),
        ("com.example.product1", "promo_offer_1", "", "空用户名（有效）"),
        (None, "promo_offer_1", "user123", "产品ID为None"),
    ]

    for product_id, offer_id, username, description in test_cases:
        is_valid = 服务.验证签名参数(product_id, offer_id, username)
        print(f"  {description}: {'✓' if is_valid else '✗'}")


async def 示例_获取配置信息():
    """示例：获取服务配置信息"""
    print("=" * 50)
    print("示例：获取服务配置信息")
    print("=" * 50)

    # 初始化服务
    服务 = 苹果内购优惠管理服务(
        私钥文件路径=ApplePayConfig.私钥文件路径,
        密钥ID=ApplePayConfig.密钥ID,
        应用包ID=ApplePayConfig.应用包ID
    )

    # 获取配置信息
    config_info = 服务.获取签名配置信息()

    print("配置信息:")
    for key, value in config_info.items():
        print(f"  {key}: {value}")


async def main():
    """主函数：运行所有示例"""
    print("苹果内购促销优惠管理服务 - 使用示例")
    print("注意：请先修改私钥文件路径、密钥ID 和应用包ID")

    try:
        await 示例_单个促销优惠签名()
        await 示例_批量促销优惠签名()
        await 示例_参数验证()
        await 示例_获取配置信息()
    except FileNotFoundError:
        print("错误：私钥文件未找到，请检查文件路径")
    except Exception as e:
        print(f"运行示例时发生错误: {e}")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())
