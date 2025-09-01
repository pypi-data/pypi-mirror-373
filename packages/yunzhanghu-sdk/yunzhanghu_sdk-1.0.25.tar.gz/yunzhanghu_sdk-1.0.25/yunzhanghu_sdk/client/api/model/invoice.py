"""发票开具"""

from ...base import BaseRequest


class GetInvoiceStatRequest(BaseRequest):
    """
    查询平台企业已开具和待开具发票金额请求-请求

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type year: int
    :param year: 查询年份
    """
    def __init__(
        self,
        broker_id = None,
        dealer_id = None,
        year = None
    ):
        super().__init__()
        self.broker_id = broker_id
        self.dealer_id = dealer_id
        self.year = year


class GetInvoiceStatResponse(BaseRequest):
    """
    查询平台企业已开具和待开具发票金额返回-响应

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type invoiced: string
    :param invoiced: 已开发票金额

    :type invoicing: string
    :param invoicing: 开票中发票金额

    :type not_invoiced: string
    :param not_invoiced: 待开发票金额
    """
    def __init__(
        self,
        dealer_id = None,
        broker_id = None,
        invoiced = None,
        invoicing = None,
        not_invoiced = None
    ):
        super().__init__()
        self.dealer_id = dealer_id
        self.broker_id = broker_id
        self.invoiced = invoiced
        self.invoicing = invoicing
        self.not_invoiced = not_invoiced


class GetInvoiceAmountRequest(BaseRequest):
    """
    查询可开具发票额度和发票开具信息请求-请求

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


class GetInvoiceAmountResponse(BaseRequest):
    """
    查询可开具发票额度和发票开具信息返回-响应

    :type amount: string
    :param amount: 可开票额度

    :type bank_name_account: list
    :param bank_name_account: 系统支持的开户行及账号

    :type goods_services_name: list
    :param goods_services_name: 系统支持的货物或应税劳务、服务名称
    """
    def __init__(
        self,
        amount = None,
        bank_name_account = None,
        goods_services_name = None
    ):
        super().__init__()
        self.amount = amount
        self.bank_name_account = bank_name_account
        self.goods_services_name = goods_services_name


class ApplyInvoiceRequest(BaseRequest):
    """
    发票开具申请请求-请求

    :type invoice_apply_id: string
    :param invoice_apply_id: 发票申请编号

    :type broker_id: string
    :param broker_id: 综合服务主体 ID

    :type dealer_id: string
    :param dealer_id: 平台企业 ID

    :type amount: string
    :param amount: 申请开票金额

    :type invoice_type: string
    :param invoice_type: 发票类型

    :type bank_name_account: string
    :param bank_name_account: 开户行及账号

    :type goods_services_name: string
    :param goods_services_name: 货物或应税劳务、服务名称

    :type remark: string
    :param remark: 发票备注

    :type receive_emails: list
    :param receive_emails: 发票接收邮箱

    :type invoice_media: string
    :param invoice_media: 发票介质
    """
    def __init__(
        self,
        invoice_apply_id = None,
        broker_id = None,
        dealer_id = None,
        amount = None,
        invoice_type = None,
        bank_name_account = None,
        goods_services_name = None,
        remark = None,
        receive_emails = None,
        invoice_media = None
    ):
        super().__init__()
        self.invoice_apply_id = invoice_apply_id
        self.broker_id = broker_id
        self.dealer_id = dealer_id
        self.amount = amount
        self.invoice_type = invoice_type
        self.bank_name_account = bank_name_account
        self.goods_services_name = goods_services_name
        self.remark = remark
        self.receive_emails = receive_emails
        self.invoice_media = invoice_media


class ApplyInvoiceResponse(BaseRequest):
    """
    发票开具申请返回-响应

    :type application_id: string
    :param application_id: 发票申请单 ID

    :type count: int
    :param count: 发票张数
    """
    def __init__(
        self,
        application_id = None,
        count = None
    ):
        super().__init__()
        self.application_id = application_id
        self.count = count


class GetInvoiceStatusRequest(BaseRequest):
    """
    查询发票开具申请状态请求-请求

    :type invoice_apply_id: string
    :param invoice_apply_id: 发票申请编号

    :type application_id: string
    :param application_id: 发票申请单 ID
    """
    def __init__(
        self,
        invoice_apply_id = None,
        application_id = None
    ):
        super().__init__()
        self.invoice_apply_id = invoice_apply_id
        self.application_id = application_id


class GetInvoiceStatusResponse(BaseRequest):
    """
    查询发票开具申请状态返回-响应

    :type status: string
    :param status: 申请结果

    :type count: int
    :param count: 发票张数

    :type price_tax_amount: string
    :param price_tax_amount: 价税合计

    :type price_amount: string
    :param price_amount: 不含税金额

    :type tax_amount: string
    :param tax_amount: 税额

    :type invoice_type: string
    :param invoice_type: 发票类型

    :type customer_name: string
    :param customer_name: 购方名称

    :type customer_tax_num: string
    :param customer_tax_num: 纳税人识别号

    :type customer_address_tel: string
    :param customer_address_tel: 购方地址、电话

    :type bank_name_account: string
    :param bank_name_account: 开户行及账号

    :type goods_services_name: string
    :param goods_services_name: 货物或应税劳务、服务名称

    :type remark: string
    :param remark: 发票备注

    :type post_type: string
    :param post_type: 邮寄类型

    :type waybill_number: list
    :param waybill_number: 快递单号

    :type reject_reason: string
    :param reject_reason: 驳回原因

    :type invoice_media: string
    :param invoice_media: 发票介质
    """
    def __init__(
        self,
        status = None,
        count = None,
        price_tax_amount = None,
        price_amount = None,
        tax_amount = None,
        invoice_type = None,
        customer_name = None,
        customer_tax_num = None,
        customer_address_tel = None,
        bank_name_account = None,
        goods_services_name = None,
        remark = None,
        post_type = None,
        waybill_number = None,
        reject_reason = None,
        invoice_media = None
    ):
        super().__init__()
        self.status = status
        self.count = count
        self.price_tax_amount = price_tax_amount
        self.price_amount = price_amount
        self.tax_amount = tax_amount
        self.invoice_type = invoice_type
        self.customer_name = customer_name
        self.customer_tax_num = customer_tax_num
        self.customer_address_tel = customer_address_tel
        self.bank_name_account = bank_name_account
        self.goods_services_name = goods_services_name
        self.remark = remark
        self.post_type = post_type
        self.waybill_number = waybill_number
        self.reject_reason = reject_reason
        self.invoice_media = invoice_media


class GetInvoiceInformationRequest(BaseRequest):
    """
    查询发票信息请求-请求

    :type invoice_apply_id: string
    :param invoice_apply_id: 发票申请编号

    :type application_id: string
    :param application_id: 发票申请单 ID
    """
    def __init__(
        self,
        invoice_apply_id = None,
        application_id = None
    ):
        super().__init__()
        self.invoice_apply_id = invoice_apply_id
        self.application_id = application_id


class GetInvoiceInformationResponse(BaseRequest):
    """
    查询发票信息返回-响应

    :type information: list
    :param information: 发票信息
    """
    def __init__(
        self,
        information = None
    ):
        super().__init__()
        self.information = information


class InformationDataInfo(BaseRequest):
    """
    查询发票信息返回-响应

    :type goods_services_name: string
    :param goods_services_name: 货物或应税劳务、服务名称

    :type invoice_num: string
    :param invoice_num: 发票号码

    :type invoice_code: string
    :param invoice_code: 发票代码

    :type price_amount: string
    :param price_amount: 不含税金额

    :type tax_amount: string
    :param tax_amount: 税额

    :type tax_rate: string
    :param tax_rate: 税率

    :type price_tax_amount: string
    :param price_tax_amount: 价税合计

    :type invoiced_date: string
    :param invoiced_date: 开票日期

    :type status: string
    :param status: 发票状态
    """
    def __init__(
        self,
        goods_services_name = None,
        invoice_num = None,
        invoice_code = None,
        price_amount = None,
        tax_amount = None,
        tax_rate = None,
        price_tax_amount = None,
        invoiced_date = None,
        status = None
    ):
        super().__init__()
        self.goods_services_name = goods_services_name
        self.invoice_num = invoice_num
        self.invoice_code = invoice_code
        self.price_amount = price_amount
        self.tax_amount = tax_amount
        self.tax_rate = tax_rate
        self.price_tax_amount = price_tax_amount
        self.invoiced_date = invoiced_date
        self.status = status


class BankNameAccount(BaseRequest):
    """
    系统支持的开户行及账号-响应

    :type item: string
    :param item: 开户行及账号

    :type default: bool
    :param default: 是否为默认值
    """
    def __init__(
        self,
        item = None,
        default = None
    ):
        super().__init__()
        self.item = item
        self.default = default


class GoodsServicesName(BaseRequest):
    """
    系统支持的货物或应税劳务、服务名称-响应

    :type item: string
    :param item: 货物或应税劳务、服务名称

    :type default: bool
    :param default: 是否为默认值
    """
    def __init__(
        self,
        item = None,
        default = None
    ):
        super().__init__()
        self.item = item
        self.default = default


class GetInvoiceFileRequest(BaseRequest):
    """
    下载 PDF 版发票请求-请求

    :type invoice_apply_id: string
    :param invoice_apply_id: 发票申请编号

    :type application_id: string
    :param application_id: 发票申请单 ID
    """
    def __init__(
        self,
        invoice_apply_id = None,
        application_id = None
    ):
        super().__init__()
        self.invoice_apply_id = invoice_apply_id
        self.application_id = application_id


class GetInvoiceFileResponse(BaseRequest):
    """
    下载 PDF 版发票返回-响应

    :type url: string
    :param url: 下载地址

    :type name: string
    :param name: 文件名称
    """
    def __init__(
        self,
        url = None,
        name = None
    ):
        super().__init__()
        self.url = url
        self.name = name


class SendReminderEmailRequest(BaseRequest):
    """
    发送发票开具成功通知邮件请求-请求

    :type invoice_apply_id: string
    :param invoice_apply_id: 发票申请编号

    :type application_id: string
    :param application_id: 发票申请单 ID
    """
    def __init__(
        self,
        invoice_apply_id = None,
        application_id = None
    ):
        super().__init__()
        self.invoice_apply_id = invoice_apply_id
        self.application_id = application_id


class SendReminderEmailResponse(BaseRequest):
    """
    发送发票开具成功通知邮件返回-响应
    """


class NotifyInvoiceDoneRequest(BaseRequest):
    """
    发票开具完成通知-请求

    :type application_id: string
    :param application_id: 发票申请单 ID

    :type invoice_apply_id: string
    :param invoice_apply_id: 发票申请编号

    :type status: string
    :param status: 申请结果

    :type count: int
    :param count: 发票张数

    :type price_tax_amount: string
    :param price_tax_amount: 价税合计

    :type price_amount: string
    :param price_amount: 不含税金额

    :type tax_amount: string
    :param tax_amount: 税额

    :type invoice_type: string
    :param invoice_type: 发票类型

    :type customer_name: string
    :param customer_name: 购方名称

    :type customer_tax_num: string
    :param customer_tax_num: 纳税人识别号

    :type customer_address_tel: string
    :param customer_address_tel: 购方地址、电话

    :type bank_name_account: string
    :param bank_name_account: 开户行及账号

    :type goods_services_name: string
    :param goods_services_name: 货物或应税劳务、服务名称

    :type remark: string
    :param remark: 发票备注

    :type post_type: string
    :param post_type: 邮寄类型

    :type waybill_number: list
    :param waybill_number: 快递单号

    :type reject_reason: string
    :param reject_reason: 驳回原因

    :type invoice_media: string
    :param invoice_media: 发票介质
    """
    def __init__(
        self,
        application_id = None,
        invoice_apply_id = None,
        status = None,
        count = None,
        price_tax_amount = None,
        price_amount = None,
        tax_amount = None,
        invoice_type = None,
        customer_name = None,
        customer_tax_num = None,
        customer_address_tel = None,
        bank_name_account = None,
        goods_services_name = None,
        remark = None,
        post_type = None,
        waybill_number = None,
        reject_reason = None,
        invoice_media = None
    ):
        super().__init__()
        self.application_id = application_id
        self.invoice_apply_id = invoice_apply_id
        self.status = status
        self.count = count
        self.price_tax_amount = price_tax_amount
        self.price_amount = price_amount
        self.tax_amount = tax_amount
        self.invoice_type = invoice_type
        self.customer_name = customer_name
        self.customer_tax_num = customer_tax_num
        self.customer_address_tel = customer_address_tel
        self.bank_name_account = bank_name_account
        self.goods_services_name = goods_services_name
        self.remark = remark
        self.post_type = post_type
        self.waybill_number = waybill_number
        self.reject_reason = reject_reason
        self.invoice_media = invoice_media
