"""云账户新经济 H5"""

from .model.bizlicxjjh5 import *
from ..base import BaseClient
from ...utils import Utils


class BizlicXjjH5ServiceClient(BaseClient):
    """云账户新经济 H5客户端"""

    def __init__(self, config):
        super().__init__(config)

    def h5_get_start_url(self, request: H5GetStartUrlRequest):
        """ 预启动

        :type request: H5GetStartUrlRequest
        :param request: the H5GetStartUrlRequest request parameters class.

        :return: H5GetStartUrlResponse
        """
        return self._get(
            "/api/aic/new-economy/h5/v1/h5url",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )

    def h5_eco_city_aic_status(self, request: H5EcoCityAicStatusRequest):
        """ 查询个体工商户状态

        :type request: H5EcoCityAicStatusRequest
        :param request: the H5EcoCityAicStatusRequest request parameters class.

        :return: H5EcoCityAicStatusResponse
        """
        return self._get(
            "/api/aic/new-economy/h5/v1/status",
            request.request_id,
            Utils.copy_dict(request.__dict__)
        )
