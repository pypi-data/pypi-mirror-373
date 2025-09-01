"""实时支付"""

from ...base import BaseRequest


class CreateBankpayOrderRequest(BaseRequest):
    """
    银行卡实时支付请求-请求

    :type order_id: string
    :param order_id: 平台企业订单号

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type real_name: string
    :param real_name: 姓名

    :type card_no: string
    :param card_no: 银行卡号

    :type id_card: string
    :param id_card: 身份证号码

    :type phone_no: string
    :param phone_no: 手机号

    :type pay: string
    :param pay: 订单金额

    :type pay_remark: string
    :param pay_remark: 订单备注

    :type notify_url: string
    :param notify_url: 回调地址

    :type project_id: string
    :param project_id: 项目标识
    """
    def __init__(
        self,
        order_id = None,
        dealer_id = None,
        broker_id = None,
        real_name = None,
        card_no = None,
        id_card = None,
        phone_no = None,
        pay = None,
        pay_remark = None,
        notify_url = None,
        project_id = None
    ):
        super().__init__()
        self.order_id = order_id
        self.dealer_id = dealer_id
        self.broker_id = broker_id
        self.real_name = real_name
        self.card_no = card_no
        self.id_card = id_card
        self.phone_no = phone_no
        self.pay = pay
        self.pay_remark = pay_remark
        self.notify_url = notify_url
        self.project_id = project_id


class CreateBankpayOrderResponse(BaseRequest):
    """
    银行卡实时支付返回-响应

    :type order_id: string
    :param order_id: 平台企业订单号

    :type ref: string
    :param ref: 综合服务平台流水号

    :type pay: string
    :param pay: 订单金额
    """
    def __init__(
        self,
        order_id = None,
        ref = None,
        pay = None
    ):
        super().__init__()
        self.order_id = order_id
        self.ref = ref
        self.pay = pay


class CreateAlipayOrderRequest(BaseRequest):
    """
    支付宝实时支付请求-请求

    :type order_id: string
    :param order_id: 平台企业订单号

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type real_name: string
    :param real_name: 姓名

    :type card_no: string
    :param card_no: 支付宝账户

    :type id_card: string
    :param id_card: 身份证号码

    :type phone_no: string
    :param phone_no: 手机号

    :type pay: string
    :param pay: 订单金额

    :type pay_remark: string
    :param pay_remark: 订单备注

    :type notify_url: string
    :param notify_url: 回调地址

    :type project_id: string
    :param project_id: 项目标识

    :type check_name: string
    :param check_name: 校验支付宝账户姓名，固定值：Check
    """
    def __init__(
        self,
        order_id = None,
        dealer_id = None,
        broker_id = None,
        real_name = None,
        card_no = None,
        id_card = None,
        phone_no = None,
        pay = None,
        pay_remark = None,
        notify_url = None,
        project_id = None,
        check_name = None
    ):
        super().__init__()
        self.order_id = order_id
        self.dealer_id = dealer_id
        self.broker_id = broker_id
        self.real_name = real_name
        self.card_no = card_no
        self.id_card = id_card
        self.phone_no = phone_no
        self.pay = pay
        self.pay_remark = pay_remark
        self.notify_url = notify_url
        self.project_id = project_id
        self.check_name = check_name


class CreateAlipayOrderResponse(BaseRequest):
    """
    支付宝实时支付返回-响应

    :type order_id: string
    :param order_id: 平台企业订单号

    :type ref: string
    :param ref: 综合服务平台流水号

    :type pay: string
    :param pay: 订单金额
    """
    def __init__(
        self,
        order_id = None,
        ref = None,
        pay = None
    ):
        super().__init__()
        self.order_id = order_id
        self.ref = ref
        self.pay = pay


class CreateWxpayOrderRequest(BaseRequest):
    """
    微信实时支付请求-请求

    :type order_id: string
    :param order_id: 平台企业订单号

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type real_name: string
    :param real_name: 姓名

    :type openid: string
    :param openid: 微信用户 openid

    :type id_card: string
    :param id_card: 身份证号码

    :type phone_no: string
    :param phone_no: 手机号

    :type pay: string
    :param pay: 订单金额

    :type pay_remark: string
    :param pay_remark: 订单备注

    :type notify_url: string
    :param notify_url: 回调地址

    :type wx_app_id: string
    :param wx_app_id: 平台企业微信 AppID

    :type wxpay_mode: string
    :param wxpay_mode: 微信支付模式，固定值：transfer

    :type project_id: string
    :param project_id: 项目标识

    :type notes: string
    :param notes: 描述信息，该字段已废弃
    """
    def __init__(
        self,
        order_id = None,
        dealer_id = None,
        broker_id = None,
        real_name = None,
        openid = None,
        id_card = None,
        phone_no = None,
        pay = None,
        pay_remark = None,
        notify_url = None,
        wx_app_id = None,
        wxpay_mode = None,
        project_id = None,
        notes = None
    ):
        super().__init__()
        self.order_id = order_id
        self.dealer_id = dealer_id
        self.broker_id = broker_id
        self.real_name = real_name
        self.openid = openid
        self.id_card = id_card
        self.phone_no = phone_no
        self.pay = pay
        self.pay_remark = pay_remark
        self.notify_url = notify_url
        self.wx_app_id = wx_app_id
        self.wxpay_mode = wxpay_mode
        self.project_id = project_id
        self.notes = notes


class CreateWxpayOrderResponse(BaseRequest):
    """
    微信实时支付返回-响应

    :type order_id: string
    :param order_id: 平台企业订单号

    :type ref: string
    :param ref: 综合服务平台流水号，唯一

    :type pay: string
    :param pay: 订单金额
    """
    def __init__(
        self,
        order_id = None,
        ref = None,
        pay = None
    ):
        super().__init__()
        self.order_id = order_id
        self.ref = ref
        self.pay = pay


