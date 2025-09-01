"""用户信息收集"""

from ...base import BaseRequest


class GetUserCollectPhoneStatusRequest(BaseRequest):
    """
    查询手机号码绑定状态请求-请求

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type dealer_user_id: string
    :param dealer_user_id: 平台企业用户 ID

    :type real_name: string
    :param real_name: 姓名

    :type id_card: string
    :param id_card: 证件号码

    :type certificate_type: int
    :param certificate_type: 证件类型编码
    """
    def __init__(
        self,
        dealer_id = None,
        broker_id = None,
        dealer_user_id = None,
        real_name = None,
        id_card = None,
        certificate_type = None
    ):
        super().__init__()
        self.dealer_id = dealer_id
        self.broker_id = broker_id
        self.dealer_user_id = dealer_user_id
        self.real_name = real_name
        self.id_card = id_card
        self.certificate_type = certificate_type


class GetUserCollectPhoneStatusResponse(BaseRequest):
    """
    查询手机号码绑定状态返回-响应

    :type token: string
    :param token: 手机号码收集 Token

    :type status: int
    :param status: 绑定状态
    """
    def __init__(
        self,
        token = None,
        status = None
    ):
        super().__init__()
        self.token = token
        self.status = status


class GetUserCollectPhoneUrlRequest(BaseRequest):
    """
    获取收集手机号码页面请求-请求

    :type token: string
    :param token: 手机号码收集 Token

    :type color: string
    :param color: 主题颜色

    :type url: string
    :param url: 回调地址

    :type redirect_url: string
    :param redirect_url: 跳转 URL
    """
    def __init__(
        self,
        token = None,
        color = None,
        url = None,
        redirect_url = None
    ):
        super().__init__()
        self.token = token
        self.color = color
        self.url = url
        self.redirect_url = redirect_url


class GetUserCollectPhoneUrlResponse(BaseRequest):
    """
    获取收集手机号码页面返回-响应

    :type url: string
    :param url: 收集手机号码页面 URL
    """
    def __init__(
        self,
        url = None
    ):
        super().__init__()
        self.url = url


class NotifyUserCollectPhoneRequest(BaseRequest):
    """
    收集手机号码结果回调通知-请求

    :type dealer_user_id: string
    :param dealer_user_id: 平台企业用户 ID

    :type status: int
    :param status: 手机号码绑定状态
    """
    def __init__(
        self,
        dealer_user_id = None,
        status = None
    ):
        super().__init__()
        self.dealer_user_id = dealer_user_id
        self.status = status
