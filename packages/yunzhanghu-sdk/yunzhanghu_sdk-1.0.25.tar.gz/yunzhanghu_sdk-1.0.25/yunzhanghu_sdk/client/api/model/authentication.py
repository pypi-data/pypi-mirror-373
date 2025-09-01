"""用户信息验证"""

from ...base import BaseRequest


class BankCardFourAuthVerifyRequest(BaseRequest):
    """
    银行卡四要素鉴权请求（下发短信验证码）请求-请求

    :type card_no: string
    :param card_no: 银行卡号

    :type id_card: string
    :param id_card: 身份证号码

    :type real_name: string
    :param real_name: 姓名

    :type mobile: string
    :param mobile: 银行预留手机号
    """
    def __init__(
        self,
        card_no = None,
        id_card = None,
        real_name = None,
        mobile = None
    ):
        super().__init__()
        self.card_no = card_no
        self.id_card = id_card
        self.real_name = real_name
        self.mobile = mobile


class BankCardFourAuthVerifyResponse(BaseRequest):
    """
    银行卡四要素鉴权请求（下发短信验证码）返回-响应

    :type ref: string
    :param ref: 交易凭证
    """
    def __init__(
        self,
        ref = None
    ):
        super().__init__()
        self.ref = ref


class BankCardFourAuthConfirmRequest(BaseRequest):
    """
    银行卡四要素确认请求（上传短信验证码）请求-请求

    :type card_no: string
    :param card_no: 银行卡号

    :type id_card: string
    :param id_card: 身份证号码

    :type real_name: string
    :param real_name: 姓名

    :type mobile: string
    :param mobile: 银行预留手机号

    :type captcha: string
    :param captcha: 短信验证码

    :type ref: string
    :param ref: 交易凭证
    """
    def __init__(
        self,
        card_no = None,
        id_card = None,
        real_name = None,
        mobile = None,
        captcha = None,
        ref = None
    ):
        super().__init__()
        self.card_no = card_no
        self.id_card = id_card
        self.real_name = real_name
        self.mobile = mobile
        self.captcha = captcha
        self.ref = ref


class BankCardFourAuthConfirmResponse(BaseRequest):
    """
    银行卡四要素确认请求（上传短信验证码）返回-响应
    """


class BankCardFourVerifyRequest(BaseRequest):
    """
    银行卡四要素验证请求-请求

    :type card_no: string
    :param card_no: 银行卡号

    :type id_card: string
    :param id_card: 身份证号码

    :type real_name: string
    :param real_name: 姓名

    :type mobile: string
    :param mobile: 银行预留手机号
    """
    def __init__(
        self,
        card_no = None,
        id_card = None,
        real_name = None,
        mobile = None
    ):
        super().__init__()
        self.card_no = card_no
        self.id_card = id_card
        self.real_name = real_name
        self.mobile = mobile


class BankCardFourVerifyResponse(BaseRequest):
    """
    银行卡四要素验证返回-响应
    """


class BankCardThreeVerifyRequest(BaseRequest):
    """
    银行卡三要素验证请求-请求

    :type card_no: string
    :param card_no: 银行卡号

    :type id_card: string
    :param id_card: 身份证号码

    :type real_name: string
    :param real_name: 姓名
    """
    def __init__(
        self,
        card_no = None,
        id_card = None,
        real_name = None
    ):
        super().__init__()
        self.card_no = card_no
        self.id_card = id_card
        self.real_name = real_name


class BankCardThreeVerifyResponse(BaseRequest):
    """
    银行卡三要素验证返回-响应
    """


class IDCardVerifyRequest(BaseRequest):
    """
    身份证实名验证请求-请求

    :type id_card: string
    :param id_card: 身份证号码

    :type real_name: string
    :param real_name: 姓名
    """
    def __init__(
        self,
        id_card = None,
        real_name = None
    ):
        super().__init__()
        self.id_card = id_card
        self.real_name = real_name


class IDCardVerifyResponse(BaseRequest):
    """
    身份证实名验证返回-响应
    """


class UserExemptedInfoRequest(BaseRequest):
    """
    上传非居民身份证验证名单信息请求-请求

    :type card_type: string
    :param card_type: 证件类型码

    :type id_card: string
    :param id_card: 证件号码

    :type real_name: string
    :param real_name: 姓名

    :type comment_apply: string
    :param comment_apply: 申请备注

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type user_images: list
    :param user_images: 人员信息图片

    :type country: string
    :param country: 国别（地区）代码

    :type birthday: string
    :param birthday: 出生日期

    :type gender: string
    :param gender: 性别

    :type notify_url: string
    :param notify_url: 回调地址

    :type ref: string
    :param ref: 请求流水号

    :type image_urls: list
    :param image_urls: 证件照片 URL 地址
    """
    def __init__(
        self,
        card_type = None,
        id_card = None,
        real_name = None,
        comment_apply = None,
        broker_id = None,
        dealer_id = None,
        user_images = None,
        country = None,
        birthday = None,
        gender = None,
        notify_url = None,
        ref = None,
        image_urls = None
    ):
        super().__init__()
        self.card_type = card_type
        self.id_card = id_card
        self.real_name = real_name
        self.comment_apply = comment_apply
        self.broker_id = broker_id
        self.dealer_id = dealer_id
        self.user_images = user_images
        self.country = country
        self.birthday = birthday
        self.gender = gender
        self.notify_url = notify_url
        self.ref = ref
        self.image_urls = image_urls


class UserExemptedInfoResponse(BaseRequest):
    """
    上传非居民身份证验证名单信息返回-响应

    :type ok: string
    :param ok: 是否上传成功
    """
    def __init__(
        self,
        ok = None
    ):
        super().__init__()
        self.ok = ok


class NotifyUserExemptedInfoRequest(BaseRequest):
    """
    非居民身份证验证名单审核结果回调通知-请求

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type real_name: string
    :param real_name: 姓名

    :type id_card: string
    :param id_card: 证件号

    :type status: string
    :param status: 审核状态

    :type ref: string
    :param ref: 流水号

    :type comment: string
    :param comment: 审核信息
    """
    def __init__(
        self,
        broker_id = None,
        dealer_id = None,
        real_name = None,
        id_card = None,
        status = None,
        ref = None,
        comment = None
    ):
        super().__init__()
        self.broker_id = broker_id
        self.dealer_id = dealer_id
        self.real_name = real_name
        self.id_card = id_card
        self.status = status
        self.ref = ref
        self.comment = comment


class UserWhiteCheckRequest(BaseRequest):
    """
    查看用户是否在非居民身份证验证名单中请求-请求

    :type id_card: string
    :param id_card: 证件号码

    :type real_name: string
    :param real_name: 姓名
    """
    def __init__(
        self,
        id_card = None,
        real_name = None
    ):
        super().__init__()
        self.id_card = id_card
        self.real_name = real_name


class UserWhiteCheckResponse(BaseRequest):
    """
    查看用户是否在非居民身份证验证名单中返回-响应

    :type ok: bool
    :param ok: 
    """
    def __init__(
        self,
        ok = None
    ):
        super().__init__()
        self.ok = ok


class GetBankCardInfoRequest(BaseRequest):
    """
    银行卡信息查询请求-请求

    :type card_no: string
    :param card_no: 银行卡号

    :type bank_name: string
    :param bank_name: 银行名称
    """
    def __init__(
        self,
        card_no = None,
        bank_name = None
    ):
        super().__init__()
        self.card_no = card_no
        self.bank_name = bank_name


class GetBankCardInfoResponse(BaseRequest):
    """
    银行卡信息查询返回-响应

    :type bank_code: string
    :param bank_code: 银行代码

    :type bank_name: string
    :param bank_name: 银行名称

    :type card_type: string
    :param card_type: 卡类型

    :type is_support: bool
    :param is_support: 云账户是否支持向该银行支付
    """
    def __init__(
        self,
        bank_code = None,
        bank_name = None,
        card_type = None,
        is_support = None
    ):
        super().__init__()
        self.bank_code = bank_code
        self.bank_name = bank_name
        self.card_type = card_type
        self.is_support = is_support
