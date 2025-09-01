"""H5 签约"""

from ...base import BaseRequest


class H5UserPresignRequest(BaseRequest):
    """
    预申请签约请求-请求

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type real_name: string
    :param real_name: 姓名

    :type id_card: string
    :param id_card: 证件号码

    :type certificate_type: int
    :param certificate_type: 证件类型 0：身份证 2：港澳居民来往内地通行证 3：护照 5：台湾居民来往大陆通行证 9：港澳居民居住证 10：台湾居民居住证 11：外国人永久居留身份证 12：外国人工作许可证

    :type collect_phone_no: int
    :param collect_phone_no: 是否收集手机号码 0：不收集（默认） 1：收集手机号码
    """
    def __init__(
        self,
        dealer_id = None,
        broker_id = None,
        real_name = None,
        id_card = None,
        certificate_type = None,
        collect_phone_no = None
    ):
        super().__init__()
        self.dealer_id = dealer_id
        self.broker_id = broker_id
        self.real_name = real_name
        self.id_card = id_card
        self.certificate_type = certificate_type
        self.collect_phone_no = collect_phone_no


class H5UserPresignResponse(BaseRequest):
    """
    预申请签约返回-响应

    :type uid: string
    :param uid: 用户 ID（废弃字段）

    :type token: string
    :param token: H5 签约 token

    :type status: int
    :param status: 签约状态
    """
    def __init__(
        self,
        uid = None,
        token = None,
        status = None
    ):
        super().__init__()
        self.uid = uid
        self.token = token
        self.status = status


class H5UserSignRequest(BaseRequest):
    """
    申请签约请求-请求

    :type token: string
    :param token: H5 签约 token

    :type color: string
    :param color: H5 页面主题颜色

    :type url: string
    :param url: 回调 URL 地址

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


class H5UserSignResponse(BaseRequest):
    """
    申请签约返回-响应

    :type url: string
    :param url: H5 签约页面 URL
    """
    def __init__(
        self,
        url = None
    ):
        super().__init__()
        self.url = url


class GetH5UserSignStatusRequest(BaseRequest):
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


class GetH5UserSignStatusResponse(BaseRequest):
    """
    获取用户签约状态返回-响应

    :type signed_at: string
    :param signed_at: 签约时间

    :type status: int
    :param status: 用户签约状态
    """
    def __init__(
        self,
        signed_at = None,
        status = None
    ):
        super().__init__()
        self.signed_at = signed_at
        self.status = status


class H5UserReleaseRequest(BaseRequest):
    """
    用户解约（测试账号专用接口）请求-请求

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type real_name: string
    :param real_name: 姓名

    :type id_card: string
    :param id_card: 证件号码

    :type certificate_type: int
    :param certificate_type: 证件类型 0：身份证 2：港澳居民来往内地通行证 3：护照 5：台湾居民来往大陆通行证 9：港澳居民居住证 10：台湾居民居住证 11：外国人永久居留身份证 12：外国人工作许可证
    """
    def __init__(
        self,
        broker_id = None,
        dealer_id = None,
        real_name = None,
        id_card = None,
        certificate_type = None
    ):
        super().__init__()
        self.broker_id = broker_id
        self.dealer_id = dealer_id
        self.real_name = real_name
        self.id_card = id_card
        self.certificate_type = certificate_type


class H5UserReleaseResponse(BaseRequest):
    """
    用户解约（测试账号专用接口）返回-响应

    :type status: string
    :param status: 是否解约成功
    """
    def __init__(
        self,
        status = None
    ):
        super().__init__()
        self.status = status


class NotifyH5UserSignRequest(BaseRequest):
    """
    签约回调-请求

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type real_name: string
    :param real_name: 姓名

    :type id_card: string
    :param id_card: 证件号码

    :type phone: string
    :param phone: 预签约手机号
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
