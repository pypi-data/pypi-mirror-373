# 云账户 SDK for Python

欢迎使用云账户 SDK for Python。
云账户是一家专注为平台企业和新就业形态劳动者提供高质量灵活就业服务的新时代企业。云账户 SDK 对云账户综合服务平台 API 接口进行封装，帮助您快速接入到云账户综合服务平台。云账户 SDK for Python 为您提供签约、下单、回调、数据查询等功能，帮助您完成与云账户综合服务平台的接口对接及业务开发。 如果您在使用过程中遇到任何问题，请在当前 GitHub 提交 Issues，或发送邮件至技术支持组 [technicalsupport@yunzhanghu.com](mailto:technicalsupport@yunzhanghu.com)。

### 环境要求

云账户 SDK for Python 支持 Python 3.0 及以上版本。

### 快速使用

#### 通过 PIP 安装

1. 执行以下命令安装云账户 SDK for Python：

   > pip3 install yunzhanghu_sdk

2. 在您的代码中引用对应模块代码，具体引用方式可参考下文示例

#### 通过源码包安装

1. 前往 [Github 仓库](https://github.com/YunzhanghuOpen/sdk-python) 下载源码压缩包。
2. 解压源码包到您项目的合适位置。
3. 在您的代码中引用对应模块代码，可参考示例。

#### 示例

```
#提示：
   #为了保护秘钥安全，建议将密钥配置到环境变量中或者配置文件中。
   #请勿在代码中使用硬编码密钥，可能导致密钥暴露，存在安全隐患。

from yunzhanghu_sdk.client.api.model.payment import GetOrderRequest
from yunzhanghu_sdk.client.api.payment_client import PaymentClient
from yunzhanghu_sdk.config import *

if __name__ == "__main__":
    # 平台企业 ID，登录云账户综合服务平台，选择“业务中心 > 业务管理 > 对接信息”获取
    dealer_id = "xxx"
    # 综合服务主体 ID，登录云账户综合服务平台，选择“业务中心 > 业务管理 > 对接信息”获取
    broker_id = "xxx"
    # 签名方式，登录云账户综合服务平台，选择“业务中心 > 业务管理 > 对接信息”获取
    # 签名方式为 RSA，参数固定为：rsa
    sign_type = "rsa"
    # 平台企业 App Key，登录云账户综合服务平台，选择“业务中心 > 业务管理 > 对接信息”获取
    app_key = "xxx"
    # 平台企业 3DES Key，登录云账户综合服务平台，选择“业务中心 > 业务管理 > 对接信息”获取
    des3key = "xxx"
    # 平台企业私钥，自行生成 RSA 公私钥，私钥请妥善保存，谨防泄露。平台企业公钥请登录云账户综合服务平台配置，选择“业务中心 > 业务管理 > 对接信息”，单击页面右上角的“编辑”，完成平台企业公钥配置。
    dealer_private_key = '''
    -----BEGIN PRIVATE KEY-----
    xxx
    -----END PRIVATE KEY-----
    '''
    # 云账户公钥，登录云账户综合服务平台，选择“业务中心 > 业务管理 > 对接信息”获取
    yzh_public_key = '''
    -----BEGIN PUBLIC KEY-----
    xxx
    -----END PUBLIC KEY-----
    '''
    # 初始化配置参数
    config = Config(
        # host 请求域名
        host = "https://api-service.yunzhanghu.com",
        dealer_id = dealer_id,
        sign_type = sign_type,
        app_key = app_key,
        des3key = des3key,
        dealer_private_key = dealer_private_key,
        yzh_public_key = yzh_public_key,
    )
    # 获取订单详情
    request = GetOrderRequest(
        order_id = "232211231231231",
        channel = "微信",
        data_type = "encryption"
    )
    # 建议自定义并将 request-id 记录在日志中
    # request.request_id = "XXXXX"
    client = PaymentClient(config)
    resp = client.get_order(request)

    print(resp.code, resp.message, resp.request_id, resp.data)
```