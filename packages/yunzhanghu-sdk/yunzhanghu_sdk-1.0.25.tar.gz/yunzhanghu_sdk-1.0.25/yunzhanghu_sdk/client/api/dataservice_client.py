"""对账文件获取"""

from .model.dataservice import *
from ..base import BaseClient
from ...utils import Utils


class DataServiceClient(BaseClient):
    """对账文件获取客户端"""

    def __init__(self, config):
        super().__init__(config)

    def list_daily_order(self, request: ListDailyOrderRequest):
        """ 查询日订单数据

        :type request: ListDailyOrderRequest
        :param request: the ListDailyOrderRequest request parameters class.

        :return: ListDailyOrderResponse
        """
        return self._get(
            "/api/dataservice/v1/orders",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def list_daily_order_v2(self, request: ListDailyOrderV2Request):
        """ 查询日订单数据（支付和退款订单）

        :type request: ListDailyOrderV2Request
        :param request: the ListDailyOrderV2Request request parameters class.

        :return: ListDailyOrderV2Response
        """
        return self._get(
            "/api/dataservice/v2/orders",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def get_daily_order_file(self, request: GetDailyOrderFileRequest):
        """ 查询日订单文件

        :type request: GetDailyOrderFileRequest
        :param request: the GetDailyOrderFileRequest request parameters class.

        :return: GetDailyOrderFileResponse
        """
        return self._get(
            "/api/dataservice/v1/order/downloadurl",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def get_daily_order_file_v2(self, request: GetDailyOrderFileV2Request):
        """ 查询日订单文件（支付和退款订单）

        :type request: GetDailyOrderFileV2Request
        :param request: the GetDailyOrderFileV2Request request parameters class.

        :return: GetDailyOrderFileV2Response
        """
        return self._get(
            "/api/dataservice/v1/order/day/url",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def list_daily_bill(self, request: ListDailyBillRequest):
        """ 查询日流水数据

        :type request: ListDailyBillRequest
        :param request: the ListDailyBillRequest request parameters class.

        :return: ListDailyBillResponse
        """
        return self._get(
            "/api/dataservice/v1/bills",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def get_daily_bill_file_v2(self, request: GetDailyBillFileV2Request):
        """ 查询日流水文件

        :type request: GetDailyBillFileV2Request
        :param request: the GetDailyBillFileV2Request request parameters class.

        :return: GetDailyBillFileV2Response
        """
        return self._get(
            "/api/dataservice/v2/bill/downloadurl",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def list_dealer_recharge_record_v2(self, request: ListDealerRechargeRecordV2Request):
        """ 查询平台企业预付业务服务费记录

        :type request: ListDealerRechargeRecordV2Request
        :param request: the ListDealerRechargeRecordV2Request request parameters class.

        :return: ListDealerRechargeRecordV2Response
        """
        return self._get(
            "/api/dataservice/v2/recharge-record",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def list_balance_daily_statement(self, request: ListBalanceDailyStatementRequest):
        """ 查询余额日账单数据

        :type request: ListBalanceDailyStatementRequest
        :param request: the ListBalanceDailyStatementRequest request parameters class.

        :return: ListBalanceDailyStatementResponse
        """
        return self._get(
            "/api/dataservice/v1/statements-daily",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def list_daily_order_summary(self, request: ListDailyOrderSummaryRequest):
        """ 查询日订单汇总数据

        :type request: ListDailyOrderSummaryRequest
        :param request: the ListDailyOrderSummaryRequest request parameters class.

        :return: ListDailyOrderSummaryResponse
        """
        return self._get(
            "/api/dataservice/v2/order/daily-summary",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def list_monthly_order_summary(self, request: ListMonthlyOrderSummaryRequest):
        """ 查询月订单汇总数据

        :type request: ListMonthlyOrderSummaryRequest
        :param request: the ListMonthlyOrderSummaryRequest request parameters class.

        :return: ListMonthlyOrderSummaryResponse
        """
        return self._get(
            "/api/dataservice/v2/order/monthly-summary",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )
