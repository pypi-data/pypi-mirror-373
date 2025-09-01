"""云账户共享大额 H5+API"""

from ...base import BaseRequest


class GxV2H5APIPreCollectBizlicMsgRequest(BaseRequest):
    """
    工商实名信息录入请求-请求

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type dealer_user_id: string
    :param dealer_user_id: 平台企业端的用户 ID

    :type phone_no: string
    :param phone_no: 手机号

    :type id_card: string
    :param id_card: 身份证号码

    :type real_name: string
    :param real_name: 姓名

    :type id_card_address: string
    :param id_card_address: 身份证住址

    :type id_card_agency: string
    :param id_card_agency: 身份证签发机关

    :type id_card_nation: string
    :param id_card_nation: 身份证民族

    :type id_card_validity_start: string
    :param id_card_validity_start: 身份证有效期开始时间

    :type id_card_validity_end: string
    :param id_card_validity_end: 身份证有效期结束时间
    """
    def __init__(
        self,
        dealer_id = None,
        broker_id = None,
        dealer_user_id = None,
        phone_no = None,
        id_card = None,
        real_name = None,
        id_card_address = None,
        id_card_agency = None,
        id_card_nation = None,
        id_card_validity_start = None,
        id_card_validity_end = None
    ):
        super().__init__()
        self.dealer_id = dealer_id
        self.broker_id = broker_id
        self.dealer_user_id = dealer_user_id
        self.phone_no = phone_no
        self.id_card = id_card
        self.real_name = real_name
        self.id_card_address = id_card_address
        self.id_card_agency = id_card_agency
        self.id_card_nation = id_card_nation
        self.id_card_validity_start = id_card_validity_start
        self.id_card_validity_end = id_card_validity_end


class GxV2H5APIPreCollectBizlicMsgResponse(BaseRequest):
    """
    工商实名信息录入返回-响应

    :type dealer_user_id: string
    :param dealer_user_id: 平台企业端的用户 ID
    """
    def __init__(
        self,
        dealer_user_id = None
    ):
        super().__init__()
        self.dealer_user_id = dealer_user_id


class GxV2H5APIGetStartUrlRequest(BaseRequest):
    """
    预启动请求-请求

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type dealer_user_id: string
    :param dealer_user_id: 平台企业端的用户 ID

    :type client_type: int
    :param client_type: 客户端类型

    :type notify_url: string
    :param notify_url: 异步通知 URL

    :type color: string
    :param color: H5 页面主题颜色

    :type return_url: string
    :param return_url: 跳转 URL

    :type customer_title: int
    :param customer_title: H5 页面 Title
    """
    def __init__(
        self,
        dealer_id = None,
        broker_id = None,
        dealer_user_id = None,
        client_type = None,
        notify_url = None,
        color = None,
        return_url = None,
        customer_title = None
    ):
        super().__init__()
        self.dealer_id = dealer_id
        self.broker_id = broker_id
        self.dealer_user_id = dealer_user_id
        self.client_type = client_type
        self.notify_url = notify_url
        self.color = color
        self.return_url = return_url
        self.customer_title = customer_title


class GxV2H5APIGetStartUrlResponse(BaseRequest):
    """
    预启动返回-响应

    :type h5_url: string
    :param h5_url: 跳转 URL
    """
    def __init__(
        self,
        h5_url = None
    ):
        super().__init__()
        self.h5_url = h5_url


class GxV2H5APIGetAicStatusRequest(BaseRequest):
    """
    查询个体工商户状态请求-请求

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type open_id: string
    :param open_id: 用户唯一标识

    :type real_name: string
    :param real_name: 姓名

    :type id_card: string
    :param id_card: 身份证号码

    :type dealer_user_id: string
    :param dealer_user_id: 平台企业端的用户 ID
    """
    def __init__(
        self,
        dealer_id = None,
        broker_id = None,
        open_id = None,
        real_name = None,
        id_card = None,
        dealer_user_id = None
    ):
        super().__init__()
        self.dealer_id = dealer_id
        self.broker_id = broker_id
        self.open_id = open_id
        self.real_name = real_name
        self.id_card = id_card
        self.dealer_user_id = dealer_user_id


class GxV2H5APIGetAicStatusResponse(BaseRequest):
    """
    查询个体工商户状态返回-响应

    :type status: int
    :param status: 用户注册状态

    :type status_message: string
    :param status_message: 注册状态描述

    :type status_detail: int
    :param status_detail: 注册详情状态码

    :type status_detail_message: string
    :param status_detail_message: 注册详情状态码描述

    :type applyed_at: string
    :param applyed_at: 注册发起时间

    :type registed_at: string
    :param registed_at: 注册完成时间

    :type uscc: string
    :param uscc: 统一社会信用代码

    :type id_card: string
    :param id_card: 身份证号码

    :type real_name: string
    :param real_name: 姓名
    """
    def __init__(
        self,
        status = None,
        status_message = None,
        status_detail = None,
        status_detail_message = None,
        applyed_at = None,
        registed_at = None,
        uscc = None,
        id_card = None,
        real_name = None
    ):
        super().__init__()
        self.status = status
        self.status_message = status_message
        self.status_detail = status_detail
        self.status_detail_message = status_detail_message
        self.applyed_at = applyed_at
        self.registed_at = registed_at
        self.uscc = uscc
        self.id_card = id_card
        self.real_name = real_name


class NotifyGxV2H5APIAicRequest(BaseRequest):
    """
    个体工商户注册/注销结果回调通知-请求

    :type open_id: string
    :param open_id: 用户唯一标识

    :type dealer_user_id: string
    :param dealer_user_id: 平台企业端的用户 ID

    :type submit_at: string
    :param submit_at: 注册/注销提交时间

    :type registed_at: string
    :param registed_at: 注册/注销完成时间

    :type status: int
    :param status: 用户注册/注销状态

    :type status_message: string
    :param status_message: 注册/注销状态描述

    :type status_detail: int
    :param status_detail: 注册/注销详情状态码

    :type status_detail_message: string
    :param status_detail_message: 注册/注销详情状态码描述

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type uscc: string
    :param uscc: 统一社会信用代码

    :type id_card: string
    :param id_card: 身份证号码

    :type real_name: string
    :param real_name: 姓名

    :type type: int
    :param type: 回调类型
    """
    def __init__(
        self,
        open_id = None,
        dealer_user_id = None,
        submit_at = None,
        registed_at = None,
        status = None,
        status_message = None,
        status_detail = None,
        status_detail_message = None,
        dealer_id = None,
        broker_id = None,
        uscc = None,
        id_card = None,
        real_name = None,
        type = None
    ):
        super().__init__()
        self.open_id = open_id
        self.dealer_user_id = dealer_user_id
        self.submit_at = submit_at
        self.registed_at = registed_at
        self.status = status
        self.status_message = status_message
        self.status_detail = status_detail
        self.status_detail_message = status_detail_message
        self.dealer_id = dealer_id
        self.broker_id = broker_id
        self.uscc = uscc
        self.id_card = id_card
        self.real_name = real_name
        self.type = type
