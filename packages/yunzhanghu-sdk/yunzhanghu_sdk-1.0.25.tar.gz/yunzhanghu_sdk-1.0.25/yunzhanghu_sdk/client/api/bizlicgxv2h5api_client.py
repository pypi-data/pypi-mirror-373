"""云账户共享大额 H5+API"""

from .model.bizlicgxv2h5api import *
from ..base import BaseClient
from ...utils import Utils


class BizlicGxV2H5APIServiceClient(BaseClient):
    """云账户共享大额 H5+API客户端"""

    def __init__(self, config):
        super().__init__(config)

    def gx_v2_h5_api_pre_collect_bizlic_msg(self, request: GxV2H5APIPreCollectBizlicMsgRequest):
        """ 工商实名信息录入

        :type request: GxV2H5APIPreCollectBizlicMsgRequest
        :param request: the GxV2H5APIPreCollectBizlicMsgRequest request parameters class.

        :return: GxV2H5APIPreCollectBizlicMsgResponse
        """
        return self._post(
            "/api/aic/sharing-economy/api-h5/v1/collect",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def gx_v2_h5_api_get_start_url(self, request: GxV2H5APIGetStartUrlRequest):
        """ 预启动

        :type request: GxV2H5APIGetStartUrlRequest
        :param request: the GxV2H5APIGetStartUrlRequest request parameters class.

        :return: GxV2H5APIGetStartUrlResponse
        """
        return self._get(
            "/api/aic/sharing-economy/api-h5/v1/h5url",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def gx_v2_h5_api_get_aic_status(self, request: GxV2H5APIGetAicStatusRequest):
        """ 查询个体工商户状态

        :type request: GxV2H5APIGetAicStatusRequest
        :param request: the GxV2H5APIGetAicStatusRequest request parameters class.

        :return: GxV2H5APIGetAicStatusResponse
        """
        return self._get(
            "/api/aic/sharing-economy/api-h5/v1/status",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )
