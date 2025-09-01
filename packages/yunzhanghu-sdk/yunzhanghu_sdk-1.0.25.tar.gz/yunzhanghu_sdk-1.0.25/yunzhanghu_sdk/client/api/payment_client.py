"""实时支付"""

from .model.payment import *
from ..base import BaseClient
from ...utils import Utils


class PaymentClient(BaseClient):
    """实时支付客户端"""

    def __init__(self, config):
        super().__init__(config)

    def create_bankpay_order(self, request: CreateBankpayOrderRequest):
        """ 银行卡实时支付

        :type request: CreateBankpayOrderRequest
        :param request: the CreateBankpayOrderRequest request parameters class.

        :return: CreateBankpayOrderResponse
        """
        return self._post(
            "/api/payment/v1/order-bankpay",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def create_alipay_order(self, request: CreateAlipayOrderRequest):
        """ 支付宝实时支付

        :type request: CreateAlipayOrderRequest
        :param request: the CreateAlipayOrderRequest request parameters class.

        :return: CreateAlipayOrderResponse
        """
        return self._post(
            "/api/payment/v1/order-alipay",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def create_wxpay_order(self, request: CreateWxpayOrderRequest):
        """ 微信实时支付

        :type request: CreateWxpayOrderRequest
        :param request: the CreateWxpayOrderRequest request parameters class.

        :return: CreateWxpayOrderResponse
        """
        return self._post(
            "/api/payment/v1/order-wxpay",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def get_order(self, request: GetOrderRequest):
        """ 查询单笔订单信息

        :type request: GetOrderRequest
        :param request: the GetOrderRequest request parameters class.

        :return: GetOrderResponse
        """
        return self._get(
            "/api/payment/v1/query-order",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def get_dealer_va_recharge_account(self, request: GetDealerVARechargeAccountRequest):
        """ 查询平台企业汇款信息

        :type request: GetDealerVARechargeAccountRequest
        :param request: the GetDealerVARechargeAccountRequest request parameters class.

        :return: GetDealerVARechargeAccountResponse
        """
        return self._get(
            "/api/payment/v1/va-account",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def list_account(self, request: ListAccountRequest):
        """ 查询平台企业余额

        :type request: ListAccountRequest
        :param request: the ListAccountRequest request parameters class.

        :return: ListAccountResponse
        """
        return self._get(
            "/api/payment/v1/query-accounts",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def get_ele_receipt_file(self, request: GetEleReceiptFileRequest):
        """ 查询电子回单

        :type request: GetEleReceiptFileRequest
        :param request: the GetEleReceiptFileRequest request parameters class.

        :return: GetEleReceiptFileResponse
        """
        return self._get(
            "/api/payment/v1/receipt/file",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def cancel_order(self, request: CancelOrderRequest):
        """ 取消待支付订单

        :type request: CancelOrderRequest
        :param request: the CancelOrderRequest request parameters class.

        :return: CancelOrderResponse
        """
        return self._post(
            "/api/payment/v1/order/fail",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def retry_order(self, request: RetryOrderRequest):
        """ 重试挂起状态订单

        :type request: RetryOrderRequest
        :param request: the RetryOrderRequest request parameters class.

        :return: RetryOrderResponse
        """
        return self._post(
            "/api/payment/v1/order/retry",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def create_batch_order(self, request: CreateBatchOrderRequest):
        """ 批次下单

        :type request: CreateBatchOrderRequest
        :param request: the CreateBatchOrderRequest request parameters class.

        :return: CreateBatchOrderResponse
        """
        return self._post(
            "/api/payment/v1/order-batch",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def confirm_batch_order(self, request: ConfirmBatchOrderRequest):
        """ 批次确认

        :type request: ConfirmBatchOrderRequest
        :param request: the ConfirmBatchOrderRequest request parameters class.

        :return: ConfirmBatchOrderResponse
        """
        return self._post(
            "/api/payment/v1/confirm-batch",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def query_batch_order(self, request: QueryBatchOrderRequest):
        """ 查询批次订单信息

        :type request: QueryBatchOrderRequest
        :param request: the QueryBatchOrderRequest request parameters class.

        :return: QueryBatchOrderResponse
        """
        return self._get(
            "/api/payment/v1/query-batch",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def cancel_batch_order(self, request: CancelBatchOrderRequest):
        """ 批次撤销

        :type request: CancelBatchOrderRequest
        :param request: the CancelBatchOrderRequest request parameters class.

        :return: CancelBatchOrderResponse
        """
        return self._post(
            "/api/payment/v1/cancel-batch",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def check_user_amount(self, request: CheckUserAmountRequest):
        """ 用户结算金额校验

        :type request: CheckUserAmountRequest
        :param request: the CheckUserAmountRequest request parameters class.

        :return: CheckUserAmountResponse
        """
        return self._post(
            "/api/payment/v1/risk-check/amount",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def get_order_lxlw(self, request: GetOrderLxlwRequest):
        """ 查询劳务模式单笔订单信息

        :type request: GetOrderLxlwRequest
        :param request: the GetOrderLxlwRequest request parameters class.

        :return: GetOrderLxlwResponse
        """
        return self._get(
            "/api/payment/v1/query-order",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )
