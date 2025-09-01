"""连续劳务税费试算"""

from ...base import BaseRequest


class LaborCaculatorRequest(BaseRequest):
    """
    连续劳务税费试算（计算器）请求-请求

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type month_settlement_list: list
    :param month_settlement_list: 月度收入列表
    """
    def __init__(
        self,
        dealer_id = None,
        broker_id = None,
        month_settlement_list = None
    ):
        super().__init__()
        self.dealer_id = dealer_id
        self.broker_id = broker_id
        self.month_settlement_list = month_settlement_list


class MonthSettlement(BaseRequest):
    """
    月度收入-响应

    :type month: int
    :param month: 月份

    :type month_pre_tax_amount: string
    :param month_pre_tax_amount: 月度收入
    """
    def __init__(
        self,
        month = None,
        month_pre_tax_amount = None
    ):
        super().__init__()
        self.month = month
        self.month_pre_tax_amount = month_pre_tax_amount


class LaborCaculatorResponse(BaseRequest):
    """
    连续劳务税费试算（计算器）返回-响应

    :type year_tax_info: YearTaxInfo
    :param year_tax_info: 综合所得汇算清缴

    :type month_tax_list: list
    :param month_tax_list: 月度税务信息列表
    """
    def __init__(
        self,
        year_tax_info = None,
        month_tax_list = None
    ):
        super().__init__()
        self.year_tax_info = year_tax_info
        self.month_tax_list = month_tax_list


class YearTaxInfo(BaseRequest):
    """
    综合所得汇算清缴信息-响应

    :type continuous_month_personal_tax: string
    :param continuous_month_personal_tax: 连续劳务年度个税

    :type personal_tax: string
    :param personal_tax: 综合所得汇算清缴年度个税

    :type deduct_cost: string
    :param deduct_cost: 年度扣除费用

    :type personal_tax_rate: string
    :param personal_tax_rate: 个税税率

    :type deduct_tax: string
    :param deduct_tax: 速算扣除数

    :type total_tax_rate: string
    :param total_tax_rate: 税负率
    """
    def __init__(
        self,
        continuous_month_personal_tax = None,
        personal_tax = None,
        deduct_cost = None,
        personal_tax_rate = None,
        deduct_tax = None,
        total_tax_rate = None
    ):
        super().__init__()
        self.continuous_month_personal_tax = continuous_month_personal_tax
        self.personal_tax = personal_tax
        self.deduct_cost = deduct_cost
        self.personal_tax_rate = personal_tax_rate
        self.deduct_tax = deduct_tax
        self.total_tax_rate = total_tax_rate


class MontTax(BaseRequest):
    """
    月度税务信息-响应

    :type month: int
    :param month: 月份

    :type pre_tax_amount: string
    :param pre_tax_amount: 含增值税收入

    :type excluding_vat_amount: string
    :param excluding_vat_amount: 不含增值税收入

    :type value_added_tax: string
    :param value_added_tax: 增值税

    :type additional_tax: string
    :param additional_tax: 附加税

    :type personal_tax: string
    :param personal_tax: 个税

    :type personal_tax_rate: string
    :param personal_tax_rate: 个税税率

    :type deduct_tax: string
    :param deduct_tax: 速算扣除数

    :type post_tax_amount: string
    :param post_tax_amount: 税后金额

    :type total_tax_rate: string
    :param total_tax_rate: 税负率
    """
    def __init__(
        self,
        month = None,
        pre_tax_amount = None,
        excluding_vat_amount = None,
        value_added_tax = None,
        additional_tax = None,
        personal_tax = None,
        personal_tax_rate = None,
        deduct_tax = None,
        post_tax_amount = None,
        total_tax_rate = None
    ):
        super().__init__()
        self.month = month
        self.pre_tax_amount = pre_tax_amount
        self.excluding_vat_amount = excluding_vat_amount
        self.value_added_tax = value_added_tax
        self.additional_tax = additional_tax
        self.personal_tax = personal_tax
        self.personal_tax_rate = personal_tax_rate
        self.deduct_tax = deduct_tax
        self.post_tax_amount = post_tax_amount
        self.total_tax_rate = total_tax_rate


class CalcTaxRequest(BaseRequest):
    """
    订单税费试算请求-请求

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type real_name: string
    :param real_name: 姓名

    :type id_card: string
    :param id_card: 证件号

    :type pay: string
    :param pay: 订单金额
    """
    def __init__(
        self,
        dealer_id = None,
        broker_id = None,
        real_name = None,
        id_card = None,
        pay = None
    ):
        super().__init__()
        self.dealer_id = dealer_id
        self.broker_id = broker_id
        self.real_name = real_name
        self.id_card = id_card
        self.pay = pay


class CalcTaxResponse(BaseRequest):
    """
    订单税费试算返回-响应

    :type pay: string
    :param pay: 订单金额

    :type tax: string
    :param tax: 税费总额

    :type after_tax_amount: string
    :param after_tax_amount: 税后金额

    :type tax_detail: CalcTaxDetail
    :param tax_detail: 税费明细
    """
    def __init__(
        self,
        pay = None,
        tax = None,
        after_tax_amount = None,
        tax_detail = None
    ):
        super().__init__()
        self.pay = pay
        self.tax = tax
        self.after_tax_amount = after_tax_amount
        self.tax_detail = tax_detail


class CalcTaxDetail(BaseRequest):
    """
    税费明细-响应

    :type personal_tax: string
    :param personal_tax: 应纳个税

    :type value_added_tax: string
    :param value_added_tax: 应纳增值税

    :type additional_tax: string
    :param additional_tax: 应纳附加税费
    """
    def __init__(
        self,
        personal_tax = None,
        value_added_tax = None,
        additional_tax = None
    ):
        super().__init__()
        self.personal_tax = personal_tax
        self.value_added_tax = value_added_tax
        self.additional_tax = additional_tax
