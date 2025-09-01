"""对账文件获取"""

from ...base import BaseRequest


class GetDailyOrderFileRequest(BaseRequest):
    """
    查询日订单文件请求-请求

    :type order_date: string
    :param order_date: 订单查询日期, 格式：yyyy-MM-dd
    """
    def __init__(
        self,
        order_date = None
    ):
        super().__init__()
        self.order_date = order_date


class GetDailyOrderFileResponse(BaseRequest):
    """
    查询日订单文件返回-响应

    :type order_download_url: string
    :param order_download_url: 下载地址
    """
    def __init__(
        self,
        order_download_url = None
    ):
        super().__init__()
        self.order_download_url = order_download_url


class GetDailyBillFileV2Request(BaseRequest):
    """
    查询日流水文件请求-请求

    :type bill_date: string
    :param bill_date: 所需获取的日流水日期，格式：yyyy-MM-dd
    """
    def __init__(
        self,
        bill_date = None
    ):
        super().__init__()
        self.bill_date = bill_date


class GetDailyBillFileV2Response(BaseRequest):
    """
    查询日流水文件返回-响应

    :type bill_download_url: string
    :param bill_download_url: 下载地址
    """
    def __init__(
        self,
        bill_download_url = None
    ):
        super().__init__()
        self.bill_download_url = bill_download_url


class ListDealerRechargeRecordV2Request(BaseRequest):
    """
    平台企业预付业务服务费记录请求-请求

    :type begin_at: string
    :param begin_at: 开始时间，格式：yyyy-MM-dd

    :type end_at: string
    :param end_at: 结束时间，格式：yyyy-MM-dd
    """
    def __init__(
        self,
        begin_at = None,
        end_at = None
    ):
        super().__init__()
        self.begin_at = begin_at
        self.end_at = end_at


class ListDealerRechargeRecordV2Response(BaseRequest):
    """
    平台企业预付业务服务费记录返回-响应

    :type data: list
    :param data: 预付业务服务费记录
    """
    def __init__(
        self,
        data = None
    ):
        super().__init__()
        self.data = data


class RechargeRecordInfo(BaseRequest):
    """
    预付业务服务费记录信息-响应

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type recharge_id: int
    :param recharge_id: 预付业务服务费记录 ID

    :type amount: float
    :param amount: 预付业务服务费

    :type actual_amount: float
    :param actual_amount: 实际到账金额

    :type created_at: string
    :param created_at: 创建时间

    :type recharge_channel: string
    :param recharge_channel: 资金用途

    :type remark: string
    :param remark: 预付业务服务费备注

    :type recharge_account_no: string
    :param recharge_account_no: 平台企业付款银行账号
    """
    def __init__(
        self,
        dealer_id = None,
        broker_id = None,
        recharge_id = None,
        amount = None,
        actual_amount = None,
        created_at = None,
        recharge_channel = None,
        remark = None,
        recharge_account_no = None
    ):
        super().__init__()
        self.dealer_id = dealer_id
        self.broker_id = broker_id
        self.recharge_id = recharge_id
        self.amount = amount
        self.actual_amount = actual_amount
        self.created_at = created_at
        self.recharge_channel = recharge_channel
        self.remark = remark
        self.recharge_account_no = recharge_account_no


class ListDailyOrderRequest(BaseRequest):
    """
    查询日订单数据请求-请求

    :type order_date: string
    :param order_date: 订单查询日期, 格式：yyyy-MM-dd格式：yyyy-MM-dd

    :type offset: int
    :param offset: 偏移量

    :type length: int
    :param length: 长度

    :type channel: string
    :param channel: 支付路径名，银行卡（默认）、支付宝、微信

    :type data_type: string
    :param data_type: 如果为 encryption，则对返回的 data 进行加密
    """
    def __init__(
        self,
        order_date = None,
        offset = None,
        length = None,
        channel = None,
        data_type = None
    ):
        super().__init__()
        self.order_date = order_date
        self.offset = offset
        self.length = length
        self.channel = channel
        self.data_type = data_type


class ListDailyOrderResponse(BaseRequest):
    """
    查询日订单数据返回-响应

    :type total_num: int
    :param total_num: 总数目

    :type list: list
    :param list: 条目信息
    """
    def __init__(
        self,
        total_num = None,
        list = None
    ):
        super().__init__()
        self.total_num = total_num
        self.list = list


class DealerOrderInfo(BaseRequest):
    """
    平台企业支付订单信息-响应

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type order_id: string
    :param order_id: 平台企业订单号

    :type ref: string
    :param ref: 订单流水号

    :type batch_id: string
    :param batch_id: 批次ID

    :type real_name: string
    :param real_name: 姓名

    :type card_no: string
    :param card_no: 收款账号

    :type broker_amount: string
    :param broker_amount: 综合服务主体订单金额

    :type broker_fee: string
    :param broker_fee: 应收综合服务主体加成服务费金额

    :type received_broker_fee: string
    :param received_broker_fee: 实收综合服务主体加成服务费金额

    :type bill: string
    :param bill: 支付路径流水号

    :type status: string
    :param status: 订单状态

    :type status_message: string
    :param status_message: 订单状态码描述

    :type status_detail: string
    :param status_detail: 订单详情

    :type status_detail_message: string
    :param status_detail_message: 订单详细状态码描述

    :type supplemental_detail_message: string
    :param supplemental_detail_message: 订单状态补充信息

    :type statement_id: string
    :param statement_id: 短周期授信账单号

    :type fee_statement_id: string
    :param fee_statement_id: 服务费账单号

    :type bal_statement_id: string
    :param bal_statement_id: 余额账单号

    :type channel: string
    :param channel: 支付路径

    :type created_at: string
    :param created_at: 创建时间

    :type finished_time: string
    :param finished_time: 完成时间
    """
    def __init__(
        self,
        broker_id = None,
        dealer_id = None,
        order_id = None,
        ref = None,
        batch_id = None,
        real_name = None,
        card_no = None,
        broker_amount = None,
        broker_fee = None,
        received_broker_fee = None,
        bill = None,
        status = None,
        status_message = None,
        status_detail = None,
        status_detail_message = None,
        supplemental_detail_message = None,
        statement_id = None,
        fee_statement_id = None,
        bal_statement_id = None,
        channel = None,
        created_at = None,
        finished_time = None
    ):
        super().__init__()
        self.broker_id = broker_id
        self.dealer_id = dealer_id
        self.order_id = order_id
        self.ref = ref
        self.batch_id = batch_id
        self.real_name = real_name
        self.card_no = card_no
        self.broker_amount = broker_amount
        self.broker_fee = broker_fee
        self.received_broker_fee = received_broker_fee
        self.bill = bill
        self.status = status
        self.status_message = status_message
        self.status_detail = status_detail
        self.status_detail_message = status_detail_message
        self.supplemental_detail_message = supplemental_detail_message
        self.statement_id = statement_id
        self.fee_statement_id = fee_statement_id
        self.bal_statement_id = bal_statement_id
        self.channel = channel
        self.created_at = created_at
        self.finished_time = finished_time


class ListDailyOrderV2Request(BaseRequest):
    """
    查询日订单数据（支付和退款订单）请求-请求

    :type order_date: string
    :param order_date: 订单查询日期, yyyy-MM-dd 格式

    :type offset: int
    :param offset: 偏移量

    :type length: int
    :param length: 每页返回条数

    :type channel: string
    :param channel: 支付路径名，bankpay：银行卡 alipay：支付宝 wxpay：微信

    :type data_type: string
    :param data_type: 当且仅当参数值为 encryption 时，对返回的 data 进行加密
    """
    def __init__(
        self,
        order_date = None,
        offset = None,
        length = None,
        channel = None,
        data_type = None
    ):
        super().__init__()
        self.order_date = order_date
        self.offset = offset
        self.length = length
        self.channel = channel
        self.data_type = data_type


class ListDailyOrderV2Response(BaseRequest):
    """
    查询日订单数据（支付和退款订单）返回-响应

    :type total_num: int
    :param total_num: 总条数

    :type list: list
    :param list: 条目明细
    """
    def __init__(
        self,
        total_num = None,
        list = None
    ):
        super().__init__()
        self.total_num = total_num
        self.list = list


class DealerOrderInfoV2(BaseRequest):
    """
    平台企业支付订单信息（支付和退款订单）-响应

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type order_type: string
    :param order_type: 订单类型

    :type order_id: string
    :param order_id: 平台企业订单号

    :type ref: string
    :param ref: 综合服务平台流水号

    :type batch_id: string
    :param batch_id: 批次号

    :type real_name: string
    :param real_name: 姓名

    :type card_no: string
    :param card_no: 收款账号

    :type broker_amount: string
    :param broker_amount: 综合服务主体订单金额

    :type broker_fee: string
    :param broker_fee: 应收综合服务主体加成服务费金额

    :type received_broker_fee: string
    :param received_broker_fee: 实收综合服务主体加成服务费金额

    :type bill: string
    :param bill: 支付路径流水号

    :type status: string
    :param status: 订单状态码

    :type status_message: string
    :param status_message: 订单状态码描述

    :type status_detail: string
    :param status_detail: 订单详情状态码

    :type status_detail_message: string
    :param status_detail_message: 订单详细状态码描述

    :type supplemental_detail_message: string
    :param supplemental_detail_message: 订单状态补充信息

    :type statement_id: string
    :param statement_id: 短周期授信账单号

    :type fee_statement_id: string
    :param fee_statement_id: 加成服务费账单号

    :type bal_statement_id: string
    :param bal_statement_id: 余额账单号

    :type channel: string
    :param channel: 支付路径

    :type created_at: string
    :param created_at: 订单接收时间

    :type finished_time: string
    :param finished_time: 订单完成时间

    :type refund_type: string
    :param refund_type: 退款类型

    :type pay_ref: string
    :param pay_ref: 原支付流水号
    """
    def __init__(
        self,
        broker_id = None,
        dealer_id = None,
        order_type = None,
        order_id = None,
        ref = None,
        batch_id = None,
        real_name = None,
        card_no = None,
        broker_amount = None,
        broker_fee = None,
        received_broker_fee = None,
        bill = None,
        status = None,
        status_message = None,
        status_detail = None,
        status_detail_message = None,
        supplemental_detail_message = None,
        statement_id = None,
        fee_statement_id = None,
        bal_statement_id = None,
        channel = None,
        created_at = None,
        finished_time = None,
        refund_type = None,
        pay_ref = None
    ):
        super().__init__()
        self.broker_id = broker_id
        self.dealer_id = dealer_id
        self.order_type = order_type
        self.order_id = order_id
        self.ref = ref
        self.batch_id = batch_id
        self.real_name = real_name
        self.card_no = card_no
        self.broker_amount = broker_amount
        self.broker_fee = broker_fee
        self.received_broker_fee = received_broker_fee
        self.bill = bill
        self.status = status
        self.status_message = status_message
        self.status_detail = status_detail
        self.status_detail_message = status_detail_message
        self.supplemental_detail_message = supplemental_detail_message
        self.statement_id = statement_id
        self.fee_statement_id = fee_statement_id
        self.bal_statement_id = bal_statement_id
        self.channel = channel
        self.created_at = created_at
        self.finished_time = finished_time
        self.refund_type = refund_type
        self.pay_ref = pay_ref


class ListDailyBillRequest(BaseRequest):
    """
    查询日流水数据请求-请求

    :type bill_date: string
    :param bill_date: 流水查询日期

    :type offset: int
    :param offset: 偏移量

    :type length: int
    :param length: 长度

    :type data_type: string
    :param data_type: 如果为 encryption，则对返回的 data 进行加密
    """
    def __init__(
        self,
        bill_date = None,
        offset = None,
        length = None,
        data_type = None
    ):
        super().__init__()
        self.bill_date = bill_date
        self.offset = offset
        self.length = length
        self.data_type = data_type


class ListDailyBillResponse(BaseRequest):
    """
    查询日流水数据返回-响应

    :type total_num: int
    :param total_num: 总条数

    :type list: list
    :param list: 条目信息
    """
    def __init__(
        self,
        total_num = None,
        list = None
    ):
        super().__init__()
        self.total_num = total_num
        self.list = list


class DealerBillInfo(BaseRequest):
    """
    流水详情-响应

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type order_id: string
    :param order_id: 平台企业订单号

    :type ref: string
    :param ref: 资金流水号

    :type broker_product_name: string
    :param broker_product_name: 综合服务主体名称

    :type dealer_product_name: string
    :param dealer_product_name: 平台企业名称

    :type biz_ref: string
    :param biz_ref: 业务订单流水号

    :type acct_type: string
    :param acct_type: 账户类型

    :type amount: string
    :param amount: 入账金额

    :type balance: string
    :param balance: 账户余额

    :type business_category: string
    :param business_category: 业务分类

    :type business_type: string
    :param business_type: 业务类型

    :type consumption_type: string
    :param consumption_type: 收支类型

    :type created_at: string
    :param created_at: 入账时间

    :type remark: string
    :param remark: 备注
    """
    def __init__(
        self,
        broker_id = None,
        dealer_id = None,
        order_id = None,
        ref = None,
        broker_product_name = None,
        dealer_product_name = None,
        biz_ref = None,
        acct_type = None,
        amount = None,
        balance = None,
        business_category = None,
        business_type = None,
        consumption_type = None,
        created_at = None,
        remark = None
    ):
        super().__init__()
        self.broker_id = broker_id
        self.dealer_id = dealer_id
        self.order_id = order_id
        self.ref = ref
        self.broker_product_name = broker_product_name
        self.dealer_product_name = dealer_product_name
        self.biz_ref = biz_ref
        self.acct_type = acct_type
        self.amount = amount
        self.balance = balance
        self.business_category = business_category
        self.business_type = business_type
        self.consumption_type = consumption_type
        self.created_at = created_at
        self.remark = remark


class GetDailyOrderFileV2Request(BaseRequest):
    """
    查询日订单文件（支付和退款订单）请求-请求

    :type order_date: string
    :param order_date: 订单查询日期, 格式：yyyy-MM-dd
    """
    def __init__(
        self,
        order_date = None
    ):
        super().__init__()
        self.order_date = order_date


class GetDailyOrderFileV2Response(BaseRequest):
    """
    查询日订单文件（支付和退款订单）返回-响应

    :type url: string
    :param url: 下载地址
    """
    def __init__(
        self,
        url = None
    ):
        super().__init__()
        self.url = url


class ListBalanceDailyStatementRequest(BaseRequest):
    """
    查询余额日账单数据请求-请求

    :type statement_date: string
    :param statement_date: 账单查询日期 格式：yyyy-MM-dd
    """
    def __init__(
        self,
        statement_date = None
    ):
        super().__init__()
        self.statement_date = statement_date


class ListBalanceDailyStatementResponse(BaseRequest):
    """
    查询余额日账单数据返回-响应

    :type list: list
    :param list: 条目信息
    """
    def __init__(
        self,
        list = None
    ):
        super().__init__()
        self.list = list


