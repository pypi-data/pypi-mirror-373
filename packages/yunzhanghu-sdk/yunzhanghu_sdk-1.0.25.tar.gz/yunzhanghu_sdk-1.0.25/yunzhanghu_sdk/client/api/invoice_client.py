"""发票开具"""

from .model.invoice import *
from ..base import BaseClient
from ...utils import Utils


class InvoiceClient(BaseClient):
    """发票开具客户端"""

    def __init__(self, config):
        super().__init__(config)

    def get_invoice_stat(self, request: GetInvoiceStatRequest):
        """ 查询平台企业已开具和待开具发票金额

        :type request: GetInvoiceStatRequest
        :param request: the GetInvoiceStatRequest request parameters class.

        :return: GetInvoiceStatResponse
        """
        return self._get(
            "/api/payment/v1/invoice-stat",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def get_invoice_amount(self, request: GetInvoiceAmountRequest):
        """ 查询可开具发票额度和发票开具信息

        :type request: GetInvoiceAmountRequest
        :param request: the GetInvoiceAmountRequest request parameters class.

        :return: GetInvoiceAmountResponse
        """
        return self._post(
            "/api/invoice/v2/invoice-amount",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def apply_invoice(self, request: ApplyInvoiceRequest):
        """ 发票开具申请

        :type request: ApplyInvoiceRequest
        :param request: the ApplyInvoiceRequest request parameters class.

        :return: ApplyInvoiceResponse
        """
        return self._post(
            "/api/invoice/v2/apply",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def get_invoice_status(self, request: GetInvoiceStatusRequest):
        """ 查询发票开具申请状态

        :type request: GetInvoiceStatusRequest
        :param request: the GetInvoiceStatusRequest request parameters class.

        :return: GetInvoiceStatusResponse
        """
        return self._post(
            "/api/invoice/v2/invoice/invoice-status",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def get_invoice_information(self, request: GetInvoiceInformationRequest):
        """ 查询发票信息

        :type request: GetInvoiceInformationRequest
        :param request: the GetInvoiceInformationRequest request parameters class.

        :return: GetInvoiceInformationResponse
        """
        return self._post(
            "/api/invoice/v2/invoice-face-information",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def get_invoice_file(self, request: GetInvoiceFileRequest):
        """ 下载 PDF 版发票

        :type request: GetInvoiceFileRequest
        :param request: the GetInvoiceFileRequest request parameters class.

        :return: GetInvoiceFileResponse
        """
        return self._post(
            "/api/invoice/v2/invoice/invoice-pdf",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def send_reminder_email(self, request: SendReminderEmailRequest):
        """ 发送发票开具成功通知邮件

        :type request: SendReminderEmailRequest
        :param request: the SendReminderEmailRequest request parameters class.

        :return: SendReminderEmailResponse
        """
        return self._post(
            "/api/invoice/v2/invoice/reminder/email",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )
