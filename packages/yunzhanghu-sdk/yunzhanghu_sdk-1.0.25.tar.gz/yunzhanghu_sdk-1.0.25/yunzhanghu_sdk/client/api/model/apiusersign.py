"""API 签约"""

from ...base import BaseRequest


class ApiUseSignContractRequest(BaseRequest):
    """
    获取协议预览 URL 请求-请求

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type broker_id: string
    :param broker_id: 综合服务主体 ID
    """
    def __init__(
        self,
        dealer_id = None,
        broker_id = None
    ):
        super().__init__()
        self.dealer_id = dealer_id
        self.broker_id = broker_id


class ApiUseSignContractResponse(BaseRequest):
    """
    获取协议预览 URL 返回-响应

    :type url: string
    :param url: 预览跳转 URL

    :type title: string
    :param title: 协议名称
    """
    def __init__(
        self,
        url = None,
        title = None
    ):
        super().__init__()
        self.url = url
        self.title = title


class ApiUserSignContractRequest(BaseRequest):
    """
    获取协议预览 URL 请求 V2-请求

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type broker_id: string
    :param broker_id: 综合服务主体 ID
    """
    def __init__(
        self,
        dealer_id = None,
        broker_id = None
    ):
        super().__init__()
        self.dealer_id = dealer_id
        self.broker_id = broker_id


class ApiUserSignContractResponse(BaseRequest):
    """
    获取协议预览 URL 返回 V2-响应

    :type url: string
    :param url: 预览跳转 URL

    :type title: string
    :param title: 协议名称
    """
    def __init__(
        self,
        url = None,
        title = None
    ):
        super().__init__()
        self.url = url
        self.title = title


class ApiUserSignRequest(BaseRequest):
    """
    用户签约请求-请求

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type real_name: string
    :param real_name: 姓名

    :type id_card: string
    :param id_card: 证件号码

    :type card_type: string
    :param card_type: 证件类型 idcard：身份证 passport：护照 mtphkm：港澳居民来往内地通行证  mtpt：台湾居民往来大陆通行证 rphkm：中华人民共和国港澳居民居住证 rpt：中华人民共和国台湾居民居住证 fpr：外国人永久居留身份证 ffwp：中华人民共和国外国人就业许可证书
    """
    def __init__(
        self,
        broker_id = None,
        dealer_id = None,
        real_name = None,
        id_card = None,
        card_type = None
    ):
        super().__init__()
        self.broker_id = broker_id
        self.dealer_id = dealer_id
        self.real_name = real_name
        self.id_card = id_card
        self.card_type = card_type


class ApiUserSignResponse(BaseRequest):
    """
    用户签约返回-响应

    :type status: string
    :param status: 是否签约成功
    """
    def __init__(
        self,
        status = None
    ):
        super().__init__()
        self.status = status


class GetApiUserSignStatusRequest(BaseRequest):
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


class GetApiUserSignStatusResponse(BaseRequest):
    """
    获取用户签约状态返回-响应

    :type signed_at: string
    :param signed_at: 签约时间

    :type status: string
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


class ApiUserSignReleaseRequest(BaseRequest):
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

    :type card_type: string
    :param card_type: 证件类型 idcard：身份证 passport：护照 mtphkm：港澳居民来往内地通行证  mtpt：台湾居民往来大陆通行证 rphkm：中华人民共和国港澳居民居住证 rpt：中华人民共和国台湾居民居住证 fpr：外国人永久居留身份证 ffwp：中华人民共和国外国人就业许可证书
    """
    def __init__(
        self,
        broker_id = None,
        dealer_id = None,
        real_name = None,
        id_card = None,
        card_type = None
    ):
        super().__init__()
        self.broker_id = broker_id
        self.dealer_id = dealer_id
        self.real_name = real_name
        self.id_card = id_card
        self.card_type = card_type


class ApiUserSignReleaseResponse(BaseRequest):
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