class StatementDetail(BaseRequest):
    """
    余额账单信息详情-响应

    :type statement_id: string
    :param statement_id: 账单 ID

    :type statement_date: string
    :param statement_date: 账单日期

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type broker_product_name: string
    :param broker_product_name: 综合服务主体名称

    :type dealer_product_name: string
    :param dealer_product_name: 平台企业名称

    :type biz_type: string
    :param biz_type: 业务类型

    :type total_money: string
    :param total_money: 账单金额

    :type amount: string
    :param amount: 订单金额

    :type reex_amount: string
    :param reex_amount: 退汇金额

    :type fee_amount: string
    :param fee_amount: 实收综合服务主体加成服务费金额

    :type deduct_rebate_fee_amount: string
    :param deduct_rebate_fee_amount: 实收加成服务费抵扣金额

    :type money_adjust: string
    :param money_adjust: 冲补金额

    :type status: string
    :param status: 账单状态

    :type invoice_status: string
    :param invoice_status: 开票状态

    :type project_id: string
    :param project_id: 项目 ID

    :type project_name: string
    :param project_name: 项目名称
    """
    def __init__(
        self,
        statement_id = None,
        statement_date = None,
        broker_id = None,
        dealer_id = None,
        broker_product_name = None,
        dealer_product_name = None,
        biz_type = None,
        total_money = None,
        amount = None,
        reex_amount = None,
        fee_amount = None,
        deduct_rebate_fee_amount = None,
        money_adjust = None,
        status = None,
        invoice_status = None,
        project_id = None,
        project_name = None
    ):
        super().__init__()
        self.statement_id = statement_id
        self.statement_date = statement_date
        self.broker_id = broker_id
        self.dealer_id = dealer_id
        self.broker_product_name = broker_product_name
        self.dealer_product_name = dealer_product_name
        self.biz_type = biz_type
        self.total_money = total_money
        self.amount = amount
        self.reex_amount = reex_amount
        self.fee_amount = fee_amount
        self.deduct_rebate_fee_amount = deduct_rebate_fee_amount
        self.money_adjust = money_adjust
        self.status = status
        self.invoice_status = invoice_status
        self.project_id = project_id
        self.project_name = project_name


class ListDailyOrderSummaryRequest(BaseRequest):
    """
    查询日订单汇总数据请求-请求

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type channel: string
    :param channel: 支付路径，银行卡、支付宝、微信

    :type begin_at: string
    :param begin_at: 订单查询开始日期，格式：yyyy-MM-dd

    :type end_at: string
    :param end_at: 订单查询结束日期，格式：yyyy-MM-dd

    :type filter_type: string
    :param filter_type: 筛选类型，apply：按订单创建时间汇总 complete：按订单完成时间汇总
    """
    def __init__(
        self,
        broker_id = None,
        dealer_id = None,
        channel = None,
        begin_at = None,
        end_at = None,
        filter_type = None
    ):
        super().__init__()
        self.broker_id = broker_id
        self.dealer_id = dealer_id
        self.channel = channel
        self.begin_at = begin_at
        self.end_at = end_at
        self.filter_type = filter_type


class ListDailyOrderSummaryResponse(BaseRequest):
    """
    查询日订单汇总数据返回-响应

    :type summary_list: list
    :param summary_list: 汇总数据列表
    """
    def __init__(
        self,
        summary_list = None
    ):
        super().__init__()
        self.summary_list = summary_list


class ListDailyOrderSummary(BaseRequest):
    """
    日订单汇总数据详情-响应

    :type date: string
    :param date: 订单查询日期，格式：yyyy-MM-dd

    :type success: DailyOrderSummary
    :param success: 成功订单汇总

    :type processing: DailyOrderSummary
    :param processing: 处理中订单汇总

    :type failed: DailyOrderSummary
    :param failed: 失败订单汇总
    """
    def __init__(
        self,
        date = None,
        success = None,
        processing = None,
        failed = None
    ):
        super().__init__()
        self.date = date
        self.success = success
        self.processing = processing
        self.failed = failed