class GetOrderRequest(BaseRequest):
    """
    查询单笔订单信息请求-请求

    :type order_id: string
    :param order_id: 平台企业订单号

    :type channel: string
    :param channel: 支付路径名，银行卡（默认）、支付宝、微信

    :type data_type: string
    :param data_type: 数据类型，如果为 encryption，则对返回的 data 进行加密
    """
    def __init__(
        self,
        order_id = None,
        channel = None,
        data_type = None
    ):
        super().__init__()
        self.order_id = order_id
        self.channel = channel
        self.data_type = data_type


class GetOrderResponse(BaseRequest):
    """
    查询单笔订单信息返回-响应

    :type order_id: string
    :param order_id: 平台企业订单号

    :type pay: string
    :param pay: 订单金额

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type real_name: string
    :param real_name: 姓名

    :type card_no: string
    :param card_no: 收款人账号

    :type id_card: string
    :param id_card: 身份证号码

    :type phone_no: string
    :param phone_no: 手机号

    :type status: string
    :param status: 订单状态码

    :type status_detail: string
    :param status_detail: 订单详细状态码

    :type status_message: string
    :param status_message: 订单状态码描述

    :type status_detail_message: string
    :param status_detail_message: 订单详细状态码描述

    :type supplemental_detail_message: string
    :param supplemental_detail_message: 订单状态补充信息

    :type broker_amount: string
    :param broker_amount: 综合服务主体支付金额

    :type ref: string
    :param ref: 综合服务平台流水号

    :type broker_bank_bill: string
    :param broker_bank_bill: 支付交易流水号

    :type withdraw_platform: string
    :param withdraw_platform: 支付路径

    :type created_at: string
    :param created_at: 订单接收时间，精确到秒

    :type finished_time: string
    :param finished_time: 订单完成时间，精确到秒

    :type broker_fee: string
    :param broker_fee: 应收综合服务主体加成服务费金额

    :type broker_real_fee: string
    :param broker_real_fee: 应收余额账户支出加成服务费金额

    :type broker_deduct_fee: string
    :param broker_deduct_fee: 应收加成服务费抵扣金额

    :type user_fee: string
    :param user_fee: 应收用户加成服务费金额

    :type received_broker_fee: string
    :param received_broker_fee: 实收综合服务主体加成服务费金额

    :type received_broker_real_fee: string
    :param received_broker_real_fee: 实收余额账户支出加成服务费金额

    :type received_broker_deduct_fee: string
    :param received_broker_deduct_fee: 实收加成服务费抵扣金额

    :type received_user_fee: string
    :param received_user_fee: 实收用户加成服务费金额

    :type pay_remark: string
    :param pay_remark: 订单备注

    :type bank_name: string
    :param bank_name: 银行名称

    :type project_id: string
    :param project_id: 项目标识

    :type anchor_id: string
    :param anchor_id: 新就业形态劳动者 ID，该字段已废弃

    :type notes: string
    :param notes: 描述信息，该字段已废弃

    :type sys_amount: string
    :param sys_amount: 系统支付金额，该字段已废弃

    :type tax: string
    :param tax: 税费，该字段已废弃

    :type sys_fee: string
    :param sys_fee: 系统支付费用，该字段已废弃
    """
    def __init__(
        self,
        order_id = None,
        pay = None,
        broker_id = None,
        dealer_id = None,
        real_name = None,
        card_no = None,
        id_card = None,
        phone_no = None,
        status = None,
        status_detail = None,
        status_message = None,
        status_detail_message = None,
        supplemental_detail_message = None,
        broker_amount = None,
        ref = None,
        broker_bank_bill = None,
        withdraw_platform = None,
        created_at = None,
        finished_time = None,
        broker_fee = None,
        broker_real_fee = None,
        broker_deduct_fee = None,
        user_fee = None,
        received_broker_fee = None,
        received_broker_real_fee = None,
        received_broker_deduct_fee = None,
        received_user_fee = None,
        pay_remark = None,
        bank_name = None,
        project_id = None,
        anchor_id = None,
        notes = None,
        sys_amount = None,
        tax = None,
        sys_fee = None
    ):
        super().__init__()
        self.order_id = order_id
        self.pay = pay
        self.broker_id = broker_id
        self.dealer_id = dealer_id
        self.real_name = real_name
        self.card_no = card_no
        self.id_card = id_card
        self.phone_no = phone_no
        self.status = status
        self.status_detail = status_detail
        self.status_message = status_message
        self.status_detail_message = status_detail_message
        self.supplemental_detail_message = supplemental_detail_message
        self.broker_amount = broker_amount
        self.ref = ref
        self.broker_bank_bill = broker_bank_bill
        self.withdraw_platform = withdraw_platform
        self.created_at = created_at
        self.finished_time = finished_time
        self.broker_fee = broker_fee
        self.broker_real_fee = broker_real_fee
        self.broker_deduct_fee = broker_deduct_fee
        self.user_fee = user_fee
        self.received_broker_fee = received_broker_fee
        self.received_broker_real_fee = received_broker_real_fee
        self.received_broker_deduct_fee = received_broker_deduct_fee
        self.received_user_fee = received_user_fee
        self.pay_remark = pay_remark
        self.bank_name = bank_name
        self.project_id = project_id
        self.anchor_id = anchor_id
        self.notes = notes
        self.sys_amount = sys_amount
        self.tax = tax
        self.sys_fee = sys_fee


class GetDealerVARechargeAccountRequest(BaseRequest):
    """
    查询平台企业汇款信息请求-请求

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type dealer_id: string
    :param dealer_id: 平台企业 ID
    """
    def __init__(
        self,
        broker_id = None,
        dealer_id = None
    ):
        super().__init__()
        self.broker_id = broker_id
        self.dealer_id = dealer_id


class GetDealerVARechargeAccountResponse(BaseRequest):
    """
    查询平台企业汇款信息返回-响应

    :type acct_name: string
    :param acct_name: 账户名称

    :type acct_no: string
    :param acct_no: 专属账户

    :type bank_name: string
    :param bank_name: 银行名称

    :type dealer_acct_name: string
    :param dealer_acct_name: 付款账户
    """
    def __init__(
        self,
        acct_name = None,
        acct_no = None,
        bank_name = None,
        dealer_acct_name = None
    ):
        super().__init__()
        self.acct_name = acct_name
        self.acct_no = acct_no
        self.bank_name = bank_name
        self.dealer_acct_name = dealer_acct_name


class CancelOrderRequest(BaseRequest):
    """
    取消待支付订单请求-请求

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type order_id: string
    :param order_id: 平台企业订单号

    :type ref: string
    :param ref: 综合服务平台流水号

    :type channel: string
    :param channel: 支付路径名，银行卡（默认）、支付宝、微信
    """
    def __init__(
        self,
        dealer_id = None,
        order_id = None,
        ref = None,
        channel = None
    ):
        super().__init__()
        self.dealer_id = dealer_id
        self.order_id = order_id
        self.ref = ref
        self.channel = channel


class CancelOrderResponse(BaseRequest):
    """
    取消待支付订单返回-响应

    :type ok: string
    :param ok: 
    """
    def __init__(
        self,
        ok = None
    ):
        super().__init__()
        self.ok = ok


class RetryOrderRequest(BaseRequest):
    """
    重试挂起状态订单请求-请求

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type order_id: string
    :param order_id: 平台企业订单号

    :type ref: string
    :param ref: 综合服务平台流水号

    :type channel: string
    :param channel: 支付路径名
    """
    def __init__(
        self,
        dealer_id = None,
        order_id = None,
        ref = None,
        channel = None
    ):
        super().__init__()
        self.dealer_id = dealer_id
        self.order_id = order_id
        self.ref = ref
        self.channel = channel


class RetryOrderResponse(BaseRequest):
    """
    重试挂起状态订单返回-响应

    :type ok: string
    :param ok: 请求标识
    """
    def __init__(
        self,
        ok = None
    ):
        super().__init__()
        self.ok = ok


class ListAccountRequest(BaseRequest):
    """
    查询平台企业余额请求-请求

    :type dealer_id: string
    :param dealer_id: 平台企业 ID
    """
    def __init__(
        self,
        dealer_id = None
    ):
        super().__init__()
        self.dealer_id = dealer_id


class ListAccountResponse(BaseRequest):
    """
    查询平台企业余额返回-响应

    :type dealer_infos: list
    :param dealer_infos: 
    """
    def __init__(
        self,
        dealer_infos = None
    ):
        super().__init__()
        self.dealer_infos = dealer_infos


class AccountInfo(BaseRequest):
    """
    账户信息-响应

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type bank_card_balance: string
    :param bank_card_balance: 银行卡余额

    :type is_bank_card: bool
    :param is_bank_card: 是否开通银行卡支付路径

    :type alipay_balance: string
    :param alipay_balance: 支付宝余额

    :type is_alipay: bool
    :param is_alipay: 是否开通支付宝支付路径

    :type wxpay_balance: string
    :param wxpay_balance: 微信余额

    :type is_wxpay: bool
    :param is_wxpay: 是否开通微信支付路径

    :type rebate_fee_balance: string
    :param rebate_fee_balance: 加成服务费返点余额

    :type acct_balance: string
    :param acct_balance: 业务服务费余额

    :type total_balance: string
    :param total_balance: 总余额
    """
    def __init__(
        self,
        broker_id = None,
        bank_card_balance = None,
        is_bank_card = None,
        alipay_balance = None,
        is_alipay = None,
        wxpay_balance = None,
        is_wxpay = None,
        rebate_fee_balance = None,
        acct_balance = None,
        total_balance = None
    ):
        super().__init__()
        self.broker_id = broker_id
        self.bank_card_balance = bank_card_balance
        self.is_bank_card = is_bank_card
        self.alipay_balance = alipay_balance
        self.is_alipay = is_alipay
        self.wxpay_balance = wxpay_balance
        self.is_wxpay = is_wxpay
        self.rebate_fee_balance = rebate_fee_balance
        self.acct_balance = acct_balance
        self.total_balance = total_balance


class GetEleReceiptFileRequest(BaseRequest):
    """
    查询电子回单请求-请求

    :type order_id: string
    :param order_id: 平台企业订单号

    :type ref: string
    :param ref: 综合服务平台流水号
    """
    def __init__(
        self,
        order_id = None,
        ref = None
    ):
        super().__init__()
        self.order_id = order_id
        self.ref = ref


class GetEleReceiptFileResponse(BaseRequest):
    """
    查询电子回单返回-响应

    :type expire_time: string
    :param expire_time: 链接失效时间

    :type file_name: string
    :param file_name: 回单名

    :type url: string
    :param url: 下载链接
    """
    def __init__(
        self,
        expire_time = None,
        file_name = None,
        url = None
    ):
        super().__init__()
        self.expire_time = expire_time
        self.file_name = file_name
        self.url = url


class NotifyOrderRequest(BaseRequest):
    """
    订单支付状态回调通知-请求

    :type notify_id: string
    :param notify_id: 通知 ID

    :type notify_time: string
    :param notify_time: 通知时间

    :type data: NotifyOrderData
    :param data: 返回数据
    """
    def __init__(
        self,
        notify_id = None,
        notify_time = None,
        data = None
    ):
        super().__init__()
        self.notify_id = notify_id
        self.notify_time = notify_time
        self.data = data


class NotifyOrderData(BaseRequest):
    """
    订单支付状态回调通知数据-响应

    :type order_id: string
    :param order_id: 平台企业订单号

    :type pay: string
    :param pay: 订单金额

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type real_name: string
    :param real_name: 姓名

    :type card_no: string
    :param card_no: 收款人账号

    :type id_card: string
    :param id_card: 身份证号码

    :type phone_no: string
    :param phone_no: 手机号

    :type status: string
    :param status: 订单状态码

    :type status_detail: string
    :param status_detail: 订单详细状态码

    :type status_message: string
    :param status_message: 订单状态码描述

    :type status_detail_message: string
    :param status_detail_message: 订单详细状态码描述

    :type supplemental_detail_message: string
    :param supplemental_detail_message: 订单状态补充信息

    :type broker_amount: string
    :param broker_amount: 综合服务主体支付金额

    :type ref: string
    :param ref: 综合服务平台流水号

    :type broker_bank_bill: string
    :param broker_bank_bill: 支付交易流水号

    :type withdraw_platform: string
    :param withdraw_platform: 支付路径

    :type created_at: string
    :param created_at: 订单接收时间，精确到秒

    :type finished_time: string
    :param finished_time: 订单完成时间，精确到秒

    :type broker_fee: string
    :param broker_fee: 应收综合服务主体加成服务费金额

    :type broker_real_fee: string
    :param broker_real_fee: 应收余额账户支出加成服务费金额

    :type broker_deduct_fee: string
    :param broker_deduct_fee: 应收加成服务费抵扣金额

    :type user_fee: string
    :param user_fee: 应收用户加成服务费金额

    :type received_broker_fee: string
    :param received_broker_fee: 实收综合服务主体加成服务费金额

    :type received_broker_real_fee: string
    :param received_broker_real_fee: 实收余额账户支出加成服务费金额

    :type received_broker_deduct_fee: string
    :param received_broker_deduct_fee: 实收加成服务费抵扣金额

    :type received_user_fee: string
    :param received_user_fee: 实收用户加成服务费金额

    :type pay_remark: string
    :param pay_remark: 订单备注

    :type bank_name: string
    :param bank_name: 银行名称

    :type project_id: string
    :param project_id: 项目标识

    :type user_id: string
    :param user_id: 平台企业用户 ID
    """
    def __init__(
        self,
        order_id = None,
        pay = None,
        broker_id = None,
        dealer_id = None,
        real_name = None,
        card_no = None,
        id_card = None,
        phone_no = None,
        status = None,
        status_detail = None,
        status_message = None,
        status_detail_message = None,
        supplemental_detail_message = None,
        broker_amount = None,
        ref = None,
        broker_bank_bill = None,
        withdraw_platform = None,
        created_at = None,
        finished_time = None,
        broker_fee = None,
        broker_real_fee = None,
        broker_deduct_fee = None,
        user_fee = None,
        received_broker_fee = None,
        received_broker_real_fee = None,
        received_broker_deduct_fee = None,
        received_user_fee = None,
        pay_remark = None,
        bank_name = None,
        project_id = None,
        user_id = None
    ):
        super().__init__()
        self.order_id = order_id
        self.pay = pay
        self.broker_id = broker_id
        self.dealer_id = dealer_id
        self.real_name = real_name
        self.card_no = card_no
        self.id_card = id_card
        self.phone_no = phone_no
        self.status = status
        self.status_detail = status_detail
        self.status_message = status_message
        self.status_detail_message = status_detail_message
        self.supplemental_detail_message = supplemental_detail_message
        self.broker_amount = broker_amount
        self.ref = ref
        self.broker_bank_bill = broker_bank_bill
        self.withdraw_platform = withdraw_platform
        self.created_at = created_at
        self.finished_time = finished_time
        self.broker_fee = broker_fee
        self.broker_real_fee = broker_real_fee
        self.broker_deduct_fee = broker_deduct_fee
        self.user_fee = user_fee
        self.received_broker_fee = received_broker_fee
        self.received_broker_real_fee = received_broker_real_fee
        self.received_broker_deduct_fee = received_broker_deduct_fee
        self.received_user_fee = received_user_fee
        self.pay_remark = pay_remark
        self.bank_name = bank_name
        self.project_id = project_id
        self.user_id = user_id


class CreateBatchOrderRequest(BaseRequest):
    """
    批次下单请求-请求

    :type batch_id: string
    :param batch_id: 平台企业批次号

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type channel: string
    :param channel: 支付路径

    :type wx_app_id: string
    :param wx_app_id: 平台企业的微信 AppID

    :type total_pay: string
    :param total_pay: 订单总金额

    :type total_count: string
    :param total_count: 总笔数

    :type mode: string
    :param mode: 支付模式

    :type order_list: list
    :param order_list: 订单列表
    """
    def __init__(
        self,
        batch_id = None,
        dealer_id = None,
        broker_id = None,
        channel = None,
        wx_app_id = None,
        total_pay = None,
        total_count = None,
        mode = None,
        order_list = None
    ):
        super().__init__()
        self.batch_id = batch_id
        self.dealer_id = dealer_id
        self.broker_id = broker_id
        self.channel = channel
        self.wx_app_id = wx_app_id
        self.total_pay = total_pay
        self.total_count = total_count
        self.mode = mode
        self.order_list = order_list


class BatchOrderInfo(BaseRequest):
    """
    批次下单订单信息-响应

    :type order_id: string
    :param order_id: 平台企业订单号

    :type real_name: string
    :param real_name: 姓名

    :type id_card: string
    :param id_card: 身份证号码

    :type card_no: string
    :param card_no: 收款账号

    :type openid: string
    :param openid: 微信用户 openid

    :type phone_no: string
    :param phone_no: 手机号

    :type project_id: string
    :param project_id: 项目标识

    :type pay: string
    :param pay: 订单金额

    :type pay_remark: string
    :param pay_remark: 订单备注

    :type notify_url: string
    :param notify_url: 回调地址
    """
    def __init__(
        self,
        order_id = None,
        real_name = None,
        id_card = None,
        card_no = None,
        openid = None,
        phone_no = None,
        project_id = None,
        pay = None,
        pay_remark = None,
        notify_url = None
    ):
        super().__init__()
        self.order_id = order_id
        self.real_name = real_name
        self.id_card = id_card
        self.card_no = card_no
        self.openid = openid
        self.phone_no = phone_no
        self.project_id = project_id
        self.pay = pay
        self.pay_remark = pay_remark
        self.notify_url = notify_url


class CreateBatchOrderResponse(BaseRequest):
    """
    批次下单返回-响应

    :type batch_id: string
    :param batch_id: 平台企业批次号

    :type result_list: list
    :param result_list: 订单结果列表
    """
    def __init__(
        self,
        batch_id = None,
        result_list = None
    ):
        super().__init__()
        self.batch_id = batch_id
        self.result_list = result_list


class BatchOrderResult(BaseRequest):
    """
    批次下单返回订单信息-响应

    :type order_id: string
    :param order_id: 平台企业订单号

    :type ref: string
    :param ref: 综合服务平台流水号

    :type pay: string
    :param pay: 订单金额

    :type status: string
    :param status: 下单状态

    :type error_reasons: list
    :param error_reasons: 下单失败原因
    """
    def __init__(
        self,
        order_id = None,
        ref = None,
        pay = None,
        status = None,
        error_reasons = None
    ):
        super().__init__()
        self.order_id = order_id
        self.ref = ref
        self.pay = pay
        self.status = status
        self.error_reasons = error_reasons


class BatchOrderErrorReasons(BaseRequest):
    """
    下单失败原因信息-响应

    :type error_code: string
    :param error_code: 不允许下单原因码

    :type error_message: string
    :param error_message: 不允许下单原因描述
    """
    def __init__(
        self,
        error_code = None,
        error_message = None
    ):
        super().__init__()
        self.error_code = error_code
        self.error_message = error_message


class ConfirmBatchOrderRequest(BaseRequest):
    """
    批次确认请求-请求

    :type batch_id: string
    :param batch_id: 平台企业批次号

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type channel: string
    :param channel: 支付路径
    """
    def __init__(
        self,
        batch_id = None,
        dealer_id = None,
        broker_id = None,
        channel = None
    ):
        super().__init__()
        self.batch_id = batch_id
        self.dealer_id = dealer_id
        self.broker_id = broker_id
        self.channel = channel


class ConfirmBatchOrderResponse(BaseRequest):
    """
    批次确认返回-响应
    """


class QueryBatchOrderRequest(BaseRequest):
    """
    查询批次订单信息请求-请求

    :type batch_id: string
    :param batch_id: 平台企业批次号

    :type dealer_id: string
    :param dealer_id: 平台企业 ID
    """
    def __init__(
        self,
        batch_id = None,
        dealer_id = None
    ):
        super().__init__()
        self.batch_id = batch_id
        self.dealer_id = dealer_id


class QueryBatchOrderResponse(BaseRequest):
    """
    查询批次订单信息返回-响应

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type batch_id: string
    :param batch_id: 平台企业批次号

    :type total_count: string
    :param total_count: 总笔数

    :type total_pay: string
    :param total_pay: 订单总金额

    :type channel: string
    :param channel: 支付路径

    :type batch_status: string
    :param batch_status: 批次状态码

    :type batch_status_message: string
    :param batch_status_message: 批次状态码描述

    :type batch_received_time: string
    :param batch_received_time: 批次接收时间

    :type order_list: list
    :param order_list: 批次订单列表
    """
    def __init__(
        self,
        broker_id = None,
        dealer_id = None,
        batch_id = None,
        total_count = None,
        total_pay = None,
        channel = None,
        batch_status = None,
        batch_status_message = None,
        batch_received_time = None,
        order_list = None
    ):
        super().__init__()
        self.broker_id = broker_id
        self.dealer_id = dealer_id
        self.batch_id = batch_id
        self.total_count = total_count
        self.total_pay = total_pay
        self.channel = channel
        self.batch_status = batch_status
        self.batch_status_message = batch_status_message
        self.batch_received_time = batch_received_time
        self.order_list = order_list


class QueryBatchOrderInfo(BaseRequest):
    """
    查询批次订单信息订单详情-响应

    :type order_id: string
    :param order_id: 平台企业订单号

    :type pay: string
    :param pay: 订单金额

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type real_name: string
    :param real_name: 姓名

    :type card_no: string
    :param card_no: 收款人账号

    :type id_card: string
    :param id_card: 身份证号码

    :type phone_no: string
    :param phone_no: 手机号

    :type status: string
    :param status: 订单状态码

    :type status_detail: string
    :param status_detail: 订单详情状态码

    :type status_message: string
    :param status_message: 订单状态码描述

    :type status_detail_message: string
    :param status_detail_message: 订单详情状态码描述

    :type supplemental_detail_message: string
    :param supplemental_detail_message: 订单状态补充信息

    :type broker_amount: string
    :param broker_amount: 综合服务主体支付金额

    :type ref: string
    :param ref: 综合服务平台流水号

    :type broker_bank_bill: string
    :param broker_bank_bill: 支付交易流水号

    :type withdraw_platform: string
    :param withdraw_platform: 支付路径

    :type created_at: string
    :param created_at: 订单接收时间

    :type finished_time: string
    :param finished_time: 订单完成时间

    :type broker_fee: string
    :param broker_fee: 应收综合服务主体加成服务费金额

    :type broker_real_fee: string
    :param broker_real_fee: 应收余额账户支出加成服务费金额

    :type broker_deduct_fee: string
    :param broker_deduct_fee: 应收加成服务费抵扣金额

    :type user_fee: string
    :param user_fee: 应收用户加成服务费金额

    :type received_broker_fee: string
    :param received_broker_fee: 实收综合服务主体加成服务费金额

    :type received_broker_real_fee: string
    :param received_broker_real_fee: 实收余额账户支出加成服务费金额

    :type received_broker_deduct_fee: string
    :param received_broker_deduct_fee: 实收加成服务费抵扣金额

    :type received_user_fee: string
    :param received_user_fee: 实收用户加成服务费金额

    :type pay_remark: string
    :param pay_remark: 订单备注

    :type bank_name: string
    :param bank_name: 银行名称

    :type project_id: string
    :param project_id: 业务线标识
    """
    def __init__(
        self,
        order_id = None,
        pay = None,
        broker_id = None,
        dealer_id = None,
        real_name = None,
        card_no = None,
        id_card = None,
        phone_no = None,
        status = None,
        status_detail = None,
        status_message = None,
        status_detail_message = None,
        supplemental_detail_message = None,
        broker_amount = None,
        ref = None,
        broker_bank_bill = None,
        withdraw_platform = None,
        created_at = None,
        finished_time = None,
        broker_fee = None,
        broker_real_fee = None,
        broker_deduct_fee = None,
        user_fee = None,
        received_broker_fee = None,
        received_broker_real_fee = None,
        received_broker_deduct_fee = None,
        received_user_fee = None,
        pay_remark = None,
        bank_name = None,
        project_id = None
    ):
        super().__init__()
        self.order_id = order_id
        self.pay = pay
        self.broker_id = broker_id
        self.dealer_id = dealer_id
        self.real_name = real_name
        self.card_no = card_no
        self.id_card = id_card
        self.phone_no = phone_no
        self.status = status
        self.status_detail = status_detail
        self.status_message = status_message
        self.status_detail_message = status_detail_message
        self.supplemental_detail_message = supplemental_detail_message
        self.broker_amount = broker_amount
        self.ref = ref
        self.broker_bank_bill = broker_bank_bill
        self.withdraw_platform = withdraw_platform
        self.created_at = created_at
        self.finished_time = finished_time
        self.broker_fee = broker_fee
        self.broker_real_fee = broker_real_fee
        self.broker_deduct_fee = broker_deduct_fee
        self.user_fee = user_fee
        self.received_broker_fee = received_broker_fee
        self.received_broker_real_fee = received_broker_real_fee
        self.received_broker_deduct_fee = received_broker_deduct_fee
        self.received_user_fee = received_user_fee
        self.pay_remark = pay_remark
        self.bank_name = bank_name
        self.project_id = project_id


class CancelBatchOrderRequest(BaseRequest):
    """
    批次撤销请求-请求

    :type batch_id: string
    :param batch_id: 平台企业批次号

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type broker_id: string
    :param broker_id: 综合服务主体 ID
    """
    def __init__(
        self,
        batch_id = None,
        dealer_id = None,
        broker_id = None
    ):
        super().__init__()
        self.batch_id = batch_id
        self.dealer_id = dealer_id
        self.broker_id = broker_id


class CancelBatchOrderResponse(BaseRequest):
    """
    批次撤销返回-响应
    """


class CheckUserAmountRequest(BaseRequest):
    """
    用户结算金额校验请求-请求

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type real_name: string
    :param real_name: 姓名

    :type id_card: string
    :param id_card: 身份证号码

    :type amount: string
    :param amount: 校验金额
    """
    def __init__(
        self,
        broker_id = None,
        real_name = None,
        id_card = None,
        amount = None
    ):
        super().__init__()
        self.broker_id = broker_id
        self.real_name = real_name
        self.id_card = id_card
        self.amount = amount


class CheckUserAmountResponse(BaseRequest):
    """
    用户结算金额校验返回-响应

    :type is_over_whole_user_month_quota: bool
    :param is_over_whole_user_month_quota: 是否超过月限额

    :type is_over_whole_user_year_quota: bool
    :param is_over_whole_user_year_quota: 是否超过年限额
    """
    def __init__(
        self,
        is_over_whole_user_month_quota = None,
        is_over_whole_user_year_quota = None
    ):
        super().__init__()
        self.is_over_whole_user_month_quota = is_over_whole_user_month_quota
        self.is_over_whole_user_year_quota = is_over_whole_user_year_quota


class GetOrderLxlwRequest(BaseRequest):
    """
    查询劳务模式单笔订单信息请求-请求

    :type order_id: string
    :param order_id: 平台企业订单号

    :type channel: string
    :param channel: 支付路径

    :type data_type: string
    :param data_type: 数据类型
    """
    def __init__(
        self,
        order_id = None,
        channel = None,
        data_type = None
    ):
        super().__init__()
        self.order_id = order_id
        self.channel = channel
        self.data_type = data_type


class GetOrderLxlwResponse(BaseRequest):
    """
    查询劳务模式单笔订单信息返回-响应

    :type order_id: string
    :param order_id: 平台企业订单号

    :type pay: string
    :param pay: 订单金额

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type real_name: string
    :param real_name: 姓名

    :type card_no: string
    :param card_no: 收款人账号

    :type id_card: string
    :param id_card: 身份证号码

    :type phone_no: string
    :param phone_no: 手机号

    :type status: string
    :param status: 订单状态码

    :type status_detail: string
    :param status_detail: 订单详细状态码

    :type status_message: string
    :param status_message: 订单状态码描述

    :type status_detail_message: string
    :param status_detail_message: 订单详情状态码描述

    :type supplemental_detail_message: string
    :param supplemental_detail_message: 订单状态补充信息

    :type broker_amount: string
    :param broker_amount: 综合服务主体支付金额

    :type ref: string
    :param ref: 综合服务平台流水号

    :type broker_bank_bill: string
    :param broker_bank_bill: 支付交易流水号

    :type withdraw_platform: string
    :param withdraw_platform: 支付路径

    :type created_at: string
    :param created_at: 订单接收时间，精确到秒

    :type finished_time: string
    :param finished_time: 订单完成时间，精确到秒

    :type broker_fee: string
    :param broker_fee: 应收综合服务主体加成服务费金额

    :type broker_real_fee: string
    :param broker_real_fee: 应收余额账户支出加成服务费金额

    :type broker_deduct_fee: string
    :param broker_deduct_fee: 应收加成服务费抵扣金额

    :type user_fee: string
    :param user_fee: 应收用户加成服务费金额

    :type received_broker_fee: string
    :param received_broker_fee: 实收综合服务主体加成服务费金额

    :type received_broker_real_fee: string
    :param received_broker_real_fee: 实收余额账户支出加成服务费金额

    :type received_broker_deduct_fee: string
    :param received_broker_deduct_fee: 实收加成服务费抵扣金额

    :type received_user_fee: string
    :param received_user_fee: 实收用户加成服务费金额

    :type pay_remark: string
    :param pay_remark: 订单备注

    :type bank_name: string
    :param bank_name: 银行名称

    :type project_id: string
    :param project_id: 业务线标识

    :type anchor_id: string
    :param anchor_id: 新就业形态劳动者 ID，该字段已废弃

    :type notes: string
    :param notes: 描述信息，该字段已废弃

    :type sys_amount: string
    :param sys_amount: 系统支付金额，该字段已废弃

    :type tax: string
    :param tax: 税费，该字段已废弃

    :type sys_fee: string
    :param sys_fee: 系统支付费用，该字段已废弃

    :type user_real_amount: string
    :param user_real_amount: 用户实收金额

    :type tax_detail: TaxDetail
    :param tax_detail: 缴税明细
    """
    def __init__(
        self,
        order_id = None,
        pay = None,
        broker_id = None,
        dealer_id = None,
        real_name = None,
        card_no = None,
        id_card = None,
        phone_no = None,
        status = None,
        status_detail = None,
        status_message = None,
        status_detail_message = None,
        supplemental_detail_message = None,
        broker_amount = None,
        ref = None,
        broker_bank_bill = None,
        withdraw_platform = None,
        created_at = None,
        finished_time = None,
        broker_fee = None,
        broker_real_fee = None,
        broker_deduct_fee = None,
        user_fee = None,
        received_broker_fee = None,
        received_broker_real_fee = None,
        received_broker_deduct_fee = None,
        received_user_fee = None,
        pay_remark = None,
        bank_name = None,
        project_id = None,
        anchor_id = None,
        notes = None,
        sys_amount = None,
        tax = None,
        sys_fee = None,
        user_real_amount = None,
        tax_detail = None
    ):
        super().__init__()
        self.order_id = order_id
        self.pay = pay
        self.broker_id = broker_id
        self.dealer_id = dealer_id
        self.real_name = real_name
        self.card_no = card_no
        self.id_card = id_card
        self.phone_no = phone_no
        self.status = status
        self.status_detail = status_detail
        self.status_message = status_message
        self.status_detail_message = status_detail_message
        self.supplemental_detail_message = supplemental_detail_message
        self.broker_amount = broker_amount
        self.ref = ref
        self.broker_bank_bill = broker_bank_bill
        self.withdraw_platform = withdraw_platform
        self.created_at = created_at
        self.finished_time = finished_time
        self.broker_fee = broker_fee
        self.broker_real_fee = broker_real_fee
        self.broker_deduct_fee = broker_deduct_fee
        self.user_fee = user_fee
        self.received_broker_fee = received_broker_fee
        self.received_broker_real_fee = received_broker_real_fee
        self.received_broker_deduct_fee = received_broker_deduct_fee
        self.received_user_fee = received_user_fee
        self.pay_remark = pay_remark
        self.bank_name = bank_name
        self.project_id = project_id
        self.anchor_id = anchor_id
        self.notes = notes
        self.sys_amount = sys_amount
        self.tax = tax
        self.sys_fee = sys_fee
        self.user_real_amount = user_real_amount
        self.tax_detail = tax_detail


class TaxDetail(BaseRequest):
    """
    缴税明细-响应

    :type personal_tax: string
    :param personal_tax: 应纳个税

    :type value_added_tax: string
    :param value_added_tax: 应纳增值税

    :type additional_tax: string
    :param additional_tax: 应纳附加税费

    :type received_personal_tax: string
    :param received_personal_tax: 实纳个税

    :type received_value_added_tax: string
    :param received_value_added_tax: 实纳增值税

    :type received_additional_tax: string
    :param received_additional_tax: 实纳附加税费
    """
    def __init__(
        self,
        personal_tax = None,
        value_added_tax = None,
        additional_tax = None,
        received_personal_tax = None,
        received_value_added_tax = None,
        received_additional_tax = None
    ):
        super().__init__()
        self.personal_tax = personal_tax
        self.value_added_tax = value_added_tax
        self.additional_tax = additional_tax
        self.received_personal_tax = received_personal_tax
        self.received_value_added_tax = received_value_added_tax
        self.received_additional_tax = received_additional_tax


class NotifyOrderLxlwRequest(BaseRequest):
    """
    劳务模式订单支付状态回调通知-请求

    :type notify_id: string
    :param notify_id: 通知 ID

    :type notify_time: string
    :param notify_time: 通知时间

    :type data: NotifyOrderLxlwData
    :param data: 返回数据
    """
    def __init__(
        self,
        notify_id = None,
        notify_time = None,
        data = None
    ):
        super().__init__()
        self.notify_id = notify_id
        self.notify_time = notify_time
        self.data = data


class NotifyOrderLxlwData(BaseRequest):
    """
    劳务模式订单支付状态回调通知数据-响应

    :type order_id: string
    :param order_id: 平台企业订单号

    :type pay: string
    :param pay: 订单金额

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type real_name: string
    :param real_name: 姓名

    :type card_no: string
    :param card_no: 收款人账号

    :type id_card: string
    :param id_card: 身份证号码

    :type phone_no: string
    :param phone_no: 手机号

    :type status: string
    :param status: 订单状态码

    :type status_detail: string
    :param status_detail: 订单详情状态码

    :type status_message: string
    :param status_message: 订单状态码描述

    :type status_detail_message: string
    :param status_detail_message: 订单详情状态码描述

    :type supplemental_detail_message: string
    :param supplemental_detail_message: 订单状态补充信息

    :type broker_amount: string
    :param broker_amount: 综合服务主体支付金额

    :type ref: string
    :param ref: 综合服务平台流水号

    :type broker_bank_bill: string
    :param broker_bank_bill: 支付交易流水号

    :type withdraw_platform: string
    :param withdraw_platform: 支付路径

    :type created_at: string
    :param created_at: 订单接收时间，精确到秒

    :type finished_time: string
    :param finished_time: 订单完成时间，精确到秒

    :type broker_fee: string
    :param broker_fee: 应收综合服务主体加成服务费金额

    :type broker_real_fee: string
    :param broker_real_fee: 应收余额账户支出加成服务费金额

    :type broker_deduct_fee: string
    :param broker_deduct_fee: 应收加成服务费抵扣金额

    :type user_fee: string
    :param user_fee: 应收用户加成服务费金额

    :type received_broker_fee: string
    :param received_broker_fee: 实收综合服务主体加成服务费金额

    :type received_broker_real_fee: string
    :param received_broker_real_fee: 实收余额账户支出加成服务费金额

    :type received_broker_deduct_fee: string
    :param received_broker_deduct_fee: 实收加成服务费抵扣金额

    :type received_user_fee: string
    :param received_user_fee: 实收用户加成服务费金额

    :type pay_remark: string
    :param pay_remark: 订单备注

    :type bank_name: string
    :param bank_name: 银行名称

    :type project_id: string
    :param project_id: 业务线标识

    :type user_real_amount: string
    :param user_real_amount: 用户实收金额

    :type tax_detail: TaxDetail
    :param tax_detail: 缴税明细
    """
    def __init__(
        self,
        order_id = None,
        pay = None,
        broker_id = None,
        dealer_id = None,
        real_name = None,
        card_no = None,
        id_card = None,
        phone_no = None,
        status = None,
        status_detail = None,
        status_message = None,
        status_detail_message = None,
        supplemental_detail_message = None,
        broker_amount = None,
        ref = None,
        broker_bank_bill = None,
        withdraw_platform = None,
        created_at = None,
        finished_time = None,
        broker_fee = None,
        broker_real_fee = None,
        broker_deduct_fee = None,
        user_fee = None,
        received_broker_fee = None,
        received_broker_real_fee = None,
        received_broker_deduct_fee = None,
        received_user_fee = None,
        pay_remark = None,
        bank_name = None,
        project_id = None,
        user_real_amount = None,
        tax_detail = None
    ):
        super().__init__()
        self.order_id = order_id
        self.pay = pay
        self.broker_id = broker_id
        self.dealer_id = dealer_id
        self.real_name = real_name
        self.card_no = card_no
        self.id_card = id_card
        self.phone_no = phone_no
        self.status = status
        self.status_detail = status_detail
        self.status_message = status_message
        self.status_detail_message = status_detail_message
        self.supplemental_detail_message = supplemental_detail_message
        self.broker_amount = broker_amount
        self.ref = ref
        self.broker_bank_bill = broker_bank_bill
        self.withdraw_platform = withdraw_platform
        self.created_at = created_at
        self.finished_time = finished_time
        self.broker_fee = broker_fee
        self.broker_real_fee = broker_real_fee
        self.broker_deduct_fee = broker_deduct_fee
        self.user_fee = user_fee
        self.received_broker_fee = received_broker_fee
        self.received_broker_real_fee = received_broker_real_fee
        self.received_broker_deduct_fee = received_broker_deduct_fee
        self.received_user_fee = received_user_fee
        self.pay_remark = pay_remark
        self.bank_name = bank_name
        self.project_id = project_id
        self.user_real_amount = user_real_amount
        self.tax_detail = tax_detail
