"""云账户新经济 H5+API"""

from .model.bizlicxjjh5api import *
from ..base import BaseClient
from ...utils import Utils


class BizlicXjjH5APIServiceClient(BaseClient):
    """云账户新经济 H5+API客户端"""

    def __init__(self, config):
        super().__init__(config)

    def h5_pre_collect_bizlic_msg(self, request: H5PreCollectBizlicMsgRequest):
        """ 工商实名信息录入

        :type request: H5PreCollectBizlicMsgRequest
        :param request: the H5PreCollectBizlicMsgRequest request parameters class.

        :return: H5PreCollectBizlicMsgResponse
        """
        return self._post(
            "/api/aic/new-economy/api-h5/v1/collect",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def h5_api_get_start_url(self, request: H5APIGetStartUrlRequest):
        """ 预启动

        :type request: H5APIGetStartUrlRequest
        :param request: the H5APIGetStartUrlRequest request parameters class.

        :return: H5APIGetStartUrlResponse
        """
        return self._get(
            "/api/aic/new-economy/api-h5/v1/h5url",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def h5_api_eco_city_aic_status(self, request: H5APIEcoCityAicStatusRequest):
        """ 查询个体工商户状态

        :type request: H5APIEcoCityAicStatusRequest
        :param request: the H5APIEcoCityAicStatusRequest request parameters class.

        :return: H5APIEcoCityAicStatusResponse
        """
        return self._get(
            "/api/aic/new-economy/api-h5/v1/status",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )
