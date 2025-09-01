"""云账户共享大额 H5"""

from .model.bizlicgxv2h5 import *
from ..base import BaseClient
from ...utils import Utils


class BizlicGxV2H5ServiceClient(BaseClient):
    """云账户共享大额 H5客户端"""

    def __init__(self, config):
        super().__init__(config)

    def gx_v2_h5_get_start_url(self, request: GxV2H5GetStartUrlRequest):
        """ 预启动

        :type request: GxV2H5GetStartUrlRequest
        :param request: the GxV2H5GetStartUrlRequest request parameters class.

        :return: GxV2H5GetStartUrlResponse
        """
        return self._get(
            "/api/aic/sharing-economy/h5/v1/h5url",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def gx_v2_h5_get_aic_status(self, request: GxV2H5GetAicStatusRequest):
        """ 查询个体工商户状态

        :type request: GxV2H5GetAicStatusRequest
        :param request: the GxV2H5GetAicStatusRequest request parameters class.

        :return: GxV2H5GetAicStatusResponse
        """
        return self._get(
            "/api/aic/sharing-economy/h5/v1/status",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )
