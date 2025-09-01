# 基础信息配置
class Config(object):
    """

    :type host: string
    :param host: 请求域名

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type sign_type: string
    :param sign_type: 签名算法

    :type app_key: string
    :param app_key: App Key

    :type des3key: string
    :param des3key: 3DES Key

    :type dealer_private_key: string
    :param dealer_private_key: 平台企业私钥

    :type yzh_public_key: string
    :param yzh_public_key: 云账户公钥

    :type timeout: float
    :param timeout: 超时时间
    """

    def __init__(self, host, dealer_id, broker_id, sign_type, app_key, des3key,
                 dealer_private_key: str, yzh_public_key: str, timeout=30):
        self.host = host
        self.dealer_id = dealer_id
        self.broker_id = broker_id
        self.sign_type = sign_type
        self.app_key = app_key
        self.des3key = des3key
        self.dealer_private_key = dealer_private_key
        self.yzh_public_key = yzh_public_key
        self.timeout = timeout
        self.check_config()

    def check_config(self):
        if self.dealer_private_key is not None:
            self.dealer_private_key = self.dealer_private_key.strip()
        if self.yzh_public_key is not None:
            self.yzh_public_key = self.yzh_public_key.strip()
        if self.sign_type not in ("sha256", "rsa"):
            raise ValueError("sign_type error! signType must be rsa or sha256!")
        if self.host is None:
            self.host = "https://api-service.yunzhanghu.com"
