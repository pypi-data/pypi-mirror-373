"""签约信息上传"""

from ...base import BaseRequest


class UploadUserSignRequest(BaseRequest):
    """
    用户签约信息上传请求-请求

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type real_name: string
    :param real_name: 姓名

    :type id_card: string
    :param id_card: 证件号码

    :type phone: string
    :param phone: 手机号

    :type is_abroad: bool
    :param is_abroad: 是否是海外用户

    :type notify_url: string
    :param notify_url: 签约回调地址
    """
    def __init__(
        self,
        dealer_id = None,
        broker_id = None,
        real_name = None,
        id_card = None,
        phone = None,
        is_abroad = None,
        notify_url = None
    ):
        super().__init__()
        self.dealer_id = dealer_id
        self.broker_id = broker_id
        self.real_name = real_name
        self.id_card = id_card
        self.phone = phone
        self.is_abroad = is_abroad
        self.notify_url = notify_url


class UploadUserSignResponse(BaseRequest):
    """
    用户签约信息上传返回-响应

    :type status: string
    :param status: 上传状态
    """
    def __init__(
        self,
        status = None
    ):
        super().__init__()
        self.status = status


class GetUploadUserSignStatusRequest(BaseRequest):
    """
    获取用户签约状态请求-请求

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type real_name: string
    :param real_name: 姓名

    :type id_card: string
    :param id_card: 证件号码
    """
    def __init__(
        self,
        dealer_id = None,
        broker_id = None,
        real_name = None,
        id_card = None
    ):
        super().__init__()
        self.dealer_id = dealer_id
        self.broker_id = broker_id
        self.real_name = real_name
        self.id_card = id_card


class GetUploadUserSignStatusResponse(BaseRequest):
    """
    获取用户签约状态返回-响应

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type real_name: string
    :param real_name: 姓名

    :type id_card: string
    :param id_card: 证件号码

    :type status: int
    :param status: 签约状态

    :type created_at: int
    :param created_at: 创建时间

    :type updated_at: int
    :param updated_at: 更新时间
    """
    def __init__(
        self,
        dealer_id = None,
        broker_id = None,
        real_name = None,
        id_card = None,
        status = None,
        created_at = None,
        updated_at = None
    ):
        super().__init__()
        self.dealer_id = dealer_id
        self.broker_id = broker_id
        self.real_name = real_name
        self.id_card = id_card
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at


class NotifyUploadUserSignRequest(BaseRequest):
    """
    签约成功状态回调通知-请求

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type real_name: string
    :param real_name: 姓名

    :type id_card: string
    :param id_card: 证件号码

    :type phone: string
    :param phone: 手机号
    """
    def __init__(
        self,
        dealer_id = None,
        broker_id = None,
        real_name = None,
        id_card = None,
        phone = None
    ):
        super().__init__()
        self.dealer_id = dealer_id
        self.broker_id = broker_id
        self.real_name = real_name
        self.id_card = id_card
        self.phone = phone