class DailyOrderSummary(BaseRequest):
    """
    日订单汇总详情-响应

    :type order_num: int
    :param order_num: 订单数量

    :type pay: string
    :param pay: 订单金额

    :type broker_fee: string
    :param broker_fee: 应收综合服务主体加成服务费金额

    :type broker_real_fee: string
    :param broker_real_fee: 应收余额账户支出加成服务费金额

    :type broker_rebate_fee: string
    :param broker_rebate_fee: 应收加成服务费抵扣金额

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
    """
    def __init__(
        self,
        order_num = None,
        pay = None,
        broker_fee = None,
        broker_real_fee = None,
        broker_rebate_fee = None,
        user_fee = None,
        received_broker_fee = None,
        received_broker_real_fee = None,
        received_broker_deduct_fee = None,
        received_user_fee = None
    ):
        super().__init__()
        self.order_num = order_num
        self.pay = pay
        self.broker_fee = broker_fee
        self.broker_real_fee = broker_real_fee
        self.broker_rebate_fee = broker_rebate_fee
        self.user_fee = user_fee
        self.received_broker_fee = received_broker_fee
        self.received_broker_real_fee = received_broker_real_fee
        self.received_broker_deduct_fee = received_broker_deduct_fee
        self.received_user_fee = received_user_fee


class ListMonthlyOrderSummaryRequest(BaseRequest):
    """
    查询月订单汇总数据请求-请求

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type channel: string
    :param channel: 支付路径，银行卡、支付宝、微信

    :type month: string
    :param month: 汇总月份，格式：yyyy-MM

    :type filter_type: string
    :param filter_type: 筛选类型，apply：按订单创建时间汇总 complete：按订单完成时间汇总
    """
    def __init__(
        self,
        broker_id = None,
        dealer_id = None,
        channel = None,
        month = None,
        filter_type = None
    ):
        super().__init__()
        self.broker_id = broker_id
        self.dealer_id = dealer_id
        self.channel = channel
        self.month = month
        self.filter_type = filter_type


class ListMonthlyOrderSummaryResponse(BaseRequest):
    """
    查询月订单汇总数据返回-响应

    :type summary: ListMonthlyOrderSummary
    :param summary: 汇总数据列表
    """
    def __init__(
        self,
        summary = None
    ):
        super().__init__()
        self.summary = summary


class ListMonthlyOrderSummary(BaseRequest):
    """
    月订单汇总数据详情-响应

    :type success: MonthlyOrderSummary
    :param success: 成功订单汇总

    :type processing: MonthlyOrderSummary
    :param processing: 处理中订单汇总

    :type failed: MonthlyOrderSummary
    :param failed: 失败订单汇总
    """
    def __init__(
        self,
        success = None,
        processing = None,
        failed = None
    ):
        super().__init__()
        self.success = success
        self.processing = processing
        self.failed = failed


class MonthlyOrderSummary(BaseRequest):
    """
    月订单汇总详情-响应

    :type order_num: int
    :param order_num: 订单数量

    :type pay: string
    :param pay: 订单金额

    :type broker_fee: string
    :param broker_fee: 应收综合服务主体加成服务费金额

    :type broker_real_fee: string
    :param broker_real_fee: 应收余额账户支出加成服务费金额

    :type broker_rebate_fee: string
    :param broker_rebate_fee: 应收加成服务费抵扣金额

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
    """
    def __init__(
        self,
        order_num = None,
        pay = None,
        broker_fee = None,
        broker_real_fee = None,
        broker_rebate_fee = None,
        user_fee = None,
        received_broker_fee = None,
        received_broker_real_fee = None,
        received_broker_deduct_fee = None,
        received_user_fee = None
    ):
        super().__init__()
        self.order_num = order_num
        self.pay = pay
        self.broker_fee = broker_fee
        self.broker_real_fee = broker_real_fee
        self.broker_rebate_fee = broker_rebate_fee
        self.user_fee = user_fee
        self.received_broker_fee = received_broker_fee
        self.received_broker_real_fee = received_broker_real_fee
        self.received_broker_deduct_fee = received_broker_deduct_fee
        self.received_user_fee = received_user_fee
